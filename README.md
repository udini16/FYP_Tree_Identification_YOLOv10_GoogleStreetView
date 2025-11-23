That's great\! A strong `README.md` is essential for any repository. It acts as the project's homepage, explaining what the project does, how to set it up, and how to use it.

Here is a comprehensive structure and content for your **Tree Scanner Project** README, formatted using Markdown.

## 🌳 Tree Scanner: Malaysian Urban Canopy Analysis

-----

## 🧭 Project Overview

The **Tree Scanner** project is an application designed to automatically detect and classify common Malaysian street trees using Computer Vision on Google Street View images.

This project utilizes the **YOLOv10** object detection model, trained on a custom dataset of urban trees (Angsana, Rain Tree, Coconut Palm, Royal Palm). The application allows users to navigate the streets, capture the current view, run the trained model on the image, and log the inventory of detected trees.

### Key Features

  * **🌐 Google Street View Integration:** Interactive map/panorama for real-world testing.
  * **🧠 YOLOv10 Detection:** Fast and accurate detection of specific tree species in urban environments.
  * **💾 Server-Side Logging:** Automatically logs all scan results (coordinates, time, tree counts) to a persistent CSV file (`treeInventory.csv`).
  * **📊 Live Inventory Table:** Displays all historical scan data directly on the web interface.
  * **📥 CSV Export:** Allows users to download the complete **`treeInventory.csv`** for further analysis.

-----

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **Django** | Handles routing, API endpoints, and server-side processing. |
| **Computer Vision** | **YOLOv10 (Ultralytics)** | The core object detection model for tree classification. |
| **Image Source** | **Google Street View Static API** | Fetches the street images for scanning. |
| **Database/Storage** | **CSV Files** | Used for logging tree inventory data (`treeInventory.csv`). |
| **Frontend** | **HTML, CSS, Bootstrap 5, JavaScript** | Interactive interface and display of results. |

-----


