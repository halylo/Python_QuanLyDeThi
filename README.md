# 🎯 Quiz App - Hệ thống Quản lý Đề Thi & Trắc Nghiệm

## 📌 Giới thiệu

Đây là ứng dụng desktop được xây dựng bằng **Python + Tkinter** nhằm hỗ trợ:

* Quản lý đề thi trắc nghiệm
* Làm bài thi và bài tập
* Quản lý tài khoản người dùng
* Tự động crawl câu hỏi từ API

Ứng dụng phù hợp cho mục đích học tập và thực hành trong lĩnh vực **Công nghệ thông tin / Trí tuệ nhân tạo**

---

## 🚀 Tính năng chính

### 👤 Người dùng

* Đăng nhập hệ thống
* Chọn chế độ:

  * 📝 Làm đề thi
  * 📚 Làm bài tập
* Làm bài trắc nghiệm
* Xem kết quả và điểm số

### 🛠️ Admin

* Quản lý môn học & đề thi
* Thêm / sửa / xóa câu hỏi
* Tạo tài khoản người dùng
* Crawl dữ liệu câu hỏi từ API

---

## 🧠 Công nghệ sử dụng

* Python 🐍
* Tkinter (GUI)
* JSON (lưu dữ liệu)
* Open Trivia API
* Matplotlib

---

## 📂 Cấu trúc project

.
├── run.py
├── main.py
├── src/
│   ├── quiz_app.py
│   ├── data_manager.py
│   ├── api_crawler.py
│   ├── ui/
│   │   ├── login_ui.py
│   │   ├── main_ui.py
│   │   ├── account_ui.py
│   │   ├── result_ui.py
│   │   └── mode_selection_ui.py
├── data/

---

## ▶️ Cách chạy project

### 1. Cài thư viện

pip install requests matplotlib tkcalendar pillow

### 2. Chạy chương trình

python run.py

---

## 🔑 Tài khoản mặc định

username: admin
password: admin123

---

## 📊 Luồng hoạt động

1. Người dùng đăng nhập
2. Chọn chế độ (Exam / Practice)
3. Làm bài trắc nghiệm
4. Hệ thống chấm điểm tự động
5. Lưu kết quả vào file JSON

---

## 🌐 API sử dụng

https://opentdb.com/api.php

---

## 💾 Lưu trữ dữ liệu

* data.json → đề thi
* test_questions.json → bài tập
* account.json → tài khoản
* answers_exam.json → kết quả thi
* answers_test.json → kết quả bài tập

---

## ⚠️ Lưu ý

* Chỉ admin mới có quyền crawl dữ liệu
* Dữ liệu lưu local (JSON)
* Không sử dụng database

---

## 📸 Demo
<img width="1201" height="900" alt="image" src="https://github.com/user-attachments/assets/48d58481-ef7b-4deb-87d9-6f9e72bef793" />
<img width="1152" height="788" alt="image" src="https://github.com/user-attachments/assets/117fa3af-cab8-4323-ad1d-23c8af0ca21f" />

---

## 👨‍💻 Tác giả

* Phùng Thị Ly (IT Student)

---

## ⭐ Định hướng phát triển

* Kết nối database (MySQL / MongoDB)
* Phát triển web version (Django / Flask)
* Tích hợp AI gợi ý câu hỏi


