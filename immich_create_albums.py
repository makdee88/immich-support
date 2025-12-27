import requests
from requests.exceptions import HTTPError
from collections import defaultdict
from datetime import datetime
import time
import argparse
from dotenv import load_dotenv
import os

# ================= CONFIG =================

load_dotenv()  # loads .env file
API_KEY = os.getenv("IMMICH_API_KEY")

IMMICH_URL = "http://localhost:2283"

START_YEAR = 2010
END_YEAR = 2025

PAGE_SIZE = 1000
REQUEST_DELAY = 0.2

# ==========================================

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}


def get_all_assets():
    assets = []
    for asset_type in ["IMAGE", "VIDEO"]:
        page = 1
        while True:
            resp = requests.post(
                f"{IMMICH_URL}/api/search/metadata",
                headers=HEADERS,
                json={
                    "page": page,
                    "size": PAGE_SIZE,
                    "type": asset_type,
                    "filters": {},
                },
            )
            if resp.status_code != 200:
                print(resp.text)
                resp.raise_for_status()
            data = resp.json()
            items = data.get("assets", {}).get("items", [])
            if not items:
                break
            assets.extend(items)
            page += 1
            time.sleep(REQUEST_DELAY)
    return assets


def get_existing_albums():
    resp = requests.get(f"{IMMICH_URL}/api/albums", headers=HEADERS)
    resp.raise_for_status()
    return {a["albumName"]: a["id"] for a in resp.json()}


def create_album(name, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Would create album: {name}")
        return None
    resp = requests.post(
        f"{IMMICH_URL}/api/albums",
        headers=HEADERS,
        json={"albumName": name},
    )
    resp.raise_for_status()
    return resp.json()["id"]


def add_assets(album_id, asset_ids, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Would add {len(asset_ids)} assets to album ID {album_id}")
        return

    CHUNK = 200
    for i in range(0, len(asset_ids), CHUNK):
        requests.put(
            f"{IMMICH_URL}/api/albums/{album_id}/assets",
            headers=HEADERS,
            json={"ids": asset_ids[i:i + CHUNK]},
        ).raise_for_status()


def delete_old_albums(flag="folder-based", dry_run=False):
    existing_albums = get_existing_albums()
    deleted = 0
    for name, album_id in existing_albums.items():
        if flag in name:
            if dry_run:
                print(f"[DRY-RUN] Would delete album: {name}")
            else:
                requests.delete(f"{IMMICH_URL}/api/albums/{album_id}", headers=HEADERS).raise_for_status()
                print(f"Deleted album: {name}")
            deleted += 1
    if dry_run:
        print(f"[DRY-RUN] Would delete {deleted} albums matching flag.")
    else:
        print(f"Deleted {deleted} albums matching flag.")

def get_current_user():
    resp = requests.get(f"{IMMICH_URL}/api/users/me", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def get_all_users():
    current_user_id = get_current_user()
    resp = requests.get(f"{IMMICH_URL}/api/users", headers=HEADERS)
    resp.raise_for_status()
    return [
        u["id"]
        for u in resp.json()
        if u["id"] != current_user_id
    ]

def share_album_with_users(album_id, user_ids, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Would share album ID {album_id} with {len(user_ids)} users")
        return

    if not user_ids:
        print(f"No users found to share album {album_id}")
        return

    print(f"Share album: {album_id} with {user_ids}")
    payload = { "albumUsers": [{"userId": uid, "role": "viewer"} for uid in user_ids] }
    print(f"Payload: {payload}")

    try:
        resp = requests.put(
            f"{IMMICH_URL}/api/albums/{album_id}/users",
            headers=HEADERS,
            json=payload,
        )
        resp.raise_for_status()
        print(f"Shared album {album_id} with {len(user_ids)} users")
    except HTTPError as e:
        # Status code + reason
        print("Status:", resp.status_code, resp.reason)

        # Raw response text (often contains the useful error from Immich)
        print("Body:", resp.text)


def main(delete_old=False, dry_run=False):
    if delete_old:
        delete_old_albums(dry_run=dry_run)

    print("Fetching assets...")
    assets = get_all_assets()
    print(f"Total assets found: {len(assets)}")

    grouped = defaultdict(list)
    for asset in assets:
        path = asset.get("originalPath")
        if not path:
            continue
        # Get parent folder
        parent_folder = os.path.dirname(path)
        parent_name = os.path.basename(parent_folder)

        # If folder name matches "data-download-*", use the top folder as album
        if parent_name.startswith("data-download-"):
            top_folder = os.path.basename(os.path.dirname(parent_folder))
            album_name = f"{top_folder} (library)"
        else:
            album_name = f"{parent_name} (folder-based)"

        grouped[album_name].append(asset["id"])

    existing_albums = get_existing_albums()
    user_ids = get_all_users()  # fetch once outside the loop

    for album_name, asset_ids in grouped.items():
        if not asset_ids:
            continue

        if album_name in existing_albums:
            album_id = existing_albums[album_name]
            print(f"Using existing album: {album_name}")
        else:
            album_id = create_album(album_name, dry_run=dry_run)
            if dry_run:
                album_id = f"[DRY-RUN ID for {album_name}]"

        add_assets(album_id, asset_ids, dry_run=dry_run)
        # Share the album with all users
        share_album_with_users(album_id, user_ids, dry_run=dry_run)
        if dry_run:
            print(f"[DRY-RUN] {len(asset_ids)} assets would be added to {album_name}")

    print("Done ✔" + (" (dry-run)" if dry_run else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Immich Folder-based Albums")
    parser.add_argument(
        "--delete-old-albums",
        action="store_true",
        help="Delete previously created folder-based albums before running",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do a dry-run: show album structure without creating anything",
    )
    args = parser.parse_args()
    main(delete_old=args.delete_old_albums, dry_run=args.dry_run)
