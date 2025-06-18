import logging
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from datetime import datetime
from tkcalendar import DateEntry
import os
import json
from src.data_manager import DataManager
from src.ui.login_ui import create_login_widgets
from src.ui.mode_selection_ui import create_mode_selection_widgets
from src.ui.main_ui import create_widgets
from src.ui.account_ui import create_account
from src.ui.result_ui import submit_exam, submit_test
from src.api_crawler import crawl_data_from_api
from src.utils.password_validator import validate_password
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class QuizApp:
    def __init__(self, root, data_filename="data.json", test_filename="test_questions.json", 
                 account_filename="account.json", exam_answers_filename="answers_exam.json", 
                 test_answers_filename="answers_test.json"):
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file)
        self.logger = logging.getLogger(__name__)
        self.root = root

        try:
            self.data_manager = DataManager(data_filename, test_filename, account_filename, 
                                           exam_answers_filename, test_answers_filename)
            self.logger.info("Khởi tạo DataManager thành công")
        except Exception as e:
            self.logger.error(f"Lỗi khởi tạo DataManager: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể khởi tạo DataManager: {str(e)}")
            self.root.quit()
            return

        try:
            self.exam_data = self.data_manager.load_data()
            self.test_data = self.data_manager.load_data(is_test=True)
            self.account_data = self.data_manager.load_account_data()
            self.exam_answers = self.data_manager.load_user_answers_data()
            self.test_answers = self.data_manager.load_user_answers_data(is_test=True)
            
            if not self.exam_data.get("mon_thi"):
                self.exam_data = {"mon_thi": [], "cau_hoi": {}}
                self.data_manager.save_data(self.exam_data)
            if not self.test_data.get("mon_thi"):
                self.test_data = {"mon_thi": [], "cau_hoi": {}}
                self.data_manager.save_data(self.test_data, is_test=True)
            if not self.exam_answers:
                self.exam_answers = {}
                self.data_manager.save_user_answers_data(self.exam_answers)
            if not self.test_answers:
                self.test_answers = {}
                self.data_manager.save_user_answers_data(self.test_answers, is_test=True)
            
            self.logger.info("Tải dữ liệu ban đầu thành công")
        except Exception as e:
            self.logger.error(f"Lỗi tải dữ liệu ban đầu: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {str(e)}")
            self.root.quit()
            return

        self.current_user = None
        self.mode = None
        self.show_answers = tk.BooleanVar(value=False)
        self.selected_questions = {}
        self.listbox_mon = None
        self.text_cau_hoi = None
        self.answer_frame = None
        self.timer_label = None
        self.timer_seconds = 0
        self.timer_running = False
        self.frame_right = None
        self.combobox_mon = None
        self.mon_var = tk.StringVar()
        self.root.title("Phần mềm Ôn Thi")
        self.root.geometry("800x600")
        self.root.configure(bg='#f5f7fa')

        self.title_bar = tk.Frame(self.root, bg='#343a40', relief='raised', bd=0)
        self.title_bar.pack(fill=tk.X)
        tk.Button(self.title_bar, text="−", command=self.minimize_window, bg='#343a40', fg='white',
                 font=('Arial', 12), relief='flat', activebackground='#495057').pack(side=tk.RIGHT, padx=2)
        tk.Button(self.title_bar, text="🗖", command=self.maximize_window, bg='#343a40', fg='white',
                 font=('Arial', 12), relief='flat', activebackground='#495057').pack(side=tk.RIGHT, padx=2)

        try:
            self.create_login_widgets()
            self.logger.info("Tạo giao diện đăng nhập thành công")
        except Exception as e:
            self.logger.error(f"Lỗi tạo giao diện đăng nhập: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể tạo giao diện đăng nhập: {str(e)}")
            self.root.quit()

    def minimize_window(self):
        self.root.iconify()

    def maximize_window(self):
        current_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_fullscreen)
        if not current_fullscreen:
            self.root.geometry("800x600")

    def create_login_widgets(self):
        create_login_widgets(self)
        self.logger.debug("Giao diện đăng nhập được tạo")

    def create_mode_selection_widgets(self):
        try:
            create_mode_selection_widgets(self)
            self.logger.info("Tạo giao diện chọn chế độ thành công")
        except Exception as e:
            self.logger.error(f"Lỗi tạo giao diện chọn chế độ: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể tạo giao diện chọn chế độ: {str(e)}")

    def create_widgets(self):
        try:
            create_widgets(self)
            if self.mode == "admin" and self.frame_right:
                self.logger.info("Tạo giao diện chính thành công")
        except Exception as e:
            self.logger.error(f"Lỗi tạo giao diện chính: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể tạo giao diện chính: {str(e)}")

    def ensure_data_structure(self, user_answers, user, mon):
        if user not in user_answers:
            user_answers[user] = {}
        if mon not in user_answers[user]:
            user_answers[user][mon] = {}
        return user_answers

    def start_timer(self, duration_minutes):
        if self.mode != "exam" or not self.timer_label:
            return
        self.timer_seconds = duration_minutes * 60
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or not self.timer_label:
            return
        if self.timer_seconds <= 0:
            self.timer_running = False
            self.timer_label.config(text="Hết giờ!")
            messagebox.showinfo("Hết giờ", "Thời gian làm bài đã kết thúc. Bài thi sẽ được nộp tự động.")
            self.submit_exam()
            return
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.config(text=f"Thời gian còn lại: {minutes} phút {seconds:02d} giây")
        self.timer_seconds -= 1
        self.root.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False
        if self.timer_label:
            self.timer_label.config(text="")

    def cap_nhat_danh_sach_mon(self):
        try:
            subjects = []
            data = self.test_data if self.mode == "practice" else self.exam_data
            if not data or "mon_thi" not in data:
                self.logger.warning("Dữ liệu môn thi không tồn tại hoặc rỗng")
                messagebox.showwarning("Cảnh báo", "Không có môn học nào trong dữ liệu!")
                self.combobox_mon['values'] = []
                self.combobox_mon.set("")
                return

            for mon in data["mon_thi"]:
                ten_mon = mon["ten_mon"]
                if ten_mon not in data["cau_hoi"]:
                    data["cau_hoi"][ten_mon] = {}
                subjects.append(ten_mon)
            
            self.combobox_mon['values'] = subjects
            if subjects:
                self.combobox_mon.current(0)
            else:
                self.combobox_mon.set("")
                messagebox.showinfo("Thông báo", "Hiện tại chưa có môn học nào được thêm.")
            
            self.logger.debug("Cập nhật danh sách môn thành công")
        except Exception as e:
            self.logger.error(f"Lỗi cập nhật danh sách môn: {str(e)}")

    def hien_thi_cau_hoi(self):
        if not hasattr(self, 'combobox_mon') or self.combobox_mon is None:
            self.logger.warning("combobox_mon chưa được khởi tạo")
            messagebox.showwarning("Cảnh báo", "Danh sách môn chưa được khởi tạo. Vui lòng thử lại!")
            return
        try:
            mon = self.mon_var.get()
            data = self.test_data if self.mode == "practice" else self.exam_data
            user_answers = self.test_answers if self.mode == "practice" else self.exam_answers
            if not mon or mon not in data["cau_hoi"]:
                messagebox.showwarning("Cảnh báo", "Không có câu hỏi cho môn này!")
                self.stop_timer()
                return

            self.logger.debug(f"Hiển thị câu hỏi cho môn: {mon}")

            if self.mode == "exam":
                total_questions = sum(len(de_thi.get("cau_hoi", [])) for de_thi in data["cau_hoi"][mon].values())
                thoi_gian = 45 if total_questions <= 15 else 60
                self.start_timer(thoi_gian)

            self.text_cau_hoi.configure(state='normal')
            self.text_cau_hoi.delete("1.0", tk.END)
            for tag in self.text_cau_hoi.window_names():
                self.text_cau_hoi.delete(tag)
            for widget in self.answer_frame.winfo_children():
                widget.destroy()
            self.selected_questions.clear()
            self.answer_vars = {}

            if not data["cau_hoi"][mon]:
                self.text_cau_hoi.insert(tk.END, "Chưa có câu hỏi nào cho môn này.\n")
                self.text_cau_hoi.configure(state='disabled')
                self.stop_timer()
                return

            is_admin = self.account_data["users"].get(self.current_user, {}).get("role") == "admin"
            question_index = 0

            for ma_de, de_thi in sorted(data["cau_hoi"][mon].items()):
                self.text_cau_hoi.insert(tk.END, f"Đề: {de_thi['ten_de']} (Hạn: {de_thi.get('ngay_den_han', 'Không áp dụng')})\n\n")
                for question in de_thi.get("cau_hoi", []):
                    if not isinstance(question, dict) or "id" not in question or "cau_hoi" not in question:
                        self.logger.warning(f"Câu hỏi không hợp lệ trong {mon}: {question}")
                        continue
                    self.selected_questions[question_index] = tk.BooleanVar(value=False)
                    self.text_cau_hoi.insert(tk.END, f"Câu {question_index + 1}: {question['cau_hoi']}\n")

                    if not isinstance(question.get("dap_an", []), list) or len(question["dap_an"]) < 4:
                        self.logger.warning(f"Câu hỏi {question['id']} trong {mon} có đáp án không hợp lệ: {question.get('dap_an')}")
                        self.text_cau_hoi.insert(tk.END, "Câu hỏi có đáp án không hợp lệ.\n\n")
                        question_index += 1
                        continue

                    self.answer_vars[question_index] = tk.StringVar(value="")

                    for i, answer in enumerate(question["dap_an"]):
                        self.text_cau_hoi.insert(tk.END, "   ")
                        radiobutton = tk.Radiobutton(
                            self.text_cau_hoi,
                            text=f"{'ABCD'[i]}. {answer}",
                            variable=self.answer_vars[question_index],
                            value=str(i),
                            bg='#f5f7fa',
                            fg='#2d3748',
                            font=('Arial', 11),
                            command=lambda qid=question["id"], ans=i, m=mon: self.select_answer(m, qid, ans)
                        )
                        self.text_cau_hoi.window_create(tk.END, window=radiobutton)
                        self.text_cau_hoi.insert(tk.END, "\n")

                    if is_admin and self.show_answers.get():
                        correct_idx = question.get('dap_an_dung', -1)
                        if correct_idx >= 0 and correct_idx < len(question["dap_an"]):
                            self.text_cau_hoi.insert(tk.END, f"✅ Đáp án đúng: {'ABCD'[correct_idx]}\n")

                    self.text_cau_hoi.insert(tk.END, "\n")
                    question_index += 1

            self.text_cau_hoi.configure(state='disabled')
            self.logger.info(f"Hiển thị {question_index} câu hỏi cho môn {mon}")
        except Exception as e:
            self.logger.error(f"Lỗi hiển thị câu hỏi: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể hiển thị câu hỏi: {str(e)}")

    def select_answer(self, mon, qid, answer_idx):
        if not self.has_permission("select_answers"):
            self.logger.warning("Người dùng không có quyền chọn đáp án")
            messagebox.showerror("Lỗi", "Bạn không có quyền chọn đáp án!")
            return
        user_answers = self.test_answers if self.mode == "practice" else self.exam_answers
        user_answers = self.ensure_data_structure(user_answers, self.current_user, mon)
        if answer_idx >= 0:
            user_answers[self.current_user][mon][str(qid)] = answer_idx
            self.logger.debug(f"Lưu đáp án {answer_idx} cho câu hỏi {qid} trong {mon}")
        else:
            user_answers[self.current_user][mon].pop(str(qid), None)
            self.logger.debug(f"Bỏ chọn đáp án cho câu hỏi {qid} trong {mon}")
        try:
            self.data_manager.save_user_answers_data(user_answers, is_test=(self.mode == "practice"))
            self.logger.info(f"Đã lưu đáp án cho câu hỏi {qid}")
        except Exception as e:
            self.logger.error(f"Lỗi lưu đáp án: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể lưu đáp án: {str(e)}")

    def submit_exam(self):
        self.stop_timer()
        if not self.current_user or not self.mon_var.get():
            messagebox.showerror("Lỗi", "Không có người dùng hoặc môn học được chọn!")
            return
        try:
            mon = self.mon_var.get()
            self.exam_answers = self.data_manager.load_user_answers_data()
            self.exam_answers = self.ensure_data_structure(self.exam_answers, self.current_user, mon)
            user_answers = self.exam_answers[self.current_user][mon]
            if not any(k.isdigit() for k in user_answers.keys()):
                messagebox.showwarning("Cảnh báo", "Bạn chưa trả lời câu hỏi nào!")
                return
            total_questions = sum(len(de_thi.get("cau_hoi", [])) for de_thi in self.exam_data["cau_hoi"].get(mon, {}).values())
            correct_count = 0
            for ma_de, de_thi in self.exam_data["cau_hoi"].get(mon, {}).items():
                for cau in de_thi.get("cau_hoi", []):
                    if str(cau["id"]) in user_answers and user_answers[str(cau["id"])] == cau["dap_an_dung"]:
                        correct_count += 1
            score = (correct_count / total_questions * 10) if total_questions > 0 else 0
            user_answers.update({
                "total_questions": total_questions,
                "correct_count": correct_count,
                "score": score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.data_manager.save_user_answers_data(self.exam_answers)
            saved_data = self.data_manager.load_user_answers_data()
            if self.current_user in saved_data and mon in saved_data[self.current_user]:
                self.logger.info(f"Đã lưu bài thi thành công cho user {self.current_user}, môn {mon}")
            else:
                self.logger.error(f"Lỗi: Dữ liệu bài thi không được lưu đúng cho user {self.current_user}, môn {mon}")
                messagebox.showerror("Lỗi", "Không thể lưu bài thi vào file!")
                return
            messagebox.showinfo("Thành công", f"Bài thi đã nộp! Điểm: {score:.2f}/10")
            self.show_default_interface()
        except Exception as e:
            self.logger.error(f"Lỗi nộp bài thi: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể nộp bài thi: {str(e)}")

    def submit_test(self):
        if not self.current_user or not self.mon_var.get():
            messagebox.showerror("Lỗi", "Không có người dùng hoặc môn học được chọn!")
            return
        try:
            mon = self.mon_var.get()
            self.test_answers = self.data_manager.load_user_answers_data(is_test=True)
            self.test_answers = self.ensure_data_structure(self.test_answers, self.current_user, mon)
            user_answers = self.test_answers[self.current_user][mon]
            if not any(k.isdigit() for k in user_answers.keys()):
                messagebox.showwarning("Cảnh báo", "Bạn chưa trả lời câu hỏi nào!")
                return
            total_questions = sum(len(de_thi.get("cau_hoi", [])) for de_thi in self.test_data["cau_hoi"].get(mon, {}).values())
            correct_count = 0
            for ma_de, de_thi in self.test_data["cau_hoi"].get(mon, {}).items():
                for cau in de_thi.get("cau_hoi", []):
                    if str(cau["id"]) in user_answers and user_answers[str(cau["id"])] == cau["dap_an_dung"]:
                        correct_count += 1
            score = (correct_count / total_questions * 10) if total_questions > 0 else 0
            user_answers.update({
                "total_questions": total_questions,
                "correct_count": correct_count,
                "score": score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.data_manager.save_user_answers_data(self.test_answers, is_test=True)
            saved_data = self.data_manager.load_user_answers_data(is_test=True)
            if self.current_user in saved_data and mon in saved_data[self.current_user]:
                self.logger.info(f"Đã lưu bài kiểm tra thành công cho user {self.current_user}, môn {mon}")
            else:
                self.logger.error(f"Lỗi: Dữ liệu bài kiểm tra không được lưu đúng cho user {self.current_user}, môn {mon}")
                messagebox.showerror("Lỗi", "Không thể lưu bài kiểm tra vào file!")
                return
            messagebox.showinfo("Thành công", f"Bài tập đã nộp! Điểm: {score:.2f}/10")
            self.show_default_interface()
        except Exception as e:
            self.logger.error(f"Lỗi nộp bài kiểm tra: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể nộp bài kiểm tra: {str(e)}")
            
    def create_account(self):
        if self.current_user and not self.has_permission("add_account"):
            self.logger.warning("Người dùng không có quyền tạo tài khoản")
            messagebox.showerror("Lỗi", "Bạn không có quyền để tạo tài khoản!")
            return
        try:
            create_account(self)
            self.account_data = self.data_manager.load_account_data()
            self.logger.info("Tạo tài khoản mới thành công")
        except Exception as e:
            self.logger.error(f"Lỗi tạo tài khoản: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể tạo tài khoản: {str(e)}")

    def crawl_data_from_api(self, is_test=False):
        if not self.has_permission("crawl_data"):
            self.logger.warning("Người dùng không có quyền crawl dữ liệu")
            messagebox.showerror("Lỗi", "Bạn không có quyền crawl dữ liệu!")
            return
        try:
            crawl_data_from_api(self, is_test=is_test)
            self.logger.info(f"Crawl dữ liệu {'bài tập' if is_test else 'đề thi'} thành công")
        except Exception as e:
            self.logger.error(f"Lỗi crawl dữ liệu: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể crawl dữ liệu: {str(e)}")

    def validate_password(self, password):
        return validate_password(password)

    def login(self):
        username = self.entry_username.get().strip().lower()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Tên đăng nhập và mật khẩu không được để trống!")
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            return

        if "users" not in self.account_data:
            self.account_data["users"] = {
                "admin": {"password": "admin123", "role": "admin"}
            }
            self.data_manager.save_account_data(self.account_data)
            self.logger.info("Tạo tài khoản mặc định: admin/admin123")
            messagebox.showinfo("Thông báo", "Dữ liệu người dùng không tồn tại. Đã tạo tài khoản mặc định: admin/admin123")

        if not self.account_data["users"]:
            messagebox.showerror("Lỗi", "Không có người dùng nào trong hệ thống. Vui lòng liên hệ quản trị viên!")
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            return

        try:
            if username in self.account_data["users"] and self.account_data["users"][username]["password"] == password:
                self.current_user = username
                if hasattr(self, 'login_frame') and self.login_frame.winfo_exists():
                    self.login_frame.destroy()
                else:
                    self.logger.warning("login_frame không tồn tại hoặc đã bị hủy")
            
                for widget in self.root.winfo_children():
                    if widget != self.title_bar:
                        widget.destroy()
            
                if self.account_data["users"][username]["role"] == "user":
                    self.create_mode_selection_widgets()
                    self.logger.info(f"Người dùng {username} đăng nhập thành công, hiển thị giao diện chọn chế độ")
                else:
                    self.mode = "admin"
                    self.create_widgets()
                    self.cap_nhat_danh_sach_mon()
                    self.root.update()
                    self.logger.info(f"Quản trị viên {username} đăng nhập thành công")
            else:
                if username not in self.account_data["users"]:
                    messagebox.showerror("Error", f"Tên đăng nhập '{username}' không tồn tại!")
                else:
                    messagebox.showerror("Error", "Mật khẩu không đúng!")
                self.entry_username.delete(0, tk.END)
                self.entry_password.delete(0, tk.END)
        except Exception as e:
            self.logger.error(f"Lỗi khi đăng nhập: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể đăng nhập: {str(e)}")

    def switch_to_login(self):
        for widget in self.root.winfo_children():
            if widget != self.title_bar:
                widget.destroy()
        self.create_login_widgets()

    def set_mode(self, mode):
        self.mode = mode
        try:
            if hasattr(self, 'mode_frame') and self.mode_frame.winfo_exists():
                self.mode_frame.destroy()
            self.create_widgets()
            self.cap_nhat_danh_sach_mon()
            self.root.update()
            self.logger.info(f"Chế độ được đặt thành {mode}")
        except Exception as e:
            self.logger.error(f"Lỗi đặt chế độ: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể chuyển sang trang chủ: {str(e)}")

    def has_permission(self, action):
        if not self.current_user:
            return False
        role = self.account_data["users"].get(self.current_user, {}).get("role")
        permissions = {
            "admin": ["add_subject", "delete_subject", "add_question", "delete_question", 
                      "update_question", "view_questions", "search_questions", 
                      "select_answers", "toggle_checkboxes", "crawl_data", "add_account", "view_stats", "manage_accounts"],
            "user": ["view_questions", "select_answers", "toggle_checkboxes"] + 
                    (["search_questions"] if self.mode == "practice" else [])
        }
        return action in permissions.get(role, [])

    def manage_accounts(self):
        if not self.has_permission("manage_accounts"):
            self.logger.warning("Người dùng không có quyền quản lý tài khoản")
            messagebox.showerror("Lỗi", "Bạn không có quyền quản lý tài khoản!")
            return

        account_window = tk.Toplevel(self.root)
        account_window.title("Quản lý tài khoản")
        account_window.geometry("600x500")
        account_window.configure(bg='#f5f7fa')

        container = tk.Frame(account_window, bg='#f5f7fa', bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5)

        tk.Label(container, text="Danh sách tài khoản:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)
        account_listbox = tk.Listbox(container, width=50, height=10, font=('Arial', 10))
        account_listbox.pack(padx=10, pady=5)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=account_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        account_listbox.config(yscrollcommand=scrollbar.set)

        def update_account_list():
            account_listbox.delete(0, tk.END)
            for username, info in self.account_data["users"].items():
                account_listbox.insert(tk.END, f"{username} ({info['role'].capitalize()})")

        update_account_list()

        def add_account():
            add_window = tk.Toplevel(account_window)
            add_window.title("Thêm tài khoản")
            add_window.geometry("400x300")
            add_window.configure(bg='#f5f7fa')

            form_frame = tk.Frame(add_window, bg='#f5f7fa', padx=10, pady=10)
            form_frame.pack(expand=True, fill=tk.BOTH)

            tk.Label(form_frame, text="Tên đăng nhập:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
            entry_username = tk.Entry(form_frame, width=20, font=('Arial', 12))
            entry_username.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Mật khẩu:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            entry_password = tk.Entry(form_frame, width=20, font=('Arial', 12), show="*")
            entry_password.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Vai trò:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            role_var = tk.StringVar(value="user")
            ttk.Combobox(form_frame, textvariable=role_var, values=['user', 'admin'], width=17, font=('Arial', 12), state='readonly').grid(row=2, column=1, padx=5, pady=5)

            def confirm_add():
                username = entry_username.get().strip().lower()
                password = entry_password.get().strip()
                role = role_var.get()

                if not username or not password:
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
                    return

                if username in self.account_data["users"]:
                    messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
                    return

                if not self.validate_password(password):
                    messagebox.showerror("Lỗi", "Mật khẩu không hợp lệ! Phải có ít nhất 6 ký tự, bao gồm chữ và số.")
                    return

                self.account_data["users"][username] = {
                    "password": password,
                    "role": role
                }
                self.data_manager.save_account_data(self.account_data)
                self.logger.info(f"Thêm tài khoản {username} ({role}) thành công")
                messagebox.showinfo("Thành công", "Thêm tài khoản thành công!")
                update_account_list()
                add_window.destroy()

            tk.Button(form_frame, text="Thêm", command=confirm_add, bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat').grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(form_frame, text="Hủy", command=add_window.destroy, bg='#e63946', fg='white', font=('Arial', 12), relief='flat').grid(row=4, column=0, columnspan=2, pady=5)

        def delete_account():
            if not account_listbox.curselection():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để xóa!")
                return

            selected = account_listbox.get(account_listbox.curselection()[0])
            username = selected.split(" (")[0]

            if username == self.current_user:
                messagebox.showerror("Lỗi", "Không thể xóa tài khoản đang đăng nhập!")
                return

            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tài khoản '{username}'?"):
                del self.account_data["users"][username]
                self.data_manager.save_account_data(self.account_data)
                self.logger.info(f"Xóa tài khoản {username} thành công")
                messagebox.showinfo("Thành công", f"Đã xóa tài khoản '{username}'!")
                update_account_list()

        def edit_account():
            if not account_listbox.curselection():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để sửa!")
                return

            selected = account_listbox.get(account_listbox.curselection()[0])
            username = selected.split(" (")[0]

            edit_window = tk.Toplevel(account_window)
            edit_window.title(f"Sửa tài khoản - {username}")
            edit_window.geometry("400x300")
            edit_window.configure(bg='#f5f7fa')

            form_frame = tk.Frame(edit_window, bg='#f5f7fa', padx=10, pady=10)
            form_frame.pack(expand=True, fill=tk.BOTH)

            tk.Label(form_frame, text="Tên đăng nhập:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
            tk.Label(form_frame, text=username, bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=0, column=1, padx=5, pady=5, sticky="w")

            tk.Label(form_frame, text="Mật khẩu mới:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            entry_password = tk.Entry(form_frame, width=20, font=('Arial', 12), show="*")
            entry_password.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(form_frame, text="Vai trò:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            role_var = tk.StringVar(value=self.account_data["users"][username]["role"])
            ttk.Combobox(form_frame, textvariable=role_var, values=['user', 'admin'], width=17, font=('Arial', 12), state='readonly').grid(row=2, column=1, padx=5, pady=5)

            def confirm_edit():
                password = entry_password.get().strip()
                role = role_var.get()

                if password and not self.validate_password(password):
                    messagebox.showerror("Lỗi", "Mật khẩu không hợp lệ! Phải có ít nhất 6 ký tự, bao gồm chữ và số.")
                    return

                if password:
                    self.account_data["users"][username]["password"] = password
                self.account_data["users"][username]["role"] = role
                self.data_manager.save_account_data(self.account_data)
                self.logger.info(f"Sửa tài khoản {username} ({role}) thành công")
                messagebox.showinfo("Thành công", "Sửa tài khoản thành công!")
                update_account_list()
                edit_window.destroy()

            tk.Button(form_frame, text="Cập nhật", command=confirm_edit, bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat').grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(form_frame, text="Hủy", command=edit_window.destroy, bg='#e63946', fg='white', font=('Arial', 12), relief='flat').grid(row=4, column=0, columnspan=2, pady=5)

        button_frame = tk.Frame(container, bg='#f5f7fa')
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="Thêm tài khoản", command=add_account, bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Xóa tài khoản", command=delete_account, bg='#e63946', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sửa tài khoản", command=edit_account, bg='#f6ad55', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Đóng", command=account_window.destroy, bg='#6b7280', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.RIGHT, padx=5)

    def view_stats(self):
        if not self.has_permission("view_stats"):
            self.logger.warning("Người dùng không có quyền xem thống kê")
            messagebox.showerror("Lỗi", "Bạn không có quyền xem thống kê!")
            return

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Thống kê đậu/rớt")
        stats_window.geometry("800x600")
        stats_window.configure(bg='#f5f7fa')

        container = tk.Frame(stats_window, bg='#f5f7fa', bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5)

        tk.Label(container, text="Chọn môn học:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)
        mon_var = tk.StringVar(value="")
        mon_combobox = ttk.Combobox(container, textvariable=mon_var, width=30, font=('Arial', 12))
        subjects = [mon["ten_mon"] for mon in self.exam_data["mon_thi"]]
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

            for user, user_data in self.exam_answers.items():
                if mon in user_data and "score" in user_data[mon]:
                    score = user_data[mon]["score"]
                    scores.append(score)
                    if score >= pass_threshold:
                        pass_count += 1
                    else:
                        fail_count += 1

            ax.clear()
            ax.bar(['Đậu', 'Rớt'], [pass_count, fail_count], color=['#4a90e2', '#e63946'])
            ax.set_title(f'Thống kê đậu/rớt môn {mon}')
            ax.set_ylabel('Số lượng học sinh')
            ax.set_ylim(0, max(pass_count, fail_count, 1) + 1)
            for i, v in enumerate([pass_count, fail_count]):
                ax.text(i, v + 0.1, str(v), ha='center', va='bottom')
            canvas.draw()

            stats_text = f"Tổng số học sinh: {pass_count + fail_count}\n"
            stats_text += f"Đậu: {pass_count} ({pass_count / (pass_count + fail_count) * 100:.2f}%)\n"
            stats_text += f"Rớt: {fail_count} ({fail_count / (pass_count + fail_count) * 100:.2f}%)\n"
            if scores:
                stats_text += f"Điểm trung bình: {sum(scores) / len(scores):.2f}\n"
                stats_text += f"Điểm cao nhất: {max(scores):.2f}\n"
                stats_text += f"Điểm thấp nhất: {min(scores):.2f}"

            stats_label.config(text=stats_text)

            self.logger.info(f"Hiển thị thống kê đậu/rớt cho môn {mon}")

        mon_combobox.bind('<<ComboboxSelected>>', lambda e: update_stats())

        stats_label = tk.Label(container, text="", bg='#2d3748', fg='white', font=('Arial', 12), justify='left')
        stats_label.pack(pady=10)

        tk.Button(container, text="Đóng", command=stats_window.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 12), relief='flat').pack(pady=10)

    def view_user_submission(self):
        if not self.has_permission("view_stats"):
            self.logger.warning("Người dùng không có quyền xem bài làm")
            messagebox.showerror("Lỗi", "Bạn không có quyền xem bài làm của học sinh!")
            return

        submission_window = tk.Toplevel(self.root)
        submission_window.title("Xem bài làm của học sinh")
        submission_window.geometry("800x600")
        submission_window.configure(bg='#f5f7fa')

        container = tk.Frame(submission_window, bg='#f5f7fa', bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5)

        tk.Label(container, text="Chọn môn học:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)
        mon_var = tk.StringVar(value="")
        mon_combobox = ttk.Combobox(container, textvariable=mon_var, width=30, font=('Arial', 12))
        subjects = [mon["ten_mon"] for mon in self.exam_data["mon_thi"]]
        mon_combobox['values'] = subjects
        mon_combobox.pack(pady=5)

        tk.Label(container, text="Chọn học sinh:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)
        user_var = tk.StringVar(value="")
        user_combobox = ttk.Combobox(container, textvariable=user_var, width=30, font=('Arial', 12))
        users = [user for user in self.exam_answers.keys() if self.account_data["users"].get(user, {}).get("role") == "user"]
        user_combobox['values'] = users
        user_combobox.pack(pady=5)

        text_area = tk.Text(container, width=70, height=20, font=('Arial', 10))
        text_area.pack(padx=10, pady=10)
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
            answers = self.exam_answers.get(user, {}).get(mon, {})
            if not answers or not any(k.isdigit() for k in answers.keys()):
                text_area.insert(tk.END, "Học sinh này chưa nộp bài cho môn này.\n")
                text_area.config(state='disabled')
                self.logger.info(f"Không tìm thấy bài làm cho user {user}, môn {mon}")
                return

            text_area.insert(tk.END, f"Bài làm của {user} - Môn {mon}\n")
            text_area.insert(tk.END, f"Thời gian nộp: {answers.get('timestamp', 'N/A')}\n")
            text_area.insert(tk.END, f"Điểm: {answers.get('score', 0):.2f}/10\n")
            text_area.insert(tk.END, f"Số câu đúng: {answers.get('correct_count', 0)}/{answers.get('total_questions', 0)}\n\n")

            question_index = 1
            data = self.exam_data
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
            self.logger.info(f"Hiển thị bài làm của user {user} cho môn {mon}")

        tk.Button(container, text="Hiển thị bài làm", command=show_submission,
                 bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat').pack(pady=5)
        tk.Button(container, text="Đóng", command=submission_window.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 12), relief='flat').pack(pady=5)

    def add_practice_subject(self):
        if not self.has_permission("add_subject"):
            messagebox.showerror("Error", "Bạn không có quyền thêm môn học!")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm môn học")
        add_window.geometry("400x300")
        add_window.configure(bg='#f5f7fa')

        form_frame = tk.Frame(add_window, bg='#f5f7fa', padx=10, pady=10)
        form_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(form_frame, text="Mã môn học:", bg='#f5f7fa', fg='#2d3748',
                 font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_ma_mon = tk.Entry(form_frame, width=30, font=('Arial', 12))
        entry_ma_mon.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Tên môn học:", bg='#f5f7fa', fg='#2d3748',
                 font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_ten_mon = tk.Entry(form_frame, width=30, font=('Arial', 12))
        entry_ten_mon.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Hạn nộp bài (YYYY-MM-DD):", bg='#f5f7fa', fg='#2d3748',
                 font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_han_nop = DateEntry(form_frame, width=27, font=('Arial', 12), date_pattern='yyyy-mm-dd')
        entry_han_nop.grid(row=2, column=1, padx=5, pady=5)

        def confirm_add():
            ma_mon = entry_ma_mon.get().strip()
            ten_mon = entry_ten_mon.get().strip()
            han_nop = entry_han_nop.get().strip()

            if not ma_mon or not ten_mon:
                messagebox.showerror("Error", "Vui lòng nhập đầy đủ Mã môn và Tên môn!")
                return

            for mon in self.test_data["mon_thi"]:
                if mon["ma_mon"] == ma_mon:
                    messagebox.showerror("Error", "Mã môn đã tồn tại!")
                    return
                if mon["ten_mon"] == ten_mon:
                    messagebox.showerror("Error", "Tên môn đã tồn tại!")
                    return

            self.test_data["mon_thi"].append({
                "ma_mon": ma_mon,
                "ten_mon": ten_mon,
                "han_nop_bai": han_nop or None
            })
            self.test_data["cau_hoi"][ten_mon] = {}
            self.data_manager.save_data(self.test_data, is_test=True)
            messagebox.showinfo("Thành công", "Thêm môn học thành công!")
            add_window.destroy()
            self.cap_nhat_danh_sach_mon()

        btn_confirm = tk.Button(form_frame, text="Thêm môn", command=confirm_add,
                               bg='#4a90e2', fg='white', font=('Arial', 11), relief='flat')
        btn_confirm.grid(row=3, column=0, columnspan=2, pady=10)
        btn_confirm.bind("<Button-1>", lambda e: btn_confirm.config(bg='#357abd'))
        btn_confirm.bind("<ButtonRelease-1>", lambda e: btn_confirm.config(bg='#4a90e2'))

        btn_cancel = tk.Button(form_frame, text="Hủy", command=add_window.destroy,
                              bg='#e63946', fg='white', font=('Arial', 11), relief='flat')
        btn_cancel.grid(row=4, column=0, columnspan=2, pady=5)
        btn_cancel.bind("<Button-1>", lambda e: btn_cancel.config(bg='#c53030'))
        btn_cancel.bind("<ButtonRelease-1>", lambda e: btn_cancel.config(bg='#e63946'))

    def delete_practice_subject(self, tree):
        if not self.has_permission("delete_subject"):
            messagebox.showerror("Error", "Bạn không có quyền xóa môn học!")
            return

        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một môn học để xóa!")
            return

        ten_mon = tree.item(selected_item)["values"][1]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa môn '{ten_mon}'?"):
            self.test_data["mon_thi"] = [mon for mon in self.test_data["mon_thi"] if mon["ten_mon"] != ten_mon]
            if ten_mon in self.test_data["cau_hoi"]:
                del self.test_data["cau_hoi"][ten_mon]
            self.data_manager.save_data(self.test_data, is_test=True)
            messagebox.showinfo("Thành công", f"Đã xóa môn '{ten_mon}' thành công!")
            tree.delete(selected_item)
            self.cap_nhat_danh_sach_mon()

    def delete_exam_subject(self, tree):
        if not self.has_permission("delete_subject"):
            messagebox.showerror("Error", "Bạn không có quyền xóa môn học!")
            return

        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một môn học để xóa!")
            return

        ten_mon = tree.item(selected_item)["values"][1]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa môn '{ten_mon}'?"):
            self.exam_data["mon_thi"] = [mon for mon in self.exam_data["mon_thi"] if mon["ten_mon"] != ten_mon]
            if ten_mon in self.exam_data["cau_hoi"]:
                del self.exam_data["cau_hoi"][ten_mon]
            self.data_manager.save_data(self.exam_data)
            messagebox.showinfo("Thành công", f"Đã xóa môn '{ten_mon}' thành công!")
            tree.delete(selected_item)
            self.cap_nhat_danh_sach_mon()

    def logout(self):
        try:
            self.stop_timer()
            for widget in self.root.winfo_children():
                if widget != self.title_bar:
                    widget.destroy()
            self.current_user = None
            self.mode = None
            self.selected_questions.clear()
            self.show_answers.set(False)
            self.create_login_widgets()
            self.root.update()
            self.logger.info("Đăng xuất thành công")
            messagebox.showinfo("Thành công", "Đã đăng xuất!")
        except Exception as e:
            self.logger.error(f"Lỗi khi đăng xuất: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể đăng xuất: {str(e)}")

    def manage_practice(self):
        if not self.has_permission("add_question"):
            messagebox.showerror("Error", "Bạn không có quyền quản lý bài tập trắc nghiệm!")
            return

        practice_window = tk.Toplevel(self.root)
        practice_window.title("Quản lý bài tập trắc nghiệm")
        practice_window.geometry("800x600")
        practice_window.configure(bg='#f5f7fa')

        container = tk.Frame(practice_window, bg='#f5f7fa', bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=5)

        tk.Label(container, text="Chọn môn học:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)
        mon_var = tk.StringVar(value="")
        mon_combobox = ttk.Combobox(container, textvariable=mon_var, width=30, font=('Arial', 12))
        subjects = [mon["ten_mon"] for mon in self.test_data["mon_thi"]]
        mon_combobox['values'] = subjects
        mon_combobox.pack(pady=5)

        tk.Label(container, text="Danh sách câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)
        question_frame = tk.Frame(container, bg='#f5f7fa')
        question_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        question_listbox = tk.Listbox(question_frame, width=50, height=15, font=('Arial', 10))
        question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(question_frame, orient='vertical', command=question_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        question_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(container, bg='#f5f7fa')
        button_frame.pack(fill=tk.X, pady=5)

        def update_question_list():
            question_listbox.delete(0, tk.END)
            mon = mon_var.get()
            if not mon or mon not in self.test_data["cau_hoi"]:
                question_listbox.insert(tk.END, "Vui lòng chọn môn học.")
                return
            question_index = 1
            for ma_de, de_thi in self.test_data["cau_hoi"].get(mon, {}).items():
                for cau in de_thi.get("cau_hoi", []):
                    question_listbox.insert(tk.END, f"Câu {question_index}: {cau['cau_hoi']} (Đề {ma_de})")
                    question_index += 1
            if question_index == 1:
                question_listbox.insert(tk.END, "Chưa có câu hỏi nào cho môn này.")

        mon_combobox.bind('<<ComboboxSelected>>', lambda e: update_question_list())

        def add_practice_question():
            mon = mon_var.get()
            if not mon:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học!")
                return
            self.them_cau_hoi(mon)
            update_question_list()
            self.cap_nhat_danh_sach_mon()
            if self.combobox_mon:
                self.combobox_mon.set(mon)
            self.hien_thi_cau_hoi()

        def delete_practice_question():
            mon = mon_var.get()
            if not mon:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học!")
                return
            if not question_listbox.curselection():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn câu hỏi để xóa!")
                return
            index = question_listbox.curselection()[0]
            all_questions = []
            for ma_de, de_thi in self.test_data["cau_hoi"].get(mon, {}).items():
                for cau in de_thi.get("cau_hoi", []):
                    all_questions.append((ma_de, cau["id"]))
            if index >= len(all_questions):
                messagebox.showerror("Error", "Câu hỏi không hợp lệ!")
                return
            ma_de, cau_id = all_questions[index]
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa câu hỏi {index + 1}?"):
                questions = self.test_data["cau_hoi"][mon][ma_de]["cau_hoi"]
                questions[:] = [q for q in questions if q["id"] != cau_id]
                if not questions:
                    del self.test_data["cau_hoi"][mon][ma_de]
                self.data_manager.save_data(self.test_data, is_test=True)
                messagebox.showinfo("Thành công", "Xóa câu hỏi thành công!")
                update_question_list()
                self.cap_nhat_danh_sach_mon()
                self.hien_thi_cau_hoi()

        def edit_practice_question():
            mon = mon_var.get()
            if not mon:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học!")
                return
            if not question_listbox.curselection():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn câu hỏi để chỉnh sửa!")
                return
            self.cap_nhat_cau_hoi(mon)
            update_question_list()
            self.cap_nhat_danh_sach_mon()
            self.hien_thi_cau_hoi()

        tk.Button(button_frame, text="Thêm câu hỏi", command=add_practice_question,
                 bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Xóa câu hỏi", command=delete_practice_question,
                 bg='#e63946', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sửa câu hỏi", command=edit_practice_question,
                 bg='#f6ad55', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Đóng", command=practice_window.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 12), relief='flat', width=15).pack(side=tk.RIGHT, padx=5)

        update_question_list()

    def them_cau_hoi(self, mon):
        if not self.has_permission("add_question"):
            messagebox.showerror("Error", "Bạn không có quyền thêm câu hỏi!")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title(f"Thêm câu hỏi - {mon}")
        add_window.geometry("600x600")
        add_window.configure(bg='#f5f7fa')

        form_frame = tk.Frame(add_window, bg='#f5f7fa', padx=10, pady=10)
        form_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(form_frame, text="Mã đề:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_ma_de = tk.Entry(form_frame, width=30, font=('Arial', 12))
        entry_ma_de.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Tên đề:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_ten_de = tk.Entry(form_frame, width=30, font=('Arial', 12))
        entry_ten_de.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Hạn nộp (YYYY-MM-DD):", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_han_nop = DateEntry(form_frame, width=27, font=('Arial', 12), date_pattern='yyyy-mm-dd')
        entry_han_nop.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=3, column=0, padx=5, pady=5, sticky="ne")
        entry_cau_hoi = tk.Text(form_frame, width=30, height=5, font=('Arial', 12))
        entry_cau_hoi.grid(row=3, column=1, padx=5, pady=5)

        dap_an_entries = []
        for i in range(4):
            tk.Label(form_frame, text=f"Đáp án {chr(65 + i)}:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=4+i, column=0, padx=5, pady=5, sticky="e")
            entry_dap_an = tk.Entry(form_frame, width=30, font=('Arial', 12))
            entry_dap_an.grid(row=4+i, column=1, padx=5, pady=5)
            dap_an_entries.append(entry_dap_an)

        tk.Label(form_frame, text="Đáp án đúng:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).grid(row=8, column=0, padx=5, pady=5, sticky="e")
        dap_an_dung_var = tk.StringVar(value="A")
        ttk.Combobox(form_frame, textvariable=dap_an_dung_var, values=['A', 'B', 'C', 'D'], font=('Arial', 12), width=5, state='readonly').grid(row=8, column=1, padx=5, pady=5, sticky="w")

        def confirm_add():
            ma_de = entry_ma_de.get().strip()
            ten_de = entry_ten_de.get().strip()
            ngay_han_nop = entry_han_nop.get().strip()
            cau_hoi = entry_cau_hoi.get("1.0", tk.END).strip()
            dap_an = [entry.get().strip() for entry in dap_an_entries]
            try:
                dap_an_dung = 'ABCD'.index(dap_an_dung_var.get())
            except ValueError:
                messagebox.showerror("Error", "Đáp án đúng không hợp lệ!")
                return

            if not all([ma_de, ten_de, cau_hoi] + dap_an):
                messagebox.showerror("Error", "Vui lòng nhập đầy đủ thông tin!")
                return

            if ngay_han_nop:
                try:
                    datetime.strptime(ngay_han_nop, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Hạn nộp không đúng định dạng (YYYY-MM-DD)!")
                    return

            data = self.test_data if self.mode == "practice" else self.exam_data
            if mon not in data["cau_hoi"]:
                data["cau_hoi"][mon] = {}

            if ma_de in data["cau_hoi"][mon]:
                if data["cau_hoi"][mon][ma_de]["ten_de"] != ten_de:
                    messagebox.showerror("Error", "Mã đề đã tồn tại với tên đề khác!")
                    return
            else:
                data["cau_hoi"][mon][ma_de] = {
                    "ten_de": ten_de,
                    "ngay_den_han": ngay_han_nop or None,
                    "cau_hoi": []
                }

            current_questions = data["cau_hoi"][mon][ma_de]["cau_hoi"]
            new_id = max([q["id"] for q in current_questions], default=0) + 1

            new_question = {
                "id": new_id,
                "cau_hoi": cau_hoi,
                "dap_an": dap_an,
                "dap_an_dung": dap_an_dung
            }
            current_questions.append(new_question)

            try:
                self.data_manager.save_data(data, is_test=(self.mode == "practice"))
                self.logger.info(f"Thêm câu hỏi mới (ID: {new_id}) cho môn {mon}, đề {ma_de}")
                messagebox.showinfo("Thành công", "Thêm câu hỏi thành công!")
                add_window.destroy()
            except Exception as e:
                self.logger.error(f"Lỗi lưu câu hỏi: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể lưu câu hỏi: {str(e)}")

        tk.Button(form_frame, text="Thêm câu hỏi", command=confirm_add,
                 bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat').grid(row=9, column=0, columnspan=2, pady=10)
        tk.Button(form_frame, text="Hủy", command=add_window.destroy,
                 bg='#e63946', fg='white', font=('Arial', 12), relief='flat').grid(row=10, column=0, columnspan=2, pady=5)

    def xoa_cau_hoi(self, mon):
        if not self.has_permission("delete_question"):
            messagebox.showerror("Error", "Bạn không có quyền xóa câu hỏi!")
            return
        data = self.test_data if self.mode == "practice" else self.exam_data
        if not mon or mon not in data["cau_hoi"] or not data["cau_hoi"][mon]:
            messagebox.showwarning("Cảnh báo", "Hãy chọn một môn học có câu hỏi!")
            return

        delete_window = tk.Toplevel(self.root)
        delete_window.title(f"Xóa câu hỏi - {mon}")
        delete_window.geometry("600x400")
        delete_window.configure(bg='#f5f7fa')

        form_frame = tk.Frame(delete_window, bg='#f5f7fa', padx=10, pady=10)
        form_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(form_frame, text="Danh sách câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
        question_listbox = tk.Listbox(form_frame, width=50, height=10, font=('Arial', 10))
        question_listbox.pack(padx=5, pady=5)

        all_questions = []
        for ma_de, de_thi in data["cau_hoi"][mon].items():
            for cau in de_thi.get("cau_hoi", []):
                all_questions.append((ma_de, cau["id"], cau["cau_hoi"]))
        for idx, (ma_de, q_id, cau_hoi) in enumerate(all_questions, 1):
            question_listbox.insert(tk.END, f"Câu {idx}: {cau_hoi} (Đề {ma_de})")

        tk.Label(form_frame, text="Số thứ tự câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
        entry_index = tk.Entry(form_frame, width=10, font=('Arial', 12))
        entry_index.pack(anchor='w', padx=5, pady=5)

        def confirm_delete():
            try:
                cau_hoi_index = int(entry_index.get()) - 1
            except ValueError:
                messagebox.showerror("Error", "Số thứ tự không hợp lệ!")
                return

            if cau_hoi_index < 0 or cau_hoi_index >= len(all_questions):
                messagebox.showerror("Error", "Số thứ tự câu hỏi không hợp lệ!")
                return

            ma_de, q_id, _ = all_questions[cau_hoi_index]
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa câu hỏi {cau_hoi_index + 1}?"):
                questions = data["cau_hoi"][mon][ma_de]["cau_hoi"]
                questions[:] = [q for q in questions if q["id"] != q_id]
                if not questions:
                    del data["cau_hoi"][mon][ma_de]
                self.data_manager.save_data(data, is_test=(self.mode == "practice"))
                messagebox.showinfo("Thành công", "Xóa câu hỏi thành công!")
                delete_window.destroy()
                self.hien_thi_cau_hoi()

        tk.Button(form_frame, text="Xác nhận", command=confirm_delete,
                 bg='#e63946', fg='white', font=('Arial', 12), relief='flat').pack(pady=10)
        tk.Button(form_frame, text="Hủy", command=delete_window.destroy,
                 bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat').pack(pady=5)

    def cap_nhat_cau_hoi(self, mon):
        if not self.has_permission("update_question"):
            messagebox.showerror("Error", "Bạn không có quyền cập nhật câu hỏi!")
            return
        data = self.test_data if self.mode == "practice" else self.exam_data
        if not mon or mon not in data["cau_hoi"] or not data["cau_hoi"][mon]:
            messagebox.showwarning("Cảnh báo", "Hãy chọn một môn học có câu hỏi!")
            return

        update_window = tk.Toplevel(self.root)
        update_window.title(f"Cập nhật câu hỏi - {mon}")
        update_window.geometry("600x600")
        update_window.configure(bg='#f5f7fa')

        form_frame = tk.Frame(update_window, bg='#f5f7fa', padx=10, pady=10)
        form_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(form_frame, text="Danh sách câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
        question_listbox = tk.Listbox(form_frame, width=50, height=5, font=('Arial', 10))
        question_listbox.pack(padx=5, pady=5)

        all_questions = []
        for ma_de, de_thi in data["cau_hoi"][mon].items():
            for q in de_thi.get("cau_hoi", []):
                all_questions.append((ma_de, q["id"], q))
        for idx, (ma_de, q_id, q) in enumerate(all_questions, 1):
            question_listbox.insert(tk.END, f"Câu {idx}: {q['cau_hoi']} (Đề {ma_de})")

        tk.Label(form_frame, text="Số thứ tự câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
        entry_index = tk.Entry(form_frame, width=10, font=('Arial', 12))
        entry_index.pack(anchor='w', padx=5, pady=5)

        tk.Label(form_frame, text="Câu hỏi:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
        entry_cau_hoi = tk.Text(form_frame, width=50, height=5, font=('Arial', 12))
        entry_cau_hoi.pack(padx=5, pady=5)

        dap_an_entries = []
        for i in range(4):
            tk.Label(form_frame, text=f"Đáp án {chr(65+i)}:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
            entry_dap_an = tk.Entry(form_frame, width=50, font=('Arial', 12))
            entry_dap_an.pack(padx=5, pady=5)
            dap_an_entries.append(entry_dap_an)

        tk.Label(form_frame, text="Đáp án đúng:", bg='#f5f7fa', fg='#2d3748', font=('Arial', 12)).pack(anchor='w', padx=5, pady=5)
        dap_an_dung_var = tk.StringVar(value="A")
        ttk.Combobox(form_frame, textvariable=dap_an_dung_var, values=['A', 'B', 'C', 'D'], font=('Arial', 12), width=5, state='readonly').pack(anchor='w', padx=5, pady=5)

        def load_question():
            try:
                cau_hoi_index = int(entry_index.get()) - 1
                if cau_hoi_index < 0 or cau_hoi_index >= len(all_questions):
                    messagebox.showerror("Error", "Số thứ tự không hợp lệ!")
                    return
                ma_de, q_id, q = all_questions[cau_hoi_index]
                entry_cau_hoi.delete("1.0", tk.END)
                entry_cau_hoi.insert(tk.END, q['cau_hoi'])
                for i, entry in enumerate(dap_an_entries):
                    entry.delete(0, tk.END)
                    entry.insert(0, q['dap_an'][i])
                dap_an_dung_var.set('ABCD'[q['dap_an_dung']])
            except ValueError:
                messagebox.showerror("Error", "Số thứ tự không hợp lệ!")

        tk.Button(form_frame, text="Tải câu hỏi", command=load_question,
                 bg='#f6ad55', fg='white', font=('Arial', 12), relief='flat').pack(anchor='w', pady=5)

        def confirm_update():
            try:
                cau_hoi_index = int(entry_index.get()) - 1
            except ValueError:
                messagebox.showerror("Error", "Số thứ tự không hợp lệ!")
                return

            if cau_hoi_index < 0 or cau_hoi_index >= len(all_questions):
                messagebox.showerror("Error", "Số thứ tự câu hỏi không hợp lệ!")
                return

            ma_de, q_id, _ = all_questions[cau_hoi_index]
            cau_hoi = entry_cau_hoi.get("1.0", tk.END).strip()
            dap_an = [entry.get().strip() for entry in dap_an_entries]
            try:
                dap_an_dung = 'ABCD'.index(dap_an_dung_var.get())
            except ValueError:
                messagebox.showerror("Error", "Đáp án đúng không hợp lệ!")
                return

            if not cau_hoi or not all(dap_an):
                messagebox.showerror("Error", "Vui lòng nhập đầy đủ câu hỏi và các đáp án!")
                return

            questions = data["cau_hoi"][mon][ma_de]["cau_hoi"]
            for q in questions:
                if q["id"] == q_id:
                    q["cau_hoi"] = cau_hoi
                    q["dap_an"] = dap_an
                    q["dap_an_dung"] = dap_an_dung
                    break

            try:
                self.data_manager.save_data(data, is_test=(self.mode == "practice"))
                messagebox.showinfo("Thành công", "Cập nhật câu hỏi thành công!")
                update_window.destroy()
                self.hien_thi_cau_hoi()
            except Exception as e:
                self.logger.error(f"Lỗi lưu dữ liệu: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể lưu câu hỏi: {str(e)}")

        tk.Button(form_frame, text="Cập nhật", command=confirm_update,
                 bg='#4a90e2', fg='white', font=('Arial', 12), relief='flat').pack(pady=10)
        tk.Button(form_frame, text="Hủy", command=update_window.destroy,
                 bg='#e63946', fg='white', font=('Arial', 12), relief='flat').pack(pady=5)

    def tim_kiem_cau(self):
        if not self.has_permission("search_questions"):
            messagebox.showerror("Error", "Bạn không có quyền tìm kiếm câu hỏi!")
            return

        mon = self.mon_var.get()
        data = self.test_data if self.mode == "practice" else self.exam_data
        if not mon or mon not in data["cau_hoi"]:
            messagebox.showwarning("Cảnh báo", "Hãy chọn một môn học có câu hỏi!")
            return

        tu_khoa = simpledialog.askstring("Input", "Nhập từ khóa tìm kiếm:", parent=self.root)
        if not tu_khoa:
            return

        self.text_cau_hoi.config(state='normal')
        self.text_cau_hoi.delete("1.0", tk.END)
        for tag in self.text_cau_hoi.window_names():
            self.text_cau_hoi.delete(tag)
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
        self.selected_questions.clear()
        is_admin = self.account_data["users"].get(self.current_user, {}).get("role") == "admin"
        question_index = 1
        found = False

        for ma_de, de_thi in sorted(data["cau_hoi"].get(mon, {}).items()):
            for cau in de_thi.get("cau_hoi", []):
                if tu_khoa.lower() in cau.get("cau_hoi", "").lower():
                    found = True
                    self.text_cau_hoi.insert(tk.END, f"Câu {question_index}: {cau['cau_hoi']}\n")

                    for i, da in enumerate(cau.get("dap_an", [])):
                        self.text_cau_hoi.insert(tk.END, f"   {'ABCD'[i]}. {da}\n")

                    if is_admin and self.show_answers.get():
                        correct_idx = cau.get('dap_an_dung', -1)
                        if correct_idx >= 0 and correct_idx < len(cau["dap_an"]):
                            self.text_cau_hoi.insert(tk.END, f"✅ Đáp án đúng: {'ABCD'[correct_idx]}\n")

                    question_index += 1

        if not found:
            self.text_cau_hoi.insert(tk.END, f"Không tìm thấy câu hỏi nào chứa từ khóa '{tu_khoa}'.\n")

        self.text_cau_hoi.config(state='disabled')
        self.logger.info(f"Tìm kiếm câu hỏi với từ khóa '{tu_khoa}' trong môn {mon}: {'tìm thấy' if found else 'không tìm thấy'}")

    def show_default_interface(self):
        for widget in self.frame_right.winfo_children():
            widget.destroy()
        self.create_widgets()
        self.cap_nhat_danh_sach_mon()
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()