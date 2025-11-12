from pathlib import Path
import yaml

# Load dataset.yaml
with open("dataset_detection/data.yaml") as f:
    data = yaml.safe_load(f)

names = data["names"]
labels_dir = Path("dataset_detection/labels/train")

counts = {name: 0 for name in names}

for label_file in labels_dir.glob("*.txt"):
    if label_file.name == "classes.txt":  # 🚫 skip classes.txt
        continue
    with open(label_file) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            cls_id = int(parts[0])
            if 0 <= cls_id < len(names):
                counts[names[cls_id]] += 1
            else:
                print(f"⚠️ Invalid class id {cls_id} in {label_file}")

print("📊 Instances per class:", counts)
