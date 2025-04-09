import os
import re
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import qrcode
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

# Cấu hình giao diện cho customtkinter
ctk.set_appearance_mode("System")  # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")

# --------------------------- Các hàm hỗ trợ ---------------------------

def paste_from_clipboard(entry_widget):
    try:
        clipboard_text = root.clipboard_get()
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, clipboard_text)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không lấy được nội dung clipboard:\n{str(e)}")

# Hàm tạo mã QR
def generate_qr():
    global qr_image, qr_photo
    text = qr_entry.get().strip()
    if not text:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập text hoặc link!")
        return
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # Cập nhật hình QR trên giao diện
    qr_image_resized = qr_image.resize((200, 200))
    # Chú ý: customtkinter khuyến cáo dùng CTkImage. Tuy nhiên, để đơn giản ta vẫn dùng Pillow.
    qr_photo = ImageTk.PhotoImage(qr_image_resized)
    qr_label.configure(image=qr_photo)
    save_button.configure(state="normal")

def save_qr():
    if qr_image is None:
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="Lưu QR Code"
    )
    if file_path:
        try:
            qr_image.save(file_path)
            messagebox.showinfo("Thành công", f"Đã lưu QR Code tại:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu file:\n{str(e)}")

# Hàm phân tích QR Wifi theo định dạng: WIFI:S:<SSID>;T:<TYPE>;P:<PASSWORD>;;
def parse_wifi_qr(qr_text: str):
    ssid = password = None
    try:
        inner = qr_text[5:-2]  # bỏ "WIFI:" và ";;" ở cuối
        parts = inner.split(';')
        for part in parts:
            if part.startswith("S:"):
                ssid = part[2:]
            elif part.startswith("P:"):
                password = part[2:]
    except Exception as e:
        print("Lỗi parse wifi:", e)
    return ssid, password

# Hàm xử lý click vào URL trong text widget
def open_url_click(event):
    widget = event.widget
    index = widget.index(f"@{event.x},{event.y}")
    # Kiểm tra xem vị trí click có thuộc tag "url" không
    if "url" in widget.tag_names(index):
        # Duyệt qua các khoảng được gắn tag "url" để xác định URL được click
        for start, end in zip(widget.tag_ranges("url")[::2], widget.tag_ranges("url")[1::2]):
            if widget.compare(index, ">=", start) and widget.compare(index, "<", end):
                url_clicked = widget.get(start, end)
                webbrowser.open(url_clicked)
                break

# Hàm hiển thị nội dung giải mã lên Text widget và tô màu các URL
def display_decoded_text(decoded_text):
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, decoded_text)
    # Xác định các chuỗi URL trong decoded_text bằng regex
    for match in re.finditer(r"https?://[^\s]+", decoded_text):
        start_char = match.start()
        end_char = match.end()
        start_index = f"1.0+{start_char}chars"
        end_index = f"1.0+{end_char}chars"
        result_text.tag_add("url", start_index, end_index)
    result_text.config(state="disabled")

def open_file_and_decode():
    # Reset kết quả hiện có
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.config(state="disabled")
    wifi_frame.pack_forget()
    copy_text_button.configure(state="disabled")
    
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh chứa QR Code",
        filetypes=[("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.bmp")), ("All Files", "*.*")]
    )
    if file_path:
        try:
            img = Image.open(file_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không mở được file ảnh:\n{str(e)}")
            return
        
        decoded_objs = decode(img)
        if not decoded_objs:
            # Hiển thị thông báo lỗi trên Text widget
            result_text.config(state="normal")
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "Không phát hiện được QR Code trong ảnh!")
            result_text.config(state="disabled")
            return
        
        decoded_text = decoded_objs[0].data.decode("utf-8")
        display_decoded_text(decoded_text)
        copy_text_button.configure(state="normal")
        
        # Nếu nội dung giải mã là WiFi thì hiển thị SSID và Password
        if decoded_text.startswith("WIFI:"):
            ssid, password = parse_wifi_qr(decoded_text)
            if ssid:
                wifi_ssid_entry.configure(state="normal")
                wifi_ssid_entry.delete(0, tk.END)
                wifi_ssid_entry.insert(0, ssid)
                wifi_ssid_entry.configure(state="readonly")
            else:
                wifi_ssid_entry.configure(state="normal")
                wifi_ssid_entry.delete(0, tk.END)
                wifi_ssid_entry.insert(0, "Không xác định")
                wifi_ssid_entry.configure(state="readonly")
            if password:
                wifi_password_entry.configure(state="normal")
                wifi_password_entry.delete(0, tk.END)
                wifi_password_entry.insert(0, password)
                wifi_password_entry.configure(state="readonly")
            else:
                wifi_password_entry.configure(state="normal")
                wifi_password_entry.delete(0, tk.END)
                wifi_password_entry.insert(0, "Không xác định")
                wifi_password_entry.configure(state="readonly")
            wifi_frame.pack(pady=10)
    else:
        return

