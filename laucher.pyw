import os
import subprocess
import customtkinter as ctk
from PIL import Image
import requests
import zipfile
import tempfile
import shutil
from tkinter import messagebox
import webbrowser

# Sử dụng chế độ giao diện theo hệ thống (sáng/tối tự động)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Tạo cửa sổ chính với kích thước tối thiểu
root = ctk.CTk()
root.title("Mini apps Launcher")
root.geometry("600x400")
root.minsize(600, 400)

# Biến toàn cục lưu cửa sổ About và các tiến trình ứng dụng đã khởi chạy
about_window = None
launched_apps = {}

# Danh sách các nút ứng dụng để sắp xếp lại khi thay đổi kích thước
buttons = []
script_files = []  # danh sách các script

# Định nghĩa cửa sổ update
def custom_askyesno(title, message):
    # Tạo cửa sổ dialog mới
    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.wait_visibility()  # Đợi cho đến khi cửa sổ được hiển thị
    dialog.grab_set()         # Ngăn người dùng tương tác với cửa sổ chính khi dialog mở

    result = None

    # Hiển thị thông báo
    label = ctk.CTkLabel(dialog, text=message, wraplength=380)
    label.pack(pady=20)

    # Khai báo các hàm xử lý nút
    def on_yes():
        nonlocal result
        result = True
        dialog.destroy()

    def on_no():
        nonlocal result
        result = False
        dialog.destroy()

    # Tạo frame chứa nút
    btn_frame = ctk.CTkFrame(dialog)
    btn_frame.pack(pady=10)

    btn_yes = ctk.CTkButton(btn_frame, text="Có", command=on_yes)
    btn_yes.pack(side="left", padx=10)

    btn_no = ctk.CTkButton(btn_frame, text="Không", command=on_no)
    btn_no.pack(side="left", padx=10)

    # Đợi cho đến khi dialog bị đóng
    dialog.wait_window()
    return result

def custom_showerror(title, message):
    # Tạo cửa sổ dialog mới
    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.wait_visibility()  # Đợi cho đến khi cửa sổ hiển thị
    dialog.grab_set()

    # Hiển thị thông báo lỗi với màu chữ đỏ
    label = ctk.CTkLabel(dialog, text=message, wraplength=380, text_color="red")
    label.pack(pady=20)

    # Hàm xử lý khi nhấn OK
    def on_ok():
        dialog.destroy()

    btn_ok = ctk.CTkButton(dialog, text="OK", command=on_ok)
    btn_ok.pack(pady=10)

    dialog.wait_window()


def launch_script(script_path):
    """Khởi chạy script tương ứng nếu chưa chạy, nếu đã chạy thì không khởi chạy lại."""
    global launched_apps
    if script_path in launched_apps and launched_apps[script_path].poll() is None:
        print(f"{script_path} đã được mở.")
        return
    if os.name == "nt":
        proc = subprocess.Popen(["pythonw", script_path], cwd=os.path.dirname(script_path))
    else:
        proc = subprocess.Popen(["python", script_path], cwd=os.path.dirname(script_path))
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

    # Tạo tiêu đề
    header = ctk.CTkLabel(about_window, text="Python Launcher v1.0", justify="center")
    header.pack(pady=(20, 5))

    # Tạo label cho link Github với kiểu chữ gạch chân, màu xanh và cỡ chữ giống các text khác
    link_label = ctk.CTkLabel(
        about_window, 
        text="Tìm hiểu thêm tại Github", 
        justify="center", 
        text_color="blue", 
        font=("Helvetica", 12, "underline")
    )
    link_label.pack()
    # Bind sự kiện click vào label để mở URL bằng thư viện webbrowser
    link_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/nguyenhhoa03/mini-apps"))

    # Tạo footer
    footer = ctk.CTkLabel(about_window, text="Make with love", justify="center")
    footer.pack(pady=(5, 20))

    about_window.lift()
    about_window.focus_force()

