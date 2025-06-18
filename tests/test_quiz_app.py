import unittest
import tkinter as tk
from src.quiz_app import QuizApp

class TestQuizApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = QuizApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        self.assertEqual(self.app.root.title(), "Ứng dụng Ôn Thi")

    # Thêm các test case khác

if __name__ == '__main__':
    unittest.main()