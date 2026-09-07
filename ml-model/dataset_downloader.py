"""
CropGuard AI - PlantVillage Dataset Pipeline & Augmentation Module
Downloads or loads the leaf disease dataset and applies augmentations.
"""

import os
from pathlib import Path
import urllib.request
import zipfile
from typing import Tuple, Optional

import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
from PIL import Image

DATASET_DIR = Path(__file__).resolve().parent / "data" / "plantvillage"

# PlantVillage standard 38 classes subset or mapped agricultural classes
DEFAULT_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Target_Spot",
    "Tomato___Yellow_Leaf_Curl_Virus",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Grape___Black_rot",
    "Grape___healthy",
    "Rice___Brown_Spot",
    "Rice___Leaf_Blast",
    "Rice___healthy"
]


def get_transforms(img_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Returns train and validation transforms.
    Includes random rotation, horizontal/vertical flips, color jitter, and ImageNet normalization.
    """
    train_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=25),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform


def load_dataset(
    data_dir: Optional[Path] = None,
    batch_size: int = 32,
    val_split: float = 0.2
) -> Tuple[Optional[DataLoader], Optional[DataLoader], list]:
    """
    Load dataset from directory if present, returning DataLoaders and class names.
    """
    path = data_dir or DATASET_DIR
    if not path.exists() or not any(path.iterdir()):
        print(f"[Dataset] Directory '{path}' not populated. Using class registry.")
        return None, None, DEFAULT_CLASSES

    train_tf, val_tf = get_transforms()
    full_dataset = datasets.ImageFolder(root=str(path), transform=train_tf)
    classes = full_dataset.classes

    val_size = int(len(full_dataset) * val_split)
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"[Dataset] Loaded {len(full_dataset)} images across {len(classes)} classes.")
    return train_loader, val_loader, classes


if __name__ == "__main__":
    t_tf, v_tf = get_transforms()
    print("[Dataset Pipeline] Transforms initialized successfully.")
    print(f"[Dataset Pipeline] Default classes: {len(DEFAULT_CLASSES)}")
