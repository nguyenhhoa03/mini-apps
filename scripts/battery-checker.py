import re
import os
import sys
import subprocess
import customtkinter as ctk

# Hàm trích xuất thông tin pin từ báo cáo Windows (battery-report.html)
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
    
    # Regex để tìm cặp DESIGN CAPACITY và FULL CHARGE CAPACITY (đơn vị mWh)
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
    
    if not batteries:
        print("Không tìm thấy thông tin pin trong báo cáo.")
    return batteries

# Hàm tính toán tình trạng pin trên Windows
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

# Hàm trích xuất thông tin pin trên Linux sử dụng upower
def extract_battery_capacities_linux():
    """
    Sử dụng lệnh upower để lấy thông tin pin trên Linux.
    Trích xuất các thông tin: energy-full-design (dung lượng thiết kế) và energy-full (dung lượng tối đa hiện tại).
    Đơn vị: Wh
    Trả về danh sách các tuple: (design_capacity, full_charge_capacity, health %)
    """
    try:
        # Chạy lệnh upower và thu kết quả
        result = subprocess.run("upower -i $(upower -e | grep BAT)", shell=True, check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = result.stdout
    except Exception as e:
        print("Lỗi khi chạy upower:", e)
        return []
    
    # Sử dụng regex để tìm energy-full-design và energy-full (đơn vị Wh)
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

# Lớp giao diện chính sử dụng customtkinter
class BatteryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Battery Health Monitor")
        self.geometry("600x400")
        
        # Label tiêu đề
        self.title_label = ctk.CTkLabel(self, text="Battery Health Monitor", font=("Arial", 20))
        self.title_label.pack(pady=20)
        
        # Text box để hiển thị thông tin pin
        self.text_box = ctk.CTkTextbox(self, width=550, height=250)
        self.text_box.pack(pady=10)
        
        # Nút refresh để cập nhật thông tin
        self.refresh_button = ctk.CTkButton(self, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(pady=10)
        
        # Tải dữ liệu ban đầu
        self.refresh_data()
    
    def refresh_data(self):
        self.text_box.delete("1.0", "end")
        battery_health = []
        
        if os.name == "nt":
            # Windows: tạo báo cáo pin và trích xuất thông tin
            os.system("powercfg /batteryreport")
            current_directory = os.path.expanduser("~")
            file_path = os.path.join(current_directory, "battery-report.html")
            battery_data = extract_battery_capacities_windows(file_path)
            if battery_data:
                battery_health = calculate_battery_health_windows(battery_data)
            else:
                self.text_box.insert("end", "Không thể trích xuất thông tin pin từ báo cáo.\n")
        elif sys.platform.startswith("linux"):
            # Linux: sử dụng upower để lấy thông tin pin
            battery_data = extract_battery_capacities_linux()
            if battery_data:
                battery_health = [(idx, design, full, health) 
                                  for idx, (design, full, health) in enumerate(battery_data, start=1)]
            else:
                self.text_box.insert("end", "Không thể trích xuất thông tin pin từ upower.\n")
        else:
            self.text_box.insert("end", "Hệ điều hành không được hỗ trợ.\n")
            return
        
        # Hiển thị dữ liệu pin lên text box
        if battery_health:
            for idx, design, full, health in battery_health:
                self.text_box.insert("end", f"Pin {idx}:\n")
                unit = "mWh" if os.name == "nt" else "Wh"
                self.text_box.insert("end", f"  DESIGN CAPACITY      = {design} {unit}\n")
                self.text_box.insert("end", f"  FULL CHARGE CAPACITY = {full} {unit}\n")
                self.text_box.insert("end", f"  Health               = {health:.2f}%\n")
                self.text_box.insert("end", "-" * 40 + "\n")
        else:
            self.text_box.insert("end", "Không có dữ liệu pin để hiển thị.\n")

if __name__ == "__main__":
    app = BatteryApp()
    app.mainloop()
