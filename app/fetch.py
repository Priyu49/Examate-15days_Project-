import os

import requests


def download_shc_manual():
    os.makedirs("data/raw", exist_ok=True)
    url = "https://soilhealth.dac.gov.in/files/FAQ_Final_English.pdf"
    filepath = os.path.join("data/raw", "FAQ_Final_English.pdf")
    
    try:
        print(f"Downloading SHC manual from {url}...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Successfully downloaded SHC manual to {filepath}")
    except Exception as e:
        print(f"Error downloading SHC manual: {e}")

if __name__ == "__main__":
    download_shc_manual()