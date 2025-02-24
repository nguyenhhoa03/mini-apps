import os
import subprocess
import customtkinter as ctk
from PIL import Image

# Sử dụng chế độ giao diện theo hệ thống (sáng/tối tự động)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Tạo cửa sổ chính và đặt kích thước tối thiểu
root = ctk.CTk()
root.title("Python Launcher")
root.geometry("600x400")
root.minsize(600, 400)  # Không cho phép thu nhỏ dưới kích thước này

# Biến toàn cục để lưu cửa sổ About và các app đã khởi chạy
about_window = None
launched_apps = {}  # key: tên script, value: subprocess.Popen instance

# Danh sách các nút ứng dụng (để sắp xếp lại khi thay đổi kích thước)
buttons = []

def launch_script(script_path):
    """Khởi chạy script nếu chưa chạy, nếu đang chạy thì đưa cửa sổ (nếu có) lên trước."""
    global launched_apps
    # Nếu đã khởi chạy và vẫn còn chạy (poll() trả về None)
    if script_path in launched_apps and launched_apps[script_path].poll() is None:
        print(f"{script_path} đã được mở.")
        # Nếu các ứng dụng được phát triển dưới customtkinter, có thể thêm lệnh focus, lift
        return
    # Nếu chưa chạy thì khởi chạy script mới
    proc = subprocess.Popen(["python", script_path])
    launched_apps[script_path] = proc

def show_about():
    """Hiển thị cửa sổ About. Nếu đã mở rồi thì chỉ đưa lên trước."""
    global about_window
    if about_window is not None and about_window.winfo_exists():
        about_window.lift()
        about_window.focus_force()
        return
    about_window = ctk.CTkToplevel(root)
    about_window.title("About Launcher")
    about_window.geometry("300x200")
    about_label = ctk.CTkLabel(
        about_window,
        text="Python Launcher v1.0\n\nĐược phát triển để chạy các script CLI Python\n\n© 2025 YourName",
        justify="center"
    )
    about_label.pack(expand=True, padx=20, pady=20)
    # Đưa cửa sổ About lên trên
    about_window.lift()
    about_window.focus_force()

# Nút About với giao diện trung tính (không nổi bật)
about_button = ctk.CTkButton(root, text="About", command=show_about, fg_color="gray", hover_color="gray")
about_button.pack(side="top", anchor="ne", padx=10, pady=10)

# Khung chứa các ứng dụng (tiles)
launcher_frame = ctk.CTkFrame(root)
launcher_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Quét các file .py theo định dạng "ten-script-python.py" (loại trừ file launcher)
current_file = os.path.basename(__file__)
script_files = []
for file in os.listdir("."):
    if file.endswith(".py") and file != current_file and "-" in file:
        script_files.append(file)
script_files.sort()

# Tạo nút cho từng script và lưu vào danh sách buttons
for index, script in enumerate(script_files):
    base_name = script[:-3]  # Loại bỏ đuôi .py
    display_name = base_name.replace("-", " ").title()  # Thay "-" bằng khoảng trắng và in hoa chữ cái đầu
    icon_path = os.path.join("icons", base_name + ".png")
    if os.path.exists(icon_path):
        pil_image = Image.open(icon_path)
        icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(64, 64))
    else:
        icon_image = None

    btn = ctk.CTkButton(
        launcher_frame,
        text=display_name,
        image=icon_image,
        compound="top",
        width=100,
        height=100,
        command=lambda script=script: launch_script(script)
    )
    buttons.append(btn)
    # Ban đầu sắp xếp theo 4 cột (sẽ cập nhật lại sau)
    btn.grid(row=index // 4, column=index % 4, padx=10, pady=10)

def update_grid_layout(event):
    """
    Tính toán số cột dựa theo chiều rộng hiện tại của launcher_frame và sắp xếp lại các nút.
    Ước tính mỗi ô chiếm khoảng 120px (bao gồm padding).
    """
    tile_width = 120
    current_width = launcher_frame.winfo_width()
    new_cols = max(1, current_width // tile_width)
    for index, btn in enumerate(buttons):
        row = index // new_cols
        col = index % new_cols
        btn.grid_configure(row=row, column=col)

# Gắn sự kiện thay đổi kích thước của launcher_frame để cập nhật lại layout
launcher_frame.bind("<Configure>", update_grid_layout)

root.mainloop()

