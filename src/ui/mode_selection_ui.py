import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  
from src.utils.constants import *
import os

def create_mode_selection_widgets(app):
    app.mode_frame = tk.Frame(app.root, bg=BG_COLOR)
    app.mode_frame.pack(expand=True, fill="both")

    title = tk.Label(app.mode_frame, text="🎯 Chọn chế độ", bg=BG_COLOR,
                     font=("Segoe UI", 20, "bold"), fg="#212529")
    title.pack(pady=20)

    main_frame = tk.Frame(app.mode_frame, bg=BG_COLOR)
    main_frame.pack(pady=10)

    # Style button
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Exam.TButton", font=("Segoe UI", 12, "bold"),
                    background="#007bff", foreground="white", padding=10)
    style.map("Exam.TButton",
              background=[("active", "#0056b3"), ("pressed", "#004080")])

    style.configure("Practice.TButton", font=("Segoe UI", 12, "bold"),
                    background="#17a2b8", foreground="white", padding=10)
    style.map("Practice.TButton",
              background=[("active", "#117a8b"), ("pressed", "#0b5d6c")])

    def load_image(path, size=(150, 150)):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    practice_img_path = os.path.join(current_dir, "practice.png")
    exam_img_path = os.path.join(current_dir, "exam.png")

    # Load images
    exam_img = load_image(exam_img_path)
    practice_img = load_image(practice_img_path)

    # Cột trái: Làm đề thi
    left_frame = tk.Frame(main_frame, bg=BG_COLOR)
    left_frame.grid(row=0, column=0, padx=40)

    if exam_img:
        tk.Label(left_frame, image=exam_img, bg=BG_COLOR).pack(pady=10)
        app.exam_img = exam_img  

    ttk.Button(left_frame, text="📝 Làm đề thi",
               command=lambda: app.set_mode("exam"),
               style="Exam.TButton").pack(pady=10)

    right_frame = tk.Frame(main_frame, bg=BG_COLOR)
    right_frame.grid(row=0, column=1, padx=40)

    if practice_img:
        tk.Label(right_frame, image=practice_img, bg=BG_COLOR).pack(pady=10)
        app.practice_img = practice_img 

    ttk.Button(right_frame, text="📚 Làm bài tập trắc nghiệm",
               command=lambda: app.set_mode("practice"),
               style="Practice.TButton").pack(pady=10)