import os
import hashlib
import multiprocessing
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import platform

# Danh sách thư mục hệ thống không nên quét
EXCLUDED_DIRS = [
    os.path.normpath(path) for path in [
        'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
        '/usr', '/bin', '/sbin', '/lib', '/lib64'
    ]
]

# Định dạng dung lượng thành chuỗi dễ đọc
def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

# Hàm tính hash nhẹ (MD5) của file
def file_hash(path):
    try:
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest(), path
    except Exception:
        return None

# Hàm kiểm tra xem một đường dẫn nằm trong danh sách loại trừ
def is_excluded(path):
    path_norm = os.path.normpath(path)
    for ex in EXCLUDED_DIRS:
        try:
            common = os.path.commonpath([path_norm, ex])
            if common == ex:
                return True
        except ValueError:
            continue
    return False

# Hàm xử lý quét file trong thư mục, in tiến trình quét
def scan_files(root_dir):
    file_paths = []
    for root, _, files in os.walk(root_dir):
        if is_excluded(root):
            continue
        print(f"Scanning directory: {root}")
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path) and not is_excluded(full_path):
                file_paths.append(full_path)
                if len(file_paths) % 100 == 0:
                    print(f"Found {len(file_paths)} files so far...")
    print(f"Total files to hash: {len(file_paths)}")
    return file_paths

# Hàm khởi động quét, dùng nhiều tiến trình và in tiến trình hashing
def find_duplicates(start_dir, result_queue):
    all_files = scan_files(start_dir)
    hash_dict = {}
    total = len(all_files)
    pool = multiprocessing.Pool(processes=os.cpu_count())
    for idx, item in enumerate(pool.imap_unordered(file_hash, all_files), start=1):
        if item:
            h, path = item
            hash_dict.setdefault(h, []).append(path)
        if idx % 50 == 0 or idx == total:
            print(f"Hashed {idx}/{total} files")
    pool.close()
    pool.join()
    duplicates = [v for v in hash_dict.values() if len(v) > 1]
    result_queue.put(duplicates)

# Mở thư mục chứa file chính xác trên Windows và các OS khác
def open_file_location(path):
    try:
        system = platform.system()
        if system == "Windows":
            # Sử dụng explorer với tham số /select để chọn file
            subprocess.Popen(["explorer.exe", f"/select,{path}"])
        elif system == "Darwin":
            subprocess.Popen(["open", "-R", path])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(path)])
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở vị trí file: {e}")

# Giao diện chính
class DuplicateFinderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tìm file trùng bằng hash")
        self.geometry("850x650")
        ctk.set_default_color_theme("dark-blue")

        # Nút chọn thư mục, mặc định là profile người dùng
        self.select_btn = ctk.CTkButton(
            self, text="Chọn thư mục", command=self.select_folder
        )
        self.select_btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Chưa quét")
        self.status_label.pack(pady=5)

        # Khung cuộn kết quả
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=800, height=550)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def select_folder(self):
        home = os.path.expanduser("~")
        folder = filedialog.askdirectory(initialdir=home)
        if not folder:
            return
        if is_excluded(folder):
            messagebox.showerror("Lỗi", "Không thể quét thư mục hệ thống!")
            return
        self.status_label.configure(text="Đang quét và hash files...")
        self.clear_scroll_frame()
        self.update()

        self.result_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(
            target=find_duplicates, args=(folder, self.result_queue)
        )
        self.process.start()
        self.after(100, self.check_process)

    def check_process(self):
        if self.process.is_alive():
            self.after(100, self.check_process)
        else:
            duplicates = self.result_queue.get()
            self.display_results(duplicates)

    def clear_scroll_frame(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def display_results(self, duplicates):
        if not duplicates:
            self.status_label.configure(text="Không tìm thấy file trùng.")
            return
        total_files = sum(len(g) for g in duplicates)
        total_size = 0
        for group in duplicates:
            for f in group:
                try:
                    total_size += os.path.getsize(f)
                except Exception:
                    continue
        readable = format_size(total_size)
        self.status_label.configure(
            text=f"Tìm thấy {total_files} file trùng. Tổng dung lượng có thể dọn: {readable}"
        )

        for group in duplicates:
            ctk.CTkLabel(self.scroll_frame, text="---- NHÓM TRÙNG ----").pack(
                anchor="w", pady=(10, 0)
            )
            for path in group:
                row = ctk.CTkFrame(self.scroll_frame)
                row.pack(fill="x", padx=5, pady=2)
                row.grid_columnconfigure(0, weight=1)
                try:
                    size = os.path.getsize(path)
                    size_str = format_size(size)
                except Exception:
                    size_str = "?"
                label = ctk.CTkLabel(
                    row, text=f"{path} ({size_str})", anchor="w", wraplength=650
                )
                label.grid(row=0, column=0, sticky="ew", padx=(10, 5))
                btn = ctk.CTkButton(
                    row, text="Open location", width=120,
                    command=lambda p=path: open_file_location(p)
                )
                btn.grid(row=0, column=1, padx=(5, 10))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = DuplicateFinderApp()
    app.mainloop()
