import tkinter as tk
from tkinter import messagebox

class EditPersonDialog:
    """Dialog sửa thông tin người"""
    def __init__(self, parent, person, db, manage_dialog):
        self.parent = parent
        self.person = person
        self.db = db
        self.manage_dialog = manage_dialog
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Sửa thông tin")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg='#f5f5f5')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
        self.dialog.geometry(f"500x600+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.dialog, bg='#7c5ceb', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="✏️ SỬA THÔNG TIN", 
                font=("Arial", 16, "bold"), bg='#7c5ceb', fg='white').pack(pady=20)
        
        # Form
        form_frame = tk.Frame(self.dialog, bg='white')
        form_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(form_frame, text="THÔNG TIN CÁ NHÂN", 
                font=("Arial", 12, "bold"), bg='white', fg='#2c3e50').pack(pady=(0, 20))
        
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
            tk.Label(form_frame, text=label, font=("Arial", 10, "bold"), 
                    bg='white', fg='#555').pack(anchor='w', pady=(0, 5))
            entry = tk.Entry(form_frame, font=("Arial", 11), relief='solid',
                           bg='#f8f9fa', bd=1)
            entry.pack(fill='x', pady=(0, 15), ipady=8)
            setattr(self, attr, entry)
        
        # Fill data
        self.entry_name.insert(0, self.person.get('full_name') or '')
        self.entry_employee_id.insert(0, self.person.get('employee_id') or '')
        self.entry_department.insert(0, self.person.get('department') or '')
        self.entry_position.insert(0, self.person.get('position') or '')
        self.entry_email.insert(0, self.person.get('email') or '')
        self.entry_phone.insert(0, self.person.get('phone') or '')
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', pady=(20, 0))
        
        btn_save = tk.Button(btn_frame, text="💾 LƯU", 
                           font=("Arial", 11, "bold"), bg='#27ae60', fg='white',
                           relief='flat', cursor='hand2', command=self.save_changes,
                           activebackground='#229954')
        btn_save.pack(side='left', padx=(0, 10), ipadx=20, ipady=10)
        
        btn_cancel = tk.Button(btn_frame, text="Hủy", 
                             font=("Arial", 11), bg='#95a5a6', fg='white',
                             relief='flat', cursor='hand2', command=self.dialog.destroy,
                             activebackground='#7f8c8d')
        btn_cancel.pack(side='left', ipadx=20, ipady=10)
    
    def save_changes(self):
        """Lưu thay đổi"""
        full_name = self.entry_name.get().strip()
        
        if not full_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ và tên!", parent=self.dialog)
            return
        
        update_data = {
            'full_name': full_name,
            'employee_id': self.entry_employee_id.get().strip() or None,
            'department': self.entry_department.get().strip() or None,
            'position': self.entry_position.get().strip() or None,
            'email': self.entry_email.get().strip() or None,
            'phone': self.entry_phone.get().strip() or None,
        }
        
        success = self.db.update_person(self.person['id'], **update_data)
        
        if success:
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin thành công!", parent=self.dialog)
            self.dialog.destroy()
            # Reload danh sách
            self.manage_dialog.load_persons()
            # Cập nhật lại chi tiết nếu đang chọn người này
            if self.manage_dialog.selected_person and self.manage_dialog.selected_person['id'] == self.person['id']:
                updated_person = self.db.get_person_by_id(self.person['id'])
                if updated_person:
                    images = self.db.get_person_images(self.person['id'])
                    updated_person['image_count'] = len(images)
                    self.manage_dialog.show_person_details(updated_person)
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật thông tin!", parent=self.dialog)