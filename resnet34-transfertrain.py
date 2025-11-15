import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os

DATA_ROOT = "/path/to/dataset_root"
BATCH_SIZE = 16
EPOCHS = 15
LR = 1e-4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomRotation(5),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor()
])

val_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

train_ds = datasets.ImageFolder(os.path.join(DATA_ROOT, "train"), transform=train_tf)
val_ds   = datasets.ImageFolder(os.path.join(DATA_ROOT, "val"), transform=val_tf)

train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_dl   = DataLoader(val_ds, batch_size=BATCH_SIZE)

# -----------------------------
# TRANSFER LEARNING MODEL
# -----------------------------
model = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
for param in model.parameters():
    param.requires_grad = False  # Freeze backbone

model.fc = nn.Sequential(
    nn.Linear(model.fc.in_features, 128),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(128, 1)
)

model = model.to(device)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=LR)

# -----------------------------
# TRAINING LOOP
# -----------------------------
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for imgs, labels in train_dl:
        imgs, labels = imgs.to(device), labels.float().to(device).unsqueeze(1)

        optimizer.zero_grad()
        preds = model(imgs)
        loss = criterion(preds, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {total_loss/len(train_dl):.4f}")

# -----------------------------
# VALIDATION
# -----------------------------
model.eval()
correct, total = 0, 0
with torch.no_grad():
    for imgs, labels in val_dl:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs = torch.sigmoid(model(imgs))
        preds = (outputs > 0.5).long().squeeze()

        correct += (preds == labels).sum().item()
        total += labels.size(0)

print(f"Validation Accuracy: {correct/total:.4f}")

# -----------------------------
# SAVE
# -----------------------------
torch.save(model.state_dict(), "resnet34_transfer_binary.pth")
print("Saved resnet34_transfer_binary.pth")

# ONNX EXPORT
dummy = torch.randn(1, 3, 224, 224).to(device)
torch.onnx.export(model, dummy, "resnet34_transfer_binary.onnx",
                  input_names=['input'], output_names=['output'],
                  opset_version=11)

print("Saved resnet34_transfer_binary.onnx")
