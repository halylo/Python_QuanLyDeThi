import json
import os

class DataManager:
    def __init__(self, data_filename="data.json", test_filename="test_questions.json", 
                 account_filename="account.json", exam_answers_filename="answers_exam.json", 
                 test_answers_filename="answers_test.json"):
        self.data_filename = data_filename
        self.test_filename = test_filename
        self.account_filename = account_filename
        self.exam_answers_filename = exam_answers_filename
        self.test_answers_filename = test_answers_filename
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def load_data(self, is_test=False):
        filename = self.test_filename if is_test else self.data_filename
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not is_test and isinstance(data.get("mon_thi", []), list):
                    if data["mon_thi"] and isinstance(data["mon_thi"][0], str):
                        data["mon_thi"] = [
                            {"ma_mon": f"T{i+1:03d}", "ten_mon": mon}
                            for i, mon in enumerate(data["mon_thi"])
                        ]
                        for mon in data["mon_thi"]:
                            ten_mon = mon["ten_mon"]
                            if ten_mon in data["cau_hoi"] and isinstance(data["cau_hoi"][ten_mon], list):
                                data["cau_hoi"][ten_mon] = {
                                    f"BT{mon['ma_mon'][1:]}": {
                                        "ten_de": f"Đề thi {ten_mon}",
                                        "thoi_gian_lam_bai": 60,
                                        "cau_hoi": data["cau_hoi"][ten_mon]
                                    }
                                }
                        self.save_data(data, is_test=is_test)
                return data
        except FileNotFoundError:
            default_data = self.get_default_data(is_test=is_test)
            self.save_data(default_data, is_test=is_test)
            return default_data
        except json.JSONDecodeError:
            default_data = self.get_default_data(is_test=is_test)
            self.save_data(default_data, is_test=is_test)
            return default_data

    def load_user_answers_data(self, is_test=False):
        filename = self.test_answers_filename if is_test else self.exam_answers_filename
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = {}
            self.save_user_answers_data(default_data, is_test)
            return default_data

    def get_default_data(self, is_test=False):
        return {
            "mon_thi": [
                {"ma_mon": "T001", "ten_mon": "Bảo mật máy tính"},
                {"ma_mon": "T002", "ten_mon": "Lập trình Python"},
                {"ma_mon": "T003", "ten_mon": "Mạng máy tính"},
                {"ma_mon": "T004", "ten_mon": "Cơ sở dữ liệu"},
                {"ma_mon": "T005", "ten_mon": "Khoa học Máy tính"},
                {"ma_mon": "T006", "ten_mon": "Anh văn 3"}
            ],
            "cau_hoi": {
                "Bảo mật máy tính": {},
                "Lập trình Python": {},
                "Mạng máy tính": {},
                "Cơ sở dữ liệu": {},
                "Khoa học Máy tính": {},
                "Anh văn 3": {}
            }
        }

    def save_data(self, data, is_test=False):
        filename = self.test_filename if is_test else self.data_filename
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_user_answers_data(self, data, is_test=False):
        filename = self.test_answers_filename if is_test else self.exam_answers_filename
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_account_data(self):
        filepath = os.path.join(self.data_dir, self.account_filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = {
                "users": {
                    "admin": {"password": "admin123", "role": "admin"}
                }
            }
            self.save_account_data(default_data)
            return default_data

    def save_account_data(self, data):
        filepath = os.path.join(self.data_dir, self.account_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)