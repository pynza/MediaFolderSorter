# MediaFolderSorter

A modern GUI application for manually sorting media files from source folders to destination folders with real-time preview.

![Dark themed interface with PyQt6](https://img.shields.io/badge/PyQt6-Dark%20Theme-2d2d2d?style=for-the-badge)

## Overview

MediaFolderSorter is a simple yet powerful tool for organizing your media files. Instead of automatic sorting, it lets you manually preview and categorize each file with a single click or keypress.

![Main interface showing folder selection and configuration](https://github.com/user-attachments/assets/f6f1621b-9214-48ea-9cd3-dececa9aa321)

## Features

### Media Preview
- **Images**: PNG, JPG, JPEG, GIF, BMP, WebP - automatic scaling to fit viewport
- **Videos**: MP4, WebM, MOV, AVI, MKV, FLV - with built-in player controls
- **PDFs**: Page preview using PyMuPDF — flip pages with **PgUp/PgDn**
- **Office documents** (ODT/ODS/ODP/ODG, DOC/DOCX, XLS/XLSX, PPT/PPTX, RTF): embedded thumbnail shown instantly, then full pages rendered via LibreOffice (headless) and cached in `~/.cache/mediafoldersorter/`. The next document in the queue is pre-rendered in the background.
- **Text**: TXT, logs, CSV, JSON, YAML, source code… (and any file that looks like UTF-8 text) in a monospace viewer
- **Markdown**: rendered (MD, MARKDOWN)
- **More images**: TIFF, ICO, SVG

![Media Preview](https://github.com/user-attachments/assets/098beb3d-b4e6-4e41-bd7c-851f125625ac)

### Configurable Keybindings
Assign custom keyboard and mouse shortcuts to any destination folder for lightning-fast sorting.

- **Navigation**: Previous/Next file
- **Undo**: Revert last sort or trash
- **Trash**: Move the current file to the system trash (default key: `Delete`), undoable

### Keep / trash mode
Destination folders are optional: with only source folders you get a simple
keep (Next) / trash (Delete) workflow, like photo-cleanup apps.
- **Destinations**: Assign any key

![Keybindings configuration dialog](https://github.com/user-attachments/assets/6fb3fe79-75b3-4f6a-a0a8-a19dc34bc860)

### Configuration System
- **Save configurations**: Store your folder selections with custom names
- **Load configurations**: Quick switch between saved setups
- **Import/Export**: Share configurations as YAML files
- Configurations stored in `~/.mediafoldersorter/configs/`

![Configuration management dialog](https://github.com/user-attachments/assets/58e92512-46cc-4d56-8436-2376f72504a5)

## Installation

```bash
# Clone the repository
git clone https://github.com/pynza/MediaFolderSorter.git
cd MediaFolderSorter

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

Optional, for office document previews: LibreOffice (`soffice` on `PATH`),
e.g. `sudo apt install libreoffice-core libreoffice-writer libreoffice-calc libreoffice-impress`.
On Debian/Ubuntu (X11/XWayland) Qt6 also needs `libxcb-cursor0`.

## Usage

```bash
python -m src.main
```

### Quick Start

1. **Configure Folders**
   - Click **+ Add Source** to select source folder(s) containing your media files
   - Click **+ Add Destination** to select destination folder(s)
   - Use **⚙️ Config** to save, load, or manage configurations (optional)

2. **Set Keybindings** (Optional)
   - Click **⌨️ Keys** to open the keybindings dialog
   - Click on any field and press a key or mouse button to assign it
   - Warning labels show duplicate keybindings

3. **Start Sorting**
   - Click **Start Sorting**
   - Files are displayed one at a time
   - Click a destination button (or press its key) to move the current file
   - Use **◀** / **▶** buttons (or Left/Right keys) to navigate
   - Press **↩** (or Z) to undo the last sort

4. **Return to Setup**
   - Click **← Config** in the header to change folders or configurations

### Configuration Management

- **Save**: Store current setup with a custom name
- **Load**: Switch between saved configurations
- **Rename/Delete**: Manage your saved configurations
- **Export**: Save configuration to a YAML file
- **Import**: Load configuration from external YAML file

### Keybindings Reference

| Action | Default Key |
|--------|------------|
| Previous file | Left Arrow |
| Next file | Right Arrow |
| Undo last sort | Z |

Additional keybindings can be assigned to destination folders in the keybindings dialog.

## Requirements

| Package | Required | Purpose |
|---------|----------|---------|
| Python | 3.10+ | Runtime |
| PyQt6 | Yes | GUI Framework |
| Pillow | Recommended | Image preview |
| PyMuPDF | Recommended | PDF preview |
| PyYAML | Yes | Config storage |

## License

MIT License
