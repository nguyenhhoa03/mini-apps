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

    # 2. Cài FFmpeg trên Windows sử dụng 7z.exe kèm theo
    if os.name == 'nt':
        log("Phát hiện Windows, kiểm tra FFmpeg...")
        if not shutil.which('ffmpeg'):
            # Xác định đường dẫn đến 7z.exe nằm cùng thư mục script
            base_dir = Path(__file__).parent
            sevenz = base_dir / '7-zip' / '7z.exe'
            if not sevenz.is_file():
                log(f"Không tìm thấy 7z.exe tại {sevenz}", ERROR_PREFIX)
                sys.exit(1)

            # Tải FFmpeg
            ff7z = base_dir / 'ffmpeg-release-essentials.7z'
            url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z'
            log("Chưa tìm thấy FFmpeg, bắt đầu tải về...")
            try:
                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(ff7z, 'wb') as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                log("Tải về hoàn tất.")
            except Exception as e:
                log(f"Lỗi khi tải FFmpeg: {e}", ERROR_PREFIX)
                sys.exit(1)

            # Giải nén bằng 7z.exe
            target = Path('C:/ffmpeg')
            log(f"Giải nén FFmpeg đến {target}...")
            try:
                target.mkdir(parents=True, exist_ok=True)
                cmd = [str(sevenz), 'x', str(ff7z), f'-o{target}', '-y']
                subprocess.check_call(cmd)
                log(f"Giải nén xong tại {target}")
            except subprocess.CalledProcessError as e:
                log(f"Lỗi khi giải nén FFmpeg: mã {e.returncode}", ERROR_PREFIX)
                sys.exit(1)

            # Cập nhật PATH
            try:
                cmd = ['powershell', '-Command',
                       "setx PATH $Env:PATH + ';C:/ffmpeg/bin'"]
                subprocess.check_call(cmd)
                log("Cập nhật PATH thành công.")
            except Exception as e:
                log(f"Lỗi khi cập nhật PATH: {e}", ERROR_PREFIX)
                # Không dừng, vì FFmpeg đã được cài
        else:
            log("FFmpeg đã có sẵn trên hệ thống.")
    else:
        log("Không phải Windows, bỏ qua cài đặt FFmpeg.")

    log("Hoàn tất cập nhật. Hãy khởi động lại Launcher để áp dụng thay đổi.")
