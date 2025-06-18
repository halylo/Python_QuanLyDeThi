import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

# Define constants for consistency with login_ui.py
BG_MAIN = "#FFF8DC"        # Main background (light yellow)
BG_GROUP = "#FAEAB1"       # Frame background
BTN_BG = "#E6C87C"         # Button background
BTN_HOVER = "#D6B95F"      # Button hover
FONT = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")

def create_account(app):
    username = tk.StringVar()
    role_window = tk.Toplevel(app.root)
    role_window.title("Tạo tài khoản")
    role_window.configure(bg=BG_MAIN)
    role_window.geometry("500x600")

    shadow = tk.Frame(role_window, bg='#dee2e6', bd=5)  # Keep shadow color consistent
    shadow.pack(expand=True, padx=5, pady=5)

    container = tk.Frame(shadow, bg=BG_GROUP, bd=5, relief='flat')
    container.pack(expand=True, padx=5, pady=5, fill=tk.BOTH)

    tk.Label(container, text="Tạo tài khoản mới", bg=BG_GROUP, font=FONT_BOLD, fg='#343a40').pack(pady=15)

    username_frame = tk.Frame(container, bg=BG_GROUP, bd=2, relief='groove')
    username_frame.pack(fill=tk.X, padx=25, pady=5)
    tk.Label(username_frame, text="Tên đăng nhập:", font=FONT, bg=BG_GROUP, fg='#495057').pack(anchor='w', padx=5)
    username_entry = tk.Entry(username_frame, textvariable=username, font=FONT,
                             relief='flat', bg='#e9ecef', fg='#212529', width=30, bd=1)
    username_entry.pack(pady=5, ipady=8, fill=tk.X)

    password_frame = tk.Frame(container, bg=BG_GROUP, bd=2, relief='groove')
    password_frame.pack(fill=tk.X, padx=25, pady=5)
    tk.Label(password_frame, text="Mật khẩu:", font=FONT, bg=BG_GROUP, fg='#495057').pack(anchor='w', padx=5)
    password_entry_frame = tk.Frame(password_frame, bg=BG_GROUP)
    password_entry_frame.pack(fill=tk.X, padx=5)
    password_entry = tk.Entry(password_entry_frame, show="*", font=FONT,
                             relief='flat', bg='#e9ecef', fg='#212529', width=25, bd=1)
    password_entry.pack(side=tk.LEFT, pady=5, ipady=8, fill=tk.X, expand=True)

    show_password_var = tk.BooleanVar()
    def toggle_password():
        password_entry.config(show="" if show_password_var.get() else "*")
        confirm_entry.config(show="" if show_password_var.get() else "*")

    tk.Checkbutton(password_entry_frame, text="Hiện", variable=show_password_var,
                   command=toggle_password, bg=BG_GROUP, font=FONT).pack(side=tk.RIGHT, padx=5)

    confirm_frame = tk.Frame(container, bg=BG_GROUP, bd=2, relief='groove')
    confirm_frame.pack(fill=tk.X, padx=25, pady=5)
    tk.Label(confirm_frame, text="Xác nhận mật khẩu:", font=FONT, bg=BG_GROUP, fg='#495057').pack(anchor='w', padx=5)
    confirm_entry = tk.Entry(confirm_frame, show="*", font=FONT,
                            relief='flat', bg='#e9ecef', fg='#212529', width=30, bd=1)
    confirm_entry.pack(pady=5, ipady=8, fill=tk.X)

    tk.Label(container, text="Yêu cầu mật khẩu:", bg=BG_GROUP, font=FONT_BOLD,
             fg='#343a40').pack(pady=5, anchor='w', padx=25)
    requirements = [
        "- Từ 8 đến 16 ký tự",
        "- Ít nhất 1 chữ cái in hoa",
        "- Ít nhất 1 chữ cái thường",
        "- Ít nhất 1 số",
        "- Ít nhất 1 ký tự đặc biệt (!@#$%^&*(),.?\":{}|<>)"
    ]
    for req in requirements:
        tk.Label(container, text=req, bg=BG_GROUP, font=FONT,
                 fg='#6b7280').pack(anchor='w', padx=35)

    def try_create_account():
        username_value = username.get().strip().lower()
        if not username_value:
            tk.messagebox.showwarning("Cảnh báo", "Tên đăng nhập không được để trống!")
            return
        if username_value in app.account_data["users"]:
            tk.messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
            return

        password = password_entry.get()
        confirm_password = confirm_entry.get()

        if password != confirm_password:
            tk.messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)
            return

        is_valid, error_message = app.validate_password(password)
        if not is_valid:
            tk.messagebox.showerror("Lỗi", error_message)
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)
            return

        app.account_data["users"][username_value] = {
            "password": password,
            "role": "user"  # Default role is user
        }
        app.data_manager.save_account_data(app.account_data)
        tk.messagebox.showinfo("Thành công", f"Tạo tài khoản '{username_value}' thành công!")
        role_window.destroy()

    def cancel():
        role_window.destroy()

    btn_frame = tk.Frame(container, bg=BG_GROUP)
    btn_frame.pack(pady=15, fill=tk.X)

    center_frame = tk.Frame(btn_frame, bg=BG_GROUP)
    center_frame.pack(expand=True)

    def on_enter(e, btn):
        btn.config(bg=BTN_HOVER)
    def on_leave(e, btn):
        btn.config(bg=BTN_BG)

    confirm_btn = tk.Button(center_frame, text="Xác nhận", command=try_create_account, bg=BTN_BG, fg='white',
                            font=FONT_BOLD, relief='flat', width=12)
    confirm_btn.pack(side=tk.LEFT, padx=5, pady=5)
    confirm_btn.bind("<Enter>", lambda e: on_enter(e, confirm_btn))
    confirm_btn.bind("<Leave>", lambda e: on_leave(e, confirm_btn))

    cancel_btn = tk.Button(center_frame, text="Hủy", command=cancel, bg=BTN_BG, fg='white',
                           font=FONT_BOLD, relief='flat', width=12)
    cancel_btn.pack(side=tk.LEFT, padx=5, pady=5)
    cancel_btn.bind("<Enter>", lambda e: on_enter(e, cancel_btn))
    cancel_btn.bind("<Leave>", lambda e: on_leave(e, cancel_btn))

    # Allow Enter key to trigger confirm
    confirm_entry.bind("<Return>", lambda e: try_create_account())