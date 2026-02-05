# Authentication (Web Dashboard)

Authentication in the Web Dashboard is the gateway that ensures users can only access their own system data. Like the Desktop Agent, the Web Dashboard utilizes **Google OAuth 2.0** powered by Supabase, providing a unified Single Sign-On (SSO) experience across the entire platform.

---

## 🔐 The Streamlit Auth Challenge

Streamlit applications are **stateless** by default. Every time a user interacts with a widget (clicks a button, types text), the entire Python script reruns from top to bottom.

This creates a unique challenge for authentication:
*How do we persist a user's login session across reruns without forcing them to sign in every time they click a button?*

### The Solution: `st.session_state` + Query Parameters

We solve this by utilizing Supabase's implicit grant flow combined with Streamlit's Session State management.

---

## 🔄 The Web Login Flow

1.  **Landing:** Unauthenticated users are presented with a "Login with Google" button.
2.  **Redirect:** Clicking the button redirects the browser to the Supabase Auth URL.
3.  **Provider Handshake:** The user signs in with Google.
4.  **Callback:** Google redirects the user back to the Streamlit app URL, appending the authentication token in the URL fragment (e.g., `https://myapp.streamlit.app/#access_token=...`).
5.  **Token Capture:** On the reload, the Streamlit app detects the URL parameters, extracts the token, verifies it with Supabase, and stores the user object in `st.session_state`.
6.  **URL Cleanup:** The app clears the sensitive token from the URL bar to prevent leakage.

### Implementation Logic

```python
import streamlit as st
from supabase import create_client

def init_auth():
    # 1. Check if user is already logged in via Session State
    if 'user' in st.session_state:
        return True

    # 2. Check for Token in URL (returning from Google)
    query_params = st.query_params
    if 'access_token' in query_params:
        try:
            # Exchange token for session
            session = supabase.auth.get_session_from_url(query_params['access_token'])
            st.session_state['user'] = session.user
            # Clear URL params to hide token
            st.query_params.clear()
            return True
        except Exception as e:
            st.error(f"Login failed: {e}")
            return False

    # 3. Show Login Button
    return False

def login_ui():
    st.title("System Health AI")
    if st.button("Login with Google"):
        # Redirect to Supabase OAuth provider
        auth_url = supabase.auth.get_url_for_provider('google')
        st.link_button("Continue to Google", auth_url)
```

## 🛡 Authorization & Data Security
Authentication (Who are you?) is only half the battle. Authorization (What can you see?) is handled at the database level.

Row Level Security (RLS)
We do not filter data using Python logic alone (e.g., SELECT * FROM reports WHERE user_id = current_user). This is insecure because a bug in the code could leak data.

Instead, we rely on Postgres Row Level Security policies in Supabase:

The web app sends the user's Access Token with every database request.

Supabase confirms the user's identity (UUID).

The Postgres database automatically filters the rows.

Policy: Enable SELECT for users where auth.uid() == user_id

This ensures that even if a malicious user tries to manipulate the API calls from the browser console, the database effectively acts as a blank slate for any data that doesn't belong to them.

## 🔗 Unified Identity
A critical feature of this architecture is the Shared User ID (UID).

When you log in to the Desktop App, Supabase assigns you a specific UUID (e.g., abc-123).

That UUID is attached to every psutil metric uploaded.

When you log in to the Web App with the same Google account, you receive the same UUID (abc-123).

This shared identifier is the "glue" that allows the web dashboard to instantly display the telemetry collected by your desktop agent without any complex pairing codes or manual setup.