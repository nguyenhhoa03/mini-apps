import os
import subprocess
import customtkinter as ctk
from PIL import Image
import requests
import zipfile
import tempfile
import shutil
from tkinter import messagebox

# Sử dụng chế độ giao diện theo hệ thống (sáng/tối tự động)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Tạo cửa sổ chính với kích thước tối thiểu
root = ctk.CTk()
root.title("Python Launcher")
root.geometry("600x400")
root.minsize(600, 400)

# Biến toàn cục lưu cửa sổ About và các tiến trình ứng dụng đã khởi chạy
about_window = None
launched_apps = {}

# Danh sách các nút ứng dụng để sắp xếp lại khi thay đổi kích thước
buttons = []

def launch_script(script_path):
    """Khởi chạy script tương ứng nếu chưa chạy, nếu đã chạy thì không khởi chạy lại."""
    global launched_apps
    if script_path in launched_apps and launched_apps[script_path].poll() is None:
        print(f"{script_path} đã được mở.")
        return
    proc = subprocess.Popen(["python", script_path])
    launched_apps[script_path] = proc

def show_about():
    """Hiển thị cửa sổ About. Nếu cửa sổ đã mở thì chỉ đưa lên trên."""
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

def update_project():
    """Cập nhật dự án từ GitHub và thay thế toàn bộ file hiện tại."""
    answer = messagebox.askyesno("Update", "Quá trình update sẽ tải về phiên bản mới và cập nhật dự án.\nBạn có muốn tiếp tục không?")
    if not answer:
        return
    try:
        # URL tải file zip dự án từ GitHub (sử dụng branch main)
        zip_url = "https://github.com/nguyenhhoa03/mini-apps/archive/refs/heads/main.zip"
        response = requests.get(zip_url, stream=True)
        if response.status_code != 200:
            messagebox.showerror("Error", f"Không thể tải file update: HTTP {response.status_code}")
            return

        # Lưu file zip vào thư mục tạm
        temp_zip_path = os.path.join(tempfile.gettempdir(), "update.zip")
        with open(temp_zip_path, "wb") as f:
            f.write(response.content)

        # Tạo thư mục tạm để giải nén
        temp_extract_dir = os.path.join(tempfile.gettempdir(), "mini_apps_update")
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        os.makedirs(temp_extract_dir)

        # Giải nén file zip
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        # Thư mục chứa mã nguồn sau khi giải nén (ở đây giả sử tên là "mini-apps-main")
        extracted_dir = os.path.join(temp_extract_dir, "mini-apps-main")
        if not os.path.exists(extracted_dir):
            messagebox.showerror("Error", "Không tìm thấy thư mục mã nguồn sau khi giải nén.")
            return

        # Copy tất cả file và thư mục từ extracted_dir vào thư mục hiện tại
        current_dir = os.getcwd()
        for item in os.listdir(extracted_dir):
            s = os.path.join(extracted_dir, item)
            d = os.path.join(current_dir, item)
            if os.path.isdir(s):
                # Sử dụng copytree với dirs_exist_ok=True để ghi đè nếu thư mục đã tồn tại
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        messagebox.showinfo("Update", "Cập nhật thành công. Vui lòng khởi động lại Launcher để áp dụng thay đổi.")
    except Exception as e:
        messagebox.showerror("Error", f"Đã xảy ra lỗi khi cập nhật: {e}")

# Tạo frame trên cùng để chứa nút About và Update (đặt bên phải)
frame_top = ctk.CTkFrame(root)
frame_top.pack(side="top", fill="x", padx=10, pady=10)

about_button = ctk.CTkButton(frame_top, text="About", command=show_about, fg_color="gray", hover_color="gray")
about_button.pack(side="right", padx=5)

update_button = ctk.CTkButton(frame_top, text="Update", command=update_project, fg_color="gray", hover_color="gray")
update_button.pack(side="right", padx=5)

# Khung chứa các ứng dụng (tiles)
launcher_frame = ctk.CTkFrame(root)
launcher_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Quét các file .py theo định dạng "ten-script-python.py" (loại trừ file launcher hiện tại)
current_file = os.path.basename(__file__)
script_files = []
for file in os.listdir("."):
    if file.endswith(".py") and file != current_file and "-" in file:
        script_files.append(file)
script_files.sort()

# Tạo nút cho từng script
for index, script in enumerate(script_files):
    base_name = script[:-3]  # Loại bỏ đuôi ".py"
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
    # Ban đầu sắp xếp theo 4 cột (sẽ cập nhật lại layout khi thay đổi kích thước)
    btn.grid(row=index // 4, column=index % 4, padx=10, pady=10)

def update_grid_layout(event):
    """
    Tính toán số cột dựa trên chiều rộng của launcher_frame và sắp xếp lại các nút.
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
