import os
import sys
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

# Cờ debug để hiển thị các dòng không phải [LOG]
debug_mode = True

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
    python_exec = sys.executable
    script_dir = os.path.dirname(__file__)
    script_path = os.path.join(script_dir, 'update-script.py')

    # Kiểm tra tồn tại file
    if not os.path.isfile(script_path):
        append_log(f"[ERROR] Không tìm thấy file: {script_path}")
        append_log("--- Kết thúc do lỗi ---")
        close_button.pack(pady=5)
        return

    # Thiết lập biến môi trường để bật UTF-8 trên Windows
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'

    # Thiết lập ẩn cửa sổ console trên Windows
    creation_flags = 0
    if os.name == 'nt' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
        creation_flags = subprocess.CREATE_NO_WINDOW

    try:
        proc = subprocess.Popen(
            [python_exec, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=script_dir,
            env=env,
            creationflags=creation_flags
        )
    except Exception as e:
        append_log(f"[ERROR] Không thể chạy script: {e}")
        append_log("--- Kết thúc do lỗi ---")
        close_button.pack(pady=5)
        return

    # Đọc đầu ra của script
    for line in proc.stdout:
        line = line.rstrip()
        if line.startswith("[LOG]"):
            message = line[5:].lstrip()
            append_log(message)
        elif debug_mode:
            # Hiển thị thêm các dòng khác để debug
            append_log(f"[DBG] {line}")

    proc.stdout.close()
    proc.wait()
    if proc.returncode != 0:
        append_log(f"[ERROR] Script trả về mã lỗi {proc.returncode}")
    append_log("--- Hoàn tất update, hãy khởi động lại Laucher để áp dụng thay đổi---")
    close_button.pack(pady=5)

# Chạy trong thread để không block GUI
threading.Thread(target=run_update_script, daemon=True).start()

app.mainloop()
