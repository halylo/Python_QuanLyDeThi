import re

def validate_password(password):
    if not (8 <= len(password) <= 16):
        return False, "Mật khẩu phải từ 8 đến 16 ký tự!"
    if not re.search(r"[A-Z]", password):
        return False, "Mật khẩu phải chứa ít nhất một chữ cái in hoa!"
    if not re.search(r"[a-z]", password):
        return False, "Mật khẩu phải chứa ít nhất một chữ cái thường!"
    if not re.search(r"[0-9]", password):
        return False, "Mật khẩu phải chứa ít nhất một số!"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Mật khẩu phải chứa ít nhất một ký tự đặc biệt!"
    return True, ""