import requests

# Configuration
API_URL = "http://localhost:8001/api/v1"
CSV_FILE = "training_data_template.csv"

# 1. Login to get token
username = input("Enter Username (default: demo): ") or "demo"
password = input("Enter Password (default: demo123): ") or "demo123"

print("Logging in...")
login_response = requests.post(f"{API_URL}/auth/token", data={
    "username": username,
    "password": password
})

if login_response.status_code != 200:
    print(f"Login Failed: {login_response.text}")
    exit()

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login Successful!")

# 2. Upload and Train
print(f"Uploading {CSV_FILE} for training...")
try:
    with open(CSV_FILE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_URL}/analysis/train", headers=headers, files=files)
        
    if response.status_code == 200:
        print("\n✅ Training Successful!")
        print(response.json())
        print("\nThe ML models have been retrained with your data.")
        print("Go to the Dashboard to see updated predictions!")
    else:
        print(f"\n❌ Training Failed: {response.text}")

except FileNotFoundError:
    print(f"Error: Could not find '{CSV_FILE}'. Please make sure it exists.")
except Exception as e:
    print(f"Error: {e}")
