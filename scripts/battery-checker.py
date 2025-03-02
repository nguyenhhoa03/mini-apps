import os
import sys
import re
import subprocess
import customtkinter as ctk

class BatteryStatusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Battery Status")
        self.geometry("500x300")
        
        self.label = ctk.CTkLabel(self, text="Battery Information", font=("Arial", 18, "bold"))
        self.label.pack(pady=10)
        
        self.textbox = ctk.CTkTextbox(self, height=150, wrap="word")
        self.textbox.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.button = ctk.CTkButton(self, text="Refresh", command=self.update_battery_status)
        self.button.pack(pady=10)
        
        self.update_battery_status()
    
    def update_battery_status(self):
        battery_info = self.get_battery_status()
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", battery_info)
    
    def get_battery_status(self):
        if os.name == "nt":
            return self.get_battery_status_windows()
        elif sys.platform.startswith("linux"):
            return self.get_battery_status_linux()
        else:
            return "Unsupported OS"
    
    def get_battery_status_windows(self):
        # Xác định thư mục chứa file script hiện tại
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, "battery-report.html")
        
        # Tạo báo cáo pin với đầu ra chỉ định vào file battery-report.html
        os.system(f'powercfg /batteryreport /output "{file_path}"')
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Regex hỗ trợ tiếng Anh
            pattern = re.compile(r"Design Capacity.*?(\d+)\s*mWh.*?Full Charge Capacity.*?(\d+)\s*mWh", 
                                 re.IGNORECASE | re.DOTALL)
            match = pattern.search(content)
            if match:
                design = int(match.group(1))
                full = int(match.group(2))
                health = (full / design) * 100
                return f"Design Capacity: {design} mWh\nFull Charge Capacity: {full} mWh\nHealth: {health:.2f}%"
            else:
                # Nếu không tìm thấy, thử với định dạng tiếng Việt
                pattern_vn = re.compile(r"Dung lượng thiết kế.*?(\d+)\s*mWh.*?Dung lượng sạc đầy.*?(\d+)\s*mWh", 
                                          re.IGNORECASE | re.DOTALL)
                match_vn = pattern_vn.search(content)
                if match_vn:
                    design = int(match_vn.group(1))
                    full = int(match_vn.group(2))
                    health = (full / design) * 100
                    return f"Dung lượng thiết kế: {design} mWh\nDung lượng sạc đầy: {full} mWh\nSức khỏe: {health:.2f}%"
                return "Battery info not found"
        except Exception as e:
            return f"Error reading battery report: {e}"
    
    def get_battery_status_linux(self):
        try:
            result = subprocess.run("upower -i $(upower -e | grep BAT)", shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output = result.stdout
            design_match = re.search(r"energy-full-design:\s+(\d+\.?\d*)\s+Wh", output)
            full_match = re.search(r"energy-full:\s+(\d+\.?\d*)\s+Wh", output)
            if design_match and full_match:
                design = float(design_match.group(1))
                full = float(full_match.group(1))
                health = (full / design) * 100
                return f"Design Capacity: {design} Wh\nFull Charge Capacity: {full} Wh\nHealth: {health:.2f}%"
            return "Battery info not found"
        except Exception as e:
            return f"Error fetching battery info: {e}"

if __name__ == "__main__":
    app = BatteryStatusApp()
    app.mainloop()
