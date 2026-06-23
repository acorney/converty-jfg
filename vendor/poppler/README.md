# Poppler Windows Binaries (bundled)

The `Library/bin/` directory contains Poppler v26.02.0 Windows binaries,
committed to the repo so the app runs without any user installation.

Source: https://github.com/oschwartz10612/poppler-windows/releases/tag/v26.02.0-0

Only the runtime binaries (`Library/bin/*.exe` and `*.dll`) are included;
headers and static libs are omitted.

## Updating Poppler

1. Download the new release zip from the link above.
2. Delete `Library/bin/` and replace with the new `Library/bin/` from the zip.
3. Commit.
