# MSIX Release Notes

These notes track the Store-oriented packaging decisions for SimpleAudioBookGen.

## Recommended Route

Use MSIX/MSIX upload for Microsoft Store submission. Microsoft recommends MSIX for Store distribution because it provides package identity, clean install/uninstall behavior, Store signing, and update integration.

For a PyInstaller desktop app, the practical flow is:

1. Build the clean PyInstaller folder with `python build.py`.
2. Convert/package the built app folder with MSIX Packaging Tool or a Windows packaging project.
3. Associate the package identity with the reserved Partner Center app.
4. Generate a Store upload package (`.msixupload`) and submit it in Partner Center.

## Runtime Requirements Covered

- The packaged app stores `config.yaml` and `audiobook_gen.log` in `%LOCALAPPDATA%\SimpleAudioBookGen`.
- Bundled runtime resources include `icon.ico`, `.ffmpeg_bin`, `tesseract_bin`, and `audiobook_gen/rules`.
- UPX is disabled by default for release builds. To opt in locally, set `AUDIOBOOKGEN_USE_UPX=1` before running `python build.py`.

## References

- https://learn.microsoft.com/en-us/windows/msix/overview
- https://learn.microsoft.com/en-us/windows/apps/distribute-through-store/how-to-distribute-your-win32-app-through-microsoft-store
- https://learn.microsoft.com/en-us/windows/msix/package/packaging-uwp-apps
