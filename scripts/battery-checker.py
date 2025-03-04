import re
import os
import sys
import glob
import subprocess
import webbrowser
import customtkinter as ctk

# Cấu hình giao diện customtkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

def extract_battery_capacities_windows(file_path):
    """
    Trích xuất thông tin DESIGN CAPACITY và FULL CHARGE CAPACITY từ báo cáo pin trên Windows.
    Báo cáo được tạo ra bởi lệnh: powercfg /batteryreport
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Lỗi khi mở file báo cáo: {e}")
        return []
    
    # Sử dụng regex để tìm các giá trị (đơn vị mWh)
    pattern = re.compile(
        r'<span\s+class="label">\s*DESIGN\s+CAPACITY\s*</span>\s*</td>\s*<td>\s*([\d,]+)\s*mWh.*?'
        r'<span\s+class="label">\s*FULL\s+CHARGE\s+CAPACITY\s*</span>\s*</td>\s*<td>\s*([\d,]+)\s*mWh',
        re.IGNORECASE | re.DOTALL
    )
    
    batteries = []
    for match in pattern.finditer(content):
        design_str = match.group(1)
        full_str = match.group(2)
        try:
            design_capacity = float(design_str.replace(",", ""))
            full_charge_capacity = float(full_str.replace(",", ""))
            batteries.append((design_capacity, full_charge_capacity))
        except Exception as e:
            print("Lỗi chuyển đổi số liệu:", e)
    return batteries

def calculate_battery_health_windows(batteries):
    """
    Tính toán tình trạng pin cho Windows.
    Trả về danh sách các tuple: (pin_index, design_capacity, full_charge_capacity, health %)
    """
    results = []
    for idx, (design_capacity, full_charge_capacity) in enumerate(batteries, start=1):
        if design_capacity > 0:
            health = (full_charge_capacity / design_capacity) * 100
            results.append((idx, design_capacity, full_charge_capacity, health))
        else:
            print(f"Pin {idx}: DESIGN CAPACITY không hợp lệ.")
    return results

def extract_battery_capacities_linux():
    """
    Sử dụng lệnh upower để lấy thông tin pin trên Linux.
    Trích xuất các thông tin: energy-full-design và energy-full (đơn vị Wh).
    Trả về danh sách các tuple: (design_capacity, full_charge_capacity, health %)
    """
    # Kiểm tra xem upower có được cài đặt hay không
    if subprocess.run("which upower", shell=True, stdout=subprocess.PIPE).returncode != 0:
        print("Lệnh upower không được tìm thấy. Hãy kiểm tra xem nó đã được cài đặt chưa.")
        return []
    
    try:
        result = subprocess.run("upower -i $(upower -e | grep BAT)", shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = result.stdout
    except Exception as e:
        print("Lỗi khi chạy upower:", e)
        return []
    
    pattern_design = re.compile(r"energy-full-design:\s+([\d.]+)\s+Wh", re.IGNORECASE)
    pattern_full = re.compile(r"energy-full:\s+([\d.]+)\s+Wh", re.IGNORECASE)
    
    design_match = pattern_design.search(output)
    full_match = pattern_full.search(output)
    
    if design_match and full_match:
        try:
            design_capacity = float(design_match.group(1))
            full_charge_capacity = float(full_match.group(1))
            health = (full_charge_capacity / design_capacity) * 100 if design_capacity > 0 else 0
            return [(design_capacity, full_charge_capacity, health)]
        except Exception as e:
            print("Lỗi chuyển đổi số liệu:", e)
            return []
    else:
        print("Không tìm thấy thông tin pin từ upower.")
        return []

def find_battery_report():
    """
    Tìm file battery-report.html trong thư mục người dùng Windows.
    """
    user_home = os.path.expanduser("~")
    possible_paths = glob.glob(os.path.join(user_home, "**", "battery-report.html"), recursive=True)
    return possible_paths[0] if possible_paths else None

class BatteryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tình trạng pin")
        self.geometry("600x500")
        
        # Frame chính chứa thông tin và các nút
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Textbox hiển thị thông tin pin
        self.textbox = ctk.CTkTextbox(self.main_frame, width=560, height=380)
        self.textbox.pack(padx=10, pady=(10, 0))
        self.textbox.insert("end", "Đang lấy thông tin pin...\n")
        self.textbox.configure(state="disabled")
        
        # Nút More information ở dưới cùng
        self.button_more = ctk.CTkButton(self.main_frame, text="More information", command=self.more_info)
        self.button_more.pack(pady=(10, 10))
        
        # Tự động kiểm tra thông tin pin sau khi giao diện khởi chạy
        self.after(100, self.check_battery)
    
    def update_text(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")
    
    def check_battery(self):
        # Xoá nội dung cũ
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        
        battery_health = []
        if os.name == "nt":
            self.update_text("Đang chạy lệnh 'powercfg /batteryreport' ...")
            os.system("powercfg /batteryreport")
            file_path = find_battery_report()
            if file_path is None:
                self.update_text("Không tìm thấy file battery-report.html. Vui lòng kiểm tra lại.")
                return
            battery_data = extract_battery_capacities_windows(file_path)
            if battery_data:
                battery_health = calculate_battery_health_windows(battery_data)
            else:
                self.update_text("Không thể trích xuất thông tin pin từ báo cáo.")
        elif sys.platform.startswith("linux"):
            battery_data = extract_battery_capacities_linux()
            if battery_data:
                battery_health = [(idx, design, full, health) 
                                  for idx, (design, full, health) in enumerate(battery_data, start=1)]
            else:
                self.update_text("Không thể trích xuất thông tin pin từ upower.")
        else:
            self.update_text("Hệ điều hành không được hỗ trợ.")
            return
        
        # Hiển thị thông tin pin
        if battery_health:
            for idx, design, full, health in battery_health:
                unit = "mWh" if os.name == "nt" else "Wh"
                self.update_text(f"Pin {idx}:")
                self.update_text(f"  DESIGN CAPACITY      = {design} {unit}")
                self.update_text(f"  FULL CHARGE CAPACITY = {full} {unit}")
                self.update_text(f"  Health               = {health:.2f}%")
                self.update_text("-" * 40)
        else:
            self.update_text("Không có dữ liệu pin để hiển thị.")
    
    def more_info(self):
        """
        Khi nhấn nút More information:
          - Trên Windows: mở file battery-report.html bằng trình duyệt.
          - Trên Linux: in đầy đủ kết quả lệnh upower.
        """
        if os.name == "nt":
            file_path = find_battery_report()
            if file_path is None:
                self.update_text("Không tìm thấy battery-report.html để mở.")
            else:
                webbrowser.open(file_path)
                self.update_text("Đã mở battery-report.html trên trình duyệt.")
        elif sys.platform.startswith("linux"):
            try:
                result = subprocess.run("upower -i $(upower -e | grep BAT)", shell=True, check=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output = result.stdout
            except Exception as e:
                output = f"Lỗi khi chạy upower: {e}"
            self.update_text("Thông tin chi tiết từ lệnh upower:")
            self.update_text(output)
        else:
            self.update_text("Hệ điều hành không được hỗ trợ.")

if __name__ == "__main__":
    app = BatteryApp()
    app.mainloop()
