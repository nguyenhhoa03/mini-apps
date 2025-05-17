import os
import threading
import subprocess
import customtkinter as ctk

# Cấu hình giao diện theo hệ thống (sáng/tối tự động)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Tạo cửa sổ chính
app = ctk.CTk()
app.title("Chạy update-script.py")
app.geometry("600x400")

# Khung chứa log
log_frame = ctk.CTkFrame(app)
log_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Text widget để hiển thị log
log_text = ctk.CTkTextbox(log_frame, wrap="word", state="disabled")
log_text.pack(fill="both", expand=True)

# Nút Đóng
close_button = ctk.CTkButton(app, text="Đóng", command=app.destroy)


def append_log(message: str):
    """
    Chèn message vào log_text và tự cuộn xuống cuối
    """
    log_text.configure(state="normal")
    log_text.insert("end", message + "\n")
    log_text.see("end")
    log_text.configure(state="disabled")


def run_update_script():
    """
    Chạy file update-script.py và lấy stdout liên tục để hiển thị
    """
    # Xác định đường dẫn file script
    script_path = os.path.join(os.path.dirname(__file__), 'update-script.py')

    # Tùy chọn ẩn console trên Windows
    creation_flags = 0
    if os.name == 'nt':
        creation_flags = subprocess.CREATE_NO_WINDOW

    # Mở subprocess và lấy output line-by-line
    proc = subprocess.Popen(
        ['python', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
        creationflags=creation_flags
    )

    # Đọc từng dòng đầu ra
    for line in proc.stdout:
        append_log(line.rstrip())

    proc.stdout.close()
    proc.wait()
    append_log("--- Hoàn tất chạy update-script.py ---")
    close_button.pack(pady=5)


# Bắt đầu chạy trong thread
threading.Thread(target=run_update_script, daemon=True).start()

app.mainloop()
