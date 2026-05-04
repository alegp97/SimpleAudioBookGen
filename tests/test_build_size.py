import os
import sys
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from build import download_ffmpeg, download_upx, FFMPEG_DIR, UPX_DIR

def test_download_ffmpeg_essentials():
    # Clean existing ffmpeg dir to force download
    if FFMPEG_DIR.exists():
        shutil.rmtree(FFMPEG_DIR)
    
    download_ffmpeg()
    
    assert FFMPEG_DIR.exists(), "FFmpeg dir not created"
    ffmpeg_exe = FFMPEG_DIR / "ffmpeg.exe"
    assert ffmpeg_exe.exists(), "ffmpeg.exe not downloaded/extracted"
    
    # ffprobe is optional, but Gyan Essentials includes it, so let's verify if it's there
    ffprobe_exe = FFMPEG_DIR / "ffprobe.exe"
    if ffprobe_exe.exists():
        print(f"ffprobe.exe size: {os.path.getsize(ffprobe_exe) / (1024*1024):.2f} MB")
    
    print(f"ffmpeg.exe size: {os.path.getsize(ffmpeg_exe) / (1024*1024):.2f} MB")
    print("test_download_ffmpeg_essentials PASSED")

def test_download_upx():
    if UPX_DIR.exists():
        shutil.rmtree(UPX_DIR)
        
    download_upx()
    
    assert UPX_DIR.exists(), "UPX dir not created"
    upx_exe = UPX_DIR / "upx.exe"
    assert upx_exe.exists(), "upx.exe not downloaded/extracted"
    
    print(f"upx.exe size: {os.path.getsize(upx_exe) / (1024*1024):.2f} MB")
    print("test_download_upx PASSED")

if __name__ == "__main__":
    print("Running download tests...")
    test_download_upx()
    test_download_ffmpeg_essentials()
    print("All tests passed.")
