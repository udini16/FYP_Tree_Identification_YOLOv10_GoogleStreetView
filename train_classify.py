import glob

classes = ["Angsana", "Coconut Palm", "Rain Tree", "Royal Palm"]

for file in glob.glob("dataset_detection/images/train/*.txt"):
    with open(file, "r") as f:
        for i, line in enumerate(f, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            cls_id = int(parts[0])
            if cls_id >= len(classes):
                print(f"❌ Invalid class index {cls_id} in {file}, line {i}")
