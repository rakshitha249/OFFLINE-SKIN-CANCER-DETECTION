# Phase 11.3 Manual Authentication Test Plan

## Test 1 — First User Setup
**Expected:**
- Setup page appears when `auth/users.json` is absent/empty.
- Account can be created with valid credentials.
- Password is mathematically hashed and saved.
- No plaintext password is stored.

## Test 2 — Password Mismatch
Enter different passwords in the "Choose a password" and "Confirm password" fields.
**Expected:**
- Account is not created.
- Clear validation message indicates "Passwords do not match."

## Test 3 — Short Password
Use fewer than 8 characters.
**Expected:**
- Account is rejected.
- Clear validation message indicates "Password must be at least 8 characters."

## Test 4 — Successful Login
Use the newly created credentials to log in.
**Expected:**
- Login succeeds.
- Main application (image upload, analysis interface) appears.

## Test 5 — Incorrect Password
Provide an invalid password or username.
**Expected:**
- Generic "Invalid username or password." message appears.
- No enumeration or disclosure of whether the user account actually exists.

## Test 6 — Logout
Click the "Logout" button in the sidebar.
**Expected:**
- Login page reappears.
- Account remains stored locally.
- Prediction history remains intact.

## Test 7 — Existing Application
After logging in:
- Upload a valid project image (e.g., JPEG skin lesion).
- Verify model prediction displays accurately.
- Verify estimated model probability outputs correctly.
- Verify image quality assessment functions.
- Verify Grad-CAM renders correctly.
- Verify Prediction History appends and lists correctly.

## Test 8 — Session Refresh
Refresh the browser tab while authenticated.
**Expected:**
- Streamlit's `st.session_state` behavior should be observed (typically, a manual page refresh clears the session state and returns the user to the login screen, though this is dependent on the specific Streamlit local runtime).

## Test 9 — Missing Checkpoint
Remove `models/best_finetuned_model.pth`, log in successfully.
**Expected:**
- Authentication succeeds.
- Main application gracefully halts with the existing "Model checkpoint is missing..." message.

## Test 10 — Offline Operation
Turn off all network connections (Wi-Fi, Ethernet). Start the application and log in.
**Expected:**
- The authentication process and application execute flawlessly without internet access.
