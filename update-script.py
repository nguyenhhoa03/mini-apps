import os
import sys
import requests

print("[LOG] Cài đặt các thư viện Python cần thiết...")
# Thêm py7zr để giải nén .7z
os.system("pip install -U customtkinter yt_dlp Pillow requests py7zr")

# Chỉ cài FFmpeg trên Windows
if os.name == "nt":
    print("[LOG] Phát hiện Windows, kiểm tra FFmpeg...")
    if os.system("where ffmpeg >nul 2>&1") != 0:
        print("[LOG] Chưa tìm thấy FFmpeg, bắt đầu tải ffmpeg-release-essentials.7z...")
        try:
            url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z'
            r = requests.get(url, stream=True)
            with open('ffmpeg.7z', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("[LOG] Tải về hoàn tất.")
        except Exception as e:
            print(f"[LOG] Lỗi khi tải FFmpeg: {e}")
            sys.exit(1)

        print("[LOG] Giải nén FFmpeg bằng py7zr...")
        try:
            import py7zr
            with py7zr.SevenZipFile('ffmpeg.7z', mode='r') as archive:
                archive.extractall(path='C:\\ffmpeg')
            print("[LOG] Giải nén xong.")
        except Exception as e:
            print(f"[LOG] Lỗi khi giải nén FFmpeg: {e}")
            sys.exit(1)

        print("[LOG] Cập nhật PATH để sử dụng FFmpeg sau khi khởi động lại session...")
        os.system(
            "powershell -Command \"& {setx PATH $Env:PATH + ';C:\\ffmpeg\\bin'}\""
        )
        print("[LOG] FFmpeg đã cài vào C:\\ffmpeg.")
    else:
        print("[LOG] FFmpeg đã có sẵn trên hệ thống.")
else:
    print("[LOG] Không phải Windows, bỏ qua cài đặt FFmpeg.")

print("[LOG] Hoàn tất cập nhật.")
