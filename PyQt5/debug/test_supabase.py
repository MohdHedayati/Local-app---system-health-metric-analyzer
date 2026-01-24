from supabase import create_client
import uuid
import json

from constants import SECRETS_PATH
try:
    with open(SECRETS_PATH, 'r') as file:
        secrets = json.load(file)
    
    # print("Data successfully loaded into a Python object (likely a dictionary or list):")
    # print(data)
    # print(f"Type of data: {type(data)}")

except FileNotFoundError:
    print("Error: The file 'data.json' was not found.")
except json.JSONDecodeError:
    print("Error: Could not decode JSON from the file. Check for invalid JSON syntax.")

url = secrets["PROJECT_URL"]
key = secrets["service_role_key"]

supabase = create_client(url, key)

data = {
    "user_email": "test@local",
    "raw_data": {},
    "device_name": "arch-linux",
    "os": "Linux",
    "source" : "desktop_app",
    "status" : "pending"

}

res = supabase.table("user_system_reports").insert(data).execute()
print(res)
