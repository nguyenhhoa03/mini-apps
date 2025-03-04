import os
import time
import customtkinter as ctk

# Cấu hình giao diện theo hệ thống (sáng/tối tự động)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Tạo cửa sổ chính
app = ctk.CTk()
app.title("Cài đặt Thư viện cho Launcher")
app.geometry("400x200")

# Label thông báo trạng thái
status_label = ctk.CTkLabel(app, text="Đang cài đặt các thư viện cần thiết...")
status_label.pack(pady=20)

# Thanh progressbar để hiển thị tiến trình cài đặt
progressbar = ctk.CTkProgressBar(app, width=300)
progressbar.pack(pady=10)
progressbar.set(0)

def install_and_configure():
    # Danh sách các thư viện cần cài đặt qua pip
    pip_packages = ["customtkinter", "yt_dlp", "Pillow", "requests"]

    # Xác định các lệnh hệ thống bổ sung cho cấu hình,
    # Lưu ý: Một số lệnh này có thể không dùng được pip, hãy thay đổi theo nhu cầu.
    if os.name == "nt":
        # Các lệnh dành cho Windows
        additional_commands = [
            'echo Đang thực hiện cấu hình cho Windows',
            "where ffmpeg >nul 2>&1 || (powershell -Command \"& {Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'}\" && powershell -Command \"& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'C:\\ffmpeg' -Force}\" && for /d %D in (C:\\ffmpeg\\ffmpeg-*-essentials_build) do setx PATH \"%PATH%;%D\\bin\")"
            # 'choco install package-name',
        ]
    elif os.name == "posix":
        # Các lệnh dành cho Linux
        additional_commands = [
            'echo Đang thực hiện cấu hình cho Linux',
            # Thêm các lệnh khác, ví dụ:
            # 'sudo apt-get update',
            # 'sudo apt-get install package-name',
        ]
    else:
        additional_commands = []

    total_steps = len(pip_packages) + len(additional_commands)
    current_step = 0

    # Cài đặt các thư viện qua pip
    for pkg in pip_packages:
        status_label.configure(text=f"Đang cài đặt {pkg}...")
        app.update()
        os.system(f"pip install {pkg}")
        current_step += 1
        progressbar.set(current_step / total_steps)
        app.update()
        time.sleep(0.5)

    # Thực hiện các lệnh hệ thống bổ sung (cấu hình)
    for cmd in additional_commands:
        status_label.configure(text=f"Thực hiện lệnh: {cmd}")
        app.update()
        os.system(cmd)
        current_step += 1
        progressbar.set(current_step / total_steps)
        app.update()
        time.sleep(0.5)

    status_label.configure(text="Cập nhật hoàn tất! Hãy khởi động lại laucher để áp dụng thay đổi")
    close_button = ctk.CTkButton(app, text="Đóng", command=app.destroy)
    close_button.pack(pady=10)

# Sau 100ms, bắt đầu tiến trình cài đặt và cấu hình
app.after(100, install_and_configure)
app.mainloop()
