"""
Entry point for SimpleAudioBookGen.

Initialises the application and opens the main window.
"""

import os
import sys
from pathlib import Path

# Add the project root to sys.path so absolute imports work correctly
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def resource_path(relative_path: str) -> Path:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(project_root)
    return base_path / relative_path



def _configure_ffmpeg() -> None:
    """Configure pydub to use FFmpeg / FFprobe robustly."""
    try:
        from pydub import AudioSegment
        from pydub.utils import which
        import urllib.request
        import zipfile
        import shutil
        
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            # We are running as a PyInstaller bundle
            bin_dir = resource_path(".ffmpeg_bin")
            ffmpeg_exe = bin_dir / "ffmpeg.exe"
            ffprobe_exe = bin_dir / "ffprobe.exe"
            
            if str(bin_dir) not in os.environ["PATH"]:
                os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
                
            if ffmpeg_exe.exists():
                AudioSegment.converter = str(ffmpeg_exe)
            if ffprobe_exe.exists():
                AudioSegment.ffprobe = str(ffprobe_exe)
            else:
                print("Warning: ffprobe.exe not found in bundle, ignoring.")
            print(f"Running bundled FFmpeg from {bin_dir}")
            return

        # 1. Check if binaries are already on the system PATH
        sys_ffmpeg = which("ffmpeg")
        sys_ffprobe = which("ffprobe")
        if sys_ffmpeg:
            print(f"FFmpeg found on system: {sys_ffmpeg}")
            AudioSegment.converter = sys_ffmpeg
            if sys_ffprobe:
                AudioSegment.ffprobe = sys_ffprobe
            return

        # 2. Local binary directory inside the project (DEV MODE)
        bin_dir = Path(project_root) / ".ffmpeg_bin"
        bin_dir.mkdir(exist_ok=True)

        ffmpeg_exe = bin_dir / "ffmpeg.exe"
        ffprobe_exe = bin_dir / "ffprobe.exe"

        if str(bin_dir) not in os.environ["PATH"]:
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")

        # 3. Try to get ffmpeg from imageio-ffmpeg if not present locally
        if not ffmpeg_exe.exists():
            try:
                import imageio_ffmpeg
                imageio_ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                shutil.copy2(imageio_ffmpeg_path, ffmpeg_exe)
                print(f"FFmpeg copied from imageio-ffmpeg to {ffmpeg_exe}")
            except Exception as e:
                print(f"Warning: could not copy ffmpeg from imageio-ffmpeg: {e}")

        # 4. If still missing, download the official static Windows build
        if not ffmpeg_exe.exists():
            print("FFmpeg binaries missing. Downloading static build (this may take a moment)...")
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = bin_dir / "ffmpeg.zip"

            urllib.request.urlretrieve(url, zip_path)
            print("Extracting binaries...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.endswith("ffmpeg.exe") and not ffmpeg_exe.exists():
                        with zip_ref.open(member) as source, open(ffmpeg_exe, "wb") as target:
                            shutil.copyfileobj(source, target)
                    elif member.endswith("ffprobe.exe") and not ffprobe_exe.exists():
                        with zip_ref.open(member) as source, open(ffprobe_exe, "wb") as target:
                            shutil.copyfileobj(source, target)
            zip_path.unlink()
            print("Download complete.")

        # 5. Point pydub to the local binaries
        if ffmpeg_exe.exists():
            AudioSegment.converter = str(ffmpeg_exe)
        if ffprobe_exe.exists():
            AudioSegment.ffprobe = str(ffprobe_exe)

        print(f"FFmpeg config -> converter: {AudioSegment.converter}, ffprobe: {getattr(AudioSegment, 'ffprobe', 'N/A')}")
        print(f"PATH check    -> ffmpeg: {which('ffmpeg')}, ffprobe: {which('ffprobe')}")

    except Exception as e:
        print(f"Critical error configuring FFmpeg: {e}")


# Configure FFmpeg BEFORE pydub tries to locate it
_configure_ffmpeg()

from audiobook_gen.utils.logger import setup_logger
from audiobook_gen.config import Settings


def main() -> None:
    """Main entry point."""
    # Load configuration
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        settings = Settings.from_yaml(config_path)
    else:
        settings = Settings()

    # Initialise logger
    setup_logger(log_file=settings.log_file, debug=settings.debug)

    # Import Qt after the environment has been set up
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from audiobook_gen.gui.main_window import MainWindow

    # Set AppUserModelID on Windows so the taskbar groups and shows the correct icon
    if os.name == 'nt':
        try:
            import ctypes
            myappid = 'simpleaudiobookgen.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Create the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("SimpleAudioBookGen")
    app.setApplicationVersion("0.2.0")

    # Set the window icon
    icon_file = resource_path("icon.ico")
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    # Create and show the main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
