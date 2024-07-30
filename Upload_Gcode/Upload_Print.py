import os
import requests
import hashlib

def calculate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_and_print_gcode(relative_path, printer_url):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, relative_path)
    upload_url = f"{printer_url}/server/files/upload"
    print_url = f"{printer_url}/printer/print/start"
    
    if os.path.isfile(file_path):
        print(f"File exists at path: {file_path}")
        file_checksum = calculate_checksum(file_path)
        with open(file_path, 'rb') as file:
            files = {
                'file': (os.path.basename(file_path), file, 'application/octet-stream'),
                'root': (None, 'gcodes'),
                'checksum': (None, file_checksum)
            }
            response = requests.post(upload_url, files=files)

        if response.status_code == 201:
            print("File uploaded successfully!")
            uploaded_file_path = response.json().get('item', {}).get('path')
            if uploaded_file_path:
                data = {'filename': uploaded_file_path}
                response = requests.post(print_url, json=data)
                if response.status_code == 200:
                    print("Print started successfully!")
                else:
                    print(f"Failed to start print. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
            else:
                print("Uploaded file path not found in the response.")
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    else:
        print(f"File not found at path: {file_path}")