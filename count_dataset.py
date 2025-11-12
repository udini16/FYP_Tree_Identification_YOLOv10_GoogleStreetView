import pathlib

# Define the path to your 'train' directory
# pathlib.Path() automatically handles the / or \ slashes
train_dir = pathlib.Path("datasets/trees/images/train")

# This dictionary will hold your counts, e.g., {'Angsana': 150, 'RainTree': 120}
class_counts = {}

# Check if the directory actually exists
if not train_dir.exists():
    print(f"Error: Directory not found at {train_dir}")
    print("Please check the 'train_dir' path in the script.")
else:
    # Loop through each item in the 'train' directory
    for class_folder in train_dir.iterdir():
        
        # Check if the item is a directory (e.g., 'Angsana')
        if class_folder.is_dir():
            # Get the name of the folder (e.g., "Angsana")
            class_name = class_folder.name
            
            # Count how many files are inside this class folder
            # This is a fast way to count files without loading them all into memory
            file_count = sum(1 for item in class_folder.iterdir() if item.is_file())
            
            # Add the count to our dictionary
            class_counts[class_name] = file_count

    # Check if we found any folders
    if not class_counts:
        print(f"No class folders found in {train_dir}")
    else:
        # Sort the dictionary by class name to make it look clean
        sorted_counts = dict(sorted(class_counts.items()))
        
        # Print the final result in your desired format
        print(f"📊 Instances per class: {sorted_counts}")