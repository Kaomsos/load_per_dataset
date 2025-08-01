import tkinter as tk

class ImageDisplay(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create a container frame for the image
        self.image_container = tk.Frame(self)
        self.image_container.pack(expand=True, fill='both')
        
        # Create the image label
        self.image_label = tk.Label(self.image_container)
        self.image_label.pack(expand=True, fill='both')
        
        # Create the filename label at the bottom
        self.filename_label = tk.Label(self, text="", anchor='w')
        self.filename_label.pack(side='bottom', fill='x', padx=5, pady=2)
        
        # ...existing code...