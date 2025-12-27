# Immich Folder-Based Album Creator

This script automates the creation of albums in [Immich](https://immich.app/) based on the folder structure of your images and videos. It supports dry-run mode, deletion of old albums, and automatic sharing with all users.

---

## Features

- **Folder-Based Albums**: Creates albums based on the immediate parent folder of each file.
- **Top-Folder Logic**: If a folder matches `data-download-*`, the album is named using the top-level folder.
- **Skip Empty Albums**: Albums with no assets are automatically skipped.
- **Dry-Run Mode**: Preview album creation and asset assignments without making any changes.
- **Delete Old Albums**: Optionally delete previously created folder-based albums.
- **Automatic Sharing**: Share newly created albums with all Immich users.
- **Safe Rerun**: Existing albums are reused, making repeated runs safe.

---

## Requirements

- Python 3.10+
- `requests` library: install via `pip install requests`
- Access to your Immich server with a valid API key

---

## Installation

1. Clone or download this repository.
2. Place the script in a desired folder on your system.
3. Set your Immich API key as an environment variable:

```bash
export IMMICH_API_KEY="your_api_key_here"

