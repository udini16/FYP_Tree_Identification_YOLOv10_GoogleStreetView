import os
from ultralytics import YOLO

# --- IMPORTANT ---
# Specify the path to your training config file here
CONFIG_FILE_PATH = "configs/your_config_file.yaml"
# -----------------


def save_accuracy_report(trainer):
    """
    Callback function to run validation and save the accuracy report
    at the end of the training.
    """
    print("\nTraining complete. Running final validation and saving accuracy report...")

    try:
        # Get the directory where results were saved (e.g., 'runs/train/yolov10x_v3')
        save_dir = trainer.save_dir
        
        # Get the path to the best model weights
        best_model_path = trainer.best_model
        
        if not best_model_path or not os.path.exists(best_model_path):
            print("Could not find 'best.pt' model. Skipping report generation.")
            return

        # Load the best model
        model = YOLO(best_model_path)
        
        # Run validation on the 'val' split
        # It uses the data and imgsz from the original training arguments
        results = model.val(
            data=trainer.args.data,
            imgsz=trainer.args.imgsz,
            split='val',
            verbose=False  # We'll print the summary to the file, not the console
        )
        
        # Define the path for the new report
        report_path = os.path.join(save_dir, "final_accuracy_report.txt")
        
        # Get the full, formatted summary string (the exact table you want)
        summary_string = results.box.summary_string
        
        # Write the report to the file
        with open(report_path, 'w') as f:
            f.write(f"Final Accuracy Report for Model: {best_model_path}\n")
            f.write(f"Configuration File: {CONFIG_FILE_PATH}\n")
            f.write("=" * 40 + "\n\n")
            f.write(summary_string)
            
        print(f"✅ Successfully saved accuracy report to: {report_path}")

    except Exception as e:
        print(f"❌ Failed to generate accuracy report: {e}")


if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Error: Config file not found at '{CONFIG_FILE_PATH}'")
        print("Please update the CONFIG_FILE_PATH variable in run_training.py")
    else:
        # Load the base model from the config file (or you can hardcode 'yolov10x.pt')
        # We'll assume the config file handles which model to use (like in your v2/v3 configs)
        # If your config *doesn't* specify a model, use:
        # model = YOLO('yolov10x.pt') 
        
        # For simplicity, we'll just train using the config file directly
        # The 'model' key in your YAML (e.g., 'yolov10x.pt') will be used.
        model = YOLO() # Create an empty model; 'train' will load the correct one from cfg
        
        # Add our custom callback
        model.add_callback("on_train_end", save_accuracy_report)
        
        print(f"Starting training with config: {CONFIG_FILE_PATH}")
        
        # Start training
        model.train(cfg=CONFIG_FILE_PATH)
