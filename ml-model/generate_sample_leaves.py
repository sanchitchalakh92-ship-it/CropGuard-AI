"""
Generate synthetic realistic sample leaf images for instant UI testing and demonstration.
"""

import os
from pathlib import Path
import numpy as np
import cv2

OUTPUT_DIR_ML = Path(__file__).resolve().parent / "sample_images"
OUTPUT_DIR_FE = Path(__file__).resolve().parent.parent / "frontend" / "assets" / "samples"
OUTPUT_DIR_ML.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR_FE.mkdir(parents=True, exist_ok=True)


def create_leaf_shape(w=400, h=400, base_color=(34, 139, 34)):
    """Create a realistic leaf contour with veins on transparent/neutral background."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (245, 245, 240)  # Off-white background

    # Leaf center and axis
    center = (w // 2, h // 2)
    axes = (w // 3, h // 2 - 20)

    # Draw main leaf body
    cv2.ellipse(img, center, axes, 0, 0, 360, base_color, -1)

    # Leaf serrations / organic shape variation
    pts = np.array([
        [w // 2, 20],
        [w // 2 + 130, h // 3],
        [w // 2 + 110, 2 * h // 3],
        [w // 2, h - 30],
        [w // 2 - 110, 2 * h // 3],
        [w // 2 - 130, h // 3]
    ], np.int32)
    cv2.fillPoly(img, [pts], base_color)

    # Main central vein
    cv2.line(img, (w // 2, 25), (w // 2, h - 30), (25, 110, 25), 3)

    # Lateral veins
    for y in range(80, h - 60, 45):
        cv2.line(img, (w // 2, y), (w // 2 + 80, y - 25), (28, 115, 28), 2)
        cv2.line(img, (w // 2, y), (w // 2 - 80, y - 25), (28, 115, 28), 2)

    return img


def generate_samples():
    samples = {}

    # 1. Healthy Tomato Leaf
    img_healthy = create_leaf_shape(base_color=(46, 139, 87))
    samples["tomato_healthy.jpg"] = img_healthy

    # 2. Tomato Early Blight (Concentric rings & brown spots)
    img_eb = create_leaf_shape(base_color=(60, 145, 75))
    # Concentric rings
    for spot_center in [(170, 160), (230, 240), (190, 300), (250, 140)]:
        # Yellow chlorotic halo
        cv2.circle(img_eb, spot_center, 38, (40, 180, 200), -1)  # Yellow-orange in BGR
        # Brown outer ring
        cv2.circle(img_eb, spot_center, 28, (30, 60, 120), -1)   # Brown in BGR
        # Concentric inner rings
        cv2.circle(img_eb, spot_center, 20, (50, 90, 150), 2)
        cv2.circle(img_eb, spot_center, 12, (20, 40, 90), -1)
    samples["tomato_early_blight.jpg"] = img_eb

    # 3. Potato Late Blight (Water-soaked dark lesions)
    img_lb = create_leaf_shape(base_color=(50, 130, 65))
    for pt in [(160, 130), (240, 200), (180, 260), (220, 320)]:
        cv2.ellipse(img_lb, pt, (45, 30), 25, 0, 360, (25, 160, 190), -1) # Yellow edge
        cv2.ellipse(img_lb, pt, (38, 22), 25, 0, 360, (20, 35, 60), -1)   # Dark necrotic core
    samples["potato_late_blight.jpg"] = img_lb

    # 4. Corn Common Rust (Reddish-brown pustules)
    img_rust = create_leaf_shape(w=360, h=440, base_color=(55, 145, 60))
    for y in range(60, 400, 20):
        for x in [140, 170, 190, 220]:
            if np.random.rand() > 0.3:
                cv2.ellipse(img_rust, (x, y + np.random.randint(-5, 5)), (8, 4), 0, 0, 360, (15, 60, 160), -1)
                cv2.circle(img_rust, (x, y), 2, (10, 30, 90), -1)
    samples["corn_common_rust.jpg"] = img_rust

    # 5. Apple Scab (Olive-black corky lesions)
    img_scab = create_leaf_shape(base_color=(50, 140, 70))
    for pt in [(170, 140), (230, 170), (190, 240), (220, 290), (160, 310)]:
        cv2.circle(img_scab, pt, 24, (30, 130, 150), -1)
        cv2.circle(img_scab, pt, 18, (20, 40, 50), -1)
    samples["apple_scab.jpg"] = img_scab

    # 6. Rice Blast (Spindle/diamond-shaped lesions)
    img_blast = create_leaf_shape(w=300, h=450, base_color=(60, 150, 65))
    for pt in [(150, 120), (150, 200), (140, 280), (160, 350)]:
        # Spindle shape
        pts = np.array([
            [pt[0], pt[1] - 30],
            [pt[0] + 16, pt[1]],
            [pt[0], pt[1] + 30],
            [pt[0] - 16, pt[1]]
        ], np.int32)
        cv2.fillPoly(img_blast, [pts], (40, 160, 180)) # Yellow halo
        pts_core = np.array([
            [pt[0], pt[1] - 20],
            [pt[0] + 10, pt[1]],
            [pt[0], pt[1] + 20],
            [pt[0] - 10, pt[1]]
        ], np.int32)
        cv2.fillPoly(img_blast, [pts_core], (30, 45, 75)) # Grayish-brown center
    samples["rice_blast.jpg"] = img_blast

    for name, img_mat in samples.items():
        p1 = OUTPUT_DIR_ML / name
        p2 = OUTPUT_DIR_FE / name
        cv2.imwrite(str(p1), img_mat)
        cv2.imwrite(str(p2), img_mat)
        print(f"[Samples] Generated {name}")

    print(f"[Samples] Generated {len(samples)} sample leaf images successfully.")


if __name__ == "__main__":
    generate_samples()
