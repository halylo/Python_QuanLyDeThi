import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import json
from tkcalendar import DateEntry
from datetime import datetime
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

# Định nghĩa bảng màu và font
BG_MAIN = "#FFF8DC"        # vàng nhạt
FG_TEXT = "#2d3748"        # xám đậm
FONT_LABEL = ("Segoe UI", 12)
FONT_ENTRY = ("Segoe UI", 11)
BG_FRAME = "#FAEAB1"       # vàng nhạt đậm hơn
BG_WHITE = "#FFFFFF"       # trắng
BTN_BG = "#E6C87C"         # màu nền nút
BTN_HOVER = "#D6B95F"      # màu hover nút

def create_widgets(app):
    # Cấu hình style cho Treeview và Combobox
    style = ttk.Style()
    style.configure("Treeview", background=BG_WHITE, foreground=FG_TEXT, fieldbackground=BG_WHITE)
    style.configure("TCombobox", fieldbackground=BG_WHITE, foreground=FG_TEXT)

    if not hasattr(app, "current_user") or not app.current_user:
        app.logger.error("Không có người dùng hiện tại")
        messagebox.showerror("Lỗi", "Không có người dùng hiện tại! Vui lòng đăng nhập lại.")
        try:
            app.logout()
        except Exception as e:
            app.logger.error(f"Lỗi khi đăng xuất: {str(e)}")
            app.root.destroy()
        return

    try:
        if not isinstance(app.account_data, dict) or "users" not in app.account_data:
            raise KeyError("Dữ liệu tài khoản không hợp lệ")
        if app.current_user not in app.account_data["users"]:
            app.logger.error(f"Người dùng {app.current_user} không tồn tại")
            messagebox.showerror("Lỗi", f"Người dùng {app.current_user} không tồn tại trong hệ thống!")
            app.logout()
            return
        user_data = app.account_data["users"][app.current_user]
        role = user_data.get("role", "user")
        if role not in ["admin", "user"]:
            app.logger.error(f"Vai trò không hợp lệ: {role}")
            messagebox.showerror("Lỗi", "Vai trò người dùng không hợp lệ!")
            app.logout()
            return
    except KeyError as e:
        app.logger.error(f"Lỗi dữ liệu tài khoản: {str(e)}")
        messagebox.showerror("Lỗi", f"Lỗi dữ liệu tài khoản: {str(e)}")
        app.logout()
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    frame_left = tk.Frame(app.root, padx=15, pady=10, bg=BG_MAIN, relief='raised', bd=3)
    frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

    app.frame_right = tk.Frame(app.root, padx=10, pady=5, bg=BG_MAIN, relief='raised', bd=3)
    app.frame_right.pack(pady=10, padx=10, side=tk.RIGHT, expand=True, fill=tk.BOTH)

    tk.Label(frame_left, text=f"Người dùng: {app.current_user} ({role})", bg=BG_MAIN, fg=FG_TEXT,
             font=FONT_LABEL, padx=10, pady=5).pack(pady=10)

    main_buttons_frame = tk.Frame(frame_left, bg=BG_MAIN)
    main_buttons_frame.pack(fill=tk.X, pady=5)

    def convert_date_format(date_str, from_format="%d-%m-%Y", to_format="%Y-%m-%d"):
        try:
            date_obj = datetime.strptime(date_str, from_format)
            return date_obj.strftime(to_format)
        except ValueError:
            app.logger.warning(f"Định dạng ngày không hợp lệ: {date_str}, giữ nguyên giá trị")
            return date_str

    def load_test_data():
        json_path = os.path.join(current_dir, "test_questions.json")
        try:
            if not os.path.exists(json_path):
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump({"mon_thi": [], "cau_hoi": {}}, f, ensure_ascii=False, indent=4)
                    app.logger.info(f"Tạo file test_questions.json mặc định tại {json_path}")
                except PermissionError as e:
                    app.logger.error(f"Không thể tạo file test_questions.json: {str(e)}")
                    messagebox.showerror("Lỗi", f"Không thể tạo file test_questions.json: {str(e)}")
                    app.test_data = {"mon_thi": [], "cau_hoi": {}}
                    return
            with open(json_path, 'r', encoding='utf-8') as f:
                app.test_data = json.load(f)
            if not isinstance(app.test_data, dict) or "mon_thi" not in app.test_data or "cau_hoi" not in app.test_data:
                raise ValueError("Cấu trúc JSON không hợp lệ")
            for ten_mon in app.test_data["cau_hoi"]:
                for ma_de in app.test_data["cau_hoi"][ten_mon]:
                    ngay_den_han = app.test_data["cau_hoi"][ten_mon][ma_de].get("ngay_den_han", "")
                    if ngay_den_han:
                        app.test_data["cau_hoi"][ten_mon][ma_de]["ngay_den_han"] = convert_date_format(ngay_den_han)
            app.logger.debug("Tải dữ liệu bài tập thành công")
        except json.JSONDecodeError as e:
            app.logger.error(f"File test_questions.json không đúng định dạng: {str(e)}")
            messagebox.showerror("Lỗi", f"File test_questions.json không đúng định dạng: {str(e)}")
            app.test_data = {"mon_thi": [], "cau_hoi": {}}
        except PermissionError as e:
            app.logger.error(f"Không có quyền truy cập file test_questions.json: {str(e)}")
            messagebox.showerror("Lỗi", f"Không có quyền truy cập file test_questions.json")
            app.test_data = {"mon_thi": [], "cau_hoi": {}}
        except Exception as e:
            app.logger.error(f"Lỗi khi load test_questions.json: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi khi load test_questions.json: {str(e)}")
            app.test_data = {"mon_thi": [], "cau_hoi": {}}

    def clear_sub_frame():
        if 'sub_frame' in locals() and sub_frame.winfo_exists():
            sub_frame.destroy()

    def create_button(frame, text, command):
        btn = tk.Button(frame, text=text, command=command,
                        bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat')
        btn.pack(fill=tk.X, pady=4, padx=8, side=tk.LEFT if frame != main_buttons_frame else tk.TOP)
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_BG))
        return btn

    def show_manage_practice():
        load_test_data()
        for widget in app.frame_right.winfo_children():
            widget.destroy()

        list_frame = tk.Frame(app.frame_right, bg=BG_MAIN, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(list_frame, text="📋 Danh sách môn bài tập trắc nghiệm",
                         font=FONT_LABEL, fg=FG_TEXT, bg=BG_MAIN)
        title.pack(pady=(0, 10))
        
        FONT = ("Segoe UI", 12)  # Default font and size
        FONT_BOLD = ("Segoe UI", 12, "bold")  # For headings (optional)
        columns = ("ma_mon", "ten_mon", "han_nop_bai")
        style = ttk.Style()
        style.configure("Custom.Treeview", font=FONT)  # Set font for Treeview content
        style.configure("Custom.Treeview.Heading", font=FONT_BOLD)
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10, style="Custom.Treeview")
        tree.heading("ma_mon", text="Mã môn")
        tree.heading("ten_mon", text="Tên môn")
        tree.heading("han_nop_bai", text="Hạn nộp bài")
        tree.column("ma_mon", width=100, anchor="center")
        tree.column("ten_mon", width=300, anchor="w")
        tree.column("han_nop_bai", width=150, anchor="center")
        tree.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        def refresh_treeview():
            for item in tree.get_children():
                tree.delete(item)
            subjects = app.test_data.get("mon_thi", [])
            for subject in subjects:
                tree.insert("", "end", values=(
                    subject.get("ma_mon", "N/A"),
                    subject.get("ten_mon", "Unknown"),
                    subject.get("han_nop_bai", "N/A")
                ))

        refresh_treeview()

        def add_subject():
            for widget in app.frame_right.winfo_children():
                widget.destroy()

            form_frame = tk.Frame(app.frame_right, bg=BG_WHITE, padx=20, pady=20)
            form_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(form_frame, text="Mã môn:", bg=BG_WHITE, fg=FG_TEXT, font=FONT_LABEL).grid(
                row=1, column=0, padx=10, pady=10, sticky="e")
            entry_ma_mon = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_ma_mon.grid(row=1, column=1, padx=10, pady=10)

            tk.Label(form_frame, text="Tên môn:", bg=BG_WHITE, fg=FG_TEXT, font=FONT_LABEL).grid(
                row=2, column=0, padx=10, pady=10, sticky="e")
            entry_ten_mon = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_ten_mon.grid(row=2, column=1, padx=10, pady=10)

            tk.Label(form_frame, text="Hạn nộp bài:", bg=BG_WHITE, fg=FG_TEXT, font=FONT_LABEL).grid(
                row=3, column=0, padx=10, pady=10, sticky="e")
            entry_han_nop = DateEntry(form_frame, width=27, font=FONT_ENTRY, date_pattern='yyyy-mm-dd',
                                      background=BG_WHITE, foreground=FG_TEXT)
            entry_han_nop.grid(row=3, column=1, padx=10, pady=10)
            
            tk.Button(form_frame, text="⬅️ Trở lại", command=show_manage_practice,
                      font=FONT_ENTRY, bg=BTN_BG, fg="#FFFFFF", relief="flat", padx=10, pady=4).grid(
                row=4, column=0, columnspan=2, pady=20)

            def submit():
                ma_mon = entry_ma_mon.get().strip()
                ten_mon = entry_ten_mon.get().strip()
                han_nop = entry_han_nop.get()

                if not all([ma_mon, ten_mon, han_nop]):
                    messagebox.showerror("Lỗi!", "Vui lòng nhập đầy đủ thông tin!")
                    return

                if not (3 <= len(ma_mon) <= 10):
                    messagebox.showerror("Lỗi!", "Mã môn phải có độ dài từ 3 đến 10 ký tự!")
                    return
                if not (3 <= len(ten_mon) <= 50):
                    messagebox.showerror("Lỗi!", "Tên môn phải có độ dài từ 3 đến 50 ký tự!")
                    return
                if not re.match(r'^[a-zA-Z0-9_]+$', ma_mon):
                    messagebox.showerror("Lỗi!", "Mã môn chỉ được chứa chữ, số và gạch dưới!")
                    return

                for subject in app.test_data["mon_thi"]:
                    if subject["ma_mon"] == ma_mon or subject["ten_mon"] == ten_mon:
                        messagebox.showerror("Lỗi!", "Mã môn hoặc tên môn đã tồn tại!")
                        return

                app.test_data["mon_thi"].append({
                    "ma_mon": ma_mon,
                    "ten_mon": ten_mon,
                    "han_nop_bai": han_nop
                })
                app.test_data["cau_hoi"].setdefault(ten_mon, {})
                app.data_manager.save_data(app.test_data, is_test=True)
                messagebox.showinfo("Thành công!", "Thêm môn học thành công!")
                show_manage_practice()

            tk.Button(form_frame, text="Thêm môn", command=submit,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                row=6, column=0, columnspan=2, pady=16)

        def edit_subject():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Cảnh báo!", "Vui lòng chọn một môn để sửa!")
                return
            selected_values = tree.item(selected_item)["values"]
            ma_mon_old = selected_values[0]
            ten_mon_old = selected_values[1]
            han_nop_old = selected_values[2]

            for widget in app.frame_right.winfo_children():
                widget.destroy()

            form_frame = tk.Frame(app.frame_right, bg=BG_WHITE, padx=10, pady=10)
            form_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(form_frame, text="Mã môn:", bg=BG_WHITE, fg=FG_TEXT,
                     font=FONT_LABEL).grid(row=0, column=0, padx=5, pady=10, sticky="e")
            entry_ma_mon = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_ma_mon.insert(0, ma_mon_old)
            entry_ma_mon.grid(row=0, column=1, padx=5, pady=10)

            tk.Label(form_frame, text="Tên môn:", bg=BG_WHITE, fg=FG_TEXT,
                     font=FONT_LABEL).grid(row=1, column=0, padx=5, pady=10, sticky="e")
            entry_ten_mon = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_ten_mon.insert(0, ten_mon_old)
            entry_ten_mon.grid(row=1, column=1, padx=5, pady=10)

            tk.Label(form_frame, text="Hạn nộp bài:", bg=BG_WHITE, fg=FG_TEXT,
                     font=FONT_LABEL).grid(row=2, column=0, padx=5, pady=10, sticky="e")
            entry_han_nop = DateEntry(form_frame, width=27, font=FONT_ENTRY, date_pattern='yyyy-mm-dd',
                                      background=BG_WHITE, foreground=FG_TEXT)
            try:
                if han_nop_old != "N/A":
                    date_obj = datetime.strptime(han_nop_old, '%Y-%m-%d')
                    entry_han_nop.set_date(date_obj)
                else:
                    entry_han_nop.set_date(datetime.now().today())
            except ValueError:
                entry_han_nop.set_date(datetime.now().today())
            entry_han_nop.grid(row=2, column=1, padx=5, pady=10)

            def submit():
                ma_mon = entry_ma_mon.get().strip()
                ten_mon = entry_ten_mon.get().strip()
                han_nop = entry_han_nop.get()

                if not all([ma_mon, ten_mon, han_nop]):
                    messagebox.showerror("Lỗi!", "Vui lòng nhập đầy đủ thông tin!")
                    return

                if not (3 <= len(ma_mon) <= 10):
                    messagebox.showerror("Lỗi!", "Mã môn phải có độ dài từ 3 đến 10 ký tự!")
                    return
                if not (3 <= len(ten_mon) <= 50):
                    messagebox.showerror("Lỗi!", "Tên môn phải có độ dài từ 3 đến 50 ký tự!")
                    return
                if not re.match(r'^[a-zA-Z0-9_]+$', ma_mon):
                    messagebox.showerror("Lỗi!", "Mã môn chỉ được chứa chữ, số và gạch dưới!")
                    return

                for subject in app.test_data["mon_thi"]:
                    if (subject["ma_mon"] == ma_mon and subject["ma_mon"] != ma_mon_old) or \
                       (subject["ten_mon"] == ten_mon and subject["ten_mon"] != ten_mon_old):
                        messagebox.showerror("Lỗi!", "Mã môn hoặc tên một môn đã tồn tại!")
                        return

                for subject in app.test_data["mon_thi"]:
                    if subject["ma_mon"] == ma_mon_old:
                        subject["ma_mon"] = ma_mon
                        subject["ten_mon"] = ten_mon
                        subject["han_nop_bai"] = han_nop
                        break

                if ten_mon_old != ten_mon:
                    app.test_data["cau_hoi"][ten_mon] = app.test_data["cau_hoi"].pop(ten_mon_old, {})

                app.data_manager.save_data(app.test_data, is_test=True)
                messagebox.showinfo("Thành công!", "Sửa môn học thành công!")
                show_manage_practice()

            tk.Button(form_frame, text="Lưu", command=submit,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                row=3, column=0, columnspan=2, pady=10)
            tk.Button(form_frame, text="Hủy bỏ", command=show_manage_practice,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                row=4, column=0, columnspan=2, pady=5)

        def show_questions(selected_subject):
            for widget in app.frame_right.winfo_children():
                widget.destroy()

            questions_frame = tk.Frame(app.frame_right, bg=BG_MAIN, padx=10, pady=10)
            questions_frame.pack(fill=tk.BOTH, expand=True)

            scroll_y = tk.Scrollbar(questions_frame)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            text_questions = tk.Text(questions_frame, width=60, height=10, bg=BG_WHITE, fg=FG_TEXT,
                                     font=FONT_ENTRY, relief='flat', bd=1, yscrollcommand=scroll_y.set)
            text_questions.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
            scroll_y.config(command=text_questions.yview)

            if selected_subject not in app.test_data["cau_hoi"]:
                text_questions.insert("1.0", "Không có câu hỏi nào!")
            else:
                question_index = 1
                for ma_de, de_thi in app.test_data["cau_hoi"][selected_subject].items():
                    text_questions.insert("end", f"Đề: {de_thi['ten_de']} (Hạn: {de_thi.get('ngay_den_han', 'N/A')})\n\n")
                    questions = de_thi.get("cau_hoi", [])
                    for q in questions:
                        text_questions.insert("end", f"Câu {question_index}: {q['cau_hoi']}\n")
                        for i, dap_an in enumerate(q['dap_an']):
                            text_questions.insert("end", f"{chr(65 + i)}. {dap_an}\n")
                        text_questions.insert("end", f"Đáp án đúng: {chr(65 + q['dap_an_dung'])}\n\n")
                        question_index += 1
                    text_questions.insert("end", "\n")

            text_questions.config(state="disabled")

            action_frame = tk.Frame(app.frame_right, bg=BG_MAIN, padx=10, pady=5)
            action_frame.pack(fill=tk.X)

            def add_question():
                for widget in app.frame_right.winfo_children():
                    widget.destroy()

                form_frame = tk.Frame(app.frame_right, bg=BG_WHITE, padx=10, pady=10)
                form_frame.pack(fill=tk.BOTH, expand=True)

                tk.Label(form_frame, text="Mã đề:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=0, column=0, padx=5, pady=5, sticky="e")
                entry_ma_de = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                entry_ma_de.grid(row=0, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Tên đề:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=1, column=0, padx=5, pady=5, sticky="e")
                entry_ten_de = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                entry_ten_de.grid(row=1, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Hạn nộp:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=2, column=0, padx=5, pady=5, sticky="e")
                entry_ngay_den_han = DateEntry(form_frame, width=27, font=FONT_ENTRY, date_pattern='yyyy-mm-dd',
                                               background=BG_WHITE, foreground=FG_TEXT)
                entry_ngay_den_han.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Câu hỏi:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=3, column=0, padx=5, pady=5, sticky="ne")
                text_cau_hoi = tk.Text(form_frame, width=30, height=5, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                text_cau_hoi.grid(row=3, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Đáp án A:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=4, column=0, padx=5, pady=5, sticky="e")
                entry_dap_an_a = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                entry_dap_an_a.grid(row=4, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Đáp án B:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=5, column=0, padx=5, pady=5, sticky="e")
                entry_dap_an_b = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                entry_dap_an_b.grid(row=5, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Đáp án C:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=6, column=0, padx=5, pady=5, sticky="e")
                entry_dap_an_c = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                entry_dap_an_c.grid(row=6, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Đáp án D:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=7, column=0, padx=5, pady=5, sticky="e")
                entry_dap_an_d = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                entry_dap_an_d.grid(row=7, column=1, padx=5, pady=5)

                tk.Label(form_frame, text="Đáp án đúng:", bg=BG_WHITE, fg=FG_TEXT,
                         font=FONT_LABEL).grid(row=8, column=0, padx=5, pady=5, sticky="e")
                combo_dap_an_dung = ttk.Combobox(form_frame, values=['A', 'B', 'C', 'D'], width=5, font=FONT_ENTRY)
                combo_dap_an_dung.grid(row=8, column=1, padx=5, pady=5, sticky="w")

                def submit():
                    ma_de = entry_ma_de.get().strip()
                    ten_de = entry_ten_de.get().strip()
                    ngay_den_han = entry_ngay_den_han.get()
                    cau_hoi = text_cau_hoi.get("1.0", tk.END).strip()
                    dap_an = [
                        entry_dap_an_a.get().strip(),
                        entry_dap_an_b.get().strip(),
                        entry_dap_an_c.get().strip(),
                        entry_dap_an_d.get().strip()
                    ]
                    dap_an_dung = combo_dap_an_dung.get().strip()

                    if not all([ma_de, ten_de, ngay_den_han, cau_hoi, all(dap_an), dap_an_dung]):
                        messagebox.showerror("Lỗi!", "Vui lòng nhập đầy đủ thông tin!")
                        return

                    if not (3 <= len(ma_de) <= 10):
                        messagebox.showerror("Lỗi!", "Mã đề phải có độ dài từ 3 đến 10 ký tự!")
                        return
                    if not (3 <= len(ten_de) <= 50):
                        messagebox.showerror("Lỗi!", "Tên đề phải có độ dài từ 3 đến 50 ký tự!")
                        return

                    if dap_an_dung not in ['A', 'B', 'C', 'D']:
                        messagebox.showerror("Lỗi!", "Đáp án đúng phải là A, B, C hoặc D!")
                        return

                    if selected_subject not in app.test_data["cau_hoi"]:
                        app.test_data["cau_hoi"][selected_subject] = {}

                    if ma_de in app.test_data["cau_hoi"][selected_subject]:
                        app.test_data["cau_hoi"][selected_subject][ma_de]["ten_de"] = ten_de
                        app.test_data["cau_hoi"][selected_subject][ma_de]["ngay_den_han"] = ngay_den_han
                    else:
                        app.test_data["cau_hoi"][selected_subject][ma_de] = {
                            "ten_de": ten_de,
                            "ngay_den_han": ngay_den_han,
                            "cau_hoi": []
                        }

                    max_id = max([q["id"] for q in app.test_data["cau_hoi"][selected_subject][ma_de]["cau_hoi"]] or [0])
                    app.test_data["cau_hoi"][selected_subject][ma_de]["cau_hoi"].append({
                        "id": max_id + 1,
                        "cau_hoi": cau_hoi,
                        "dap_an": dap_an,
                        "dap_an_dung": ord(dap_an_dung) - ord('A')
                    })
                    app.data_manager.save_data(app.test_data, is_test=True)
                    messagebox.showinfo("Thành công!", "Thêm câu hỏi thành công!")
                    show_questions(selected_subject)

                tk.Button(form_frame, text="Thêm", command=submit,
                          bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                    row=9, column=0, columnspan=2, padx=10, pady=5)
                tk.Button(form_frame, text="Hủy", command=lambda: show_questions(selected_subject),
                          bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                    row=10, column=0, columnspan=2, padx=10, pady=5)

            create_button(action_frame, "Thêm câu hỏi", add_question)
            create_button(action_frame, "Xóa câu hỏi", lambda: app.delete_practice_question(selected_subject))
            create_button(action_frame, "Sửa câu hỏi", lambda: app.edit_practice_question(selected_subject))
            create_button(action_frame, "Quay lại", show_manage_practice)

        tree.bind("<Double-1>", lambda event: show_questions(tree.item(tree.selection())["values"][1]) if tree.selection() else None)

        button_frame = tk.Frame(list_frame, bg=BG_MAIN)
        button_frame.pack(fill=tk.X, pady=5)

        create_button(button_frame, "Thêm môn", add_subject)
        create_button(button_frame, "Sửa môn", edit_subject)
        create_button(button_frame, "Xóa môn", lambda: app.delete_practice_subject(tree))

    
    def show_manage_exam():
        BG_MAIN = "#FFF8DC"        
        FONT = ("Segoe UI", 12)    # Default font and size
        FONT_BOLD = ("Segoe UI", 12, "bold")  # For headings
        for widget in app.frame_right.winfo_children():
            widget.destroy()
        list_frame = tk.Frame(app.frame_right, bg=BG_MAIN, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("ma_mon", "ten_mon", "thoi_gian_lam_bai")

        style = ttk.Style()
        style.configure("Custom.Treeview", font=FONT)
        style.configure("Custom.Treeview.Heading", font=FONT_BOLD)
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15, style="Custom.Treeview")
        tree.heading("ma_mon", text="Mã môn")
        tree.heading("ten_mon", text="Tên môn")
        tree.heading("thoi_gian_lam_bai", text="Thời gian làm bài (phút)")
        tree.column("ma_mon", width=100, anchor="center")
        tree.column("ten_mon", width=300, anchor="w")
        tree.column("thoi_gian_lam_bai", width=150, anchor="center")
        tree.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        
        
        def refresh_treeview():
            for item in tree.get_children():
                tree.delete(item)
            subjects = app.exam_data.get("mon_thi", [])
            for subject in subjects:
                ma_mon = subject.get("ma_mon", "N/A")
                ten_mon = subject.get("ten_mon", "Unknown")
                so_cau_hoi = 0
                if ten_mon in app.exam_data["cau_hoi"]:
                    for de_thi in app.exam_data["cau_hoi"][ten_mon].values():
                        so_cau_hoi += len(de_thi.get("cau_hoi", []))
                thoi_gian = 60 if so_cau_hoi > 15 else 45
                tree.insert("", "end", values=(ma_mon, ten_mon, thoi_gian))

        refresh_treeview()

        def add_subject():
            for widget in app.frame_right.winfo_children():
                widget.destroy()

            form_frame = tk.Frame(app.frame_right, bg=BG_WHITE, padx=10, pady=10)
            form_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(form_frame, text="Mã môn:", bg=BG_WHITE, fg=FG_TEXT,
                     font=FONT_LABEL).grid(row=0, column=0, padx=5, pady=5, sticky="e")
            entry_ma_mon = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_ma_mon.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Tên môn:", bg=BG_WHITE, fg=FG_TEXT,
                     font=FONT_LABEL).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            entry_ten_mon = tk.Entry(form_frame, width=30, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_ten_mon.grid(row=1, column=1, padx=5, pady=5)

            def submit():
                ma_mon = entry_ma_mon.get().strip()
                ten_mon = entry_ten_mon.get().strip()

                if not all([ma_mon, ten_mon]):
                    messagebox.showerror("Lỗi!", "Vui lòng nhập đầy đủ thông tin!")
                    return

                if not (3 <= len(ma_mon) <= 10):
                    messagebox.showerror("Lỗi!", "Mã môn phải có độ dài từ 3 đến 10 ký tự!")
                    return
                if not (3 <= len(ten_mon) <= 50):
                    messagebox.showerror("Lỗi!", "Tên môn phải có độ dài từ 3 đến 50 ký tự!")
                    return
                if not re.match(r'^[a-zA-Z0-9_]+$', ma_mon):
                    messagebox.showerror("Lỗi!", "Mã môn chỉ được chứa chữ, số và gạch dưới!")
                    return

                for subject in app.exam_data["mon_thi"]:
                    if subject["ma_mon"] == ma_mon or subject["ten_mon"] == ten_mon:
                        messagebox.showerror("Lỗi!", "Mã môn hoặc tên môn đã tồn tại!")
                        return

                app.exam_data["mon_thi"].append({"ma_mon": ma_mon, "ten_mon": ten_mon})
                app.exam_data["cau_hoi"].setdefault(ten_mon, {})
                app.data_manager.save_data(app.exam_data)
                messagebox.showinfo("Thành công!", "Thêm môn học thành công!")
                show_manage_exam()

            tk.Button(form_frame, text="Thêm môn", command=submit,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                row=2, column=0, columnspan=2, pady=20)
            tk.Button(form_frame, text="Hủy", command=show_manage_exam,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(
                row=3, column=0, columnspan=2, pady=5)

        def show_questions(selected_subject):
            for widget in app.frame_right.winfo_children():
                widget.destroy()

            questions_frame = tk.Frame(app.frame_right, bg=BG_MAIN, padx=10, pady=10)
            questions_frame.pack(fill=tk.BOTH, expand=True)

            scroll_y = tk.Scrollbar(questions_frame)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

            text_questions = tk.Text(questions_frame, width=60, height=10, bg=BG_WHITE, fg=FG_TEXT,
                                     font=FONT_ENTRY, relief='flat', bd=1, yscrollcommand=scroll_y.set)
            text_questions.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
            scroll_y.config(command=text_questions.yview)

            if selected_subject not in app.exam_data["cau_hoi"]:
                text_questions.insert("1.0", "Không có câu hỏi nào!")
            else:
                question_index = 1
                for ma_de, de_thi in app.exam_data["cau_hoi"][selected_subject].items():
                    text_questions.insert("end", f"Đề: {de_thi['ten_de']}\n\n")
                    questions = de_thi.get("cau_hoi", [])
                    for q in questions:
                        text_questions.insert("end", f"Câu {question_index}: {q['cau_hoi']}\n")
                        for i, dap_an in enumerate(q['dap_an']):
                            text_questions.insert("end", f"{chr(65 + i)}. {dap_an}\n")
                        text_questions.insert("end", "\n")
                        question_index += 1
                    text_questions.insert("end", "\n")

            text_questions.config(state="disabled")

            action_frame = tk.Frame(app.frame_right, bg=BG_MAIN, padx=10, pady=5)
            action_frame.pack(fill=tk.X)

            create_button(action_frame, "Thêm câu hỏi", lambda: app.them_cau_hoi(selected_subject))
            create_button(action_frame, "Xóa câu hỏi", lambda: app.xoa_cau_hoi(selected_subject))
            create_button(action_frame, "Sửa câu hỏi", lambda: app.cap_nhat_cau_hoi(selected_subject))
            create_button(action_frame, "Quay lại", show_manage_exam)

        tree.bind("<Double-1>", lambda event: show_questions(tree.item(tree.selection())["values"][1]) if tree.selection() else None)

        button_frame = tk.Frame(list_frame, bg=BG_MAIN)
        button_frame.pack(fill=tk.X, pady=5)

        create_button(button_frame, "Thêm môn", add_subject)
        create_button(button_frame, "Xóa môn", lambda: app.delete_exam_subject(tree))

    def show_manage_accounts():
        if not app.has_permission("manage_accounts"):
            app.logger.warning("Người dùng không có quyền quản lý tài khoản")
            messagebox.showerror("Lỗi", "Bạn không có quyền quản lý tài khoản!")
            return

        for widget in app.frame_right.winfo_children():
            widget.destroy()

        container = tk.Frame(app.frame_right, bg=BG_MAIN, bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5, fill=tk.BOTH)

        tk.Label(container, text="Danh sách tài khoản:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).pack(anchor='w', padx=10, pady=5)
        account_listbox = tk.Listbox(container, width=50, height=10, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
        account_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=account_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        account_listbox.config(yscrollcommand=scrollbar.set)

        def update_account_list():
            account_listbox.delete(0, tk.END)
            for username, info in app.account_data["users"].items():
                account_listbox.insert(tk.END, f"{username} ({info['role'].capitalize()})")

        update_account_list()

        def add_account():
            for widget in container.winfo_children():
                widget.destroy()

            form_frame = tk.Frame(container, bg=BG_MAIN, padx=10, pady=10)
            form_frame.pack(expand=True, fill=tk.BOTH)

            tk.Label(form_frame, text="Tên đăng nhập:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=0, column=0, padx=5, pady=5, sticky="e")
            entry_username = tk.Entry(form_frame, width=20, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
            entry_username.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Mật khẩu:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            entry_password = tk.Entry(form_frame, width=20, font=FONT_ENTRY, show="*", bg=BG_WHITE, fg=FG_TEXT)
            entry_password.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Vai trò:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            role_var = tk.StringVar(value="user")
            ttk.Combobox(form_frame, textvariable=role_var, values=['user', 'admin'], width=17, font=FONT_ENTRY, state='readonly').grid(row=2, column=1, padx=5, pady=5)

            def confirm_add():
                username = entry_username.get().strip().lower()
                password = entry_password.get().strip()
                role = role_var.get()

                if not username or not password:
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
                    return

                if not app.validate_username(username):
                    messagebox.showerror("Lỗi", "Tên đăng nhập không hợp lệ! Chỉ chứa chữ, số, gạch dưới, dài 3-20 ký tự.")
                    return

                if username in app.account_data["users"]:
                    messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
                    return

                if not app.validate_password(password):
                    messagebox.showerror("Lỗi", "Mật khẩu không hợp lệ! Phải có ít nhất 6 ký tự, bao gồm chữ và số, không chứa khoảng trắng.")
                    return

                if role not in ['user', 'admin']:
                    messagebox.showerror("Lỗi", "Vai trò không hợp lệ!")
                    return

                app.account_data["users"][username] = {
                    "password": password,
                    "role": role
                }
                app.data_manager.save_account_data(app.account_data)
                app.logger.info(f"Thêm tài khoản {username} ({role}) thành công")
                messagebox.showinfo("Thành công", "Thêm tài khoản thành công!")
                show_manage_accounts()

            tk.Button(form_frame, text="Thêm", command=confirm_add, bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(form_frame, text="Hủy", command=show_manage_accounts, bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(row=4, column=0, columnspan=2, pady=5)

        def delete_account():
            if not account_listbox.curselection():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để xóa!")
                return

            selected = account_listbox.get(account_listbox.curselection()[0])
            username = selected.split(" (")[0]

            if username == app.current_user:
                messagebox.showerror("Lỗi", "Không thể xóa tài khoản đang đăng nhập!")
                return

            admin_count = sum(1 for user, info in app.account_data["users"].items() if info["role"] == "admin")
            if app.account_data["users"][username]["role"] == "admin" and admin_count <= 1:
                messagebox.showerror("Lỗi", "Không thể xóa tài khoản admin cuối cùng!")
                return

            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tài khoản '{username}'?"):
                del app.account_data["users"][username]
                app.data_manager.save_account_data(app.account_data)
                app.logger.info(f"Xóa tài khoản {username} thành công")
                messagebox.showinfo("Thành công", f"Đã xóa tài khoản '{username}'!")
                update_account_list()

        def edit_account():
            if not account_listbox.curselection():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để sửa!")
                return

            selected = account_listbox.get(account_listbox.curselection()[0])
            username = selected.split(" (")[0]

            for widget in container.winfo_children():
                widget.destroy()

            form_frame = tk.Frame(container, bg=BG_MAIN, padx=10, pady=10)
            form_frame.pack(expand=True, fill=tk.BOTH)

            tk.Label(form_frame, text="Tên đăng nhập:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=0, column=0, padx=5, pady=5, sticky="e")
            tk.Label(form_frame, text=username, bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=0, column=1, padx=5, pady=5, sticky="w")

            tk.Label(form_frame, text="Mật khẩu mới:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            entry_password = tk.Entry(form_frame, width=20, font=FONT_ENTRY, show="*", bg=BG_WHITE, fg=FG_TEXT)
            entry_password.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Vai trò:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            role_var = tk.StringVar(value=app.account_data["users"][username]["role"])
            ttk.Combobox(form_frame, textvariable=role_var, values=['user', 'admin'], width=17, font=FONT_ENTRY, state='readonly').grid(row=2, column=1, padx=5, pady=5)

            def confirm_edit():
                password = entry_password.get().strip()
                role = role_var.get()

                if password and not app.validate_password(password):
                    messagebox.showerror("Lỗi", "Mật khẩu không hợp lệ! Phải có ít nhất 6 ký tự, bao gồm chữ và số, không chứa khoảng trắng.")
                    return

                if role not in ['user', 'admin']:
                    messagebox.showerror("Lỗi", "Vai trò không hợp lệ!")
                    return

                admin_count = sum(1 for user, info in app.account_data["users"].items() if info["role"] == "admin")
                if app.account_data["users"][username]["role"] == "admin" and role != "admin" and admin_count <= 1:
                    messagebox.showerror("Lỗi", "Không thể thay đổi vai trò của admin cuối cùng!")
                    return

                if password:
                    app.account_data["users"][username]["password"] = password
                app.account_data["users"][username]["role"] = role
                app.data_manager.save_account_data(app.account_data)
                app.logger.info(f"Sửa tài khoản {username} ({role}) thành công")
                messagebox.showinfo("Thành công", "Sửa tài khoản thành công!")
                show_manage_accounts()

            tk.Button(form_frame, text="Cập nhật", command=confirm_edit, bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(form_frame, text="Hủy", command=show_manage_accounts, bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').grid(row=4, column=0, columnspan=2, pady=5)

        button_frame = tk.Frame(container, bg=BG_MAIN)
        button_frame.pack(fill=tk.X, pady=5)

        create_button(button_frame, "Thêm tài khoản", add_account)
        create_button(button_frame, "Xóa tài khoản", delete_account)
        create_button(button_frame, "Sửa tài khoản", edit_account)
        create_button(button_frame, "Quay lại", show_default_interface)

    def show_view_stats():
        if not app.has_permission("view_stats"):
            app.logger.warning("Người dùng không có quyền xem thống kê")
            messagebox.showerror("Lỗi", "Bạn không có quyền xem thống kê!")
            return

        for widget in app.frame_right.winfo_children():
            widget.destroy()

        container = tk.Frame(app.frame_right, bg=BG_MAIN, bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5, fill=tk.BOTH)

        tk.Label(container, text="Chọn môn học:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).pack(anchor='w', padx=10, pady=5)
        mon_var = tk.StringVar(value="")
        mon_combobox = ttk.Combobox(container, textvariable=mon_var, width=30, font=FONT_ENTRY)
        subjects = [mon["ten_mon"] for mon in app.exam_data["mon_thi"]]
        mon_combobox['values'] = subjects
        mon_combobox.pack(pady=5)

        fig, ax = plt.subplots(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.get_tk_widget().pack(pady=10)

        def update_stats():
            mon = mon_var.get()
            if not mon:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học!")
                return

            pass_count = 0
            fail_count = 0
            pass_threshold = 5.0
            scores = []

            for user, user_data in app.exam_answers.items():
                if mon in user_data and "score" in user_data[mon]:
                    score = user_data[mon]["score"]
                    scores.append(score)
                    if score >= pass_threshold:
                        pass_count += 1
                    else:
                        fail_count += 1

            ax.clear()
            ax.bar(['Đậu', 'Rớt'], [pass_count, fail_count], color=[BTN_BG, BTN_HOVER])
            ax.set_title(f'Thống kê đậu/rớt môn {mon}')
            ax.set_ylabel('Số lượng học sinh')
            ax.set_ylim(0, max(pass_count, fail_count, 1) + 1)
            for i, v in enumerate([pass_count, fail_count]):
                ax.text(i, v + 0.1, str(v), ha='center', va='bottom')
            canvas.draw()

            stats_text = f"Tổng số học sinh: {pass_count + fail_count}\n"
            stats_text += f"Đậu: {pass_count} ({pass_count / (pass_count + fail_count) * 100:.2f}%)\n" if pass_count + fail_count > 0 else "Đậu: 0 (0.00%)\n"
            stats_text += f"Rớt: {fail_count} ({fail_count / (pass_count + fail_count) * 100:.2f}%)\n" if pass_count + fail_count > 0 else "Rớt: 0 (0.00%)\n"
            if scores:
                stats_text += f"Điểm trung bình: {sum(scores) / len(scores):.2f}\n"
                stats_text += f"Điểm cao nhất: {max(scores):.2f}\n"
                stats_text += f"Điểm thấp nhất: {min(scores):.2f}"

            stats_label.config(text=stats_text)

            app.logger.info(f"Hiển thị thống kê đậu/rớt cho môn {mon}")

        mon_combobox.bind('<<ComboboxSelected>>', lambda e: update_stats())

        stats_label = tk.Label(container, text="", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL, justify='left')
        stats_label.pack(pady=10)

        tk.Button(container, text="Quay lại", command=show_default_interface,
                  bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=10)

    def show_view_user_submission():
        if not app.has_permission("view_stats"):
            app.logger.warning("Người dùng không có quyền xem bài làm")
            messagebox.showerror("Lỗi", "Bạn không có quyền xem bài làm của học sinh!")
            return

        for widget in app.frame_right.winfo_children():
            widget.destroy()

        container = tk.Frame(app.frame_right, bg=BG_MAIN, bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5, fill=tk.BOTH)

        tk.Label(container, text="Chọn môn học:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).pack(anchor='w', padx=10, pady=5)
        mon_var = tk.StringVar(value="")
        mon_combobox = ttk.Combobox(container, textvariable=mon_var, width=30, font=FONT_ENTRY)
        subjects = [mon["ten_mon"] for mon in app.exam_data["mon_thi"]]
        mon_combobox['values'] = subjects
        mon_combobox.pack(pady=5)

        tk.Label(container, text="Chọn học sinh:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).pack(anchor='w', padx=10, pady=5)
        user_var = tk.StringVar(value="")
        user_combobox = ttk.Combobox(container, textvariable=user_var, width=30, font=FONT_ENTRY)
        users = [user for user in app.exam_answers.keys() if app.account_data["users"].get(user, {}).get("role") == "user"]
        user_combobox['values'] = users
        user_combobox.pack(pady=5)

        text_area = tk.Text(container, width=70, height=20, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        text_area.config(yscrollcommand=scrollbar.set, state='disabled')

        def show_submission():
            mon = mon_var.get()
            user = user_var.get()
            if not mon or not user:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học và học sinh!")
                return

            text_area.config(state='normal')
            text_area.delete("1.0", tk.END)
            answers = app.exam_answers.get(user, {}).get(mon, {})
            if not answers or not any(k.isdigit() for k in answers.keys()):
                text_area.insert(tk.END, "Học sinh này chưa nộp bài cho môn này.\n")
                text_area.config(state='disabled')
                app.logger.info(f"Không tìm thấy bài làm cho user {user}, môn {mon}")
                return

            text_area.insert(tk.END, f"Bài làm của {user} - Môn {mon}\n")
            text_area.insert(tk.END, f"Thời gian nộp: {answers.get('timestamp', 'N/A')}\n")
            text_area.insert(tk.END, f"Điểm: {answers.get('score', 0):.2f}/10\n")
            text_area.insert(tk.END, f"Số câu đúng: {answers.get('correct_count', 0)}/{answers.get('total_questions', 0)}\n\n")

            question_index = 1
            data = app.exam_data
            for ma_de, de_thi in sorted(data["cau_hoi"].get(mon, {}).items()):
                for question in de_thi.get("cau_hoi", []):
                    qid = str(question["id"])
                    text_area.insert(tk.END, f"Câu {question_index}: {question['cau_hoi']}\n")
                    for i, dap_an in enumerate(question["dap_an"]):
                        text_area.insert(tk.END, f"   {'ABCD'[i]}. {dap_an}\n")
                    user_answer = answers.get(qid, None)
                    if user_answer is not None:
                        text_area.insert(tk.END, f"Đáp án chọn: {'ABCD'[user_answer]}\n")
                        if user_answer == question["dap_an_dung"]:
                            text_area.insert(tk.END, "✅ Đúng\n")
                        else:
                            text_area.insert(tk.END, f"❌ Sai (Đáp án đúng: {'ABCD'[question['dap_an_dung']]})\n")
                    else:
                        text_area.insert(tk.END, "Không trả lời\n")
                    text_area.insert(tk.END, "\n")
                    question_index += 1

            text_area.config(state='disabled')
            app.logger.info(f"Hiển thị bài làm của user {user} cho môn {mon}")

        tk.Button(container, text="Hiển thị bài làm", command=show_submission,
                  bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=5)
        tk.Button(container, text="Quay lại", command=show_default_interface,
                  bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=5)

    def show_view_results():
        try:
            app.logger.debug(f"Người dùng {app.current_user} mở 'Xem kết quả'")
            clear_sub_frame()
            nonlocal sub_frame
            sub_frame = tk.LabelFrame(frame_left, text="Xem kết quả", bg=BG_FRAME, fg=FG_TEXT,
                                      font=FONT_LABEL, padx=10, pady=10, relief='groove')
            sub_frame.pack(fill=tk.X, pady=5)

            def view_exam_results():
                try:
                    app.logger.debug(f"Người dùng {app.current_user} nhấp 'Xem đề thi'")
                    for widget in app.frame_right.winfo_children():
                        widget.destroy()
                    app.exam_answers = app.data_manager.load_user_answers_data()
                    if not app.exam_answers or not app.exam_answers.get(app.current_user):
                        app.logger.warning(f"Không tìm thấy kết quả đề thi cho người dùng {app.current_user}")
                        messagebox.showinfo("Thông báo", "Chưa có kết quả đề thi để xem!")
                        return
                    app.view_user_answers()
                except Exception as e:
                    app.logger.error(f"Lỗi khi xem kết quả đề thi: {str(e)}")
                    messagebox.showerror("Lỗi giao diện", f"Không thể hiển thị kết quả đề thi: {str(e)}")

            def view_practice_results():
                try:
                    app.logger.debug(f"Người dùng {app.current_user} nhấp 'Xem bài trắc nghiệm'")
                    for widget in app.frame_right.winfo_children():
                        widget.destroy()
                    app.test_answers = app.data_manager.load_user_answers_data(is_test=True)
                    if not app.test_answers or not app.test_answers.get(app.current_user):
                        app.logger.warning(f"Không tìm thấy kết quả bài trắc nghiệm cho người dùng {app.current_user}")
                        messagebox.showinfo("Thông báo", "Chưa có kết quả bài trắc nghiệm để xem!")
                        return
                    app.view_user_answers()
                except Exception as e:
                    app.logger.error(f"Lỗi khi xem kết quả bài trắc nghiệm: {str(e)}")
                    messagebox.showerror("Lỗi giao diện", f"Không thể hiển thị kết quả bài trắc nghiệm: {str(e)}")

            create_button(sub_frame, "Xem đề thi", view_exam_results)
            create_button(sub_frame, "Xem bài trắc nghiệm", view_practice_results)

        except Exception as e:
            app.logger.error(f"Lỗi khi tạo giao diện Xem kết quả: {str(e)}")
            messagebox.showerror("Lỗi giao diện", f"Không thể mở Xem kết quả: {str(e)}")

    def show_submission_history():
        try:
            app.logger.debug(f"Người dùng {app.current_user} mở 'Lịch sử làm bài'")
            for widget in app.frame_right.winfo_children():
                widget.destroy()

            container = tk.Frame(app.frame_right, bg=BG_MAIN, bd=5, relief='flat')
            container.pack(expand=True, padx=10, pady=5, fill=tk.BOTH)

            tk.Label(container, text="Lịch sử làm bài", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).pack(anchor='w', padx=10, pady=5)

            app.exam_answers = app.data_manager.load_user_answers_data()
            app.test_answers = app.data_manager.load_user_answers_data(is_test=True)

            columns = ("type", "subject", "score", "correct_count", "total_questions", "timestamp")
            tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
            tree.heading("type", text="Loại")
            tree.heading("subject", text="Môn học")
            tree.heading("score", text="Điểm")
            tree.heading("correct_count", text="Số câu đúng")
            tree.heading("total_questions", text="Tổng số câu")
            tree.heading("timestamp", text="Thời gian nộp")
            tree.column("type", width=100, anchor="center")
            tree.column("subject", width=200, anchor="w")
            tree.column("score", width=80, anchor="center")
            tree.column("correct_count", width=100, anchor="center")
            tree.column("total_questions", width=100, anchor="center")
            tree.column("timestamp", width=150, anchor="center")
            tree.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

            user_exam_answers = app.exam_answers.get(app.current_user, {})
            for subject, answers in user_exam_answers.items():
                if any(k.isdigit() for k in answers.keys()):
                    tree.insert("", "end", values=(
                        "Đề thi",
                        subject,
                        f"{answers.get('score', 0):.2f}",
                        answers.get('correct_count', 0),
                        answers.get('total_questions', 0),
                        answers.get('timestamp', 'N/A')
                    ))

            user_test_answers = app.test_answers.get(app.current_user, {})
            for subject, answers in user_test_answers.items():
                if any(k.isdigit() for k in answers.keys()):
                    tree.insert("", "end", values=(
                        "Bài tập",
                        subject,
                        f"{answers.get('score', 0):.2f}",
                        answers.get('correct_count', 0),
                        answers.get('total_questions', 0),
                        answers.get('timestamp', 'N/A')
                    ))

            if not tree.get_children():
                tk.Label(container, text="Chưa có lịch sử làm bài!", bg=BG_MAIN, fg=FG_TEXT, font=FONT_LABEL).pack(pady=10)

            def view_submission_details():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bài làm để xem chi tiết!")
                    return

                values = tree.item(selected_item)["values"]
                submission_type, subject = values[0], values[1]

                for widget in container.winfo_children():
                    widget.destroy()

                text_area = tk.Text(container, width=70, height=20, font=FONT_ENTRY, bg=BG_WHITE, fg=FG_TEXT)
                text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                scrollbar = tk.Scrollbar(container, orient='vertical', command=text_area.yview)
                scrollbar.pack(side=tk.RIGHT, fill='y')
                text_area.config(yscrollcommand=scrollbar.set, state='normal')

                answers = app.exam_answers.get(app.current_user, {}).get(subject, {}) if submission_type == "Đề thi" else app.test_answers.get(app.current_user, {}).get(subject, {})
                
                text_area.insert(tk.END, f"{submission_type} - Môn {subject}\n")
                text_area.insert(tk.END, f"Thời gian nộp: {answers.get('timestamp', 'N/A')}\n")
                text_area.insert(tk.END, f"Điểm: {answers.get('score', 0):.2f}/10\n")
                text_area.insert(tk.END, f"Số câu đúng: {answers.get('correct_count', 0)}/{answers.get('total_questions', 0)}\n\n")

                data = app.exam_data if submission_type == "Đề thi" else app.test_data
                question_index = 1
                for ma_de, de_thi in sorted(data["cau_hoi"].get(subject, {}).items()):
                    for question in de_thi.get("cau_hoi", []):
                        qid = str(question["id"])
                        text_area.insert(tk.END, f"Câu {question_index}: {question['cau_hoi']}\n")
                        for i, dap_an in enumerate(question["dap_an"]):
                            text_area.insert(tk.END, f"   {'ABCD'[i]}. {dap_an}\n")
                        user_answer = answers.get(qid, None)
                        if user_answer is not None:
                            text_area.insert(tk.END, f"Đáp án chọn: {'ABCD'[user_answer]}\n")
                            if user_answer == question["dap_an_dung"]:
                                text_area.insert(tk.END, "✅ Đúng\n")
                            else:
                                text_area.insert(tk.END, f"❌ Sai (Đáp án đúng: {'ABCD'[question['dap_an_dung']]})\n")
                        else:
                            text_area.insert(tk.END, "Không trả lời\n")
                        text_area.insert(tk.END, "\n")
                        question_index += 1

                text_area.config(state='disabled')
                tk.Button(container, text="Quay lại", command=show_submission_history,
                          bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=5)

            tk.Button(container, text="Xem chi tiết", command=view_submission_details,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=5)
            tk.Button(container, text="Quay lại", command=show_default_interface,
                      bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=5)

        except Exception as e:
            app.logger.error(f"Lỗi khi hiển thị lịch sử làm bài: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể hiển thị lịch sử làm bài: {str(e)}")

    def show_crawl_data():
        if role != "admin":
            messagebox.showerror("Lỗi", "Chỉ admin mới có quyền crawl dữ liệu!")
            return
        clear_sub_frame()
        nonlocal sub_frame
        sub_frame = tk.LabelFrame(frame_left, text="Crawl dữ liệu", bg=BG_FRAME, fg=FG_TEXT,
                                  font=FONT_LABEL, padx=10, pady=10, relief='groove')
        sub_frame.pack(fill=tk.X, pady=5)

        for widget in app.frame_right.winfo_children():
            widget.destroy()

        form_frame = tk.Frame(app.frame_right, bg=BG_WHITE, padx=10, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(form_frame, text="Chọn loại dữ liệu:", bg=BG_WHITE, fg=FG_TEXT,
                 font=FONT_LABEL).pack(anchor='w', padx=5, pady=5)
        data_type_var = tk.StringVar(value="exam")
        tk.Radiobutton(form_frame, text="Đề thi", variable=data_type_var, value="exam",
                       bg=BG_WHITE, fg=FG_TEXT, font=FONT_ENTRY).pack(anchor='w', padx=15)
        tk.Radiobutton(form_frame, text="Bài tập", variable=data_type_var, value="practice",
                       bg=BG_WHITE, fg=FG_TEXT, font=FONT_ENTRY).pack(anchor='w', padx=15)

        def submit_crawl():
            is_test = data_type_var.get() == "practice"
            app.crawl_data_from_api(is_test=is_test)
            show_default_interface()

        tk.Button(form_frame, text="Bắt đầu Crawl", command=submit_crawl,
                  bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=10)
        tk.Button(form_frame, text="Hủy", command=show_default_interface,
                  bg=BTN_BG, fg="#FFFFFF", font=FONT_ENTRY, relief='flat').pack(pady=5)

    def show_default_interface():
        for widget in app.frame_right.winfo_children():
            widget.destroy()

        scroll_y = tk.Scrollbar(app.frame_right)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        app.text_cau_hoi = tk.Text(app.frame_right, width=50, height=20, wrap='word', bg=BG_WHITE, fg=FG_TEXT,
                                   font=FONT_ENTRY, relief='flat', bd=1, yscrollcommand=scroll_y.set)
        app.text_cau_hoi.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        scroll_y.config(command=app.text_cau_hoi.yview)

        app.answer_frame = tk.Frame(app.frame_right, bg=BG_MAIN)
        app.answer_frame.pack(fill=tk.X, pady=5)

    def clear_sub_frame():
        nonlocal sub_frame
        if sub_frame and sub_frame.winfo_exists():
            sub_frame.destroy()
        sub_frame = None

    sub_frame = None
    def create_button(frame, text, command):
        btn = tk.Button(frame, text=text, command=command,
                    bg="#F6D97E", fg="black",
                    font=("Segoe UI", 11), relief="flat",
                    anchor="w", padx=10, compound="left")
        btn.pack(fill=tk.X, padx=10, pady=6)
        btn.bind("<Enter>", lambda e: btn.config(bg="#FFEFA3"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#F6D97E"))
        return btn

    if role == "admin":
        main_buttons_frame.configure(bg=BG_MAIN)

        user_label = tk.Label(main_buttons_frame, text="🔐 Đăng nhập: Admin",
                              font=FONT_LABEL, fg=FG_TEXT, bg=BG_MAIN, pady=12)
        user_label.pack(fill=tk.X, padx=10)

        content_frame = tk.LabelFrame(main_buttons_frame, text="📚 Quản lý nội dung",
                                      font=FONT_LABEL, fg=FG_TEXT, bg=BG_FRAME, bd=1,
                                      relief="solid", labelanchor="n")
        content_frame.pack(fill=tk.X, pady=6, padx=10)
        create_button(content_frame, "📋 Quản lý đề thi", show_manage_exam)
        create_button(content_frame, "📝 Quản lý bài tập trắc nghiệm", show_manage_practice)
        create_button(content_frame, "🌐 Crawl dữ liệu", show_crawl_data)

        user_stats_frame = tk.LabelFrame(main_buttons_frame, text="👥 Người dùng & thống kê",
                                         font=FONT_LABEL, fg=FG_TEXT, bg=BG_FRAME, bd=1,
                                         relief="solid", labelanchor="n")
        user_stats_frame.pack(fill=tk.X, pady=6, padx=10)
        create_button(user_stats_frame, "👤 Quản lý tài khoản", show_manage_accounts)
        create_button(user_stats_frame, "📊 Thống kê đậu/rớt", show_view_stats)
        create_button(user_stats_frame, "🧾 Xem bài làm học sinh", show_view_user_submission)

        system_frame = tk.LabelFrame(main_buttons_frame, text="⚙️ Hệ thống",
                                     font=FONT_LABEL, fg=FG_TEXT, bg=BG_FRAME, bd=1,
                                     relief="solid", labelanchor="n")
        system_frame.pack(fill=tk.X, pady=6, padx=10)

        def confirm_logout():
            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất không?"):
                app.logout()

        create_button(system_frame, "🚪 Đăng xuất", confirm_logout)

    if role == "user":
        for widget in frame_left.winfo_children():
            widget.destroy()

        tk.Label(frame_left, text=f"👤 Người dùng: {app.current_user} ({role})",
             bg=BG_MAIN, fg=FG_TEXT, font=("Segoe UI", 11)).pack(pady=(15, 5))

        tk.Label(frame_left, text=f"🎯 Chế độ: {'Làm đề thi' if app.mode == 'exam' else 'Làm bài tập'}",
             bg=BG_MAIN, fg="#1a202c", font=("Segoe UI", 12, "bold")).pack(pady=(0, 15))

        if app.mode == "exam":
            app.timer_label = tk.Label(frame_left, text="", bg=BG_MAIN, fg="#e53e3e", font=("Segoe UI", 11, "bold"))
            app.timer_label.pack(pady=(0, 10))

        tk.Label(frame_left, text="📚 Chọn môn:", bg=BG_MAIN, fg=FG_TEXT,
             font=("Segoe UI", 11)).pack(anchor='w', padx=15, pady=(0, 4))

        app.mon_var = tk.StringVar()
        app.combobox_mon = ttk.Combobox(frame_left, textvariable=app.mon_var,
                                    font=("Segoe UI", 10), state='readonly', width=28)
        app.combobox_mon.pack(pady=5, padx=15, ipady=3)

        btn_do_test = tk.Button(frame_left, text="📝 Làm đề", command=app.hien_thi_cau_hoi,
                            bg=BTN_BG, fg='white', font=("Segoe UI", 10, "bold"), relief='flat', cursor="hand2")
        btn_do_test.pack(fill=tk.X, pady=6, padx=15)
        btn_do_test.bind("<Enter>", lambda e: btn_do_test.config(bg=BTN_HOVER))
        btn_do_test.bind("<Leave>", lambda e: btn_do_test.config(bg=BTN_BG))

        button_frame = tk.Frame(frame_left, bg=BG_MAIN)
        button_frame.pack(fill=tk.X, pady=5)

        btn_submit = tk.Button(button_frame, text="📤 Nộp bài",
                           command=lambda: app.submit_exam() if app.mode == 'exam' else app.submit_test(),
                           bg=BTN_BG, fg='white', font=("Segoe UI", 10, "bold"), relief='flat', cursor="hand2")
        btn_submit.pack(fill=tk.X, pady=6, padx=15)
        btn_submit.bind("<Enter>", lambda e: btn_submit.config(bg=BTN_HOVER))
        btn_submit.bind("<Leave>", lambda e: btn_submit.config(bg=BTN_BG))

        btn_exit = tk.Button(button_frame, text="Thoát", command=app.logout,
                         bg=BTN_BG, fg='white', font=("Segoe UI", 10, "bold"), relief='flat', cursor="hand2")
        btn_exit.pack(fill=tk.X, pady=6, padx=15)
        btn_exit.bind("<Enter>", lambda e: btn_exit.config(bg=BTN_HOVER))
        btn_exit.bind("<Leave>", lambda e: btn_exit.config(bg=BTN_BG))

        question_frame = tk.Frame(app.frame_right, bg=BG_MAIN)
        question_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scroll_y = tk.Scrollbar(question_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        app.text_cau_hoi = tk.Text(question_frame, width=50, height=20, wrap='word',
                                bg='#ffffff', fg=FG_TEXT, font=FONT_ENTRY,
                                relief='flat', bd=1, yscrollcommand=scroll_y.set)
        app.text_cau_hoi.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        scroll_y.config(command=app.text_cau_hoi.yview)

        app.answer_frame = tk.Frame(question_frame, bg=BG_MAIN)
        app.answer_frame.pack(fill=tk.X, pady=10, padx=10)

    show_default_interface()
    app.logger.debug("Khởi tạo giao diện người dùng thành công")
    