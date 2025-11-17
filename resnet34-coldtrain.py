#The whole point is : 
'''
1) We will cold train the resnet34 via the resnet34-coldtrain.py template file 
            We want have split the dataset into three major parts:
                (i) Training = {(100,defective), (105,non-defective)} 
                (ii) Validation = {(100,defective), (105,non-defective)} = Copy of Training set
                (iii) Test = {(25,defective), (25,non-defective)} 
2) The point is we want to somwhat achieve overfitting (meaning the error between training and validation inferences must be negligible)
3) On test set, we will run with new images (to be made later)
4) Ideally this one python script should
        (i) Cold train to overfit on Training set
        (ii) When we validate with Validate set (which is just the copy of training set), it should help us confirm if we managed to overfit it just enough
        (iii) For test set we have no new unique set, that we will do a little later?
        (iv) save the onnx file 
        (v) compare with performance that the of the transfer learning approach 
        (vi) pick the best onnx and swap it out with the onnx being wget in the bash script of the vbx
5) In the VBX bash, we have to
(i) Make a lot of swaps and changes........



6) For recap the vbx flow is : 

How to generate the vectorblox IP (V1000!, unless we want V250, we will have to change that in the script)
        1) ssh into our container
        2) at /home/joeld, the VectorBlox SDK has already been cloned 
        3) cd into /home/joeld/VectorBlox-SDK/ and run "bash install_dependencies.sh"
        4) cd into /home/joeld/VectorBlox-SDK/ and run "source setup_vars.sh"
        5) Confirm whether the virtual environment has been configured and activated
        6) cd $VBX_SDK/tutorials/{network_source}/{network} (for example; cd $VBX_SDK/tutorials/onnx/yolov7, for our case it's cd $VBX_SDK/tutorials/onnx/onnx_resnet34-v1/)
        7) bash {network}.sh (for example; bash yolov7.sh, in our case it's bash onnx_resnet34-v1.sh) 
        8) before running (7) we need to ensure our build flags is set to V1000 or V250 or V500 (accordingly)
The VBXIP gets compiled and creates .vnnx, .hex and a lot many files
'''

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
import os

DATA_ROOT = "/path/to/dataset_root"


BATCH_SIZE = 10 # could be 5 as well i guess # matching the batch_size according to our dataset size 
EPOCHS = 30
LR = 1e-4 # i reduced the learning rate to overfit better

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomRotation(degrees=10),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(brightness=0.01, contrast=0.01),
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

model = models.resnet34(weights=None)  # untrained resnet34 architecture

#note to self - tabulate architecture details in a seperate txt file 

model.fc = nn.Linear(model.fc.in_features, 1) 
model = model.to(device)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

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

torch.save(model.state_dict(), "resnet34_scratch_binary.pth")
print("Saved resnet34_scratch_binary.pth")

dummy = torch.randn(1, 3, 224, 224).to(device)
torch.onnx.export(model, dummy, "resnet34_scratch_binary.onnx",
                  input_names=['input'], output_names=['output'],
                  opset_version=11)
print("Saved resnet34_scratch_binary.onnx")
