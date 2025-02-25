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

# Progressbar để hiển thị tiến trình cài đặt
progressbar = ctk.CTkProgressBar(app, width=300)
progressbar.pack(pady=10)
progressbar.set(0)

# Danh sách các thư viện cần cài đặt
packages = ["customtkinter", "tkinter", "yt_dlp"]

def install_packages():
    total = len(packages)
    for index, pkg in enumerate(packages):
        status_label.configure(text=f"Đang cài đặt {pkg}...")
        app.update()
        # Sử dụng os.system để gọi pip cài đặt thư viện
        os.system(f"pip install {pkg}")
        # Cập nhật progressbar
        progressbar.set((index + 1) / total)
        app.update()
        time.sleep(0.5)  # Tạm dừng ngắn để người dùng thấy được tiến trình
    status_label.configure(text="Cài đặt hoàn tất!")
    # Nút đóng cửa sổ sau khi cài đặt xong
    close_button = ctk.CTkButton(app, text="Đóng", command=app.destroy)
    close_button.pack(pady=10)

# Sau 100ms, bắt đầu cài đặt
app.after(100, install_packages)
app.mainloop()
