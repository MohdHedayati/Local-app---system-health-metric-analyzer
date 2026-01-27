from utils.path_helper import resource_path, writable_path
# Use writable path for runtime data (history) so bundled exe can write to it.
TOKEN_FILE = writable_path("data/token.json")
DATA_FILE = writable_path("data/history.json")
SECRETS_PATH = resource_path("data/supabase_secrets.json")
CLIENT_SECRETS_PATH = resource_path("data/client_secrets.json")
ICON_PATH = resource_path("data/appiconmain.png")