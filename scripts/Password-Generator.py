import customtkinter as ctk
import tkinter as tk  # Để dùng các hằng số như tk.END
import random
import string

class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Password Generator")
        self.geometry("400x400")

        # Tiêu đề ứng dụng
        self.label = ctk.CTkLabel(self, text="Password Generator", font=("Arial", 20))
        self.label.pack(pady=20)

        # Thanh trượt để chọn độ dài mật khẩu
        self.length_slider = ctk.CTkSlider(self, from_=4, to=32, command=self.update_length_entry_from_slider)
        self.length_slider.set(12)
        self.length_slider.pack(pady=10)

        # Ô nhập hiển thị độ dài mật khẩu
        self.length_entry = ctk.CTkEntry(self, width=120)
        self.length_entry.insert(0, "12")
        self.length_entry.pack(pady=10)
        # Bind sự kiện khi thay đổi ô nhập (mỗi khi nhấn phím)
        self.length_entry.bind("<KeyRelease>", self.update_slider_from_length_entry)

        # Các checkbox cho lựa chọn ký tự
        self.var_letters = tk.BooleanVar(value=True)
        self.var_numbers = tk.BooleanVar(value=True)
        self.var_special = tk.BooleanVar(value=True)

        self.chk_letters = ctk.CTkCheckBox(self, text="Chữ", variable=self.var_letters, command=self.generate_password)
        self.chk_letters.pack(pady=5)

        self.chk_numbers = ctk.CTkCheckBox(self, text="Số", variable=self.var_numbers, command=self.generate_password)
        self.chk_numbers.pack(pady=5)

        self.chk_special = ctk.CTkCheckBox(self, text="Kí tự đặc biệt", variable=self.var_special, command=self.generate_password)
        self.chk_special.pack(pady=5)

        # Ô hiển thị mật khẩu đã tạo
        self.password_entry = ctk.CTkEntry(self, width=250)
        self.password_entry.pack(pady=10)

        # Nút copy mật khẩu vào clipboard
        self.copy_button = ctk.CTkButton(self, text="Copy", command=self.copy_password)
        self.copy_button.pack(pady=10)

        # Tạo mật khẩu ngay khi khởi chạy ứng dụng
        self.generate_password()

    def update_length_entry_from_slider(self, value):
        # Cập nhật ô nhập khi thanh trượt được kéo và tạo lại mật khẩu
        new_value = str(int(float(value)))
        self.length_entry.delete(0, tk.END)
        self.length_entry.insert(0, new_value)
        self.generate_password()

    def update_slider_from_length_entry(self, event):
        # Khi người dùng nhập số vào ô nhập, cập nhật vị trí của thanh trượt
        try:
            value = int(self.length_entry.get())
        except ValueError:
            return  # Nếu không phải số, bỏ qua
        # Giới hạn giá trị từ 4 đến 32
        if value < 4:
            value = 4
        elif value > 32:
            value = 32
        self.length_slider.set(value)
        self.generate_password()

    def generate_password(self):
        try:
            length = int(self.length_entry.get())
        except ValueError:
            length = 12  # Mặc định nếu nhập sai
        characters = ""
        if self.var_letters.get():
            characters += string.ascii_letters
        if self.var_numbers.get():
            characters += string.digits
        if self.var_special.get():
            characters += string.punctuation
        if not characters:
            # Nếu không có lựa chọn nào thì mặc định sử dụng chữ cái
            characters = string.ascii_letters

        password = "".join(random.choice(characters) for _ in range(length))
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def copy_password(self):
        password = self.password_entry.get()
        self.clipboard_clear()
        self.clipboard_append(password)

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
