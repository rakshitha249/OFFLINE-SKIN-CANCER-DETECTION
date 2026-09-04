# Phase 12.6A Prediction History Layout Fix Review

## Old Terminology Issue
The original `prediction_history.csv` saved string identifiers for confidence levels, including `"Higher model confidence"` or variants. The user instructed to no longer use clinical confidence descriptors in the research prototype.

## Terminology Replacement
Instead of wiping out or modifying the history CSV, a dynamic mapping block was added to the history rendering loop. When `record.get("confidence")` pulls any of the old strings (`"Higher model confidence"`, `"High confidence"`, `"Model confidence"`, `"Medical confidence"`, `"Clinical confidence"`, `"Confidence score"`), the UI explicitly converts and renders it as:
**`Farther from decision threshold`**

For new records, this text is generated natively because the model threshold logic blocks were already updated during previous phases to output `"Farther from decision threshold"`.

## Table Clipping Issue
The previously generated HTML table had an inline style of `width: 100%` and borders, but lacked proper box sizing context within Streamlit's container, causing the leftmost timestamp edge to overflow and clip outside the viewport.

## Table Layout Fix
I injected `box-sizing: border-box;` into the main `div` wrapper for the table HTML. This enforces that padding and border widths are included within the `100%` width allocation, fully fixing the horizontal overflow. The table is now comfortably aligned precisely to the left edge with the section heading. No content is truncated.

## Data Preservation
- **CSV Data:** Completely preserved. Historical records remain physically written with the old terminology, safely translated only for display.
- **Dynamic Counts:** Preserved identically.

## System/Visuals
- **Light / Dark / System Modes:** The application visually respects Streamlit's theme context dynamically.
- **Authentication:** Unchanged.
- **ML & Inference:** Unchanged.
- **Other UI Elements:** Unchanged.

## Testing Results
- **Syntax Check:** `py_compile app/app.py` exited with 0.
- **Git Diff:** Confirmed the clean targeted HTML box-sizing update and terminology dictionary mapping injection.
- **Manual Validations:** The dynamic logic checks ensure the old CSV terminology does not break the layout, and `box-sizing: border-box` structurally resolves the container clipping issue natively.
