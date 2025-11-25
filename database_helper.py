import psycopg2
from psycopg2 import pool
from datetime import datetime
from config import DB_CONFIG

class DatabaseHelper:
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Khởi tạo connection pool"""
        try:
            self._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,  # min và max connections
                **DB_CONFIG
            )
            print("[INFO] Kết nối database thành công!")
        except Exception as e:
            print(f"[LỖI] Không thể kết nối database: {e}")
            raise
    
    def get_connection(self):
        """Lấy connection từ pool"""
        return self._connection_pool.getconn()
    
    def return_connection(self, conn):
        """Trả connection về pool"""
        self._connection_pool.putconn(conn)
    
    # ==================== PERSONS ====================
    
    def add_person(self, full_name, employee_id=None, department=None, 
                   position=None, email=None, phone=None, notes=None):
        """Thêm người mới"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO persons (full_name, employee_id, department, position, email, phone, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            cursor.execute(query, (full_name, employee_id, department, position, email, phone, notes))
            person_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return person_id
        except Exception as e:
            conn.rollback()
            print(f"[LỖI] add_person: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def get_all_persons(self, search_text=None):
        """Lấy danh sách tất cả người"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.*, COUNT(pi.id) as image_count
                FROM persons p
                LEFT JOIN person_images pi ON p.id = pi.person_id
                WHERE p.is_active = TRUE
            """
            
            if search_text:
                query += " AND (p.full_name ILIKE %s OR p.employee_id ILIKE %s)"
                search_pattern = f"%{search_text}%"
                cursor.execute(query + " GROUP BY p.id ORDER BY p.date_added DESC", 
                             (search_pattern, search_pattern))
            else:
                cursor.execute(query + " GROUP BY p.id ORDER BY p.date_added DESC")
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            return results
        except Exception as e:
            print(f"[LỖI] get_all_persons: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def get_person_by_id(self, person_id):
        """Lấy thông tin người theo ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM persons WHERE id = %s"
            cursor.execute(query, (person_id,))
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            return dict(zip(columns, row)) if row else None
        except Exception as e:
            print(f"[LỖI] get_person_by_id: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def update_person(self, person_id, **kwargs):
        """Cập nhật thông tin người"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            fields = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(person_id)
            
            query = f"UPDATE persons SET {fields} WHERE id = %s"
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[LỖI] update_person: {e}")
            return False
        finally:
            self.return_connection(conn)
    
    def delete_person(self, person_id):
        """Xóa người (soft delete)"""
        return self.update_person(person_id, is_active=False)
    
    # ==================== PERSON IMAGES ====================
    
    def add_person_image(self, person_id, image_path, image_quality):
        """Thêm ảnh cho người"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO person_images (person_id, image_path, image_quality)
                VALUES (%s, %s, %s)
                RETURNING id
            """
            cursor.execute(query, (person_id, image_path, image_quality))
            image_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return image_id
        except Exception as e:
            conn.rollback()
            print(f"[LỖI] add_person_image: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def get_person_images(self, person_id):
        """Lấy danh sách ảnh của người"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM person_images WHERE person_id = %s ORDER BY date_captured DESC"
            cursor.execute(query, (person_id,))
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()
            return results
        except Exception as e:
            print(f"[LỖI] get_person_images: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    # ==================== RECOGNITION LOGS ====================
    
    def add_recognition_log(self, person_id, identified_name, confidence, image_snapshot=None):
        """Thêm log nhận diện"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO recognition_logs (person_id, identified_name, confidence, image_snapshot)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (person_id, identified_name, confidence, image_snapshot))
            conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            print(f"[LỖI] add_recognition_log: {e}")
        finally:
            self.return_connection(conn)
    
    def get_recognition_logs(self, limit=100, person_id=None, from_date=None, to_date=None):
        """Lấy lịch sử nhận diện"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT rl.*, p.full_name, p.employee_id
                FROM recognition_logs rl
                LEFT JOIN persons p ON rl.person_id = p.id
                WHERE 1=1
            """
            params = []
            
            if person_id:
                query += " AND rl.person_id = %s"
                params.append(person_id)
            
            if from_date:
                query += " AND rl.recognition_time >= %s"
                params.append(from_date)
            
            if to_date:
                query += " AND rl.recognition_time <= %s"
                params.append(to_date)
            
            query += " ORDER BY rl.recognition_time DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()
            return results
        except Exception as e:
            print(f"[LỖI] get_recognition_logs: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    # ==================== SYSTEM SETTINGS ====================
    
    def get_setting(self, setting_key):
        """Lấy giá trị setting"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT setting_value FROM system_settings WHERE setting_key = %s"
            cursor.execute(query, (setting_key,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            print(f"[LỖI] get_setting: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def set_setting(self, setting_key, setting_value):
        """Cập nhật setting"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO system_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON CONFLICT (setting_key) DO UPDATE SET setting_value = %s
            """
            cursor.execute(query, (setting_key, setting_value, setting_value))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[LỖI] set_setting: {e}")
            return False
        finally:
            self.return_connection(conn)
    
    def close(self):
        """Đóng connection pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            print("[INFO] Đã đóng connection pool")