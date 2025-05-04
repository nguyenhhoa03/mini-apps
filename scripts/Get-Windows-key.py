import sys
import subprocess
import re
import platform
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os

# Function to check environment

def check_windows_environment():
    return platform.system() == 'Windows'

# Function to get Windows product key

def get_windows_key():
    try:
        # Query the DigitalProductId from registry
        output = subprocess.check_output(
            ['powershell', '-Command',
             "(Get-WmiObject -query 'select * from SoftwareLicensingService').OA3xOriginalProductKey"],
            universal_newlines=True)
        key = output.strip()
        if not key:
            return 'Digital License (no embedded key)'
        return key
    except subprocess.CalledProcessError:
        return 'Could not retrieve Windows key'

# Function to get Office product key

def get_office_keys():
    try:
        # Office keys retrieval script via vbscript
        script = (
            "Set WshShell = CreateObject(\"WScript.Shell\")\n"
            "Const HKEY_LOCAL_MACHINE = &H80000002\n"
            "strKeyPath = \"SOFTWARE\\Microsoft\\Office\\ClickToRun\\Configuration\"\n"
            "Set oReg=GetObject(\"winmgmts:{impersonationLevel=impersonate}!\\\\.\\root\\default:StdRegProv\")\n"
            "oReg.GetStringValue HKEY_LOCAL_MACHINE, strKeyPath, \"DigitalProductId\", sValue\n"
            "If IsNull(sValue) Then\n"
            "    Wscript.Echo \"No key found\"\n"
            "Else\n"
            "    Wscript.Echo sValue\n"
            "End If\n"
        )
        with open('get_office_key.vbs', 'w') as f:
            f.write(script)
        output = subprocess.check_output(
            ['cscript', '//NoLogo', 'get_office_key.vbs'],
            universal_newlines=True)
        os.remove('get_office_key.vbs')
        key = output.strip()
        return key or 'No Office key found'
    except Exception as e:
        return f'Error retrieving Office key: {e}'

# GUI setup

def main():
    if not check_windows_environment():
        tk.messagebox.showerror("Environment Error", "This tool can only run on Windows.")
        sys.exit(1)

    app = ctk.CTk()
    app.title("Windows & Office Key Retriever")
    app.geometry("500x300")

    # Windows key frame
    win_frame = ctk.CTkFrame(app)
    win_frame.pack(pady=20, padx=20, fill='x')

    win_label = ctk.CTkLabel(win_frame, text="Windows Key:")
    win_label.grid(row=0, column=0, sticky='w')

    win_key = get_windows_key()
    win_key_var = tk.StringVar(value=win_key)
    win_entry = ctk.CTkEntry(win_frame, textvariable=win_key_var, width=300, state='readonly')
    win_entry.grid(row=1, column=0, padx=(0,10))

    def copy_win_key():
        app.clipboard_clear()
        app.clipboard_append(win_key_var.get())
        tk.messagebox.showinfo("Copied", "Windows key copied to clipboard.")

    win_copy_btn = ctk.CTkButton(win_frame, text="Copy", command=copy_win_key)
    win_copy_btn.grid(row=1, column=1)

    # Office key frame
    office_frame = ctk.CTkFrame(app)
    office_frame.pack(pady=20, padx=20, fill='x')

    office_label = ctk.CTkLabel(office_frame, text="Office Key:")
    office_label.grid(row=0, column=0, sticky='w')

    office_key = get_office_keys()
    office_key_var = tk.StringVar(value=office_key)
    office_entry = ctk.CTkEntry(office_frame, textvariable=office_key_var, width=300, state='readonly')
    office_entry.grid(row=1, column=0, padx=(0,10))

    def copy_office_key():
        app.clipboard_clear()
        app.clipboard_append(office_key_var.get())
        tk.messagebox.showinfo("Copied", "Office key copied to clipboard.")

    office_copy_btn = ctk.CTkButton(office_frame, text="Copy", command=copy_office_key)
    office_copy_btn.grid(row=1, column=1)

    app.mainloop()

if __name__ == '__main__':
    main()
