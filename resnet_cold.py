import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast


# Optional wrapper for ONNX export
class ExportWrapper(nn.Module):
    def __init__(self, backbone, classifier):
        super().__init__()
        self.backbone = backbone
        self.classifier = classifier

    def forward(self, x):
        feats = self.backbone(x)
        feats = feats.view(feats.size(0), -1)
        return self.classifier(feats)


def main():
    # -----------------------------
    # CONFIG
    # -----------------------------
    # !!! CHANGE THIS TO YOUR REAL PATH IF NEEDED !!!
    DATA_ROOT = r"C:\Users\LENOVO\Desktop\VLSID\dataset-resnet34\dataset-resnet34"

    BATCH_SIZE = 10
    EPOCHS = 15
    LR = 1e-4

    # For Windows + small dataset, start with num_workers=0 (simpler, avoids issues)
    NUM_WORKERS = 0
    PIN_MEMORY = True

    USE_AMP = False  # automatic mixed precision if on CUDA

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    # -----------------------------
    # DIRECTORIES (match your structure)
    # dataset-resnet34 ->
    #   /trainingdata/{training-defective, training-undefective}
    #   /validation_set/{validation_defective, validation_non_defective}
    #   /test_data/{test-defective, test-non_defective}
    # -----------------------------
    train_dir = os.path.join(DATA_ROOT, "training-dataset")
    val_dir = os.path.join(DATA_ROOT, "validation-dataset")
    test_dir = os.path.join(DATA_ROOT, "test-dataset")

    for p in [train_dir, val_dir, test_dir]:
        if not os.path.exists(p):
            print(f"WARNING: expected directory not found: {p}")

    # -----------------------------
    # TRANSFORMS
    # -----------------------------
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(5),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()
    ])

    eval_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])

    # -----------------------------
    # DATASETS & DATALOADERS
    # -----------------------------
    train_ds = datasets.ImageFolder(train_dir, transform=train_tf)
    val_ds = datasets.ImageFolder(val_dir, transform=eval_tf)
    test_ds = datasets.ImageFolder(test_dir, transform=eval_tf)

    train_dl = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY
    )
    val_dl = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY
    )
    test_dl = DataLoader(
        test_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY
    )

    print("Classes:", train_ds.classes)
    print("Train samples:", len(train_ds),
          "Val samples:", len(val_ds),
          "Test samples:", len(test_ds))

    # -----------------------------
    # MODEL: RESNET34 BACKBONE + NEW CLASSIFIER
    # -----------------------------
    backbone_model = models.resnet34(weights=None)

    # Freeze all parameters in the backbone
    for p in backbone_model.parameters():
        p.requires_grad = False

    # Backbone = all layers except the final fc
    backbone = nn.Sequential(*list(backbone_model.children())[:-1])  # outputs [B, 512, 1, 1]

    # New classifier (trainable)
    classifier = nn.Sequential(
        nn.Linear(backbone_model.fc.in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(128, 1)
    )

    backbone = backbone.to(device)
    classifier = classifier.to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(classifier.parameters(), lr=LR)

    scaler = GradScaler() if (USE_AMP and device.type == "cuda") else None

    # -----------------------------
    # TRAIN / EVAL FUNCTIONS
    # -----------------------------
    def train_one_epoch(epoch_idx: int):
        classifier.train()
        running_loss = 0.0
        n_batches = 0

        for imgs, labels in train_dl:
            imgs = imgs.to(device, non_blocking=True)
            labels = labels.float().to(device, non_blocking=True).unsqueeze(1)

            # 1) Feature extraction with frozen backbone (no grad)
            with torch.no_grad():
                feats = backbone(imgs)  # [B, 512, 1, 1]
            feats = feats.view(feats.size(0), -1)  # [B, 512]

            optimizer.zero_grad()

            # 2) Classifier forward + backward (only this part tracks gradients)
            if scaler is not None:
                with autocast():
                    preds = classifier(feats)
                    loss = criterion(preds, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                preds = classifier(feats)
                loss = criterion(preds, labels)
                loss.backward()
                optimizer.step()

            running_loss += loss.item()
            n_batches += 1

        avg_loss = running_loss / max(1, n_batches)
        print(f"Epoch {epoch_idx + 1} - Train Loss: {avg_loss:.4f}")
        return avg_loss

    def evaluate(loader):
        classifier.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for imgs, labels in loader:
                imgs = imgs.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)

                feats = backbone(imgs)
                feats = feats.view(feats.size(0), -1)

                outputs = torch.sigmoid(classifier(feats))
                preds = (outputs > 0.5).long().squeeze(1)

                correct += (preds == labels).sum().item()
                total += labels.size(0)

        acc = correct / total if total > 0 else 0.0
        return acc

    # -----------------------------
    # TRAINING LOOP
    # -----------------------------
    for epoch in range(EPOCHS):
        train_one_epoch(epoch)
        val_acc = evaluate(val_dl)
        print(f"Epoch {epoch + 1} - Validation Accuracy: {val_acc:.4f}")

    # Final test evaluation
    test_acc = evaluate(test_dl)
    print(f"Test Accuracy: {test_acc:.4f}")

    # -----------------------------
    # SAVE WEIGHTS
    # -----------------------------
    save_path = "resnet34_transfer_binary_split.pth"
    torch.save(
        {
            "backbone_state_dict": backbone.state_dict(),
            "classifier_state_dict": classifier.state_dict(),
            "classes": train_ds.classes,
        },
        save_path,
    )
    print(f"Saved {save_path}")

    # -----------------------------
    # ONNX EXPORT (backbone + classifier wrapped)
    # -----------------------------
    export_model = ExportWrapper(backbone, classifier).to("cpu").eval()
    dummy = torch.randn(1, 3, 224, 224, device="cpu")

    onnx_path = "resnet34_transfer_binary.onnx"
    torch.onnx.export(
        export_model,
        dummy,
        onnx_path,
        input_names=["input"],
        output_names=["output"],
        opset_version=11,
    )
    print(f"Saved {onnx_path}")


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()  
    main()
