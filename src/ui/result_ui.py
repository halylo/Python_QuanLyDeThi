import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from src.utils.constants import *

def submit_exam(app):
    mon = app.listbox_mon.get(tk.ACTIVE)
    if not mon or mon not in app.exam_answers.get(app.current_user, {}):
        messagebox.showwarning("Cảnh báo", "Bạn chưa trả lời câu hỏi nào để nộp bài!")
        return

    correct_count = 0
    total_questions = 0
    user_answers = app.exam_answers.get(app.current_user, {}).get(mon, {})

    # Duyệt qua tất cả các đề trong môn
    for ma_de, de_thi in app.exam_data["cau_hoi"].get(mon, {}).items():
        total_questions += len(de_thi.get("cau_hoi", []))
        for cau in de_thi.get("cau_hoi", []):
            idx = str(cau["id"])  # ID câu hỏi
            if idx in user_answers:
                if user_answers[idx] == cau["dap_an_dung"]:
                    correct_count += 1

    score = (correct_count / total_questions) * 10 if total_questions > 0 else 0

    # Lưu bài làm vào exam_answers
    if app.current_user not in app.exam_answers:
        app.exam_answers[app.current_user] = {}
    app.exam_answers[app.current_user][mon] = {
        "answers": user_answers,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "correct_count": correct_count,
        "total_questions": total_questions,
        "score": round(score, 2)
    }
    app.data_manager.save_user_answers_data(app.exam_answers, is_test=False)
    app.logger.info(f"Exam submitted for user {app.current_user}, subject {mon}: {app.exam_answers[app.current_user][mon]}")

    # Xóa bài làm tạm thời sau khi nộp
    app.exam_answers[app.current_user][mon] = {}
    app.data_manager.save_user_answers_data(app.exam_answers, is_test=False)
    app.hien_thi_cau_hoi()

    result_window = tk.Toplevel(app.root)
    result_window.title("Kết quả bài thi")
    result_window.configure(bg=BG_COLOR)
    result_window.geometry("500x350")

    container = tk.Frame(result_window, bg=FRAME_BG, bd=5, relief='flat')
    container.pack(expand=True, padx=10, pady=10)

    tk.Label(container, text="Kết quả bài thi", bg=FRAME_BG,
            font=('Times New Roman', 20, 'bold'), fg='#343a40').pack(pady=20)

    result_frame = tk.Frame(container, bg=FRAME_BG)
    result_frame.pack(pady=20)

    tk.Label(result_frame, text=f"Môn: {mon}", bg=FRAME_BG,
            font=('Times New Roman', 14), fg='#495057').pack(anchor='w', padx=20)
    tk.Label(result_frame, text=f"Số câu đúng: {correct_count}/{total_questions}", bg=FRAME_BG,
            font=('Times New Roman', 14), fg='#495057').pack(anchor='w', padx=20, pady=5)
    tk.Label(result_frame, text=f"Điểm: {round(score, 2)}/10", bg=FRAME_BG,
            font=('Times New Roman', 14, 'bold'), fg=SUCCESS_BG).pack(anchor='w', padx=20, pady=5)
    tk.Label(result_frame, text=f"Thời gian nộp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", bg=FRAME_BG,
            font=('Times New Roman', 12), fg='#6c757d').pack(anchor='w', padx=20, pady=5)

    def on_enter(e):
        e.widget.config(bg=BUTTON_HOVER)
    def on_leave(e):
        e.widget.config(bg=BUTTON_BG)

    ok_btn = tk.Button(container, text="OK", command=result_window.destroy,
                      bg=BUTTON_BG, fg='white', font=BUTTON_FONT,
                      relief='flat', width=12)
    ok_btn.pack(pady=20)
    ok_btn.bind("<Enter>", on_enter)
    ok_btn.bind("<Leave>", on_leave)

