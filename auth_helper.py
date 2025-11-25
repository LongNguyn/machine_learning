# File: D:\machine_learning\auth_helper.py
import hashlib
import psycopg2
from datetime import datetime
from config import DB_CONFIG

class AuthHelper:
    @staticmethod
    def hash_password(password):
        """Hash password bằng SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_login(username, password):
        """
        Xác thực đăng nhập
        Returns: (success, user_info, message)
        """
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            password_hash = AuthHelper.hash_password(password)
            
            query = """
                SELECT id, username, full_name, email, is_active
                FROM admin_users
                WHERE username = %s AND password_hash = %s
            """
            cursor.execute(query, (username, password_hash))
            result = cursor.fetchone()
            
            if result:
                user_id, username, full_name, email, is_active = result
                
                if not is_active:
                    cursor.close()
                    conn.close()
                    return False, None, "Tài khoản đã bị vô hiệu hóa!"
                
                # Cập nhật thời gian đăng nhập
                cursor.execute("""
                    UPDATE admin_users 
                    SET last_login = %s 
                    WHERE id = %s
                """, (datetime.now(), user_id))
                conn.commit()
                
                user_info = {
                    'id': user_id,
                    'username': username,
                    'full_name': full_name,
                    'email': email
                }
                
                cursor.close()
                conn.close()
                return True, user_info, "Đăng nhập thành công!"
            else:
                cursor.close()
                conn.close()
                return False, None, "Tên đăng nhập hoặc mật khẩu không đúng!"
                
        except Exception as e:
            return False, None, f"Lỗi: {str(e)}"
    
    @staticmethod
    def change_password(username, old_password, new_password):
        """Đổi mật khẩu"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            old_hash = AuthHelper.hash_password(old_password)
            new_hash = AuthHelper.hash_password(new_password)
            
            # Kiểm tra mật khẩu cũ
            cursor.execute("""
                SELECT id FROM admin_users 
                WHERE username = %s AND password_hash = %s
            """, (username, old_hash))
            
            if cursor.fetchone():
                # Cập nhật mật khẩu mới
                cursor.execute("""
                    UPDATE admin_users 
                    SET password_hash = %s 
                    WHERE username = %s
                """, (new_hash, username))
                conn.commit()
                cursor.close()
                conn.close()
                return True, "Đổi mật khẩu thành công!"
            else:
                cursor.close()
                conn.close()
                return False, "Mật khẩu cũ không đúng!"
                
        except Exception as e:
            return False, f"Lỗi: {str(e)}"