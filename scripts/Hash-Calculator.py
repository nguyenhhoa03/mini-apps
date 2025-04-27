import customtkinter as ctk
import threading
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox

# Configure customtkinter theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

HASH_FUNCTIONS = {
    'MD5': hashlib.md5,
    'SHA1': hashlib.sha1,
    'SHA224': hashlib.sha224,
    'SHA256': hashlib.sha256,
    'SHA384': hashlib.sha384,
    'SHA512': hashlib.sha512,
}

class HashApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hash Calculator")
        self.geometry("600x500")

        # Mode selection
        self.mode_var = tk.StringVar(value="text")
        self.radio_text = ctk.CTkRadioButton(self, text="Text", variable=self.mode_var, value="text", command=self._update_mode)
        self.radio_file = ctk.CTkRadioButton(self, text="File", variable=self.mode_var, value="file", command=self._update_mode)
        self.radio_text.pack(pady=10)
        self.radio_file.pack(pady=0)

        # Frame for input
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=20, pady=10)

        self.text_input = ctk.CTkTextbox(self.input_frame, height=100)
        self.text_input.pack(fill="both", expand=True, padx=10, pady=10)

        self.file_button = ctk.CTkButton(self.input_frame, text="Select File...", command=self._select_file)
        self.file_label = ctk.CTkLabel(self.input_frame, text="No file selected")
        # initially hide file widgets
        self.file_button.pack_forget()
        self.file_label.pack_forget()

        # Compute button
        self.compute_button = ctk.CTkButton(self, text="Compute Hashes", command=self._start_hash_thread)
        self.compute_button.pack(pady=10)

        # Results frame
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.hash_widgets = {}

    def _update_mode(self):
        mode = self.mode_var.get()
        # Clear input frame
        self.text_input.pack_forget()
        self.file_button.pack_forget()
        self.file_label.pack_forget()
        if mode == "text":
            self.text_input.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.file_button.pack(pady=10)
            self.file_label.pack()

    def _select_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.selected_file = filepath
            self.file_label.configure(text=filepath)

    def _start_hash_thread(self):
        # Disable button to prevent re-click
        self.compute_button.configure(state="disabled")
        # Clear previous results
        for widget in self.hash_widgets.values():
            widget['frame'].destroy()
        self.hash_widgets.clear()

        thread = threading.Thread(target=self._compute_hashes)
        thread.start()

    def _compute_hashes(self):
        try:
            data = b""
            if self.mode_var.get() == "text":
                txt = self.text_input.get("1.0", "end-1c")
                data = txt.encode('utf-8')
            else:
                filepath = getattr(self, 'selected_file', None)
                if not filepath:
                    raise ValueError("No file selected")
                with open(filepath, 'rb') as f:
                    data = f.read()

            # Compute each hash
            for name, func in HASH_FUNCTIONS.items():
                hasher = func()
                hasher.update(data)
                digest = hasher.hexdigest()
                # Update UI in main thread
                self.after(0, self._add_result, name, digest)

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.after(0, lambda: self.compute_button.configure(state="normal"))

    def _add_result(self, algo, digest):
        frame = ctk.CTkFrame(self.results_frame)
        frame.pack(fill="x", pady=5)

        label = ctk.CTkLabel(frame, text=f"{algo}:")
        label.pack(side="left", padx=(10,5))

        entry = ctk.CTkEntry(frame, width=350)
        entry.insert(0, digest)
        entry.configure(state="readonly")
        entry.pack(side="left", padx=(0,5))

        button = ctk.CTkButton(frame, text="Copy", width=60, command=lambda d=digest: self._copy_to_clipboard(d))
        button.pack(side="left", padx=(0,10))

        self.hash_widgets[algo] = {'frame': frame, 'entry': entry, 'button': button}

    def _copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Hash copied to clipboard!")

if __name__ == "__main__":
    app = HashApp()
    app.mainloop()
