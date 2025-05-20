import os
import sys
import subprocess
import requests
import shutil
from pathlib import Path

LOG_PREFIX = "[LOG]"
ERROR_PREFIX = "[ERROR]"


def log(msg: str, prefix: str = LOG_PREFIX):
    try:
        print(f"{prefix} {msg}")
    except UnicodeEncodeError:
        safe = msg.encode('utf-8', errors='replace').decode('utf-8')
        print(f"{prefix} {safe}")


def run_windows_ffmpeg_install(base_dir: Path):
    """
    Sử dụng lệnh batch để kiểm tra và cài FFmpeg qua 7z.exe nằm trong thư mục 7-zip.
    """
    sevenz = base_dir / '7-zip' / '7z.exe'
    if not sevenz.is_file():
        log(f"Không tìm thấy 7z.exe tại {sevenz}", ERROR_PREFIX)
        sys.exit(1)

    # Tải và giải nén FFmpeg, cập nhật PATH trong 1 dòng batch
    batch = (
        f"where ffmpeg >nul 2>&1 || ("
        f"powershell -Command \"Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z' -OutFile 'ffmpeg.7z'\" && "
        f"{sevenz} x ffmpeg.7z -oC:\\ffmpeg -y && "
        f"for /d %D in (C:\\ffmpeg\\ffmpeg-*-essentials_build) do setx PATH \"%PATH%;%D\\bin\"")"
    )
    log("Chạy batch cài đặt FFmpeg via 7z.exe...")
    rc = os.system(batch)
    if rc != 0:
        log(f"Batch FFmpeg thất bại với mã {rc}", ERROR_PREFIX)
        sys.exit(1)
    else:
        log("FFmpeg đã được cài và PATH được cập nhật.")


if __name__ == '__main__':
    # 1. Cài thư viện cần thiết
    log("Cài đặt các thư viện Python cần thiết...")
    pip_cmd = [sys.executable, "-m", "pip", "install", "-U",
               "customtkinter", "yt_dlp", "Pillow", "requests"]
    try:
        subprocess.check_call(pip_cmd)
    except subprocess.CalledProcessError as e:
        log(f"Cài pip thất bại ({e.returncode})", ERROR_PREFIX)
        sys.exit(1)

    # 2. Cài FFmpeg trên Windows bằng batch + 7z.exe
    if os.name == 'nt':
        log("Phát hiện Windows, kiểm tra và cài FFmpeg nếu cần...")
        # shutil.which trả về None nếu không tìm thấy ffmpeg
        if not shutil.which('ffmpeg'):
            run_windows_ffmpeg_install(Path(__file__).parent)
        else:
            log("FFmpeg đã có sẵn trên hệ thống.")
    else:
        log("Không phải Windows, bỏ qua cài đặt FFmpeg.")

    log("Hoàn tất cập nhật. Hãy khởi động lại Launcher để áp dụng thay đổi.")
