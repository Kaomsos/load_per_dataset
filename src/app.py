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

        self.scrollbar = Scrollbar(self.list_frame)
        self.scrollbar.pack(side="right", fill="y")

        # Right side content
        image_frame = Frame(self.master)  # Added: new frame for right side content
        image_frame.pack(side="left", fill="both", expand=True)

        self.image_label = Label(image_frame)  # Changed: parent to right_frame
        self.image_label.pack(expand=True)

        self.filename_label = Label(image_frame)  # Changed: parent to right_frame
        self.filename_label.pack()

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
    
    def load_zipfile(self):
        zip_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if zip_path:
            self.data_loader = ZipLoader(zip_path)
            self.update_image_list()
    
    def update_image_list(self):
        self.image_list.delete(0, 'end')
        for image in self.data_loader.data_item_name_list:
            self.image_list.insert('end', image)

    def show_image(self):
        if not self.data_loader:
            return

        item = self.data_loader.get_item_by_index(self.current_image_index)
        image = self.visualizer.to_image(item)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        
        # Update filename display
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

