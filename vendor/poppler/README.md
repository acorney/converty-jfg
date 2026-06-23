# Poppler Windows Binaries

This directory should contain the Poppler Windows build so that Converty can
rasterise scanned PDF pages without requiring a separate user installation.

## How to populate

1. Download the latest release from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract the zip — you'll get a folder like `poppler-24.xx.0/`
3. Copy the contents of that folder here so the structure looks like:

```
vendor/poppler/
  Library/
    bin/
      pdftoppm.exe
      pdfinfo.exe
      ...
```

4. Commit the binaries (they are intentionally tracked in git for zero-install deployment).

The app auto-detects `vendor/poppler/Library/bin/pdftoppm.exe` on launch.
