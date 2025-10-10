"""
Setup Google Drive - Test authentication
"""
from app.uploaders.drive_uploader import DriveUploader
from pathlib import Path

print("=" * 60)
print("Google Drive Setup")
print("=" * 60)
print()

uploader = DriveUploader()

print("Initializing Google Drive service...")
print()

service = uploader.init_service()

if service:
    print("✅ Google Drive connected successfully!")
    print()
    print("Testing folder access...")
    
    try:
        # Test folder access
        folder = service.files().get(
            fileId=uploader.folder_id,
            fields='id, name'
        ).execute()
        
        print(f"✅ Folder found: {folder.get('name')}")
        print(f"   Folder ID: {folder.get('id')}")
        print()
        print("🎉 Setup complete! You can now upload videos to Google Drive.")
        
    except Exception as e:
        print(f"⚠️ Could not access folder: {e}")
        print("   Please check the folder ID and permissions")
else:
    print("❌ Failed to connect to Google Drive")
    print()
    print("Please follow these steps:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project")
    print("3. Enable Google Drive API")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download credentials.json")
    print("6. Place it in the project folder")
    print()
    print("See SETUP_GOOGLE_DRIVE.md for detailed instructions")
