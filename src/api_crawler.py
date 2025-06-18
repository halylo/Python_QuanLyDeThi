import requests
from tkinter import messagebox
import logging
import random
from datetime import datetime, timedelta
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def crawl_data_from_api(app, is_test=False):
    """
    Crawl dữ liệu từ Open Trivia Database API và cập nhật dữ liệu đề thi hoặc bài tập.

    Args:
        app: QuizApp instance
        is_test: Boolean chỉ định crawl cho bài tập (True) hoặc đề thi (False)
    """
    if not app.current_user or app.account_data["users"][app.current_user]["role"] != "admin":
        messagebox.showerror("Lỗi", "Chỉ admin mới có quyền crawl dữ liệu!")
        return

    logger = logging.getLogger(__name__)
    base_url = "https://opentdb.com/api.php?amount=10&category=17&type=multiple"  # Category 17: Khoa học & Tự nhiên (gần với Kinh tế)
    data_type = "bài tập" if is_test else "đề thi"

    try:
        logger.info(f"Bắt đầu crawl dữ liệu {data_type} từ: {base_url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        api_data = response.json()

        if api_data["response_code"] != 0:
            logger.error(f"Lỗi API OpenTDB, mã phản hồi: {api_data['response_code']}")
            messagebox.showerror("Lỗi", f"Lỗi API: Mã phản hồi {api_data['response_code']}")
            return

        # Chọn dữ liệu mục tiêu
        target_data = app.test_data if is_test else app.exam_data
        mon_thi = "Kinh tế Chính trị"  # Có thể thay bằng tên môn khác nếu cần

        # Thêm môn nếu chưa tồn tại
        if mon_thi not in [m["ten_mon"] for m in target_data["mon_thi"]]:
            ma_mon = f"M{len(target_data['mon_thi']) + 1:03d}"
            target_data["mon_thi"].append({
                "ma_mon": ma_mon,
                "ten_mon": mon_thi,
                "han_nop_bai": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d") if is_test else None
            })
            target_data["cau_hoi"][mon_thi] = {}
            logger.debug(f"Thêm môn mới: {mon_thi} (Mã: {ma_mon})")

        # Tạo đề mới
        ma_de = f"DE{len(target_data['cau_hoi'][mon_thi]) + 1:03d}"
        ten_de = f"{'Bài tập' if is_test else 'Đề thi'} {mon_thi} từ OpenTDB"
        de_info = {
            "ten_de": ten_de,
            "cau_hoi": []
        }
        if is_test:
            de_info["ngay_den_han"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            de_info["thoi_gian_lam_bai"] = 60
        target_data["cau_hoi"][mon_thi][ma_de] = de_info
        logger.debug(f"Tạo đề mới: {ten_de} (Mã: {ma_de})")

        # Xử lý câu hỏi
        for idx, question in enumerate(api_data["results"], 1):
            if not all(k in question for k in ["question", "correct_answer", "incorrect_answers"]):
                logger.warning(f"Bỏ qua câu {idx}: Dữ liệu không đầy đủ")
                continue

            dap_an = question["incorrect_answers"] + [question["correct_answer"]]
            random.shuffle(dap_an)
            dap_an_dung = dap_an.index(question["correct_answer"])

            cau_hoi = {
                "id": idx,
                "cau_hoi": question["question"],
                "dap_an": dap_an,
                "dap_an_dung": dap_an_dung
            }
            target_data["cau_hoi"][mon_thi][ma_de]["cau_hoi"].append(cau_hoi)
            logger.debug(f"Thêm câu hỏi {idx}: {question['question'][:50]}...")

        if not target_data["cau_hoi"][mon_thi][ma_de]["cau_hoi"]:
            logger.error(f"Không crawl được câu hỏi hợp lệ nào cho {data_type}")
            messagebox.showerror("Lỗi", f"Không crawl được câu hỏi nào cho {data_type}!")
            return

        # Lưu dữ liệu
        app.data_manager.save_data(target_data, is_test=is_test)
        logger.info(f"Đã crawl và lưu dữ liệu {data_type} thành công")
        messagebox.showinfo("Thành công", f"Đã crawl dữ liệu {data_type} thành công!")
        app.cap_nhat_danh_sach_mon()

    except requests.exceptions.HTTPError as e:
        logger.error(f"Lỗi HTTP: {str(e)}")
        messagebox.showerror("Lỗi", f"Lỗi HTTP: {str(e)}")
    except requests.exceptions.ConnectionError:
        logger.error("Lỗi kết nối mạng")
        messagebox.showerror("Lỗi", "Không thể kết nối đến API. Kiểm tra mạng.")
    except requests.exceptions.Timeout:
        logger.error("Yêu cầu hết thời gian chờ")
        messagebox.showerror("Lỗi", "Yêu cầu hết thời gian chờ. Thử lại sau.")
    except Exception as e:
        logger.error(f"Lỗi không xác định: {str(e)}")
        messagebox.showerror("Lỗi", f"Lỗi khi crawl dữ liệu {data_type}: {str(e)}")