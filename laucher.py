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

SCRIPTS_DIR = "scripts"  # Thư mục chứa script

# Đảm bảo thư mục tồn tại
if not os.path.exists(SCRIPTS_DIR):
    os.makedirs(SCRIPTS_DIR)

def launch_script(script_path):
    """Khởi chạy script nếu chưa chạy, nếu đang chạy thì đưa cửa sổ (nếu có) lên trước."""
    global launched_apps
    full_script_path = os.path.join(SCRIPTS_DIR, script_path)

    if script_path in launched_apps and launched_apps[script_path].poll() is None:
        print(f"{script_path} đã được mở.")
        return

    proc = subprocess.Popen(["python", full_script_path])
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
        text="Python Launcher v1.0\n\nTìm hiểu thêm tại https://github.com/nguyenhhoa03/mini-apps\n\nMake with love",
        justify="center"
    )
    about_label.pack(expand=True, padx=20, pady=20)
    about_window.lift()
    about_window.focus_force()

# Nút About
about_button = ctk.CTkButton(root, text="About", command=show_about, fg_color="gray", hover_color="gray")
about_button.pack(side="top", anchor="ne", padx=10, pady=10)

# Khung chứa các ứng dụng (tiles)
launcher_frame = ctk.CTkFrame(root)
launcher_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Quét các file .py trong thư mục scripts/
script_files = []
for file in os.listdir(SCRIPTS_DIR):
    if file.endswith(".py") and "-" in file:
        script_files.append(file)
script_files.sort()

# Tạo nút cho từng script
for index, script in enumerate(script_files):
    base_name = script[:-3]
    display_name = base_name.replace("-", " ").title()
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
    btn.grid(row=index // 4, column=index % 4, padx=10, pady=10)

def update_grid_layout(event):
    """Cập nhật lại layout dựa trên chiều rộng."""
    tile_width = 120
    current_width = launcher_frame.winfo_width()
    new_cols = max(1, current_width // tile_width)
    for index, btn in enumerate(buttons):
        row = index // new_cols
        col = index % new_cols
        btn.grid_configure(row=row, column=col)

launcher_frame.bind("<Configure>", update_grid_layout)

root.mainloop()
