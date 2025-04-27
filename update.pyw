import os
import time
import threading
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

# Nút Đóng (ẩn lúc đầu)
close_button = ctk.CTkButton(app, text="Đóng", command=app.destroy)


def run_command(cmd):
    """Chạy lệnh hệ thống và trả về status"""
    return os.system(cmd)


def install_and_configure():
    pip_packages = ["customtkinter", "yt_dlp", "Pillow", "requests", "qrcode", "pyzbar"]

    if os.name == "nt":
        additional_commands = [
            'echo Đang thực hiện cấu hình cho Windows',
            "where ffmpeg >nul 2>&1 || (powershell -Command \"& {Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'}\" && powershell -Command \"& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'C:\\ffmpeg' -Force}\" && for /d %D in (C:\\ffmpeg\\ffmpeg-*-essentials_build) do setx PATH \"%PATH%;%D\\bin\")"
        ]
    else:
        additional_commands = [
            'echo "Đang thực hiện cấu hình cho Linux"',
            '[ -f /etc/debian_version ] && sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y zbar-tools',
            '[ -f /etc/fedora-release ] && sudo dnf install -y zbar',
            '[ -f /etc/arch-release ] && sudo pacman -Sy --noconfirm zbar',
            '[ -f /etc/SuSE-release ] && sudo zypper --non-interactive install zbar',
            '[ -f /etc/alpine-release ] && sudo apk add --no-cache zbar',
        ]

    steps = [(f"pip install {pkg}", pkg) for pkg in pip_packages] + [(cmd, cmd) for cmd in additional_commands]
    total_steps = len(steps)

    for idx, (cmd, label) in enumerate(steps, start=1):
        status_label.configure(text=f"Đang cấu hình, việc này có thể mất một khoảng thời gian.")
        progressbar.set((idx - 1) / total_steps)
        app.update()

        # Chạy lệnh trong subprocess để không block
        thread = threading.Thread(target=run_command, args=(cmd,))
        thread.start()
        # Chờ thread kết thúc hoặc timeout nếu cần
        thread.join()

        progressbar.set(idx / total_steps)
        app.update()
        time.sleep(0.3)

    status_label.configure(text="Cập nhật hoàn tất! Hãy khởi động lại launcher.")
    close_button.pack(pady=10)

# Bắt đầu chạy install_and_configure trong thread để không block mainloop
threading.Thread(target=install_and_configure, daemon=True).start()
app.mainloop()
