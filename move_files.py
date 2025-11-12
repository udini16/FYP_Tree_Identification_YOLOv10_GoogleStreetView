import os
import random
import shutil
import glob

# --- Configuration ---
dataset_dir = 'dataset_detection'
royal_palm_class_id = 3  # !!! IMPORTANT: Verify this ID from your data.yaml !!!
num_images_to_move = 10 # How many images containing Royal Palms to move

# Define source and destination directories
img_train_dir = os.path.join(dataset_dir, 'images', 'train')
lbl_train_dir = os.path.join(dataset_dir, 'labels', 'train')
img_test_dir = os.path.join(dataset_dir, 'images', 'test')
lbl_test_dir = os.path.join(dataset_dir, 'labels', 'test')

# Ensure test directories exist
os.makedirs(img_test_dir, exist_ok=True)
os.makedirs(lbl_test_dir, exist_ok=True)

# --- Find training files containing Royal Palms ---
royal_palm_files = []
label_files = glob.glob(os.path.join(lbl_train_dir, '*.txt'))
print(f"Checking {len(label_files)} label files in {lbl_train_dir}...")

for lbl_file_path in label_files:
    try:
        with open(lbl_file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if not parts: continue # Skip empty lines
                class_id = int(parts[0])
                if class_id == royal_palm_class_id:
                    # Get the base filename (without extension)
                    base_filename = os.path.splitext(os.path.basename(lbl_file_path))[0]
                    royal_palm_files.append(base_filename)
                    break # Move to the next file once a Royal Palm is found
    except Exception as e:
        print(f"Error reading {lbl_file_path}: {e}")

print(f"Found {len(royal_palm_files)} training files containing Royal Palms.")

# --- Select files to move ---
if len(royal_palm_files) < num_images_to_move:
    print(f"Warning: Only found {len(royal_palm_files)} files with Royal Palms. Moving all of them.")
    files_to_move = royal_palm_files
else:
    files_to_move = random.sample(royal_palm_files, num_images_to_move)

print(f"Selected {len(files_to_move)} files to move to the test set.")

# --- Move the selected image and label files ---
moved_count = 0
for base_filename in files_to_move:
    # Find the corresponding image file (handle different extensions)
    img_file_pattern = os.path.join(img_train_dir, base_filename + '.*')
    img_matches = glob.glob(img_file_pattern)

    src_lbl_path = os.path.join(lbl_train_dir, base_filename + '.txt')
    dest_lbl_path = os.path.join(lbl_test_dir, base_filename + '.txt')

    if not img_matches:
        print(f"  Warning: No image file found for label {base_filename}.txt. Skipping.")
        continue

    src_img_path = img_matches[0] # Assume only one image matches
    img_extension = os.path.splitext(src_img_path)[1]
    dest_img_path = os.path.join(img_test_dir, base_filename + img_extension)

    # Move the label file
    if os.path.exists(src_lbl_path):
        try:
            shutil.move(src_lbl_path, dest_lbl_path)
            # Move the image file
            shutil.move(src_img_path, dest_img_path)
            # print(f"  Moved {base_filename}{img_extension} and {base_filename}.txt")
            moved_count += 1
        except Exception as e:
            print(f"  Error moving files for {base_filename}: {e}")
    else:
        print(f"  Warning: Label file {src_lbl_path} not found. Skipping image move.")


print(f"\nSuccessfully moved {moved_count} image/label pairs from train to test.")
print("Please re-run your dataset analysis script to check the new class distribution.")