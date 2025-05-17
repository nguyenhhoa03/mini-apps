import os
import sys
import requests

print("Cài đặt các thư viện Python cần thiết...")
# Thêm py7zr để giải nén .7z
os.system("pip install -U customtkinter yt_dlp Pillow requests py7zr")

# Chỉ cài FFmpeg trên Windows
if os.name == "nt":
    print("Phát hiện Windows, kiểm tra FFmpeg...")
    if os.system("where ffmpeg >nul 2>&1") != 0:
        print("Chưa tìm thấy FFmpeg, bắt đầu tải ffmpeg-release-essentials.7z...")
        try:
            url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z'
            r = requests.get(url, stream=True)
            with open('ffmpeg.7z', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Tải về hoàn tất.")
        except Exception as e:
            print(f"Lỗi khi tải FFmpeg: {e}")
            sys.exit(1)

        print("Giải nén FFmpeg bằng py7zr...")
        try:
            import py7zr
            with py7zr.SevenZipFile('ffmpeg.7z', mode='r') as archive:
                archive.extractall(path='C:\\ffmpeg')
            print("Giải nén xong.")
        except Exception as e:
            print(f"Lỗi khi giải nén FFmpeg: {e}")
            sys.exit(1)

        print("Cập nhật PATH để sử dụng FFmpeg sau khi khởi động lại session...")
        os.system(
            "powershell -Command \"& {setx PATH $Env:PATH + ';C:\\ffmpeg\\bin'}\""
        )
        print("FFmpeg đã cài vào C:\\ffmpeg.")
    else:
        print("FFmpeg đã có sẵn trên hệ thống.")
else:
    print("Không phải Windows, bỏ qua cài đặt FFmpeg.")

print("Hoàn tất cập nhật.")
