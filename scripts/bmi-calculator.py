import customtkinter as ctk
from tkinter import messagebox

# Calculate BMI and suggest the ideal weight
def calculate_bmi():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        if weight <= 0 or height <= 0:
            raise ValueError("Weight and height must be greater than 0.")
        bmi = weight / (height ** 2)
        bmi_result_label.configure(text=f"Your BMI: {bmi:.2f}")
        
        if bmi < 18.5:
            result = "You are underweight."
        elif 18.5 <= bmi < 24.9:
            result = "Your weight is normal."
        elif 25 <= bmi < 29.9:
            result = "You are overweight."
        else:
            result = "You are obese."
        
        conclusion_label.configure(text=result)
        
        # Calculate ideal weight range
        min_weight = 18.5 * (height ** 2)
        max_weight = 24.9 * (height ** 2)
        ideal_weight_label.configure(
            text=f"Ideal weight range: {min_weight:.1f} kg to {max_weight:.1f} kg"
        )
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Set up the CustomTkinter interface
ctk.set_appearance_mode("System")  # Light or dark mode based on system settings
ctk.set_default_color_theme("blue")  # Default color theme

# Create main application window
app = ctk.CTk()
app.title("BMI Calculator")
app.geometry("400x450")

# Title
title_label = ctk.CTkLabel(app, text="BMI Calculator", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=20)

# Height input
height_label = ctk.CTkLabel(app, text="Height (m):")
height_label.pack(pady=5)
height_entry = ctk.CTkEntry(app, placeholder_text="Enter your height")
height_entry.pack(pady=5)

# Weight input
weight_label = ctk.CTkLabel(app, text="Weight (kg):")
weight_label.pack(pady=5)
weight_entry = ctk.CTkEntry(app, placeholder_text="Enter your weight")
weight_entry.pack(pady=5)

# Calculate button
calculate_button = ctk.CTkButton(app, text="Calculate", command=calculate_bmi)
calculate_button.pack(pady=20)

# Display BMI result
bmi_result_label = ctk.CTkLabel(app, text="")
bmi_result_label.pack(pady=5)

# Display conclusion
conclusion_label = ctk.CTkLabel(app, text="")
conclusion_label.pack(pady=5)

# Display ideal weight range
ideal_weight_label = ctk.CTkLabel(app, text="")
ideal_weight_label.pack(pady=10)

# Run the application
app.mainloop()

