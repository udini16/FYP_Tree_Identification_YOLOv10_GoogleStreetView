import os
import shutil
import random
from pathlib import Path

# Paths
base_dir = Path("dataset_detection")
images_dir = base_dir / "images"
labels_dir = base_dir / "labels"

# Collect from old train + val into a pool
pool_images = []
for sub in ["train", "val"]:
    for ext in ("*.jpg", "*.png", "*.jpeg"):
        pool_images.extend((images_dir / sub).glob(ext))

print(f"📦 Found {len(pool_images)} images in pool.")

# Make fresh split folders
for split in ["train", "val", "test"]:
    (images_dir / split).mkdir(parents=True, exist_ok=True)
    (labels_dir / split).mkdir(parents=True, exist_ok=True)

# Shuffle for randomness
random.shuffle(pool_images)

# Ratios
train_ratio, val_ratio, test_ratio = 0.7, 0.2, 0.1
n = len(pool_images)
n_train = int(n * train_ratio)
n_val = int(n * val_ratio)
n_test = n - n_train - n_val

train_files = pool_images[:n_train]
val_files = pool_images[n_train:n_train + n_val]
test_files = pool_images[n_train + n_val:]

splits_dict = {
    "train": train_files,
    "val": val_files,
    "test": test_files
}

# Copy images + labels
for split, files in splits_dict.items():
    for img_path in files:
        dst_img = images_dir / split / img_path.name
        if not dst_img.exists():  # ✅ skip if already copied
            shutil.copy(img_path, dst_img)

        # Copy label if exists
        old_label = labels_dir / img_path.parent.name / f"{img_path.stem}.txt"
        dst_label = labels_dir / split / f"{img_path.stem}.txt"
        if old_label.exists() and not dst_label.exists():
            shutil.copy(old_label, dst_label)

print("✅ Dataset split complete!")
print(f"Train: {len(train_files)} | Val: {len(val_files)} | Test: {len(test_files)}")
