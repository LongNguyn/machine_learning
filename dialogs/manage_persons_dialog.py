import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import threading

class ManagePersonsDialog:
    """Dialog quản lý đối tượng"""
    def __init__(self, parent, face_service, db, main_app=None):
        self.parent = parent
        self.face_service = face_service
        self.db = db
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Quản lý đối tượng")
        self.dialog.geometry("1000x700")
        self.dialog.configure(bg='#f5f5f5')
        self.dialog.transient(parent)
        
        # Center window
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 500
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 350
        self.dialog.geometry(f"1000x700+{x}+{y}")
        
        self.selected_person = None
        self.setup_ui()
        self.load_persons()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.dialog, bg='#7c5ceb', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="👥 QUẢN LÝ ĐỐI TƯỢNG", 
                font=("Arial", 20, "bold"), bg='#7c5ceb', fg='white').pack(pady=25)
        
        # Main content
        main_frame = tk.Frame(self.dialog, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # LEFT - List
        left_panel = tk.Frame(main_frame, bg='white', width=400)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Search frame
        search_frame = tk.Frame(left_panel, bg='white')
        search_frame.pack(fill='x', padx=15, pady=15)
        
        tk.Label(search_frame, text="🔍 Tìm kiếm", 
                font=("Arial", 11, "bold"), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 8))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_persons())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=("Arial", 11), relief='solid', bg='#f8f9fa', bd=1)
        search_entry.pack(fill='x', ipady=8)
        
        # List frame
        list_frame = tk.Frame(left_panel, bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.listbox = tk.Listbox(list_frame, font=("Arial", 11), 
                                 bg='#f8f9fa', selectbackground='#7c5ceb',
                                 yscrollcommand=scrollbar.set, relief='solid', bd=1)
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_person)
        scrollbar.config(command=self.listbox.yview)
        
        # RIGHT - Details
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Details header
        details_header = tk.Frame(right_panel, bg='#7c5ceb', height=60)
        details_header.pack(fill='x')
        details_header.pack_propagate(False)
        
        self.details_title = tk.Label(details_header, text="CHI TIẾT ĐỐI TƯỢNG", 
                                     font=("Arial", 14, "bold"), bg='#7c5ceb', fg='white')
        self.details_title.pack(pady=18)
        
        # Details content
        self.details_frame = tk.Frame(right_panel, bg='white')
        self.details_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Buttons frame
        buttons_frame = tk.Frame(right_panel, bg='white')
        buttons_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        self.btn_edit = tk.Button(buttons_frame, text="✏️ SỬA", 
                                 font=("Arial", 11, "bold"), bg='#3498db', fg='white',
                                 relief='flat', cursor='hand2', command=self.edit_person,
                                 activebackground='#2980b9', state='disabled')
        self.btn_edit.pack(side='left', padx=(0, 10), ipadx=15, ipady=10)
        
        self.btn_delete = tk.Button(buttons_frame, text="🗑️ XÓA", 
                                    font=("Arial", 11, "bold"), bg='#e74c3c', fg='white',
                                    relief='flat', cursor='hand2', command=self.delete_person,
                                    activebackground='#c0392b', state='disabled')
        self.btn_delete.pack(side='left', padx=(0, 10), ipadx=15, ipady=10)
        
        self.btn_refresh = tk.Button(buttons_frame, text="🔄 LÀM MỚI", 
                                     font=("Arial", 11, "bold"), bg='#95a5a6', fg='white',
                                     relief='flat', cursor='hand2', command=self.load_persons,
                                     activebackground='#7f8c8d')
        self.btn_refresh.pack(side='right', ipadx=15, ipady=10)
        
        self.show_empty_state()
    
    def load_persons(self):
        """Load danh sách người"""
        search_text = self.search_var.get().strip()
        persons = self.db.get_all_persons(search_text=search_text if search_text else None)
        
        self.listbox.delete(0, tk.END)
        self.persons_data = persons
        
        for person in persons:
            name = person['full_name']
            emp_id = person.get('employee_id') or 'N/A'
            image_count = person.get('image_count', 0)
            display_text = f"{name} | Mã: {emp_id} | Ảnh: {image_count}"
            self.listbox.insert(tk.END, display_text)
        
        if len(persons) == 0:
            self.show_empty_state()
    
    def on_select_person(self, event):
        """Khi chọn một người"""
        selection = self.listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.persons_data):
            self.selected_person = self.persons_data[index]
            self.show_person_details(self.selected_person)
            self.btn_edit.config(state='normal')
            self.btn_delete.config(state='normal')
    
    def show_empty_state(self):
        """Hiển thị trạng thái trống"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.details_frame, text="Chọn một đối tượng để xem chi tiết", 
                font=("Arial", 12), bg='white', fg='#999').pack(pady=50)
        self.selected_person = None
        self.btn_edit.config(state='disabled')
        self.btn_delete.config(state='disabled')
    
    def show_person_details(self, person):
        """Hiển thị chi tiết người"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Photo
        photo_frame = tk.Frame(self.details_frame, bg='white')
        photo_frame.pack(pady=(0, 20))
        
        images = self.db.get_person_images(person['id'])
        photo_label = tk.Label(photo_frame, bg='#e0e0e0', text="Không có ảnh", 
                              font=("Arial", 11), fg='#999', width=30, height=12)
        photo_label.pack()
        
        if images and len(images) > 0:
            try:
                img_path = images[0]['image_path']
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_pil = img_pil.resize((240, 300), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=img_pil)
                    photo_label.config(image=photo, text="")
                    photo_label.image = photo
            except Exception as e:
                print(f"[LỖI] Load ảnh: {e}")
        
        # Info fields
        info_frame = tk.Frame(self.details_frame, bg='white')
        info_frame.pack(fill='x')
        
        fields = [
            ("Họ và tên", person.get('full_name') or 'Chưa có'),
            ("Mã nhân viên", person.get('employee_id') or 'Chưa có'),
            ("Phòng ban", person.get('department') or 'Chưa có'),
            ("Chức vụ", person.get('position') or 'Chưa có'),
            ("Email", person.get('email') or 'Chưa có'),
            ("Số điện thoại", person.get('phone') or 'Chưa có'),
            ("Số ảnh", str(person.get('image_count', 0))),
            ("Ngày thêm", person.get('date_added').strftime('%d/%m/%Y %H:%M') if person.get('date_added') else 'N/A'),
        ]
        
        for label, value in fields:
            field_frame = tk.Frame(info_frame, bg='white')
            field_frame.pack(fill='x', pady=8)
            
            tk.Label(field_frame, text=f"{label}:", font=("Arial", 10, "bold"), 
                    bg='white', fg='#555', width=15, anchor='w').pack(side='left')
            tk.Label(field_frame, text=str(value), font=("Arial", 10), 
                    bg='white', fg='#2c3e50', anchor='w').pack(side='left', fill='x', expand=True)
    
    def edit_person(self):
        """Sửa thông tin người"""
        if not self.selected_person:
            return
        
        from dialogs.edit_person_dialog import EditPersonDialog
        EditPersonDialog(self.dialog, self.selected_person, self.db, self)
    
    def delete_person(self):
        """Xóa người - SỬA LẠI"""
        if not self.selected_person:
            return
        
        name = self.selected_person['full_name']
        result = messagebox.askyesno("Xác nhận xóa", 
                                    f"Bạn có chắc chắn muốn xóa đối tượng '{name}'?\n\n"
                                    "Hành động này sẽ xóa:\n"
                                    "- Thông tin trong database\n"
                                    "- Tất cả ảnh đã lưu\n"
                                    "- Embeddings liên quan\n\n"
                                    "Hành động này không thể hoàn tác!",
                                    parent=self.dialog)
        
        if result:
            def run_delete():
                try:
                    # Xóa trong database
                    db_success = self.db.delete_person(self.selected_person['id'])
                    # Xóa thư mục ảnh và embeddings
                    data_success = self.face_service.delete_person_data(name)
                    
                    if db_success and data_success:
                        self.dialog.after(0, lambda: messagebox.showinfo(
                            "Thành công", f"Đã xóa đối tượng '{name}'", parent=self.dialog))
                        
                        # QUAN TRỌNG: Đánh dấu cần reload embeddings
                        if self.main_app:
                            self.dialog.after(0, lambda: self.update_main_app())
                            # THÊM: Đánh dấu cần reload embeddings ngay lập tức
                            self.main_app.need_reload_embeddings = True
                        
                        self.dialog.after(0, self.load_persons)
                        self.dialog.after(0, self.show_empty_state)
                    else:
                        self.dialog.after(0, lambda: messagebox.showerror(
                            "Lỗi", "Không thể xóa đối tượng hoàn toàn", parent=self.dialog))
                except Exception as e:
                    error_msg = f"Lỗi khi xóa: {str(e)}"
                    print(f"[LỖI] {error_msg}")
                    import traceback
                    traceback.print_exc()
                    self.dialog.after(0, lambda: messagebox.showerror(
                        "Lỗi", error_msg, parent=self.dialog))
            
            threading.Thread(target=run_delete, daemon=True).start()
            messagebox.showinfo("Đang xử lý", "Đang xóa đối tượng...", parent=self.dialog)
    
    def update_main_app(self):
        """Cập nhật main app sau khi xóa"""
        if self.main_app:
            total_persons = len(self.db.get_all_persons())
            self.main_app.counter_label.config(text=str(total_persons))
            # Đánh dấu cần reload embeddings
            self.main_app.need_reload_embeddings = True