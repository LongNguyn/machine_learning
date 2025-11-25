import tkinter as tk
from tkinter import messagebox
from auth_helper import AuthHelper

class LoginDialog:
    """Dialog đăng nhập"""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Đăng nhập Admin")
        self.dialog.geometry("450x550")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#7c5ceb')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center window
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (450 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (550 // 2)
        self.dialog.geometry(f"450x550+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Logo
        logo_frame = tk.Frame(self.dialog, bg='#7c5ceb')
        logo_frame.pack(pady=50)
        
        tk.Label(logo_frame, text="🔒", font=("Arial", 60), bg='#7c5ceb', fg='white').pack()
        tk.Label(logo_frame, text="ĐĂNG NHẬP QUẢN TRỊ", font=("Arial", 20, "bold"), 
                bg='#7c5ceb', fg='white').pack(pady=15)
        tk.Label(logo_frame, text="Để quản lý hệ thống", font=("Arial", 11), 
                bg='#7c5ceb', fg='#e0d4ff').pack()
        
        # Form
        form_frame = tk.Frame(self.dialog, bg='white', padx=40, pady=40)
        form_frame.pack(pady=20, padx=40, fill='x')
        
        # Username
        tk.Label(form_frame, text="Tên đăng nhập", font=("Arial", 11, "bold"), 
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 8))
        self.entry_username = tk.Entry(form_frame, font=("Arial", 12), 
                                      relief='solid', bg='#f8f9fa', fg='#2c3e50',
                                      bd=1, insertbackground='#7c5ceb')
        self.entry_username.pack(fill='x', ipady=10)
        self.entry_username.insert(0, "admin")
        self.entry_username.focus()
        
        # Password
        tk.Label(form_frame, text="Mật khẩu", font=("Arial", 11, "bold"), 
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(20, 8))
        self.entry_password = tk.Entry(form_frame, font=("Arial", 12), 
                                       show='●', relief='solid', bg='#f8f9fa', 
                                       fg='#2c3e50', bd=1, insertbackground='#7c5ceb')
        self.entry_password.pack(fill='x', ipady=10)
        self.entry_password.bind('<Return>', lambda e: self.login())
        
        # Buttons
        btn_login = tk.Button(form_frame, text="ĐĂNG NHẬP", font=("Arial", 12, "bold"),
                             bg='#7c5ceb', fg='white', relief='flat', cursor='hand2',
                             command=self.login, activebackground='#6a4cd9')
        btn_login.pack(fill='x', pady=(30, 0), ipady=12)
        
        btn_cancel = tk.Button(form_frame, text="Hủy", font=("Arial", 11),
                             bg='#95a5a6', fg='white', relief='flat', cursor='hand2',
                             command=self.dialog.destroy, activebackground='#7f8c8d')
        btn_cancel.pack(fill='x', pady=(12, 0), ipady=10)
    
    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!", parent=self.dialog)
            return
        
        success, user_info, message = AuthHelper.verify_login(username, password)
        
        if success:
            self.dialog.destroy()
            if self.callback:
                self.callback(user_info)
        else:
            messagebox.showerror("Lỗi đăng nhập", message, parent=self.dialog)
            self.entry_password.delete(0, 'end')