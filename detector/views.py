from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, HttpResponse
from django.conf import settings
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

# Adjust paths as necessary based on your Django project structure
model_path = os.path.join(settings.BASE_DIR, "runs", "train_streetview", "yolov10x_640_streetview_v3", "weights", "best.pt")
model = YOLO(model_path)

# Get API key from settings.py 
API_KEY = settings.GOOGLE_API_KEY 

# --- Frontend Views ---

def homepage(request):
    """Renders the main homepage."""
    return render(request, "homepage.html")

def scanner(request):
    """Renders the streetview scanner page."""
    # Pass the API key to the template for the Google Maps script tag
    context = {'GOOGLE_API_KEY': API_KEY}
    return render(request, "streetview.html", context)

def data_collection(request):
    """Renders the data collection page."""
    return render(request, "index.html")

# --- Backend API Views ---

@csrf_exempt
def streetview_save(request):
    """Handles saving new images for training data collection."""
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
        
    data = json.loads(request.body)
    lat, lng = data.get("lat"), data.get("lng")
    heading, pitch, fov = data.get("heading"), data.get("pitch"), data.get("fov")
    label = data.get("label", "Unknown") 

    if not all([lat, lng, heading is not None, pitch is not None, fov, label]):
        return JsonResponse({"error": "Missing required data"}, status=400)

    url = (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=640x640&location={lat},{lng}&heading={heading}&pitch={pitch}&fov={fov}&key={API_KEY}"
    )

    response = requests.get(url)
    if "image" not in response.headers.get("Content-Type", ""):
        return JsonResponse({"error": "Google API did not return an image. Check API key and service activation."}, status=400)
    
    # Save inside a specified dataset folder
    output_dir = os.path.join(settings.BASE_DIR, "dataset_collection", label)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{label}_{lat}_{lng}_{heading:.0f}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "wb") as f:
        f.write(response.content)

    return JsonResponse({"message": "Saved", "filename": filepath})


@csrf_exempt
def streetview_scan(request):
    """
    Scans the current Street View image using YOLOv10, logs detections to a CSV,
    and returns results and ALL log entries.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
        
    data = json.loads(request.body)
    lat, lng = data.get("lat"), data.get("lng")
    heading, pitch, fov = data.get("heading"), data.get("pitch"), data.get("fov")

    if not all([lat, lng, heading is not None, pitch is not None, fov]):
        return JsonResponse({"error": "Missing required data"}, status=400)
        
    # Request high-quality Google Street View image
    url = (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=640x640&location={lat},{lng}"
        f"&heading={heading}&pitch={pitch}&fov={fov}&key={API_KEY}"
    )

    response = requests.get(url)
    if "image" not in response.headers.get("Content-Type", ""):
        return JsonResponse({"error": "Google API did not return an image. Check API key and service activation."}, status=400)

    # Prepare image for model prediction
    image = Image.open(BytesIO(response.content))
    scan_dir = os.path.join(settings.MEDIA_ROOT, "scans")
    os.makedirs(scan_dir, exist_ok=True)
    
    raw_path = os.path.join(scan_dir, "captured_streetview.jpg")
    image.save(raw_path)

    # Run YOLOv10 detection
    results = model.predict(raw_path, conf=0.25, imgsz=640, verbose=False, augment=True)

    detections = []
    output_paths = []
    all_labels = [] 

    for i, r in enumerate(results):
        predict_filename = f"predicted_streetview_{i}.jpg"
        predict_path = os.path.join(scan_dir, predict_filename)
        r.save(filename=predict_path)
        
        # Construct public URL for the image
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

    total_trees = len(detections)
    tree_counts = Counter(all_labels) 

    # --- CSV LOGGING: Write current scan data ---
    log_dir = os.path.join(settings.MEDIA_ROOT, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "treeInventory.csv")
    file_exists = os.path.isfile(log_file_path)
    
    all_logs = [] # Changed variable name to better reflect "all" entries

    if total_trees > 0:
        try:
            counts_str = ", ".join([f"{label}: {count}" for label, count in tree_counts.items()])
            data_row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                lat, lng, total_trees, counts_str
            ]
            with open(log_file_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "Latitude", "Longitude", "Total_Trees", "Counts"])
                writer.writerow(data_row)
        except Exception as e:
            print(f"⚠️ Error writing log: {e}")

    # --- CSV READING: Read ALL log entries for the frontend table ---
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Get ALL entries
                all_logs = list(reader)
                # Reverse the list so the newest entries are at the top of the table
                all_logs.reverse() 
        except Exception as e:
            print(f"Error reading log: {e}")

    return JsonResponse({
        "message": "✅ Scan successful",
        "outputs": output_paths,
        "detections": detections,
        "tree_counts": tree_counts,
        "total_trees": total_trees,
        "recent_logs": all_logs # Returning all logs under the existing key
    })


def download_inventory_csv(request):
    """Handles downloading the complete tree inventory CSV file."""
    log_file_path = os.path.join(settings.MEDIA_ROOT, "logs", "treeInventory.csv")
    if os.path.exists(log_file_path):
        # Serve the file securely
        return FileResponse(open(log_file_path, 'rb'), as_attachment=True, filename="treeInventory.csv")
    else:
        return HttpResponse("No CSV file found. Run a scan first.", status=404)