import unittest
from src.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.data_manager = DataManager("test_data.json", "test_exam_submissions.json")

    def test_load_data(self):
        data = self.data_manager.load_data()
        self.assertIn("users", data)
        self.assertIn("user_answers", data)

    # Thêm các test case khác

if __name__ == '__main__':
    unittest.main()