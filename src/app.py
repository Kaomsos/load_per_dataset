# Author: Tao Wen
# Description: 
#   main application logic to visualize the dataset, 
#   i.e., put everything together.

from tkinter import Tk, Frame, Button, Listbox, Scrollbar, filedialog, Label
from ui import ImageDisplay
from PIL import ImageTk
from typing_ import DataLoaderProtocol
from data_loader import FolderLoader, ZipLoader
from visualizer import AnnotatedImageVisualizer


class ImageBrowser:
    def __init__(self, master: Tk):
        self.master = master
        self.master.title("Image Browser")
        
        self._create_ui()
        self._bind_events()

        self.data_loader: DataLoaderProtocol = None
        self.visualizer = AnnotatedImageVisualizer()
        self.current_image_index = 0

    def _create_ui(self):
        # Control buttons frame
        self.button_frame = Frame(self.master)
        self.button_frame.pack(fill="x")

        self.load_button = Button(self.button_frame, text="Load Folder")
        self.load_button.pack(side="left")

        self.load_zip_button = Button(self.button_frame, text="Load ZIP")
        self.load_zip_button.pack(side="left")

        # Frame for list and scrollbar
        self.list_frame = Frame(self.master)
        self.list_frame.pack(side="left", fill="y")

        self.image_list = Listbox(self.list_frame)
        self.image_list.pack(side="left", fill="both")

        self.scrollbar = Scrollbar(self.list_frame)
        self.scrollbar.pack(side="right", fill="y")

        # Configure scrollbar and listbox to work together
        self.image_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.image_list.yview)

        # Navigation buttons frame with vertical centering
        nav_frame = Frame(self.list_frame)
        nav_frame.pack(side="left", fill="y")

        # Add spacer frame for vertical centering
        Frame(nav_frame).pack(expand=True)  # Top spacer
        
        self.prev_button = Button(nav_frame, text="↑")
        self.prev_button.pack(side="top", pady=2)

        self.next_button = Button(nav_frame, text="↓")
        self.next_button.pack(side="top", pady=2)
        
        Frame(nav_frame).pack(expand=True)  # Bottom spacer

        

        # Right side content
        image_frame = Frame(self.master)  # Added: new frame for right side content
        image_frame.pack(side="left", fill="both", expand=True)
        # Changed: parent to right_frame
        self.filename_label = Label(image_frame)  
        self.filename_label.pack()
        # Changed: parent to right_frame
        self.image_label = Label(image_frame)  
        self.image_label.pack(expand=True)

    def _bind_events(self):
        # Bind list click event
        self.image_list.bind('<<ListboxSelect>>', self.on_select)

        # Bind control button click events
        self.load_button.config(command=self.load_folder)
        self.load_zip_button.config(command=self.load_zipfile)
        self.prev_button.config(command=self.show_previous_image)
        self.next_button.config(command=self.show_next_image)

        # Bind keyboard events
        self.master.bind('<Left>', lambda e: self.show_previous_image())
        self.master.bind('<Up>', lambda e: self.show_previous_image())
        self.master.bind('<Right>', lambda e: self.show_next_image())
        self.master.bind('<Down>', lambda e: self.show_next_image())
        
        # Bind mouse wheel events
        self.master.bind('<MouseWheel>', self._on_mousewheel)  # Windows
        self.master.bind('<Button-4>', lambda e: self.show_previous_image())  # Linux
        self.master.bind('<Button-5>', lambda e: self.show_next_image())  # Linux
        
        # Add list scroll binding
        self.list_frame.bind('<MouseWheel>', self._on_list_scroll)  # Windows
        self.list_frame.bind('<Button-4>', lambda e: self._on_list_scroll(e, 120))  # Linux
        self.list_frame.bind('<Button-5>', lambda e: self._on_list_scroll(e, -120))  # Linux
        
    def _on_list_scroll(self, event, delta=None):
        # Use provided delta for Linux, or get from event for Windows
        scroll_delta = delta if delta is not None else event.delta
        # Scroll 2 units at a time
        self.image_list.yview_scroll(-1 * (scroll_delta // 120), "units")
        # Prevent event propagation
        return "break"

    def _on_mousewheel(self, event):
        # Only handle image navigation when not in list frame
        if not str(event.widget).startswith(str(self.list_frame)):
            if event.delta > 0:
                self.show_previous_image()
            else:
                self.show_next_image()

    def on_select(self, event):
        selection = self.image_list.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.show_image()

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.data_loader = FolderLoader(folder_path)
            self.update_image_list()
            self.current_image_index = 0  # Reset to first image
            self.show_image()  # Show the first image
    
    def load_zipfile(self):
        zip_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if zip_path:
            self.data_loader = ZipLoader(zip_path)
            self.update_image_list()
            self.current_image_index = 0  # Reset to first image
            self.show_image()  # Show the first image
    
    def update_image_list(self):
        self.image_list.delete(0, 'end')
        for idx, name in enumerate(self.data_loader.data_item_name_list):
            self.image_list.insert('end', name)
            # NOTE: this could be slow 
            # Check if the item has annotation
            # item = self.data_loader.get_item_by_index(idx)
            # if getattr(item, "annotation", None) is None:
            #     self.image_list.itemconfig(idx, fg='red')
    
    def show_image(self):
        if not self.data_loader:
            return

        item = self.data_loader.get_item_by_index(self.current_image_index)
        image = self.visualizer.to_drawn_image(item)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        
        # Update filename display
        if getattr(item, "annotation", None) is None:
            self.filename_label.config(text=item.name, fg='red')
        else:
            self.filename_label.config(text=item.name)

    def show_previous_image(self):
        if self.data_loader:
            self.current_image_index = (self.current_image_index - 1) % len(self.data_loader)
            self.show_image()
            # Update listbox selection
            self.image_list.selection_clear(0, "end")
            self.image_list.selection_set(self.current_image_index)
            self.image_list.see(self.current_image_index)

    def show_next_image(self):
        if self.data_loader:
            self.current_image_index = (self.current_image_index + 1) % len(self.data_loader)
            self.show_image()
            # Update listbox selection
            self.image_list.selection_clear(0, "end")
            self.image_list.selection_set(self.current_image_index)
            self.image_list.see(self.current_image_index)

