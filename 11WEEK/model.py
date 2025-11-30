import os
import json
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import f1_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="PIL")
from PIL import Image

def load_rgb(path):
    return Image.open(path).convert("RGB")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PIN = True if DEVICE == "cuda" else False

DATA_DIR = "../data" 
train_dir = os.path.join(DATA_DIR, "train")
val_dir   = os.path.join(DATA_DIR, "validation")
test_dir  = os.path.join(DATA_DIR, "test")

IMG_SIZE = (224, 224)
BATCH = 32
EPOCHS = 10
NUM_WORKERS = 0

IMNET_MEAN = (0.485, 0.456, 0.406)
IMNET_STD  = (0.229, 0.224, 0.225)

tr_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
    transforms.ToTensor(),
    transforms.Normalize(IMNET_MEAN, IMNET_STD),
])

te_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(IMNET_MEAN, IMNET_STD),
])

train_ds = datasets.ImageFolder(train_dir, transform=tr_tf, loader=load_rgb)
val_ds   = datasets.ImageFolder(val_dir,   transform=te_tf, loader=load_rgb)
test_ds  = datasets.ImageFolder(test_dir,  transform=te_tf, loader=load_rgb)
CLASS_NAMES = train_ds.classes
NUM_CLS = len(CLASS_NAMES)
print("Classes:", NUM_CLS, CLASS_NAMES)

train_dl = DataLoader(train_ds, batch_size=BATCH, shuffle=True,
                      num_workers=NUM_WORKERS, pin_memory=PIN)
val_dl   = DataLoader(val_ds,   batch_size=BATCH, shuffle=False,
                      num_workers=NUM_WORKERS, pin_memory=PIN)
test_dl  = DataLoader(test_ds,  batch_size=BATCH, shuffle=False,
                      num_workers=NUM_WORKERS, pin_memory=PIN)

model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
for param in model.parameters():
    param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, NUM_CLS)

for param in model.layer4.parameters():
    param.requires_grad = True

model = model.to(DEVICE)
#print(model)

def train_one_model(model_name, epochs=20, lr=3e-4, wd=1e-4):
    opt = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr,
        weight_decay=wd
    )
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    criterion = nn.CrossEntropyLoss()

    history = {
        "ep": [], "tr_loss": [], "val_loss": [],
        "val_acc": [], "val_macroF1": [], "images_per_sec": []
    }
    best_acc = 0.0
    best_state = None

    for ep in range(1, epochs + 1):
        # ---- Train ----
        model.train()
        t0 = time.time()
        total_loss, n = 0.0, 0

        for x, y in train_dl:
            x, y = x.to(DEVICE), y.to(DEVICE)
            opt.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            opt.step()

            total_loss += loss.item() * x.size(0)
            n += x.size(0)

        tr_time = time.time() - t0
        ips = len(train_ds) / tr_time

        # ---- Validation ----
        model.eval()
        corr, val_loss, nval = 0, 0.0, 0
        all_y, all_p = [], []

        with torch.no_grad():
            for x, y in val_dl:
                x, y = x.to(DEVICE), y.to(DEVICE)
                out = model(x)
                loss = criterion(out, y)

                val_loss += loss.item() * x.size(0)
                nval += x.size(0)

                pred = out.argmax(1)
                corr += (pred == y).sum().item()

                all_y.extend(y.detach().cpu().tolist())
                all_p.extend(pred.detach().cpu().tolist())

        val_acc = corr / nval
        val_f1 = f1_score(all_y, all_p, average="macro")

        history["ep"].append(ep)
        history["tr_loss"].append(total_loss / n)
        history["val_loss"].append(val_loss / nval)
        history["val_acc"].append(val_acc)
        history["val_macroF1"].append(val_f1)
        history["images_per_sec"].append(ips)

        print(f"[{model_name}] epoch{ep:02d} | "
              f"train_loss {total_loss/n:.4f} | "
              f"val_loss {val_loss/nval:.4f} | "
              f"val_acc {val_acc:.4f} | "
              f"val_macroF1 {val_f1:.4f} | images/sec {ips:.1f}")

        if val_acc > best_acc:
            best_acc = val_acc
            best_state = model.state_dict()

        sch.step()

    # ---- Test ----
    model.load_state_dict(best_state)
    model.eval()

    all_y, all_p = [], []
    with torch.no_grad():
        for x, y in test_dl:
            x = x.to(DEVICE)
            out = model(x)
            pred = out.argmax(1).detach().cpu().numpy()

            all_p.extend(pred)
            all_y.extend(y.numpy())

    all_y = np.array(all_y)
    all_p = np.array(all_p)

    test_acc = (all_y == all_p).mean()
    test_macroF1 = f1_score(all_y, all_p, average="macro")
    cm = confusion_matrix(all_y, all_p)
    report = classification_report(all_y, all_p,
                                   target_names=CLASS_NAMES,
                                   zero_division=0)

    result = {
        "name": model_name,
        "images_per_sec_avg": float(np.mean(history["images_per_sec"])),
        "history": history,
        "test_acc": float(test_acc),
        "test_macroF1": float(test_macroF1),
        "cm": cm,
        "report": report,
    }
    return result

if __name__ == "__main__":
    res = train_one_model("resnet18", epochs=EPOCHS)

    MODEL_PATH = "fruit_veg_resnet18.pt"
    LABEL_PATH = "class_indices.json"

    torch.save(model.state_dict(), MODEL_PATH)
    print(f"모델 위치: {MODEL_PATH}")

    with open(LABEL_PATH, "w", encoding="utf-8") as f:
        json.dump(CLASS_NAMES, f, ensure_ascii=False, indent=2)
    print(f"클래스 라벨: {LABEL_PATH}")

