##Job to sync uploaded images to a NAS which is RAID protected disks
*/15 * * * * ping -c1 -W1 192.168.10.100 >/dev/null 2>&1 && find /root/MobileUpload/upload -mindepth 2 -type f \( -iname '*.jpg' -o -iname '*.mov' -o -iname '*.heic' \) -exec bash -c 'f="{}"; uuid=$(echo "$f" | cut -d/ -f5); mkdir -p "/mnt/ImportantData/PhotosVideos/ImmichMobileUploads/$uuid"; rsync -a --progress "$f" "/mnt/ImportantData/PhotosVideos/ImmichMobileUploads/$uuid/"' \; >> /var/log/mobileupload-cron.log 2>&1

##Job to update external library when NAS is available
*/15 * * * * ping -c1 -W1 192.168.10.100 >/dev/null 2>&1 && curl -X POST -H "x-api-key: <replace_api_key>" http://localhost:2283/api/libraries/630b44a8-5b0a-4b3d-82e0-58568934270c/scan >> /var/log/immich-scan.log 2>&1

##Job to create new albums based on folders
0 * * * * ping -c1 -W1 192.168.10.100 >/dev/null 2>&1 && python3 /opt/immich-app/immich_create_albums.py >> /var/log/immich-album-creation-share.log 2>&1
