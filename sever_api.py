from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Cấu hình Header giả lập trình duyệt di động để tránh bị quét
DEFAULT_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}

def check_facebook_live(cookie):
    """Logic cốt lõi để kiểm tra trạng thái Cookie"""
    try:
        session = requests.Session()
        # Bước 1: Truy cập trang mbasic để lấy thông tin
        response = session.get(
            "https://mbasic.facebook.com/profile.php", 
            headers={**DEFAULT_HEADERS, 'cookie': cookie}, 
            timeout=15
        )
        
        # Bước 2: Phân tích phản hồi
        # Nếu có nút 'Đăng xuất' (logout) trong mã nguồn thì chắc chắn cookie sống
        if "logout.php" in response.text or "mbasic_logout_button" in response.text:
            
            # Tách ID người dùng từ Cookie
            uid_match = re.search(r'c_user=(\d+)', cookie)
            uid = uid_match.group(1) if uid_match else "Unknown"
            
            # Tách Tên người dùng từ thẻ title
            name_match = re.search(r'<title>(.*?)</title>', response.text)
            name = name_match.group(1) if name_match else "Facebook User"
            
            return {
                "status": "success",
                "data": {
                    "id": uid,
                    "name": name,
                    "msg": "Cookie Live"
                }
            }
        
        # Nếu bị chuyển hướng về trang login
        elif "checkpoint" in response.url or "login" in response.url:
            return {"status": "fail", "message": "Cookie bị Checkpoint hoặc đã Logout"}
        
        else:
            return {"status": "fail", "message": "Cookie không hợp lệ hoặc không có quyền truy cập"}

    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Kết nối tới Facebook bị quá hạn (Timeout)"}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}

@app.route('/api/checklive', methods=['GET'])
def api_handler():
    # Lấy tham số cookie từ URL: /api/checklive?cookie=abc...
    cookie_param = request.args.get('cookie')
    
    if not cookie_param:
        return jsonify({"status": "error", "message": "Vui lòng cung cấp tham số 'cookie'"}), 400
    
    result = check_facebook_live(cookie_param)
    return jsonify(result)

if __name__ == "__main__":
    # Chạy server tại port 5000
    print("--- API Check Live Facebook đang khởi chạy ---")
    app.run(host='0.0.0.0', port=5000, debug=False)
