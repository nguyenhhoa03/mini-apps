import sys
import os
import ctypes
import re
import customtkinter as ctk
from tkinter import messagebox

# --- Tự động xin quyền admin trên Windows ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if os.name == "nt" and not is_admin():
    # Yêu cầu chạy lại với quyền admin
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- Định nghĩa file hosts thật ---
HOSTS_FILENAME = r"C:\Windows\System32\drivers\etc\hosts"

def load_rules():
    """
    Đọc file hosts thật và tách ra các dòng do chương trình tạo.
    Các dòng do chương trình tạo có định dạng:
    127.0.0.1 www.example.com #Status: Block website, create by Windows Website Blocker
    """
    rules = []
    other_lines = []
    if not os.path.exists(HOSTS_FILENAME):
        messagebox.showerror("Lỗi", f"Không tìm thấy file hosts: {HOSTS_FILENAME}")
        sys.exit(1)

    with open(HOSTS_FILENAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if "create by Windows Website Blocker" in line:
            # Chỉ parse những dòng chứa "www." ở phần domain
            match = re.search(r"127\.0\.0\.1\s+(www\.\S+)\s+#Status:\s+Block website, create by Windows Website Blocker", line)
            if match:
                domain = match.group(1)
                rules.append({"domain": domain})
        else:
            other_lines.append(line)
    return rules, other_lines

def save_rules(rules, other_lines):
    """
    Ghi lại file hosts bằng cách giữ lại các dòng không do chương trình tạo và
    cập nhật các dòng do chương trình tạo.
    """
    with open(HOSTS_FILENAME, "w", encoding="utf-8") as f:
        # Ghi lại các dòng không quản lý
        for line in other_lines:
            f.write(line.rstrip("\n") + "\n")
        # Ghi các dòng do chương trình tạo
        for rule in rules:
            f.write(f"127.0.0.1 {rule['domain']} #Status: Block website, create by Windows Website Blocker\n")

class WebsiteBlockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows Website Blocker")
        self.geometry("600x400")
        # Load các rule và các dòng hosts khác
        self.rules, self.other_lines = load_rules()
        self.create_widgets()
        self.update_rules_list()

    def create_widgets(self):
        # Frame chứa danh sách rule
        self.rules_frame = ctk.CTkFrame(self)
        self.rules_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Các nút điều khiển
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(padx=10, pady=10)

        self.new_rule_button = ctk.CTkButton(control_frame, text="Thêm mới", command=self.open_new_rule_window)
        self.new_rule_button.grid(row=0, column=0, padx=10)

        self.apply_button = ctk.CTkButton(control_frame, text="Apply", command=self.apply_changes)
        self.apply_button.grid(row=0, column=1, padx=10)

        self.refresh_button = ctk.CTkButton(control_frame, text="Refresh", command=self.refresh_rules)
        self.refresh_button.grid(row=0, column=2, padx=10)

    def update_rules_list(self):
        # Xóa các widget cũ
        for widget in self.rules_frame.winfo_children():
            widget.destroy()
        # Tạo nút cho mỗi rule
        for idx, rule in enumerate(self.rules):
            btn_text = f"{rule['domain']} - Block"
            btn = ctk.CTkButton(self.rules_frame, text=btn_text, command=lambda idx=idx: self.open_edit_rule_window(idx))
            btn.pack(pady=5, fill="x")

    def open_edit_rule_window(self, rule_index):
        EditRuleWindow(self, rule_index)

    def open_new_rule_window(self):
        NewRuleWindow(self)

    def apply_changes(self):
        save_rules(self.rules, self.other_lines)
        messagebox.showinfo("Thông báo", "Đã lưu các thay đổi vào file hosts!")

    def refresh_rules(self):
        self.rules, self.other_lines = load_rules()
        self.update_rules_list()

class EditRuleWindow(ctk.CTkToplevel):
    def __init__(self, parent, rule_index):
        super().__init__(parent)
        self.parent = parent
        self.rule_index = rule_index
        self.rule = parent.rules[rule_index]
        self.title(f"Chỉnh sửa rule: {self.rule['domain']}")
        self.geometry("400x200")
        self.create_widgets()

    def create_widgets(self):
        # Nhãn hiển thị domain hiện tại
        self.domain_label = ctk.CTkLabel(self, text="Domain:")
        self.domain_label.pack(pady=5)
        # Entry cho phép chỉnh sửa domain
        self.domain_entry = ctk.CTkEntry(self)
        self.domain_entry.insert(0, self.rule["domain"])
        self.domain_entry.pack(pady=5)

        # Nút lưu thay đổi
        self.save_button = ctk.CTkButton(self, text="Lưu thay đổi", command=self.save_changes)
        self.save_button.pack(pady=10)
        # Nút xóa rule
        self.delete_button = ctk.CTkButton(self, text="Xóa rule", command=self.delete_rule)
        self.delete_button.pack(pady=10)

    def save_changes(self):
        new_domain = self.domain_entry.get().strip()
        if new_domain == "":
            messagebox.showerror("Lỗi", "Vui lòng nhập domain!")
            return
        # Đảm bảo domain có tiền tố www.
        if not new_domain.startswith("www."):
            new_domain = "www." + new_domain

        # Kiểm tra xem domain mới có trùng với rule khác không (ngoại trừ rule hiện tại)
        for idx, rule in enumerate(self.parent.rules):
            if idx != self.rule_index and rule["domain"].lower() == new_domain.lower():
                messagebox.showerror("Lỗi", f"Rule cho {new_domain} đã tồn tại!")
                return

        # Cập nhật rule
        self.parent.rules[self.rule_index]["domain"] = new_domain
        self.parent.update_rules_list()
        self.destroy()

    def delete_rule(self):
        del self.parent.rules[self.rule_index]
        self.parent.update_rules_list()
        self.destroy()

class NewRuleWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Thêm rule mới")
        self.geometry("400x200")
        self.create_widgets()

    def create_widgets(self):
        # Nhập domain
        self.domain_label = ctk.CTkLabel(self, text="Domain:")
        self.domain_label.pack(pady=5)
        self.domain_entry = ctk.CTkEntry(self)
        self.domain_entry.pack(pady=5)
        # Nút thêm rule
        self.save_button = ctk.CTkButton(self, text="Thêm rule", command=self.add_rule)
        self.save_button.pack(pady=10)

    def add_rule(self):
        domain = self.domain_entry.get().strip()
        if domain == "":
            messagebox.showerror("Lỗi", "Vui lòng nhập domain!")
            return
        # Đảm bảo domain có tiền tố www.
        if not domain.startswith("www."):
            domain = "www." + domain

        # Kiểm tra nếu rule đã tồn tại thì ghi đè
        updated = False
        for rule in self.parent.rules:
            if rule["domain"].lower() == domain.lower():
                rule["domain"] = domain  # Cập nhật (trong trường hợp người dùng nhập khác về viết hoa,...)
                updated = True
                break
        if not updated:
            self.parent.rules.append({"domain": domain})
        self.parent.update_rules_list()
        self.destroy()

if __name__ == "__main__":
    app = WebsiteBlockerApp()
    app.mainloop()
