import unittest
from src.utils.password_validator import validate_password

class TestPasswordValidator(unittest.TestCase):
    def test_valid_password(self):
        result, message = validate_password("Password123!")
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_invalid_length(self):
        result, message = validate_password("Pass1!")
        self.assertFalse(result)
        self.assertEqual(message, "Mật khẩu phải từ 8 đến 16 ký tự!")

    def test_missing_uppercase(self):
        result, message = validate_password("password123!")
        self.assertFalse(result)
        self.assertEqual(message, "Mật khẩu phải chứa ít nhất một chữ cái in hoa!")

if __name__ == '__main__':
    unittest.main()