import customtkinter
import os
import platform
import threading
import datetime

class AutoShutdownApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Shutdown")
        self.geometry("350x300")
        self.timer = None  # Biến lưu Timer hiện tại

        # Frame chính
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Frame lựa chọn chế độ hẹn giờ (delay hoặc time)
        self.mode_frame = customtkinter.CTkFrame(self.main_frame)
        self.mode_frame.pack(pady=5, fill="x")

        self.mode_var = customtkinter.StringVar(value="delay")
        self.delay_radio = customtkinter.CTkRadioButton(self.mode_frame, text="Sau X giây", variable=self.mode_var, value="delay", command=self.update_mode)
        self.delay_radio.grid(row=0, column=0, padx=5, pady=5)
        self.time_radio = customtkinter.CTkRadioButton(self.mode_frame, text="Vào thời gian HH:MM", variable=self.mode_var, value="time", command=self.update_mode)
        self.time_radio.grid(row=0, column=1, padx=5, pady=5)

        # Frame nhập số giây (cho chế độ delay)
        self.delay_frame = customtkinter.CTkFrame(self.main_frame)
        self.delay_frame.pack(pady=5, fill="x")
        self.delay_entry = customtkinter.CTkEntry(self.delay_frame, placeholder_text="Nhập số giây")
        self.delay_entry.pack(fill="x", padx=10)

        # Frame nhập thời gian (cho chế độ time) - ẩn ban đầu
        self.time_frame = customtkinter.CTkFrame(self.main_frame)
        self.time_entry = customtkinter.CTkEntry(self.time_frame, placeholder_text="Nhập thời gian (HH:MM)")
        self.time_entry.pack(fill="x", padx=10)
        self.time_frame.pack_forget()

        # Frame lựa chọn hành động (shutdown, restart, sleep, lock)
        self.action_frame = customtkinter.CTkFrame(self.main_frame)
        self.action_frame.pack(pady=10, fill="x")
        self.action_var = customtkinter.StringVar(value="shutdown")
        self.shutdown_radio = customtkinter.CTkRadioButton(self.action_frame, text="Tắt máy", variable=self.action_var, value="shutdown")
        self.shutdown_radio.grid(row=0, column=0, padx=5, pady=5)
        self.restart_radio = customtkinter.CTkRadioButton(self.action_frame, text="Restart", variable=self.action_var, value="restart")
        self.restart_radio.grid(row=0, column=1, padx=5, pady=5)
        self.sleep_radio = customtkinter.CTkRadioButton(self.action_frame, text="Sleep", variable=self.action_var, value="sleep")
        self.sleep_radio.grid(row=0, column=2, padx=5, pady=5)
        self.lock_radio = customtkinter.CTkRadioButton(self.action_frame, text="Lock", variable=self.action_var, value="lock")
        self.lock_radio.grid(row=0, column=3, padx=5, pady=5)

        # Frame cho nút điều khiển
        self.button_frame = customtkinter.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=10, fill="x")
        self.start_button = customtkinter.CTkButton(self.button_frame, text="Bắt đầu", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        self.cancel_button = customtkinter.CTkButton(self.button_frame, text="Hủy", command=self.cancel_timer)
        self.cancel_button.grid(row=0, column=1, padx=5)

        # Nhãn hiển thị trạng thái
        self.status_label = customtkinter.CTkLabel(self.main_frame, text="Chưa đặt lịch")
        self.status_label.pack(pady=5)

    def update_mode(self):
        # Ẩn/hiện các frame nhập liệu dựa trên chế độ chọn
        mode = self.mode_var.get()
        if mode == "delay":
            self.time_frame.pack_forget()
            self.delay_frame.pack(pady=5, fill="x")
        else:
            self.delay_frame.pack_forget()
            self.time_frame.pack(pady=5, fill="x")

    def start_timer(self):
        # Hủy lệnh timer cũ nếu có
        self.cancel_timer()
        action = self.action_var.get()
        mode = self.mode_var.get()
        delay_seconds = 0

        if mode == "delay":
            try:
                delay_seconds = int(self.delay_entry.get())
            except ValueError:
                self.status_label.configure(text="Vui lòng nhập số giây hợp lệ!")
                return
        else:
            time_str = self.time_entry.get()
            try:
                target_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                now = datetime.datetime.now()
                target_datetime = datetime.datetime.combine(now.date(), target_time)
                if target_datetime <= now:
                    target_datetime += datetime.timedelta(days=1)
                delay_seconds = int((target_datetime - now).total_seconds())
            except ValueError:
                self.status_label.configure(text="Vui lòng nhập thời gian hợp lệ (HH:MM)!")
                return

        self.status_label.configure(text=f"Đã đặt lịch '{action}' sau {delay_seconds} giây")
        self.timer = threading.Timer(delay_seconds, self.execute_action, args=(action,))
        self.timer.start()

    def cancel_timer(self):
        # Hủy timer nếu đang chạy và gửi lệnh hủy tới hệ thống nếu cần
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            self.status_label.configure(text="Lệnh đã được hủy")
            self.timer = None
        if platform.system() == "Windows":
            os.system("shutdown /a")
        elif platform.system() == "Linux":
            os.system("shutdown -c")

    def execute_action(self, action):
        # Thực thi lệnh theo hành động được chọn và dựa trên hệ điều hành
        sys_platform = platform.system()
        if sys_platform == "Windows":
            if action == "shutdown":
                os.system("shutdown /s /t 0")
            elif action == "restart":
                os.system("shutdown /r /t 0")
            elif action == "sleep":
                os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
            elif action == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
        elif sys_platform == "Linux":
            if action == "shutdown":
                os.system("shutdown -h now")
            elif action == "restart":
                os.system("shutdown -r now")
            elif action == "sleep":
                os.system("systemctl suspend")
            elif action == "lock":
                os.system("xdg-screensaver lock")
        else:
            self.status_label.configure(text="Hệ điều hành không được hỗ trợ")

if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")  # Chọn chế độ: "Light", "Dark", "System"
    customtkinter.set_default_color_theme("blue")  # Màu chủ đạo: blue, dark-blue, green,...
    app = AutoShutdownApp()
    app.mainloop()
