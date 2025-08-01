# Author: Tao Wen
# Description: 
#   main application logic to visualize the dataset, 
#   i.e., put everything together.

from tkinter import Tk, Frame, Button, Listbox, Scrollbar, filedialog, Label
from PIL import Image, ImageTk
import os
from typing_ import DataLoaderProtocol
from data_loader import FolderLoader, ZipLoader
from visualizer import AnnotatedImageVisualizer


class ImageBrowser:
    def __init__(self, master: Tk):
        self.master = master
        self.master.title("Image Browser")
        
        self.frame = Frame(self.master)
        self.frame.pack()

        self.image_list = Listbox(self.frame)
        self.image_list.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        self.image_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.image_list.yview)

        self.load_button = Button(self.master, text="Load Images", command=self.load_folder)
        self.load_button.pack()

        self.load_zip_button = Button(self.master, text="Load ZIP file", command=self.load_zipfile)
        self.load_zip_button.pack()

        self.prev_button = Button(self.master, text="Previous", command=self.show_previous_image)
        self.prev_button.pack(side="left")

        self.next_button = Button(self.master, text="Next", command=self.show_next_image)
        self.next_button.pack(side="right")

        self.image_label = Label(self.master)
        self.image_label.pack()

        self.data_loader: DataLoaderProtocol = None
        self.current_image_index = 0

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

    def show_image(self, index):
        if not self.data_loader:
            return

        data_item = self.data_loader.get_item_by_index(index)
        image = AnnotatedImageVisualizer().to_image(data_item)
        
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def show_previous_image(self):
        if self.data_loader:
            self.current_image_index = (self.current_image_index - 1) % len(self.data_loader.data_item_name_list)
            self.show_image(self.current_image_index)

    def show_next_image(self):
        if self.data_loader:
            self.current_image_index = (self.current_image_index + 1) % len(self.data_loader.data_item_name_list)
            self.show_image(self.current_image_index)

    def show_previous_image(self):
        if self.data_loader:
            self.current_image_index = (self.current_image_index - 1) % len(self.data_loader)
            self.show_image(self.current_image_index)

    def show_next_image(self):
        if self.data_loader:
            self.current_image_index = (self.current_image_index + 1) % len(self.data_loader)
            self.show_image(self.current_image_index)