def submit_test(app):
    mon = app.listbox_mon.get(tk.ACTIVE)
    if not mon or mon not in app.test_answers.get(app.current_user, {}):
        messagebox.showwarning("Cảnh báo", "Bạn chưa trả lời câu hỏi nào để nộp bài tập!")
        return

    correct_count = 0
    total_questions = 0
    user_answers = app.test_answers.get(app.current_user, {}).get(mon, {})

    # Duyệt qua tất cả các bài tập trong môn
    for ma_test, test in app.test_data["cau_hoi"].get(mon, {}).items():
        total_questions += len(test.get("cau_hoi", []))
        for cau in test.get("cau_hoi", []):
            idx = str(cau["id"])
            if idx in user_answers:
                if user_answers[idx] == cau["dap_an_dung"]:
                    correct_count += 1

    score = (correct_count / total_questions) * 10 if total_questions > 0 else 0

    # Lưu bài làm vào test_answers
    if app.current_user not in app.test_answers:
        app.test_answers[app.current_user] = {}
    app.test_answers[app.current_user][mon] = {
        "answers": user_answers,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "correct_count": correct_count,
        "total_questions": total_questions,
        "score": round(score, 2)
    }
    app.data_manager.save_user_answers_data(app.test_answers, is_test=True)
    app.logger.info(f"Test submitted for user {app.current_user}, subject {mon}: {app.test_answers[app.current_user][mon]}")

    # Xóa bài làm tạm thời sau khi nộp
    app.test_answers[app.current_user][mon] = {}
    app.data_manager.save_user_answers_data(app.test_answers, is_test=True)
    app.hien_thi_bai_tap_trac_nghiem()

    result_window = tk.Toplevel(app.root)
    result_window.title("Kết quả bài tập")
    result_window.configure(bg=BG_COLOR)
    result_window.geometry("500x350")

    container = tk.Frame(result_window, bg=FRAME_BG, bd=5, relief='flat')
    container.pack(expand=True, padx=10, pady=10)

    tk.Label(container, text="Kết quả bài tập", bg=FRAME_BG,
            font=('Times New Roman', 20, 'bold'), fg='#343a40').pack(pady=20)

    result_frame = tk.Frame(container, bg=FRAME_BG)
    result_frame.pack(pady=20)

    tk.Label(result_frame, text=f"Môn: {mon}", bg=FRAME_BG,
            font=('Times New Roman', 14), fg='#495057').pack(anchor='w', padx=20)
    tk.Label(result_frame, text=f"Số câu đúng: {correct_count}/{total_questions}", bg=FRAME_BG,
            font=('Times New Roman', 14), fg='#495057').pack(anchor='w', padx=20, pady=5)
    tk.Label(result_frame, text=f"Điểm: {round(score, 2)}/10", bg=FRAME_BG,
            font=('Times New Roman', 14, 'bold'), fg=SUCCESS_BG).pack(anchor='w', padx=20, pady=5)
    tk.Label(result_frame, text=f"Thời gian nộp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", bg=FRAME_BG,
            font=('Times New Roman', 12), fg='#6c757d').pack(anchor='w', padx=20, pady=5)

    def on_enter(e):
        e.widget.config(bg=BUTTON_HOVER)
    def on_leave(e):
        e.widget.config(bg=BUTTON_BG)

    ok_btn = tk.Button(container, text="OK", command=result_window.destroy,
                      bg=BUTTON_BG, fg='white', font=BUTTON_FONT,
                      relief='flat', width=12)
    ok_btn.pack(pady=20)
    ok_btn.bind("<Enter>", on_enter)
    ok_btn.bind("<Leave>", on_leave)

