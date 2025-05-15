import math
import string
import hashlib
import requests
import customtkinter as ctk
import tkinter as tk  # for tk.END
import random

# --- Password scoring functions ---

def calculate_entropy(password: str) -> float:
    """Calculate estimated entropy of the password in bits."""
    charset_size = 0
    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
    if any(c in string.digits for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)

    if charset_size == 0 or len(password) == 0:
        return 0.0
    return len(password) * math.log2(charset_size)


def get_pwned_count(password: str) -> int:
    """Query HIBP API to get number of times password has appeared in breaches."""
    sha1pwd = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1pwd[:5], sha1pwd[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url, timeout=5)
    if res.status_code != 200:
        raise RuntimeError("Could not reach HIBP API")
    for line in res.text.splitlines():
        h, count = line.split(':')
        if h == suffix:
            return int(count)
    return 0


def score_password(password: str,
                   max_entropy: float = 80.0,
                   max_pwn_count: int = 1000000,
                   weight_entropy: float = 0.7,
                   weight_pwn: float = 0.3) -> float:
    """Return a score 0-100 combining entropy and pwn count.
    If no internet/HIBP unreachable, fallback to entropy-only with increased entropy weight."""
    ent = calculate_entropy(password)
    ent_score = min(ent / max_entropy, 1.0)

    try:
        pwn_count = get_pwned_count(password)
        pwn_score = 1.0 - min(math.log1p(pwn_count) / math.log1p(max_pwn_count), 1.0)
        total = ent_score * weight_entropy + pwn_score * weight_pwn
    except Exception:
        # No internet or HIBP failure: use entropy only, full weight to entropy
        total = ent_score

    return round(total * 100, 2)


# --- GUI Application ---

class PasswordToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator & Checker")
        self.geometry("500x450")

        # Create tab view
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Tabs: Generate, Check
        self.tabview.add("Generate")
        self.tabview.add("Check")

        self._build_generate_tab()
        self._build_check_tab()

    def _build_generate_tab(self):
        tab = self.tabview.tab("Generate")
        # Title
        ctk.CTkLabel(tab, text="Password Generator", font=(None, 20)).pack(pady=10)

        # Length controls
        self.gen_length_slider = ctk.CTkSlider(tab, from_=4, to=32,
                                               command=self._update_gen_length_entry)
        self.gen_length_slider.set(12)
        self.gen_length_slider.pack(pady=5)

        self.gen_length_entry = ctk.CTkEntry(tab, width=80)
        self.gen_length_entry.insert(0, "12")
        self.gen_length_entry.pack(pady=5)
        self.gen_length_entry.bind("<KeyRelease>", self._update_gen_slider)

        # Character options
        self.gen_var_letters = tk.BooleanVar(value=True)
        self.gen_var_numbers = tk.BooleanVar(value=True)
        self.gen_var_special = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(tab, text="Letters", variable=self.gen_var_letters,
                        command=self.generate_password).pack(pady=2)
        ctk.CTkCheckBox(tab, text="Numbers", variable=self.gen_var_numbers,
                        command=self.generate_password).pack(pady=2)
        ctk.CTkCheckBox(tab, text="Special", variable=self.gen_var_special,
                        command=self.generate_password).pack(pady=2)

        # Generated password display
        self.gen_password_entry = ctk.CTkEntry(tab, width=300)
        self.gen_password_entry.pack(pady=10)

        # Copy button
        self.gen_copy_btn = ctk.CTkButton(tab, text="Copy & Check",
                                          command=self.copy_and_check_generated)
        self.gen_copy_btn.pack(pady=5)

        # Score display
        self.gen_score_label = ctk.CTkLabel(tab, text="Score: N/A")
        self.gen_score_label.pack(pady=5)
        self.gen_score_bar = ctk.CTkProgressBar(tab, width=300)
        self.gen_score_bar.set(0)
        self.gen_score_bar.pack(pady=5)

        # Initial generate
        self.generate_password()

    def _build_check_tab(self):
        tab = self.tabview.tab("Check")
        ctk.CTkLabel(tab, text="Password Checker", font=(None, 20)).pack(pady=10)

        self.chk_password_entry = ctk.CTkEntry(tab, width=300)
        self.chk_password_entry.pack(pady=10)

        self.chk_btn = ctk.CTkButton(tab, text="Check", command=self.check_password)
        self.chk_btn.pack(pady=5)

        self.chk_score_label = ctk.CTkLabel(tab, text="Score: N/A")
        self.chk_score_label.pack(pady=5)
        self.chk_score_bar = ctk.CTkProgressBar(tab, width=300)
        self.chk_score_bar.set(0)
        self.chk_score_bar.pack(pady=5)

    # --- Generate tab callbacks ---
    def _update_gen_length_entry(self, value):
        val = str(int(float(value)))
        self.gen_length_entry.delete(0, tk.END)
        self.gen_length_entry.insert(0, val)
        self.generate_password()

    def _update_gen_slider(self, event):
        try:
            val = int(self.gen_length_entry.get())
        except ValueError:
            return
        val = max(4, min(32, val))
        self.gen_length_slider.set(val)
        self.generate_password()

    def generate_password(self):
        try:
            length = int(self.gen_length_entry.get())
        except ValueError:
            length = 12
        chars = ''
        if self.gen_var_letters.get(): chars += string.ascii_letters
        if self.gen_var_numbers.get(): chars += string.digits
        if self.gen_var_special.get(): chars += string.punctuation
        if not chars: chars = string.ascii_letters
        pwd = ''.join(random.choice(chars) for _ in range(length))
        self.gen_password_entry.delete(0, tk.END)
        self.gen_password_entry.insert(0, pwd)

    def copy_and_check_generated(self):
        pwd = self.gen_password_entry.get()
        self.clipboard_clear()
        self.clipboard_append(pwd)
        score = score_password(pwd)
        self.gen_score_label.configure(text=f"Score: {score}")
        self.gen_score_bar.set(score / 100)
        self.chk_password_entry.delete(0, tk.END)
        self.chk_password_entry.insert(0, pwd)
        self.chk_score_label.configure(text=f"Score: {score}")
        self.chk_score_bar.set(score / 100)

    # --- Check tab callback ---
    def check_password(self):
        pwd = self.chk_password_entry.get()
        score = score_password(pwd)
        self.chk_score_label.configure(text=f"Score: {score}")
        self.chk_score_bar.set(score / 100)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = PasswordToolApp()
    app.mainloop()
