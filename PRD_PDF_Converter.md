# PRD: PDF Converter Tool
**Version:** 1.1  
**Audience:** Claude Design (UI) + Claude Code (build)  
**Platform:** Windows (primary), local-only, no cloud dependencies

---

## 1. Overview

A desktop GUI tool that converts PDF files — including scanned/image-based documents — into editable formats (DOCX, MD). OCR is performed locally via Tesseract. Designed for non-technical office staff processing client and business documents.

---

## 2. Goals

- Let office staff convert PDFs to editable formats without technical knowledge
- Support both single-file and batch (folder-level) conversion
- Run entirely offline — no data leaves the machine
- Produce clean, readable output with sensible structure preservation
- Be simple enough that no training is required beyond a 2-minute walkthrough

---

## 3. Non-Goals

- No cloud upload or API calls of any kind
- No PDF editing or annotation
- No image extraction or embedded media handling (v1)
- No support for password-protected PDFs (v1)
- No automatic language detection (English only in v1)
- No DOC (legacy format) output — DOCX and MD only

---

## 4. Users

**Primary:** Office admin/support staff at a financial advice firm  
**Technical level:** Low — comfortable with file explorer and basic Windows apps, not with terminals or config files  
**Context:** Processing scanned client documents (statements, forms, signed agreements) for further editing or record-keeping

---

## 5. Core Features

### 5.1 File Input

- **Single file:** Drag a PDF onto the app, or use a file picker button
- **Batch:** Drop a folder or use a folder picker; tool detects all `.pdf` files one level deep by default
- Visual file list shows each file queued for conversion, with status indicators (pending / processing / done / error)

### 5.2 Output Format Selection

- Radio buttons or a dropdown to select output format: **DOCX** or **MD**
- One format per conversion run (not simultaneous multi-format export in v1)
- Output files saved to the same folder as the source PDF by default
- Optional: user can override the output directory via a folder picker

### 5.3 Output File Naming

- Output files named: `original-name-converted.docx` / `original-name-converted.md`
- Hyphens used as separators (not underscores)
- Source filename spaces converted to hyphens (e.g. `Client Statement 2024.pdf` → `client-statement-2024-converted.docx`)
- If a file with that name already exists in the output directory, the user is prompted: overwrite or skip

### 5.4 OCR via Tesseract

- Tool detects whether a PDF has a native text layer
  - If yes: extract text directly (faster, more accurate)
  - If no (image-only/scanned): rasterise pages and run Tesseract OCR
- Tesseract assumed pre-installed; tool validates on launch and shows a clear error if not found
- OCR language: English (`eng`) in v1

### 5.5 Conversion Pipeline (per file)

```
PDF in
  → Detect text layer
    → [Text PDF]  Extract text via pdfplumber / pdftotext
    → [Image PDF] Rasterise pages (pdftoppm) → Tesseract OCR → extracted text
  → Parse extracted text into structured content (headings, paragraphs, lists where detectable)
  → Write output file in selected format
    → DOCX: python-docx
    → MD:   plain markdown text file
  → Delete all temp files (rasterised page images, intermediate text files)
  → Report result (success / file path / error message)
```

### 5.6 Temp File Cleanup

- All temporary files created during processing (rasterised page images, intermediate text) are deleted immediately after each file conversion completes
- Cleanup runs even if conversion fails
- No residual data retained on disk post-run

### 5.7 Progress & Feedback

- Progress bar per file and overall batch progress
- Per-file status: queued → processing → done ✓ / failed ✗
- On failure: plain-English error message (not a stack trace) shown inline
- "Open output folder" button on completion

### 5.8 Run Log

- Plain-text log generated per session: timestamp, source file, output file, status, any errors
- Log is displayed in-app during the session and available to download before closing
- Log is **cleared on close** — not persisted between sessions
- This is a quick-task tool, not a compliance record

---

## 6. UI Design Brief (for Claude Design)

### Layout

- Single-window app, no navigation tabs needed
- Three zones:
  1. **Top:** File/folder input area (drag-and-drop target + picker buttons)
  2. **Middle:** File queue list with per-file status
  3. **Bottom:** Format selector (DOCX / MD), output directory override, Convert button, progress indicators

### Aesthetic

- Clean, minimal, professional — fits a financial services office context
- Light theme by default (Windows native feel)
- No unnecessary chrome, icons, or decorative elements
- Clear visual hierarchy: the Convert button is the dominant CTA

### Key UX Constraints

- No settings screen or config file in v1 — all options visible on the main screen
- Overwrite prompt must be clear and non-alarming: "A file named X already exists. Overwrite it or skip this file?"
- Error states must be human-readable (e.g. "Could not read this file — it may be password-protected")
- Empty state: drag-and-drop zone should have clear instructional copy, not just an icon
- Accessible font sizes (min 13px body text)

### Recommended Stack (for Claude Design to consider)

- Python + tkinter or PyQt6, launched via `.bat` or bundled as `.exe` via PyInstaller
- Consistent with existing internal tooling (Monkey Launcher precedent)
- No installer required — single executable or ZIP drop

---

## 7. Technical Constraints & Assumptions

| Item | Detail |
|---|---|
| OS | Windows 11 (primary), Windows 10 compatible |
| Tesseract | Pre-installed; tool detects on launch, shows error if missing |
| Python | Bundled via PyInstaller (not assumed on end-user machines) |
| LibreOffice | Not required (DOC format dropped) |
| Internet access | None required or used |
| File size | Should handle multi-page documents (50+ pages) without freezing the UI |
| Concurrency | Single-threaded conversion in v1 (batch runs sequentially) |
| Temp files | Deleted after each file completes, regardless of success/failure |

---

## 8. Dependency Stack

| Purpose | Library/Tool |
|---|---|
| PDF text extraction | `pdfplumber` |
| PDF rasterisation | `pdf2image` / `pdftoppm` (Poppler) |
| OCR | `pytesseract` (wrapper for Tesseract) |
| DOCX output | `python-docx` |
| MD output | Custom text formatter (no extra lib needed) |
| GUI | `tkinter` (stdlib) or `PyQt6` |
| Packaging | PyInstaller (produces standalone `.exe`) |

---

## 9. Error Handling

| Scenario | Behaviour |
|---|---|
| Tesseract not found on launch | Blocking error dialog with install instructions; app does not proceed |
| Output file already exists | Prompt user: overwrite or skip (per file) |
| File is password-protected | Skip file, log error, continue batch |
| File is corrupt / unreadable | Skip file, log error, continue batch |
| Output directory not writable | Error shown before conversion starts |
| OCR produces empty output | Warn user — output file still created but flagged in log |
| Temp file cleanup fails | Log warning silently; do not surface to user |

---

## 10. Out of Scope (v1)

- DOC (legacy format) output
- Multi-language OCR
- Table detection and formatting
- Image/figure extraction
- PDF form field extraction
- Side-by-side preview of source vs output
- Cloud sync or sharing
- Persistent run logs across sessions
- User accounts or access control

---

## 11. Success Criteria

- A non-technical staff member can convert a scanned PDF to DOCX in under 60 seconds with no instruction
- Batch of 10 PDFs converts without manual intervention
- No conversion triggers any network request
- Output DOCX is openable and editable in Microsoft Word without errors
- No temp files remain on disk after conversion completes
- Overwrite prompt is clear and does not block the rest of the batch
