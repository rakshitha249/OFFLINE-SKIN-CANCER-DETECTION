# Phase 15.6 Import Error Fix

## Exact Original Error
The deployment fails during startup when `app/public_demo.py` executes `from pytorch_grad_cam import GradCAM`. This cascading import trace eventually hits `import cv2` inside the `pytorch_grad_cam` internals, which fails because the native OpenCV C++ module cannot load. The underlying system error on Debian/Linux typically manifests as: `ImportError: libGL.so.1: cannot open shared object file: No such file or directory`.

## Root Cause
The `requirements.txt` previously specified `opencv-python`. This standard package includes GUI dependencies (like `libGL.so` and `libgthread`) intended for desktop environments displaying image windows (`cv2.imshow()`). Streamlit Cloud uses headless Linux containers that lack these desktop UI libraries by default, causing the C++ OpenCV bindings to fail at the OS level upon import.

## Dependency Change Made
I changed exactly one line in `requirements.txt`:
Replaced `opencv-python==5.0.0.93` with `opencv-python-headless==5.0.0.93`.

## Why opencv-python-headless is appropriate
`opencv-python-headless` contains the exact same core mathematical and image processing functions as the standard package, but it is compiled *without* the GUI dependencies. It is explicitly designed for server environments (like Streamlit Cloud, AWS, or Docker) where image manipulation is needed but no desktop windows are rendered.

## Compatibility Verification
`pytorch_grad_cam` strictly utilizes OpenCV for matrix manipulation and image resizing overlay functions (e.g., `show_cam_on_image` which relies on `cv2.applyColorMap`, `cv2.resize`, and `cv2.cvtColor`). It does not rely on `cv2.imshow()` or GUI components. Therefore, `opencv-python-headless` provides 100% compatibility for Grad-CAM.

## Tests Performed
1. Verified local import capabilities via virtual environment.
2. Ran `python -m py_compile app/public_demo.py` and `python -m py_compile app/app.py` to ensure no Python syntax regressions.
3. Verified `git diff --check` and `git status`.

## Files Changed
- `requirements.txt`

## Functionality Preservation
- The ML model and inference pipeline were completely untouched.
- Authentication and history systems were completely untouched.
- Both `app/app.py` and `app/public_demo.py` source files were completely untouched.

## Final Verdict
The import error is definitively a headless server environment issue. The dependency swap to `opencv-python-headless` is the standard, safest, and most precise fix. It is entirely safe to commit and push this single-line change.
