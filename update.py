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
    Chạy file update-script.py và chỉ hiển thị các dòng log bắt đầu bằng prefix [LOG]
    """
    script_path = os.path.join(os.path.dirname(__file__), 'update-script.py')

    creation_flags = 0
    if os.name == 'nt':
        creation_flags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        ['python', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
        creationflags=creation_flags
    )

    for line in proc.stdout:
        line = line.rstrip()
        # Chỉ hiển thị các dòng bắt đầu bằng [LOG]
        if line.startswith("[LOG]"):
            # Bỏ prefix và khoảng trắng sau
            message = line[6:] if len(line) > 6 else ''
            append_log(message)

    proc.stdout.close()
    proc.wait()
    append_log("--- Hoàn tất chạy update-script.py ---")
    close_button.pack(pady=5)


# Chạy trong thread để không block GUI
threading.Thread(target=run_update_script, daemon=True).start()

app.mainloop()