def update_project():
    """Cập nhật dự án từ GitHub, copy file mới vào thư mục hiện tại và chạy file update.pyw để cấu hình."""
    answer = custom_askyesno("Update", "Quá trình update sẽ tải về phiên bản mới và cập nhật dự án.\nBạn có muốn tiếp tục không?")
    if not answer:
        return
    try:
        zip_url = "https://github.com/nguyenhhoa03/mini-apps/archive/refs/heads/main.zip"
        response = requests.get(zip_url, stream=True)
        if response.status_code != 200:
            custom_showerror("Error", f"Không thể tải file update: HTTP {response.status_code}")
            return

        temp_zip_path = os.path.join(tempfile.gettempdir(), "update.zip")
        with open(temp_zip_path, "wb") as f:
            f.write(response.content)

        temp_extract_dir = os.path.join(tempfile.gettempdir(), "mini_apps_update")
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        os.makedirs(temp_extract_dir)

        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        extracted_dir = os.path.join(temp_extract_dir, "mini-apps-main")
        if not os.path.exists(extracted_dir):
            custom_showerror("Error", "Không tìm thấy thư mục mã nguồn sau khi giải nén.")
            return

        current_dir = os.getcwd()
        for item in os.listdir(extracted_dir):
            s = os.path.join(extracted_dir, item)
            d = os.path.join(current_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        try:
            subprocess.Popen(["python", "update.py"])
        except Exception as e:
            custom_showerror("Error", f"Đã xảy ra lỗi khi chạy update.pyw: {e}")
            return

        print("Đang cập nhật thư viện")
    except Exception as e:
        custom_showerror("Error", f"Đã xảy ra lỗi khi cập nhật: {e}")

# Tạo frame trên cùng để chứa nút About và Update (đặt bên phải)
frame_top = ctk.CTkFrame(root)
frame_top.pack(side="top", fill="x", padx=10, pady=10)

about_button = ctk.CTkButton(frame_top, text="About", command=show_about, fg_color="gray", hover_color="gray")
about_button.pack(side="right", padx=5)

update_button = ctk.CTkButton(frame_top, text="Update", command=update_project, fg_color="gray", hover_color="gray")
update_button.pack(side="right", padx=5)

# Thêm ô tìm kiếm ở trên khu vực launcher
search_entry = ctk.CTkEntry(root, placeholder_text="Tìm kiếm ứng dụng")
search_entry.pack(padx=20, pady=(0,10), fill="x")

# Khung chứa các ứng dụng (tiles) với thanh cuộn
launcher_frame = ctk.CTkScrollableFrame(root)
launcher_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Đường dẫn tới thư mục chứa các script (chỉ chứa các file app)
current_dir = os.path.dirname(os.path.realpath(__file__))
scripts_dir = os.path.join(current_dir, "scripts")

# Quét các file .py theo định dạng "ten-script-python.py" trong thư mục scripts
if os.path.isdir(scripts_dir):
    for file in os.listdir(scripts_dir):
        if file.endswith(".py") and "-" in file:
            # Lưu đường dẫn tương đối (ví dụ: "scripts/ten-script-python.py")
            script_files.append(os.path.abspath(os.path.join("scripts", file)))
    script_files.sort()
else:
    messagebox.showerror("Error", f"Thư mục '{scripts_dir}' không tồn tại.")

# Tạo nút cho từng script
for index, script in enumerate(script_files):
    script_name = os.path.basename(script)  # Lấy tên file không kèm đường dẫn
    base_name = script_name[:-3]  # Loại bỏ đuôi ".py"
    display_name = base_name.replace("-", " ")  # Thay "-" bằng khoảng trắng 
    current_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(current_dir, "icons", base_name + ".png")
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
    Tính toán số cột dựa trên chiều rộng của launcher_frame và sắp xếp lại các nút đang hiển thị.
    Ước tính mỗi ô chiếm khoảng 120px (bao gồm padding).
    """
    visible_buttons = [btn for btn in buttons if btn.winfo_ismapped()]
    tile_width = 120
    current_width = launcher_frame.winfo_width()
    new_cols = max(1, current_width // tile_width)
    for index, btn in enumerate(visible_buttons):
        row = index // new_cols
        col = index % new_cols
        btn.grid_configure(row=row, column=col)

def filter_buttons(event=None):
    """Lọc các nút dựa trên nội dung ô tìm kiếm."""
    search_text = search_entry.get().lower()
    for btn in buttons:
        # Sử dụng text của nút (display name) để so sánh
        if search_text in btn.cget("text").lower():
            btn.grid()  # hiển thị
        else:
            btn.grid_remove()  # ẩn đi
    update_grid_layout(None)

# Gắn sự kiện thay đổi kích thước của launcher_frame để cập nhật lại layout
launcher_frame.bind("<Configure>", update_grid_layout)
# Gắn sự kiện khi gõ phím vào ô tìm kiếm
search_entry.bind("<KeyRelease>", filter_buttons)

root.mainloop()
