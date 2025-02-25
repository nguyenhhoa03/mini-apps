import re
import os
import sys
import subprocess

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

def create_and_run_vbs(battery_health, temp_vbs_path):
    """
    Dành cho Windows: Tạo file VBScript tạm thời để hiển thị thông báo tình trạng pin (MsgBox).
    """
    msg_lines = []
    for idx, design, full, health in battery_health:
        line = f"Pin {idx}: DESIGN = {design} mWh, FULL = {full} mWh, Health = {health:.2f}%"
        msg_lines.append(line)
    # Nối các dòng với ký tự xuống dòng của VBScript (vbCrLf)
    vbs_message = ' & vbCrLf & '.join([f'"{line}"' for line in msg_lines])
    vbs_content = f'MsgBox {vbs_message}'
    
    try:
        with open(temp_vbs_path, "w", encoding="utf-8") as vbs_file:
            vbs_file.write(vbs_content)
    except Exception as e:
        print(f"Lỗi khi tạo file VBS: {e}")
        return
    
    os.system(f"wscript \"{temp_vbs_path}\"")

def notify_battery_status(battery_health):
    """
    Hiển thị thông báo tình trạng pin.
    - Trên Windows: dùng VBScript (MsgBox)
    - Trên Linux: dùng notify-send (nếu có cài đặt)
    """
    if os.name == "nt":
        current_directory = os.path.expanduser("~")
        temp_vbs_file = os.path.join(current_directory, "temp_battery_status.vbs")
        create_and_run_vbs(battery_health, temp_vbs_file)
    else:
        # Tạo thông báo dạng text
        msg = "\n".join(
            f"Pin {idx}: DESIGN = {design} Wh, FULL = {full} Wh, Health = {health:.2f}%"
            for idx, design, full, health in battery_health
        )
        # Gọi notify-send để hiển thị thông báo (Linux)
        os.system(f'notify-send "Tình trạng pin" "{msg}"')

def print_battery_status(battery_health):
    """
    In ra thông tin tình trạng pin trên terminal.
    """
    for idx, design, full, health in battery_health:
        print(f"Pin {idx}:")
        print(f"  DESIGN CAPACITY      = {design} {'mWh' if os.name=='nt' else 'Wh'}")
        print(f"  FULL CHARGE CAPACITY = {full} {'mWh' if os.name=='nt' else 'Wh'}")
        print(f"  Health               = {health:.2f}%")
        print("-" * 40)

if __name__ == "__main__":
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
            print("Không thể trích xuất thông tin pin từ báo cáo.")
    elif sys.platform.startswith("linux"):
        # Linux: sử dụng upower để lấy thông tin pin
        battery_data = extract_battery_capacities_linux()
        if battery_data:
            # battery_data đã là list các tuple (design, full, health)
            battery_health = [(idx, design, full, health) 
                              for idx, (design, full, health) in enumerate(battery_data, start=1)]
        else:
            print("Không thể trích xuất thông tin pin từ upower.")
    else:
        print("Hệ điều hành không được hỗ trợ.")
        sys.exit(1)
    
    if battery_health:
        print_battery_status(battery_health)
        notify_battery_status(battery_health)
    else:
        print("Không có dữ liệu pin để hiển thị.")
