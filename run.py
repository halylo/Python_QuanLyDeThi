import tkinter as tk
from src.main import main

if __name__ == "__main__":
    try:
        root = tk.Tk()
        main(root)
        root.mainloop()
    except Exception as e:
        print(f"Lỗi khi khởi động ứng dụng: {str(e)}")