import os
import shutil
import random

# Base directories
base_dir = "dataset_detection"
images_dir = os.path.join(base_dir, "images")
labels_dir = os.path.join(base_dir, "labels")

train_img_dir = os.path.join(images_dir, "train")
train_lbl_dir = os.path.join(labels_dir, "train")

# Make sure val/test folders exist
for split in ["val", "test"]:
    os.makedirs(os.path.join(images_dir, split), exist_ok=True)
    os.makedirs(os.path.join(labels_dir, split), exist_ok=True)

# Get all images from train folder
all_images = [f for f in os.listdir(train_img_dir)
              if f.lower().endswith((".jpg", ".png"))]
random.shuffle(all_images)

# Split ratios (keep 70% train, 20% val, 10% test)
n_total = len(all_images)
n_val = int(0.2 * n_total)
n_test = int(0.1 * n_total)

val_images = all_images[:n_val]
test_images = all_images[n_val:n_val + n_test]

def move_files(image_list, split):
    for img in image_list:
        img_src = os.path.join(train_img_dir, img)
        img_dst = os.path.join(images_dir, split, img)
        shutil.move(img_src, img_dst)

        # Move matching label file if exists
        label_name = os.path.splitext(img)[0] + ".txt"
        label_src = os.path.join(train_lbl_dir, label_name)
        label_dst = os.path.join(labels_dir, split, label_name)
        if os.path.exists(label_src):
            shutil.move(label_src, label_dst)

# Move to val and test
move_files(val_images, "val")
move_files(test_images, "test")

print(f"✅ Split complete: {n_total} total images originally in train/")
print(f"📁 {len(all_images) - n_val - n_test} remain in train/")
print(f"📁 {len(val_images)} moved to val/")
print(f"📁 {len(test_images)} moved to test/")
