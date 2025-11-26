import tkinter as tk
from tkinter import ttk

class ScrollableFrame(tk.Frame):
    """
    Frame có thể scroll với con lăn chuột
    Sử dụng cho các dialog cần scroll
    """
    def __init__(self, parent, bg='white', **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        
        # Tạo canvas
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        
        # Tạo scrollbar với style đẹp
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Vertical.TScrollbar", 
                       gripcount=0,
                       background="#7c5ceb",
                       darkcolor="#5940c9",
                       lightcolor="#9b7ef5",
                       troughcolor="#f0f0f0",
                       bordercolor="#7c5ceb",
                       arrowcolor="white",
                       width=12)
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", 
                                       command=self.canvas.yview,
                                       style="Custom.Vertical.TScrollbar")
        
        # Frame chứa nội dung
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg)
        
        # Bind để update scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Tạo window trong canvas
        self.canvas_frame = self.canvas.create_window((0, 0), 
                                                      window=self.scrollable_frame,
                                                      anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar và canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mouse wheel cho canvas và frame
        self._bind_mouse_wheel(self.canvas)
        self._bind_mouse_wheel(self.scrollable_frame)
        
        # Bind để update canvas width khi resize
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_canvas_configure(self, event):
        """Update width của frame trong canvas khi resize"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
    
    def _bind_mouse_wheel(self, widget):
        """Bind mouse wheel cho widget và tất cả children"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        widget.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind cho tất cả children
        for child in widget.winfo_children():
            self._bind_mouse_wheel(child)
    
    def bind_all_mousewheel(self):
        """Bind mouse wheel cho tất cả widgets hiện tại"""
        self._bind_mouse_wheel(self.scrollable_frame)


def create_custom_scrollbar_style():
    """Tạo style cho scrollbar tùy chỉnh"""
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Vertical.TScrollbar", 
                   gripcount=0,
                   background="#7c5ceb",
                   darkcolor="#5940c9",
                   lightcolor="#9b7ef5",
                   troughcolor="#f0f0f0",
                   bordercolor="#7c5ceb",
                   arrowcolor="white",
                   width=12)
    
    # Map cho các trạng thái
    style.map("Custom.Vertical.TScrollbar",
              background=[('pressed', '#5940c9'), 
                         ('active', '#9b7ef5')])


def bind_mousewheel_to_widget(widget, canvas):
    """
    Bind mouse wheel cho một widget cụ thể
    
    Args:
        widget: Widget cần bind
        canvas: Canvas để scroll
    """
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    widget.bind("<MouseWheel>", _on_mousewheel)
    
    # Bind cho tất cả children
    for child in widget.winfo_children():
        bind_mousewheel_to_widget(child, canvas)


def make_listbox_scrollable(listbox, parent):
    """
    Tạo scrollbar cho Listbox với hỗ trợ con lăn chuột
    
    Args:
        listbox: Listbox cần scroll
        parent: Parent frame chứa listbox
    
    Returns:
        scrollbar: Scrollbar đã được tạo
    """
    # Tạo style nếu chưa có
    create_custom_scrollbar_style()
    
    # Tạo scrollbar
    scrollbar = ttk.Scrollbar(parent, style="Custom.Vertical.TScrollbar")
    scrollbar.pack(side='right', fill='y')
    
    # Config listbox
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    
    # Bind mouse wheel
    def _on_mousewheel(event):
        listbox.yview_scroll(int(-1*(event.delta/120)), "units")
    
    listbox.bind("<MouseWheel>", _on_mousewheel)
    
    return scrollbar


# Ví dụ sử dụng
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ScrollableFrame Demo")
    root.geometry("500x400")
    
    # Tạo scrollable frame
    scrollable = ScrollableFrame(root, bg='white')
    scrollable.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Thêm nhiều widgets vào scrollable frame
    for i in range(50):
        tk.Label(scrollable.scrollable_frame, 
                text=f"Label {i+1}", 
                font=("Arial", 12),
                bg='white',
                pady=10).pack(fill='x')
    
    # Bind mouse wheel cho tất cả widgets
    scrollable.bind_all_mousewheel()
    
    root.mainloop()