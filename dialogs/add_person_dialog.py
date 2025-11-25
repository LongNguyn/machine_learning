import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import threading
from config import APP_CONFIG

class AddPersonDialog:
    """Dialog thêm người mới"""
    def __init__(self, parent, face_service, db, on_success_callback=None):
        self.parent = parent
        self.face_service = face_service
        self.db = db
        self.on_success_callback = on_success_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Thêm người mới")
        self.dialog.geometry("1000x700")
        self.dialog.configure(bg='#f5f5f5')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Xử lý khi đóng dialog
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.cap = None
        self.is_capturing = False
        self.captured_images = []
        self.temp_folder = "temp_captures"
        os.makedirs(self.temp_folder, exist_ok=True)
        
        self.setup_ui()
        self.dialog.after(500, self.start_camera)
    
    def on_close(self):
        """Xử lý khi đóng dialog"""
        self.cleanup()
        self.dialog.destroy()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.dialog, bg='#7c5ceb', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="➕ THÊM NGƯỜI MỚI VÀO HỆ THỐNG", 
                font=("Arial", 18, "bold"), bg='#7c5ceb', fg='white').pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.dialog, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # LEFT - Form
        left_panel = tk.Frame(main_frame, bg='white', width=380)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        form_container = tk.Frame(left_panel, bg='white')
        form_container.pack(fill='both', expand=True, padx=25, pady=25)
        
        tk.Label(form_container, text="THÔNG TIN CÁ NHÂN", 
                font=("Arial", 13, "bold"), bg='white', fg='#2c3e50').pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Họ và tên *", "entry_name"),
            ("Mã nhân viên", "entry_employee_id"),
            ("Phòng ban", "entry_department"),
            ("Chức vụ", "entry_position"),
            ("Email", "entry_email"),
            ("Số điện thoại", "entry_phone"),
        ]
        
        for label, attr in fields:
            tk.Label(form_container, text=label, font=("Arial", 10, "bold"), 
                    bg='white', fg='#555').pack(anchor='w', pady=(0, 5))
            entry = tk.Entry(form_container, font=("Arial", 11), relief='solid',
                           bg='#f8f9fa', bd=1)
            entry.pack(fill='x', pady=(0, 15), ipady=8)
            setattr(self, attr, entry)
        
        # Save button
        btn_save = tk.Button(form_container, text="💾 LƯU THÔNG TIN", 
                           font=("Arial", 12, "bold"), bg='#27ae60', fg='white',
                           relief='flat', cursor='hand2', command=self.save_person,
                           activebackground='#229954')
        btn_save.pack(fill='x', pady=(10, 0), ipady=12)
        
        # RIGHT - Camera
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True)
        
        camera_header = tk.Frame(right_panel, bg='white')
        camera_header.pack(fill='x', pady=15)
        
        tk.Label(camera_header, text="📷 CAMERA CHỤP ẢNH", 
                font=("Arial", 13, "bold"), bg='white', fg='#2c3e50').pack()
        
        self.canvas_camera = tk.Canvas(right_panel, bg='black', width=520, height=380)
        self.canvas_camera.pack(padx=15, pady=10)
        
        # Capture button
        btn_frame = tk.Frame(right_panel, bg='white')
        btn_frame.pack(pady=10)
        
        self.btn_capture = tk.Button(btn_frame, text="📸 CHỤP ẢNH", 
                                    font=("Arial", 12, "bold"), bg='#3498db', fg='white',
                                    relief='flat', cursor='hand2', command=self.capture_image,
                                    activebackground='#2980b9')
        self.btn_capture.pack(ipadx=20, ipady=10)
        
        # Images display
        self.images_label = tk.Label(right_panel, 
            text=f"Đã chụp: {len(self.captured_images)}/{APP_CONFIG['min_images_per_person']}", 
            font=("Arial", 11, "bold"), bg='white', fg='#555')
        self.images_label.pack(pady=(10, 5))
        
        self.images_frame = tk.Frame(right_panel, bg='white')
        self.images_frame.pack(fill='x', padx=15, pady=5)
    
    def start_camera(self):
        self.is_capturing = True
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries and self.cap is None:
            try:
                self.cap = cv2.VideoCapture(0)
                if self.cap.isOpened():
                    print("[INFO] Camera dialog đã sẵn sàng")
                    break
                else:
                    self.cap.release()
                    self.cap = None
                    retry_count += 1
                    print(f"[CẢNH BÁO] Thử lại mở camera lần {retry_count}/{max_retries}")
                    import time
                    time.sleep(0.5)
            except Exception as e:
                print(f"[LỖI] Không thể mở camera: {e}")
                retry_count += 1
                import time
                time.sleep(0.5)
    
        if self.cap is None or not self.cap.isOpened():
            messagebox.showerror("Lỗi", 
                "Không thể mở camera!\nVui lòng kiểm tra:\n"
                "1. Camera đang được sử dụng bởi ứng dụng khác\n"
                "2. Camera đã được kết nối đúng", 
                parent=self.dialog)
            return
    
        threading.Thread(target=self.camera_loop, daemon=True).start()
    
    def camera_loop(self):
        while self.is_capturing:
            if self.cap is None:
                break
            
            try:
                if not self.dialog.winfo_exists():
                    break
                if not self.canvas_camera.winfo_exists():
                    break
            except:
                break
            
            ret, frame = self.cap.read()
            if not ret:
                import time
                time.sleep(0.1)
                continue
            
            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (520, 380))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
                
                if self.canvas_camera.winfo_exists():
                    self.canvas_camera.create_image(0, 0, image=photo, anchor='nw')
                    self.canvas_camera.image = photo
            except tk.TclError:
                break
            except Exception as e:
                if "invalid command name" not in str(e):
                    print(f"[LỖI] camera_loop: {e}")
                break
            
            try:
                if self.dialog.winfo_exists():
                    self.dialog.update_idletasks()
            except:
                break
            
            import time
            time.sleep(0.03)
    
    def capture_image(self):
        if self.cap is None or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if ret:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_service.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    messagebox.showwarning("Cảnh báo", 
                        "Không phát hiện khuôn mặt! Vui lòng đảm bảo khuôn mặt rõ ràng trong khung hình.",
                        parent=self.dialog)
                    return
                
                if len(faces) > 1:
                    messagebox.showwarning("Cảnh báo", 
                        "Phát hiện nhiều khuôn mặt! Vui lòng chỉ có một người trong khung hình.",
                        parent=self.dialog)
                    return
                
                x, y, w, h = faces[0]
                margin = 20
                x_start = max(0, x - margin)
                y_start = max(0, y - margin)
                x_end = min(frame.shape[1], x + w + margin)
                y_end = min(frame.shape[0], y + h + margin)
                
                face_crop = frame[y_start:y_end, x_start:x_end]
                face_resized = cv2.resize(face_crop, (160, 160), interpolation=cv2.INTER_AREA)
                
                timestamp = int(cv2.getTickCount())
                img_path = os.path.join(self.temp_folder, f"capture_{timestamp}.jpg")
                cv2.imwrite(img_path, face_resized)
                self.captured_images.append(img_path)
                
                self.update_images_display()
                messagebox.showinfo("Thành công", 
                    f"Đã chụp ảnh {len(self.captured_images)}/{APP_CONFIG['min_images_per_person']}",
                    parent=self.dialog)
            except Exception as e:
                print(f"[LỖI] capture_image: {e}")
                messagebox.showerror("Lỗi", f"Không thể chụp ảnh: {str(e)}", parent=self.dialog)
    
    def update_images_display(self):
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        self.images_label.config(
            text=f"Đã chụp: {len(self.captured_images)}/{APP_CONFIG['min_images_per_person']}")
        
        for i, img_path in enumerate(self.captured_images[-5:]):
            try:
                img = cv2.imread(img_path)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, (80, 80))
                photo = ImageTk.PhotoImage(image=Image.fromarray(img_resized))
                
                frame = tk.Frame(self.images_frame, bg='white')
                frame.pack(side='left', padx=5)
                
                label = tk.Label(frame, image=photo, bg='white', relief='solid', bd=2)
                label.image = photo
                label.pack()
            except Exception as e:
                print(f"[LỖI] update_images_display: {e}")
    
    def save_person(self):
        full_name = self.entry_name.get().strip()
        
        if not full_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ và tên!", parent=self.dialog)
            return
        
        if len(self.captured_images) < APP_CONFIG['min_images_per_person']:
            messagebox.showerror("Lỗi", 
                f"Cần ít nhất {APP_CONFIG['min_images_per_person']} ảnh! "
                f"Hiện có {len(self.captured_images)} ảnh.", parent=self.dialog)
            return
        
        person_info = {
            'full_name': full_name,
            'employee_id': self.entry_employee_id.get().strip() or None,
            'department': self.entry_department.get().strip() or None,
            'position': self.entry_position.get().strip() or None,
            'email': self.entry_email.get().strip() or None,
            'phone': self.entry_phone.get().strip() or None,
            'notes': None
        }
        
        def run():
            try:
                success, message, person_id = self.face_service.add_person(
                    person_info, self.captured_images)
                
                if success:
                    import time
                    time.sleep(0.5)
                    
                    for img_path in self.captured_images:
                        try:
                            if os.path.exists(img_path):
                                os.remove(img_path)
                        except Exception as e:
                            print(f"[CẢNH BÁO] Không xóa được ảnh tạm {img_path}: {e}")
                    
                    def close_all():
                        self.cleanup()
                        self.dialog.destroy()
                        if self.on_success_callback:
                            self.on_success_callback()
                    
                    self.dialog.after(0, lambda: messagebox.showinfo("Thành công", message, parent=self.dialog))
                    self.dialog.after(100, close_all)
                else:
                    self.dialog.after(0, lambda: messagebox.showerror("Lỗi", message, parent=self.dialog))
            except Exception as e:
                error_msg = f"Lỗi khi thêm người: {str(e)}"
                print(f"[LỖI] {error_msg}")
                import traceback
                traceback.print_exc()
                self.dialog.after(0, lambda: messagebox.showerror("Lỗi", error_msg, parent=self.dialog))
        
        threading.Thread(target=run, daemon=True).start()
        messagebox.showinfo("Đang xử lý", 
            "Đang thêm người mới vào hệ thống...", parent=self.dialog)
    
    def cleanup(self):
        """Dọn dẹp camera và dialog"""
        print("[INFO] Bắt đầu cleanup camera dialog...")
        self.is_capturing = False
        import time
        time.sleep(0.2)
        if self.cap:
            try:
                self.cap.release()
                print("[INFO] Đã release camera dialog")
            except Exception as e:
                print(f"[LỖI] Lỗi khi release camera: {e}")
            finally:
                self.cap = None
        time.sleep(0.3)
    
    def __del__(self):
        self.cleanup()