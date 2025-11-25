import psycopg2
from config import DB_CONFIG
from auth_helper import AuthHelper

def create_tables():
    """Tạo tất cả các bảng trong database"""
    conn = None
    try:
        # Kết nối database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("[INFO] Dang tao cac bang trong database...")
        
        # 1. Bang admin_users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        print("[OK] Da tao bang admin_users")
        
        # 2. Bang persons
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                employee_id VARCHAR(50),
                department VARCHAR(100),
                position VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                notes TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Da tao bang persons")
        
        # 3. Bang person_images
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS person_images (
                id SERIAL PRIMARY KEY,
                person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
                image_path VARCHAR(500) NOT NULL,
                image_quality FLOAT,
                date_captured TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Da tao bang person_images")
        
        # 4. Bang recognition_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recognition_logs (
                id SERIAL PRIMARY KEY,
                person_id INTEGER REFERENCES persons(id) ON DELETE SET NULL,
                identified_name VARCHAR(100),
                confidence FLOAT,
                image_snapshot BYTEA,
                recognition_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Da tao bang recognition_logs")
        
        # 5. Bang system_settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Da tao bang system_settings")
        
        # Tao index de tang hieu suat
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_persons_employee_id ON persons(employee_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_persons_is_active ON persons(is_active)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_person_images_person_id ON person_images(person_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recognition_logs_person_id ON recognition_logs(person_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recognition_logs_time ON recognition_logs(recognition_time)
        """)
        print("[OK] Da tao cac index")
        
        # Commit
        conn.commit()
        print("\n[SUCCESS] Da tao tat ca cac bang thanh cong!")
        
        # Tao tai khoan admin mac dinh neu chua co
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            password_hash = AuthHelper.hash_password("admin123")
            cursor.execute("""
                INSERT INTO admin_users (username, password_hash, full_name, email, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """, ("admin", password_hash, "Administrator", "admin@example.com", True))
            conn.commit()
            print("\n[INFO] Da tao tai khoan admin mac dinh:")
            print("       Username: admin")
            print("       Password: admin123")
            print("       CANH BAO: Vui long doi mat khau sau lan dang nhap dau tien!")
        
        cursor.close()
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"\n[LOI] Khong the tao bang: {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n[LOI] Loi khong xac dinh: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("KHOI TAO DATABASE - HE THONG NHAN DIEN KHUON MAT")
    print("=" * 60)
    print()
    
    success = create_tables()
    
    if success:
        print("\n" + "=" * 60)
        print("HOAN TAT! Ban co the chay ung dung ngay bay gio.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("CO LOI XAY RA! Vui long kiem tra lai cau hinh database.")
        print("=" * 60)

