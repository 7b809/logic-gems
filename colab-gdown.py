import gdown
import os
import zipfile

def download_from_drive(file_id, output_name=None, zip_flag=False, extract_folder=None):
    """
    Download file from Google Drive using file_id.
    If zip_flag=True, extract zip and delete zip file.
    """

    if not output_name:
        output_name = file_id

    url = f"https://drive.google.com/uc?id={file_id}"

    print(f"📥 Downloading file from Google Drive...")
    gdown.download(url, output_name, quiet=False)

    if not os.path.exists(output_name):
        raise Exception("Download failed!")

    print(f"✅ Downloaded: {output_name}")

    # If zip file, extract it
    if zip_flag:
        if not zipfile.is_zipfile(output_name):
            raise Exception("File is not a zip archive!")

        if not extract_folder:
            extract_folder = output_name.replace(".zip", "")

        print(f"📦 Extracting zip to: {extract_folder}")
        os.makedirs(extract_folder, exist_ok=True)

        with zipfile.ZipFile(output_name, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        os.remove(output_name)
        print(f"🗑️ Zip file removed: {output_name}")
        print(f"✅ Extracted to folder: {extract_folder}")

    return extract_folder if zip_flag else output_name
