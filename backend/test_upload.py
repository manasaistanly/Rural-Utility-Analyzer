import requests
import os
import time

# Create a dummy user first to get a token, or assume auth is disabled/mocked
# For this test we'll just try to hit the endpoint. If it's protected, we need a token.
# Assuming dev environment might have loose auth or we can use the 'demo' user credentials.

API_URL = "http://localhost:8000/api/v1"
IMAGE_PATH = r"C:/Users/Manasai stanly/.gemini/antigravity/brain/2562f80d-f748-47c1-957b-7f400cd319b2/uploaded_image_1767624719742.png"

def login():
    try:
        response = requests.post(
            f"{API_URL}/auth/token",
            data={"username": "demo", "password": "demo123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        print(f"Login Failed: {response.text}")
        return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def upload_bill(token):
    if not os.path.exists(IMAGE_PATH):
        print(f"File not found: {IMAGE_PATH}")
        return

    print(f"Uploading {IMAGE_PATH}...")
    start_time = time.time()
    
    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": f}
            data = {"bill_type": "water"}
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(
                f"{API_URL}/bills/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=60 # 60 second timeout
            )
            
            elapsed = time.time() - start_time
            print(f"Response Time: {elapsed:.2f} seconds")
            
            if response.status_code == 200:
                print("✅ Upload Successful!")
                print(response.json())
            else:
                print(f"❌ Upload Failed: {response.status_code}")
                print(response.text)
                
    except requests.exceptions.Timeout:
        print("❌ Request Timed Out (>60s)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    token = login()
    if token:
        upload_bill(token)
