# Phase 11.1 Local Authentication Design

## Goal
Design a completely localized, offline authentication system to gate access to the main Streamlit application, without introducing external dependencies, cloud services, or real-world medical-grade security constraints.

## Current Application Architecture
The application runs locally via Streamlit (`app/app.py`). It currently loads the model checkpoint directly and relies entirely on Streamlit's implicit local runtime for execution. There is no session state restriction preventing users from directly accessing the model.

## Authentication Flow
1. User accesses the local Streamlit application.
2. The application checks `st.session_state` for an `"authenticated"` flag.
3. If absent or `False`, the user is shown the login interface and the main application rendering halts.
4. User enters a username and password.
5. The application validates the credentials against a local JSON file.
6. Upon successful validation, `st.session_state["authenticated"]` is set to `True`, and the main application interface is rendered.

## Credential Storage
Credentials will be stored locally in an `auth/users.json` file.
The structure will be a JSON dictionary mapping usernames to hashed passwords and salt data:
```json
{
  "username": {
    "salt": "<hex_salt>",
    "hash": "<hex_hash>"
  }
}
```
No plaintext passwords will be stored. 

## Password Hashing
To avoid adding external dependencies, Python's built-in `hashlib` and `secrets` modules will be used.
Algorithm: PBKDF2-HMAC-SHA256.
During setup/login, the password combined with a generated/retrieved salt will be processed with `hashlib.pbkdf2_hmac` over a high number of iterations (e.g., 100,000+).

## First User Setup
Because hardcoding credentials is a security anti-pattern, a first-user setup mechanism will be designed. 
When the application starts, it will check if `auth/users.json` exists. If not, the application will display an "Initialization" screen instead of the login screen.
This screen will prompt the user to establish the primary local workspace account (username and password). 
Upon submission, it generates the salt, hashes the password, saves `auth/users.json`, and automatically transitions to the login screen.

## Session Management
Authentication state will be managed exclusively using Streamlit's `st.session_state`.
`st.session_state["authenticated"] = True` will grant access.
Because it's a localized Streamlit session, closing the browser tab or restarting the Streamlit server naturally terminates the session, requiring re-authentication. No persistent tokens or cookies will be implemented.

## Login UI
The login page will be cleanly structured:
- **Title:** "Offline AI Research Prototype"
- **Description:** "Sign in to access the local analysis workspace."
- **Inputs:** Username (text input) and Password (password input type).
- **Button:** "Login"
- **Error Handling:** "Invalid username or password." shown if validation fails.
No medical terminology (e.g., "Doctor login," "Clinical access") will be used.

## Logout
A "Logout" button will be placed in the Streamlit sidebar of the main application. When clicked, it will set `st.session_state["authenticated"] = False` and call `st.rerun()` to return the user to the login page.

## Offline Operation
The entire authentication process relies solely on the local filesystem (`auth/users.json`) and the local Python standard library. It requires zero network connectivity.

## Security Boundaries
This authentication layer is intended strictly for local access control in a research/educational context. It is **not** an enterprise-grade security system. It does not provide medical-grade HIPAA compliance, does not protect against an attacker with host file-system access, and is not designed for deployment on public web servers.

## Git / Credential Handling
The credential file must not be version-controlled.
The `.gitignore` will be updated (when implementation begins) to exclude `auth/users.json` or the entire `auth/` directory (except a `.gitkeep` if needed).
No default credentials will be shipped in the repository.

## Implementation Plan
1. Update `.gitignore` to exclude `auth/users.json`.
2. Create authentication helper functions in `app/app.py` or a dedicated module `src/auth.py`.
3. Wrap the main logic in `app/app.py` within an authentication check.
4. Implement the First User Setup flow.
5. Implement the Login UI.
6. Test session state integrity and logout functionality.

## Risks and Limitations
- An attacker with access to the local machine can delete `auth/users.json` to trigger the First User Setup and lock out the previous owner, or simply read the models/history directly.
- The system provides application-level gating, not local file encryption.
