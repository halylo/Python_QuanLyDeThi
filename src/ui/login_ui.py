import tkinter as tk
from PIL import Image, ImageTk
import os

# Define constants (replace imported ones for consistency)
BG_MAIN = "#FFF8DC"        # Main background
BG_GROUP = "#FAEAB1"       # Frame background
BTN_BG = "#E6C87C"         # Button background
BTN_HOVER = "#D6B95F"      # Button hover
FONT = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")

def create_login_widgets(app):
    app.login_frame = tk.Frame(app.root, bg=BG_MAIN)
    app.login_frame.pack(expand=True, fill=tk.BOTH)

    shadow = tk.Frame(app.login_frame, bg='#dee2e6', bd=5)
    shadow.pack(expand=True, padx=5, pady=5)

    container = tk.Frame(shadow, bg=BG_GROUP, bd=5, relief='flat')
    container.pack(expand=True, padx=5, pady=5, fill=tk.BOTH)

    tk.Label(container, text="Ứng dụng Quản lý đề", font=FONT_BOLD,
             bg=BG_GROUP, fg='#343a40').pack(pady=10)

    # Logo
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logo.png")
        if not os.path.exists(logo_path):
            raise FileNotFoundError("File logo.png không tồn tại!")
        image = Image.open(logo_path)
        image = image.resize((165, 165), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(image)
        logo_label = tk.Label(container, image=logo_img, bg=BG_GROUP)
        logo_label.image = logo_img
        logo_label.pack(pady=10)
    except Exception as e:
        tk.Label(container, text="Logo không khả dụng", font=FONT,
                 bg=BG_GROUP, fg='#ff0000').pack(pady=10)

    # Username
    username_frame = tk.Frame(container, bg=BG_GROUP, bd=2, relief='groove')
    username_frame.pack(fill=tk.X, padx=30, pady=5)
    tk.Label(username_frame, text="Tên đăng nhập:", font=FONT,
             bg=BG_GROUP, fg='#495057').pack(anchor='w', padx=5, pady=5)
    app.entry_username = tk.Entry(username_frame, font=FONT,
                                 relief='flat', bg='#e9ecef', fg='#212529', width=30, bd=1)
    app.entry_username.pack(pady=5, ipady=8, padx=5)

    # Password
    password_frame = tk.Frame(container, bg=BG_GROUP, bd=2, relief='groove')
    password_frame.pack(fill=tk.X, padx=30, pady=5)
    tk.Label(password_frame, text="Mật khẩu:", font=FONT,
             bg=BG_GROUP, fg='#495057').pack(anchor='w', padx=5, pady=5)
    password_entry_frame = tk.Frame(password_frame, bg=BG_GROUP)
    password_entry_frame.pack(fill=tk.X, padx=5)
    app.entry_password = tk.Entry(password_entry_frame, show="*", font=FONT,
                                 relief='flat', bg='#e9ecef', fg='#212529', width=25, bd=1)
    app.entry_password.pack(side=tk.LEFT, pady=5, ipady=8, fill=tk.X, expand=True)

    show_password_var = tk.BooleanVar()
    def toggle_password():
        app.entry_password.config(show="" if show_password_var.get() else "*")

    tk.Checkbutton(password_entry_frame, text="Hiện", variable=show_password_var,
                   command=toggle_password, bg=BG_GROUP, font=FONT).pack(side=tk.RIGHT, padx=5)

    # Buttons
    button_frame = tk.Frame(container, bg=BG_GROUP)
    button_frame.pack(pady=15)

    def on_enter(e, btn):
        btn.config(bg=BTN_HOVER)
    def on_leave(e, btn):
        btn.config(bg=BTN_BG)

    login_btn_frame = tk.Frame(button_frame, bg=BG_GROUP)
    login_btn_frame.pack(side=tk.LEFT, padx=10)
    login_btn = tk.Button(login_btn_frame, text="Đăng nhập", command=app.login,
                          bg=BTN_BG, fg='white', font=FONT_BOLD, relief='flat', width=15)
    login_btn.pack(pady=2)
    login_btn.bind("<Enter>", lambda e: on_enter(e, login_btn))
    login_btn.bind("<Leave>", lambda e: on_leave(e, login_btn))

    create_btn_frame = tk.Frame(button_frame, bg=BG_GROUP)
    create_btn_frame.pack(side=tk.RIGHT, padx=10)
    create_btn = tk.Button(create_btn_frame, text="Tạo tài khoản", command=app.create_account,
                           bg=BTN_BG, fg='white', font=FONT_BOLD, relief='flat', width=15)
    create_btn.pack(pady=2)
    create_btn.bind("<Enter>", lambda e: on_enter(e, create_btn))
    create_btn.bind("<Leave>", lambda e: on_leave(e, create_btn))

    # Allow Enter key to trigger login
    app.entry_password.bind("<Return>", lambda e: app.login())