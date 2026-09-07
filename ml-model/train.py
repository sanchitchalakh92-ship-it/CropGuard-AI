"""
CropGuard AI - Model Training Script
Fine-tunes MobileNetV2 / ResNet18 transfer learning backbone on leaf disease dataset.
"""

import os
import time
import json
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models

from dataset_downloader import load_dataset, DEFAULT_CLASSES

MODEL_SAVE_PATH = Path(__file__).resolve().parent / "model.pt"
METADATA_SAVE_PATH = Path(__file__).resolve().parent / "model_metadata.json"


def build_model(num_classes: int, backbone: str = "mobilenet_v2", pretrained: bool = True):
    """
    Build transfer learning model with custom classifier head.
    """
    if backbone == "mobilenet_v2":
        try:
            weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
            model = models.mobilenet_v2(weights=weights)
        except Exception:
            model = models.mobilenet_v2(pretrained=pretrained)
        
        # Replace classifier
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes)
        )
    elif backbone == "resnet18":
        try:
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            model = models.resnet18(weights=weights)
        except Exception:
            model = models.resnet18(pretrained=pretrained)
        
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, num_classes)
        )
    else:
        raise ValueError(f"Unsupported backbone: {backbone}")

    return model


def train(
    epochs: int = 5,
    lr: float = 0.001,
    backbone: str = "mobilenet_v2",
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
):
    """Run model training loop or export initialized transfer model."""
    train_loader, val_loader, classes = load_dataset()
    num_classes = len(classes)

    print(f"[Train] Target classes ({num_classes}): {classes[:5]}...")
    print(f"[Train] Using device: {device}")

    model = build_model(num_classes=num_classes, backbone=backbone, pretrained=True)
    model = model.to(device)

    # Save model metadata
    metadata = {
        "backbone": backbone,
        "classes": classes,
        "num_classes": num_classes,
        "input_size": [224, 224],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(METADATA_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    if train_loader and val_loader:
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

        print(f"[Train] Starting {epochs} epochs of fine-tuning...")
        for epoch in range(epochs):
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0

            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

            scheduler.step()
            train_acc = 100.0 * correct / total if total > 0 else 0
            print(f"Epoch [{epoch+1}/{epochs}] Loss: {running_loss/total:.4f} Acc: {train_acc:.2f}%")

    # Save state dict and model
    torch.save({
        "state_dict": model.state_dict(),
        "classes": classes,
        "backbone": backbone
    }, MODEL_SAVE_PATH)
    print(f"[Train] Saved trained model to {MODEL_SAVE_PATH}")
    return model


if __name__ == "__main__":
    train(epochs=15)
