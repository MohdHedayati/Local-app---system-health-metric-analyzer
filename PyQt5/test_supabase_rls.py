import jwt  # Requires: pip install PyJWT
import json
from constants import SECRETS_PATH

def check_key_role(api_key):
    """
    Decodes the Supabase JWT to find out if it's 'anon' or 'service_role'.
    """
    try:
        # We don't verify the signature because we just want to read the role
        # from the payload to debug.
        decoded_payload = jwt.decode(api_key, options={"verify_signature": False})
        
        role = decoded_payload.get('role')
        exp = decoded_payload.get('exp')
        
        print(f"--- Key Inspection ---")
        print(f"Role found:  {role}")  # This will be 'anon' or 'service_role'
        print(f"Expiration:  {exp}")
        print(f"----------------------")
        
        return role

    except jwt.DecodeError:
        print("Error: The string provided is not a valid JWT.")
        return None

# --- Usage with your existing code ---

try:
    with open(SECRETS_PATH, 'r') as file:
        secrets = json.load(file)

    # Grab the key you are currently using
    current_key = secrets["service_role_key"]
    
    # Check it immediately
    role = check_key_role(current_key)

    if role == 'anon':
        print("⚠️  WARNING: You are using the ANON key. RLS policies apply.")
    elif role == 'service_role':
        print("✅  CONFIRMED: You are using the SERVICE_ROLE key. RLS is bypassed.")

except Exception as e:
    print(f"Error loading secrets: {e}")