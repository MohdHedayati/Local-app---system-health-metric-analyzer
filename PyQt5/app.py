import os
import sys
import json



def load_user_name_from_token():
    # import TOKEN_FILE lazily so child mode doesn't import GUI modules
    try:
        from utils.constants import TOKEN_FILE
    except Exception:
        return None

    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        # Google's userinfo response usually has "name" and "email"
        profile = data.get("profile", {})
        return profile.get("name") or profile.get("email")
    except Exception:
        return None


def main():
    # If started as a subprocess to run monitoring, handle that mode:
    if "--child-get-info" in sys.argv:
        # Run the monitoring loop directly inside this process (no extra console)
        from utils.get_info import main as _get_info_main
        _get_info_main()
        sys.exit(0)

    # Normal GUI startup: import GUI-related modules after child check
    from PyQt5.QtWidgets import QApplication
    from pages.auth import LoginWindow
    from pages.dashboard import DashboardWindow

    app = QApplication(sys.argv)

    # Check token file to decide whether user is already logged in
    user_name = load_user_name_from_token()
    if user_name:
        # Show dashboard directly
        window = DashboardWindow(user_name=user_name)
    else:
        # Show login window
        window = LoginWindow()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
