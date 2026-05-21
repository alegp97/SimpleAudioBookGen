import os
import sys
import shutil
import urllib.request
import zipfile
import subprocess
from pathlib import Path

# Try importing PIL for icon generation
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

PROJECT_ROOT = Path(__file__).parent.absolute()
BUILD_ASSETS_DIR = PROJECT_ROOT / "_build_assets"
FFMPEG_DIR = PROJECT_ROOT / ".ffmpeg_bin"
TESSERACT_DIR = BUILD_ASSETS_DIR / "tesseract_bin"
UPX_DIR = BUILD_ASSETS_DIR / "upx_bin"

def generate_icon():
    print("[*] Generating temporary icon...")
    icon_path = PROJECT_ROOT / "icon.ico"
    if HAS_PIL:
        img = Image.new('RGB', (256, 256), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        # Attempt to load a default font
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        d.text((40, 100), "SABG", fill=(255, 255, 0), font=font)
        img.save(icon_path)
    else:
        # Create a dummy file just so PyInstaller doesn't crash if it requires one
        if not icon_path.exists():
            icon_path.write_bytes(b'')
    return icon_path

def download_ffmpeg():
    print("[*] Preparing FFmpeg...")
    FFMPEG_DIR.mkdir(exist_ok=True)
    ffmpeg_exe = FFMPEG_DIR / "ffmpeg.exe"
    ffprobe_exe = FFMPEG_DIR / "ffprobe.exe"

    if not ffmpeg_exe.exists() or not ffprobe_exe.exists():
        print("    Downloading static build...")
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = FFMPEG_DIR / "ffmpeg.zip"
        urllib.request.urlretrieve(url, zip_path)
        print("    Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe") and not ffmpeg_exe.exists():
                    with zip_ref.open(member) as source, open(ffmpeg_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
                elif member.endswith("ffprobe.exe") and not ffprobe_exe.exists():
                    with zip_ref.open(member) as source, open(ffprobe_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
        zip_path.unlink()
    print("    FFmpeg ready.")

def download_tesseract():
    print("[*] Preparing Tesseract Portable...")
    BUILD_ASSETS_DIR.mkdir(exist_ok=True)
    TESSERACT_DIR.mkdir(exist_ok=True)
    tesseract_exe = TESSERACT_DIR / "tesseract.exe"
    if not tesseract_exe.exists():
        raise FileNotFoundError(
            "Tesseract portable was not found. Place a real tesseract.exe in "
            f"{TESSERACT_DIR} before building, or remove OCR packaging from build.py."
        )

def download_upx():
    print("[*] Preparing UPX...")
    BUILD_ASSETS_DIR.mkdir(exist_ok=True)
    UPX_DIR.mkdir(exist_ok=True)
    upx_exe = UPX_DIR / "upx.exe"
    
    if not upx_exe.exists():
        print("    Downloading UPX...")
        url = "https://github.com/upx/upx/releases/download/v4.2.3/upx-4.2.3-win64.zip"
        zip_path = UPX_DIR / "upx.zip"
        urllib.request.urlretrieve(url, zip_path)
        print("    Extracting UPX...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("upx.exe") and not upx_exe.exists():
                    with zip_ref.open(member) as source, open(upx_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
        zip_path.unlink()
    print("    UPX ready.")

def run_pyinstaller():
    print("[*] Running PyInstaller...")
    try:
        import PyInstaller
    except ImportError:
        raise RuntimeError(
            "PyInstaller is not installed. Install build dependencies first with "
            "'python -m pip install -r requirements.txt'."
        )

    icon_path = PROJECT_ROOT / "icon.ico"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name", "SimpleAudioBookGen",
        f"--icon={icon_path}",
        # Add Icon as data so Qt can load it
        f"--add-data={icon_path};.",
        # Add FFmpeg
        f"--add-data={FFMPEG_DIR};.ffmpeg_bin",
        # Add Tesseract
        f"--add-data={TESSERACT_DIR};tesseract_bin",
        # Explicit hidden imports for dynamic loading libraries
        "--hidden-import", "pytesseract",
        "--hidden-import", "PIL",
        "--hidden-import", "pydub",
        "--hidden-import", "imageio_ffmpeg",
        "--hidden-import", "audiobook_gen",
        # UPX config
        f"--upx-dir={UPX_DIR}",
        # Excludes to reduce size
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        "--exclude-module", "scipy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "tkinter",
        "--exclude-module", "numba",
        "--exclude-module", "PySide6.QtWebEngineCore",
        "--exclude-module", "PySide6.QtWebEngineWidgets",
        "--exclude-module", "PySide6.QtQml",
        "--exclude-module", "PySide6.QtQuick",
        "--exclude-module", "PySide6.QtNetwork",
        "--exclude-module", "PySide6.QtSql",
        # Main script
        str(PROJECT_ROOT / "audiobook_gen" / "main.py")
    ]
    
    subprocess.check_call(cmd, cwd=PROJECT_ROOT)

if __name__ == "__main__":
    generate_icon()
    download_ffmpeg()
    download_tesseract()
    download_upx()
    run_pyinstaller()
    print("[*] Build Complete. Check the 'dist' folder.")
