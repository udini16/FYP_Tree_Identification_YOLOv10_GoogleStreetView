from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings # <-- IMPORTED SETTINGS
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
from collections import Counter
from datetime import datetime
import requests
import json
import os
import csv

# --- Load Model and API Key ---

# Load your trained detection model
# Use os.path.join for cross-platform compatibility
model_path = os.path.join(settings.BASE_DIR, "runs", "train_streetview", "yolov10x_640_streetview_v3", "weights", "best.pt")
model = YOLO(model_path)

# Get API key from settings.py (MUCH SAFER)
API_KEY = settings.GOOGLE_API_KEY 

# --- Views ---

def homepage(request):
    # This view points to your main homepage
    return render(request, "homepage.html")

def scanner(request):
    # This view points to your "streetview.html" scanner page
    return render(request, "streetview.html")

def data_collection(request):
    # This view points to your "index.html" data collection page
    return render(request, "index.html")


@csrf_exempt
def streetview_save(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
        
    data = json.loads(request.body)
    lat, lng = data.get("lat"), data.get("lng")
    heading, pitch, fov = data.get("heading"), data.get("pitch"), data.get("fov")
    label = data.get("label", "Unknown") # Get label from request

    if not all([lat, lng, heading is not None, pitch is not None, fov, label]):
        return JsonResponse({"error": "Missing required data"}, status=400)

    url = (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=640x640&location={lat},{lng}&heading={heading}&pitch={pitch}&fov={fov}&key={API_KEY}"
    )

    response = requests.get(url)
    if "image" not in response.headers.get("Content-Type", ""):
        return JsonResponse({"error": "Google API did not return an image. Check if 'Street View Static API' is enabled in your Google Cloud Console."}, status=400)
    
    # Save inside a specified dataset folder (make sure this path is correct for you)
    output_dir = os.path.join(settings.BASE_DIR, "dataset_collection", label)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{label}_{lat}_{lng}_{heading:.0f}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "wb") as f:
        f.write(response.content)

    return JsonResponse({"message": "Saved", "filename": filepath})


@csrf_exempt
def streetview_scan(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
        
    data = json.loads(request.body)
    lat, lng = data.get("lat"), data.get("lng")
    heading, pitch, fov = data.get("heading"), data.get("pitch"), data.get("fov")

    if not all([lat, lng, heading is not None, pitch is not None, fov]):
        return JsonResponse({"error": "Missing required data"}, status=400)
        
    # High-quality Google Street View request
    url = (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=640x640&location={lat},{lng}"
        f"&heading={heading}&pitch={pitch}&fov={fov}&key={API_KEY}"
    )

    print("📍 Google Street View URL:", url)
    response = requests.get(url)

    if "image" not in response.headers.get("Content-Type", ""):
        return JsonResponse({"error": "Google API did not return an image. Check if 'Street View Static API' is enabled in your Google Cloud Console.", "url": url}, status=400)

    # Save the raw Street View image to media folder
    image = Image.open(BytesIO(response.content))
    
    # Ensure media/scans directory exists
    scan_dir = os.path.join(settings.MEDIA_ROOT, "scans")
    os.makedirs(scan_dir, exist_ok=True)
    
    raw_path = os.path.join(scan_dir, "captured_streetview.jpg")
    image.save(raw_path)

    # Run YOLOv10 detection
    results = model.predict(raw_path, conf=0.25, imgsz=640, verbose=False, augment=True)

    detections = []
    output_paths = []
    all_labels = [] # To store labels for counting

    for i, r in enumerate(results):
        predict_filename = f"predicted_streetview_{i}.jpg"
        predict_path = os.path.join(scan_dir, predict_filename)
        r.save(filename=predict_path)
        
        output_url = os.path.join(settings.MEDIA_URL, "scans", predict_filename).replace("\\", "/")
        output_paths.append(output_url)

        for box in r.boxes:
            label_name = model.names[int(box.cls[0])] 
            all_labels.append(label_name) 
            
            detections.append({
                "class": int(box.cls[0]),
                "label": label_name,
                "confidence": float(box.conf[0]),
                "xyxy": box.xyxy[0].tolist()
            })

    # --- Count trees and save to log file ---
    total_trees = len(detections)
    tree_counts = Counter(all_labels) # e.g., {'Angsana': 2, 'Rain Tree': 1}

    if total_trees > 0:
        try:
            # Ensure log directory exists
            log_dir = os.path.join(settings.MEDIA_ROOT, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # --- THIS IS THE CHANGE ---
            # 1. Save to "treeInventory.csv" as requested
            log_file_path = os.path.join(log_dir, "treeInventory.csv")
            
            # 2. Check if the file already exists (to know if we need headers)
            file_exists = os.path.isfile(log_file_path)

            # 3. Create a summary string of the counts
            counts_str = ", ".join([f"{label}: {count}" for label, count in tree_counts.items()])
            
            # 4. Define the data row as a list
            data_row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                lat,
                lng,
                total_trees,
                counts_str
            ]
            
            # 5. Append the entry to the CSV file
            #    'newline=""' is important for the csv module
            with open(log_file_path, "a", encoding="utf-8", newline="") as f:
                # Create a csv writer object
                writer = csv.writer(f)
                
                # If the file is new, write the headers first
                if not file_exists:
                    headers = ["Timestamp", "Latitude", "Longitude", "Total_Trees", "Counts"]
                    writer.writerow(headers)
                
                # Write the actual data row
                writer.writerow(data_row)
            # --- END OF CHANGE ---

        except Exception as e:
            print(f"⚠️ Error writing to log file: {e}")
            # Don't stop the response, just log the error to the console
    

    return JsonResponse({
        "message": "✅ Scan successful",
        "url": url,
        "outputs": output_paths,
        "detections": detections,
        "tree_counts": tree_counts,
        "total_trees": total_trees
    })
