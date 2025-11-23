from django.contrib import admin
from django.urls import path
from detector import views  # Import your app's views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('scanner/', views.scanner, name='scanner'),
    path('data-collection/', views.data_collection, name='data_collection'),
    
    # API Endpoints
    path('streetview-save/', views.streetview_save, name='streetview_save'),
    path('streetview-scan/', views.streetview_scan, name='streetview_scan'),
    
    # NEW: Download Endpoint
    path('download-inventory/', views.download_inventory_csv, name='download_inventory_csv'),
]

# --- THIS IS THE FIX ---
# This block tells the Django development server to serve
# files from your MEDIA_ROOT folder (your 'media' folder)
# when DEBUG is True.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