def copy_text():
    content = result_text.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        messagebox.showinfo("Copied", "Đã copy text từ QR Code.")

def copy_wifi(field):
    if field == "ssid":
        text = wifi_ssid_entry.get()
    elif field == "password":
        text = wifi_password_entry.get()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("Copied", f"Đã copy {field.upper()}.")

def try_again():
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.config(state="disabled")
    wifi_frame.pack_forget()
    copy_text_button.configure(state="disabled")

# --------------------------- Giao diện chính ---------------------------

root = ctk.CTk()
root.title("QR Code Generator and Reader")
root.geometry("600x550")

# Biến toàn cục để lưu QR image
qr_image = None
qr_photo = None

# Tạo Tabview
tabview = ctk.CTkTabview(root, width=580, height=520)
tabview.pack(padx=10, pady=10, fill="both", expand=True)
tabview.add("Tạo QR")
tabview.add("Đọc QR")

# --------------------------- Tab Tạo QR ---------------------------
create_frame = tabview.tab("Tạo QR")

entry_frame = ctk.CTkFrame(create_frame)
entry_frame.pack(pady=10, padx=10, fill="x")
entry_label = ctk.CTkLabel(entry_frame, text="Nhập text hoặc link:")
entry_label.pack(side="left", padx=5)
qr_entry = ctk.CTkEntry(entry_frame)
qr_entry.pack(side="left", padx=5, fill="x", expand=True)
paste_button = ctk.CTkButton(entry_frame, text="Paste", command=lambda: paste_from_clipboard(qr_entry))
paste_button.pack(side="left", padx=5)

button_frame = ctk.CTkFrame(create_frame)
button_frame.pack(pady=10)
gen_button = ctk.CTkButton(button_frame, text="Tạo QR", command=generate_qr)
gen_button.pack(side="left", padx=5)
save_button = ctk.CTkButton(button_frame, text="Save", command=save_qr, state="disabled")
save_button.pack(side="left", padx=5)

qr_label = ctk.CTkLabel(create_frame, text=" ")
qr_label.pack(pady=10)

# --------------------------- Tab Đọc QR ---------------------------
read_frame = tabview.tab("Đọc QR")

select_button = ctk.CTkButton(read_frame, text="Chọn ảnh chứa QR Code", command=open_file_and_decode, width=250, height=40)
select_button.pack(pady=10)

# Sử dụng tk.Text để hiển thị kết quả giải mã có hỗ trợ tag màu
result_text = tk.Text(read_frame, wrap="word", height=8, font=("Helvetica", 12))
result_text.pack(pady=5, padx=10, fill="x")
result_text.config(state="disabled")
# Cấu hình tag "url" để hiển thị màu xanh và gạch chân
result_text.tag_configure("url", foreground="blue", underline=1)
result_text.tag_bind("url", "<Button-1>", open_url_click)

action_frame = ctk.CTkFrame(read_frame)
action_frame.pack(pady=10)
copy_text_button = ctk.CTkButton(action_frame, text="Copy Text", command=copy_text, state="disabled")
copy_text_button.pack(side="left", padx=5)
retry_button = ctk.CTkButton(action_frame, text="Thử lại", command=try_again)
retry_button.pack(side="left", padx=5)

# Khung hiển thị thông tin Wifi nếu phát hiện QR Wifi
wifi_frame = ctk.CTkFrame(read_frame)

ssid_frame = ctk.CTkFrame(wifi_frame)
ssid_frame.pack(pady=5, padx=5, fill="x")
ssid_label = ctk.CTkLabel(ssid_frame, text="SSID:")
ssid_label.pack(side="left", padx=5)
wifi_ssid_entry = ctk.CTkEntry(ssid_frame, state="readonly")
wifi_ssid_entry.pack(side="left", fill="x", expand=True, padx=5)
copy_ssid_button = ctk.CTkButton(ssid_frame, text="Copy", command=lambda: copy_wifi("ssid"))
copy_ssid_button.pack(side="left", padx=5)

password_frame = ctk.CTkFrame(wifi_frame)
password_frame.pack(pady=5, padx=5, fill="x")
password_label = ctk.CTkLabel(password_frame, text="Password:")
password_label.pack(side="left", padx=5)
wifi_password_entry = ctk.CTkEntry(password_frame, state="readonly")
wifi_password_entry.pack(side="left", fill="x", expand=True, padx=5)
copy_password_button = ctk.CTkButton(password_frame, text="Copy", command=lambda: copy_wifi("password"))
copy_password_button.pack(side="left", padx=5)

# Ẩn khung wifi ban đầu
wifi_frame.pack_forget()

root.mainloop()