def view_user_answers(app):
    if not app.has_permission("view_questions"):
        messagebox.showerror("Lỗi", "Bạn không có quyền xem bài làm của user!")
        return

    users = [u for u in app.account_data["users"] if app.account_data["users"][u]["role"] == "user"]
    if not users:
        messagebox.showinfo("Thông báo", "Không có user nào trong hệ thống!")
        return

    user_window = tk.Toplevel(app.root)
    user_window.title("Chọn User")
    user_window.configure(bg=BG_COLOR)
    user_window.geometry("400x400")

    container = tk.Frame(user_window, bg=FRAME_BG, bd=5, relief='flat')
    container.pack(expand=True, padx=10, pady=10)

    tk.Label(container, text="Chọn user để xem bài làm:", bg=FRAME_BG,
            font=TITLE_FONT, fg='#343a40').pack(pady=20)
    user_var = tk.StringVar(value=users[0])
    user_menu = ttk.Combobox(container, textvariable=user_var, values=users, state="readonly",
                            font=LABEL_FONT, width=20)
    user_menu.pack(pady=10)

    tk.Label(container, text="Chọn loại bài làm:", bg=FRAME_BG,
            font=('Times New Roman', 14), fg='#343a40').pack(pady=20)
    type_var = tk.StringVar(value="practice")
    ttk.Radiobutton(container, text="Ôn thi", variable=type_var, value="practice",
                   style='TRadiobutton', compound='left').pack(pady=5)
    ttk.Radiobutton(container, text="Đề thi", variable=type_var, value="exam",
                   style='TRadiobutton', compound='left').pack(pady=5)

    def show_answers():
        selected_user = user_var.get()
        answer_type = type_var.get()
        user_window.destroy()

        answers_window = tk.Toplevel(app.root)
        answers_window.title(f"Bài làm của {selected_user} ({answer_type})")
        answers_window.configure(bg=BG_COLOR)
        answers_window.geometry("700x500")

        container = tk.Frame(answers_window, bg=FRAME_BG, bd=5, relief='flat')
        container.pack(expand=True, padx=10, pady=10)

        tk.Label(container, text=f"Bài làm của {selected_user} ({answer_type})", bg=FRAME_BG,
                font=TITLE_FONT, fg='#343a40').pack(pady=20)

        text_answers = tk.Text(container, width=80, height=20, wrap=tk.WORD, bg='#e9ecef', fg='#212529',
                              font=TEXT_FONT)
        text_answers.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        if answer_type == "practice":
            user_answers = app.test_answers.get(selected_user, {})
            data = app.test_data
            if not user_answers:
                text_answers.insert(tk.END, f"User {selected_user} chưa trả lời câu hỏi nào trong chế độ ôn thi.\n")
                app.logger.info(f"No practice answers for user {selected_user}.")
            else:
                for mon, answers in user_answers.items():
                    if mon not in data["cau_hoi"]:
                        text_answers.insert(tk.END, f"Môn {mon}: Không tìm thấy câu hỏi.\n")
                        app.logger.warning(f"No questions found for subject {mon}.")
                        continue
                    text_answers.insert(tk.END, f"Môn: {mon}\n")
                    for idx, answer_idx in answers.items():
                        if idx in ["timestamp", "correct_count", "total_questions", "score"]:
                            continue
                        found = False
                        for ma_de, de_thi in data["cau_hoi"][mon].items():
                            for cau in de_thi.get("cau_hoi", []):
                                if str(cau["id"]) == idx:
                                    text_answers.insert(tk.END, f"Câu {idx}: {cau['cau_hoi']}\n")
                                    text_answers.insert(tk.END, f"Đáp án user chọn: {'ABCD'[answer_idx]}. {cau['dap_an'][answer_idx]}\n")
                                    correct_idx = cau['dap_an_dung']
                                    text_answers.insert(tk.END, f"Đáp án đúng: {'ABCD'[correct_idx]}. {cau['dap_an'][correct_idx]}\n")
                                    text_answers.insert(tk.END, "\n")
                                    found = True
                                    break
                            if found:
                                break
                        if not found:
                            text_answers.insert(tk.END, f"Lỗi: Không tìm thấy câu hỏi {idx} trong môn {mon}.\n")
                            app.logger.error(f"Error displaying practice answer for user {selected_user}, subject {mon}, question {idx}.")
        else:
            user_answers = app.exam_answers.get(selected_user, {})
            data = app.exam_data
            if not user_answers:
                text_answers.insert(tk.END, f"User {selected_user} chưa nộp bài thi nào.\n")
                app.logger.info(f"No exam submissions for user {selected_user}.")
            else:
                for mon, submission in user_answers.items():
                    if mon not in data["cau_hoi"]:
                        text_answers.insert(tk.END, f"Môn {mon}: Không tìm thấy câu hỏi.\n")
                        app.logger.warning(f"No questions found for subject {mon}.")
                        continue
                    answers = submission.get("answers", {})
                    timestamp = submission.get("timestamp", "N/A")
                    correct_count = submission.get("correct_count", 0)
                    total_questions = submission.get("total_questions", 0)
                    score = submission.get("score", 0)
                    text_answers.insert(tk.END, f"Môn: {mon} (Nộp lúc: {timestamp})\n")
                    text_answers.insert(tk.END, f"Kết quả: {correct_count}/{total_questions} câu đúng\n")
                    text_answers.insert(tk.END, f"Điểm: {score}/10\n\n")
                    for idx, answer_idx in answers.items():
                        found = False
                        for ma_de, de_thi in data["cau_hoi"][mon].items():
                            for cau in de_thi.get("cau_hoi", []):
                                if str(cau["id"]) == idx:
                                    text_answers.insert(tk.END, f"Câu {idx}: {cau['cau_hoi']}\n")
                                    text_answers.insert(tk.END, f"Đáp án user chọn: {'ABCD'[answer_idx]}. {cau['dap_an'][answer_idx]}\n")
                                    correct_idx = cau['dap_an_dung']
                                    text_answers.insert(tk.END, f"Đáp án đúng: {'ABCD'[correct_idx]}. {cau['dap_an'][correct_idx]}\n")
                                    text_answers.insert(tk.END, "\n")
                                    found = True
                                    break
                            if found:
                                break
                        if not found:
                            text_answers.insert(tk.END, f"Lỗi: Không tìm thấy câu hỏi {idx} trong môn {mon}.\n")
                            app.logger.error(f"Error displaying exam answer for user {selected_user}, subject {mon}, question {idx}.")

        text_answers.config(state='disabled')

        def on_enter(e):
            e.widget.config(bg=BUTTON_HOVER)
        def on_leave(e):
            e.widget.config(bg=BUTTON_BG)

        ok_btn = tk.Button(container, text="OK", command=answers_window.destroy,
                          bg=BUTTON_BG, fg='white', font=BUTTON_FONT,
                          relief='flat', width=12)
        ok_btn.pack(pady=10)
        ok_btn.bind("<Enter>", on_enter)
        ok_btn.bind("<Leave>", on_leave)