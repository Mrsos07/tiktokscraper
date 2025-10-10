"""
Setup Google Drive authentication
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.storage.google_drive import GoogleDriveManager
from app.core.logging import log


def main():
    """Setup Google Drive authentication"""
    try:
        log.info("Setting up Google Drive authentication...")
        
        manager = GoogleDriveManager()
        manager.authenticate()
        
        log.info("Google Drive authentication successful!")
        log.info("Credentials saved. You can now use the application.")
        
        # Test by listing root folder
        try:
            files = manager.list_files_in_folder('root', page_size=5)
            log.info(f"Found {len(files)} files in root folder")
        except Exception as e:
            log.warning(f"Could not list root folder: {str(e)}")
        
    except Exception as e:
        log.error(f"Error setting up Google Drive: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
