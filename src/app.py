# Author: Tao Wen
# Description: 
#   main application logic to visualize the dataset, 
#   i.e., put everything together.

from tkinter import (
    Tk, Frame, Button, Listbox, Scrollbar, 
    filedialog, Label, PanedWindow
)
from PIL import ImageTk, Image  # Add Image import
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
        self.last_label_size = None  # Track label size

    def _create_ui(self):
        # Control buttons frame
        self.button_frame = Frame(self.master)
        self.button_frame.pack(fill="x")

        self.load_button = Button(self.button_frame, text="Load Folder")
        self.load_button.pack(side="left")

        self.load_zip_button = Button(self.button_frame, text="Load ZIP")
        self.load_zip_button.pack(side="left")

        self.batch_process_button = Button(self.button_frame, text="Batch Process")
        self.batch_process_button.pack(side="left")

        # Paned window to allow resizing
        paned = PanedWindow(self.master, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Frame for list and scrollbar with minimum width
        self.list_frame = Frame(paned, width=200, name="list_frame")  # Set minimum width
        self.list_frame.pack_propagate(False)  # Prevent frame from shrinking
        paned.add(self.list_frame)

        self.image_list = Listbox(self.list_frame)
        self.image_list.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(self.list_frame)
        self.scrollbar.pack(side="right", fill="y")

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
        image_frame = Frame(
            paned, name="image_frame", 
        )  # Changed: parent to paned window
        paned.add(image_frame)

        self.filename_label = Label(image_frame)
        self.filename_label.pack(side="top", pady=5, fill="x")

        # Make image label fill available space
        self.image_label = Label(
            image_frame,
            highlightbackground="gray",  # 边框颜色
            highlightcolor="gray",      # 获得焦点时的边框颜色，保持一致
            highlightthickness=1,       # 边框宽度
        )
        self.image_label.pack(side="top", fill="both", expand=True)

    def _bind_events(self):
        # Configure scrollbar and listbox to work together
        self.image_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.image_list.yview)

        # Bind list click event
        self.image_list.bind('<<ListboxSelect>>', self._on_select_listbox)

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
        
        # Bind scroll events to image_list instead of list_frame
        self.image_list.bind('<MouseWheel>', self._on_list_scroll)  # Windows
        self.image_list.bind('<Button-4>', lambda e: self._on_list_scroll(e, 120))  # Linux
        self.image_list.bind('<Button-5>', lambda e: self._on_list_scroll(e, -120))  # Linux
    
        self.image_label.bind('<Configure>', self._on_label_resize)

        # Bind enter listbox event to show the full name of the item
        self.image_list.bind('<Enter>', lambda e: self.image_list.bind('<Motion>', self._on_listbox_motion))
        self.image_list.bind('<Leave>', lambda e: self.image_list.unbind('<Motion>'))

    def _on_label_resize(self, event):
        # Only refresh if size actually changed
        if self.last_label_size != (event.width, event.height):
            self.last_label_size = (event.width, event.height)
            if hasattr(self, 'current_original_image'):
                self.show_image()

    def _on_mousewheel(self, event):
        # Check if mouse is over list frame
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if str(widget).startswith(str(self.image_list)):
            return  # Let the list handle its own scrolling
        
        if event.delta > 0:
            self.show_previous_image()
        else:
            self.show_next_image()

    def _on_list_scroll(self, event, delta=None):
        # Use provided delta for Linux, or get from event for Windows
        scroll_delta = delta if delta is not None else event.delta
        # Scroll 2 units at a time
        self.image_list.yview_scroll(-1 * (scroll_delta // 120), "units")
        
        # Get visible range
        first_visible = int(float(self.image_list.yview()[0]) * self.image_list.size())
        last_visible = int(float(self.image_list.yview()[1]) * self.image_list.size()) - 1
        
        # Select first or last visible item based on scroll direction,
        # If view range is not changed, increment/decrement current index
        if scroll_delta > 0:  # Scrolling up
            if first_visible <= 0:
                self.current_image_index = max(0, self.current_image_index - 1)
            else:
                self.current_image_index = last_visible
        else:  # Scrolling down
            if last_visible >= self.image_list.size() - 1:
                self.current_image_index = min(self.image_list.size() - 1, self.current_image_index + 1)
            else:
                self.current_image_index = first_visible
            
        # Update selection and show image
        self.image_list.selection_clear(0, "end")
        self.image_list.selection_set(self.current_image_index)
        self.show_image()
        
        # Prevent event propagation
        return "break"

    def _on_select_listbox(self, event):
        selection = self.image_list.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.show_image()

    def _on_listbox_motion(self, event):
        nearest_item_index = self.image_list.nearest(event.y)
        


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
    
    def _resize_to_fit(self, image, width, height):
        # Calculate scaling factor to fit in label while maintaining aspect ratio
        img_width, img_height = image.size
        scale = min(width/img_width, height/img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        return image.resize(new_size, Image.Resampling.LANCZOS)

    def show_image(self):
        if not self.data_loader:
            return

        item = self.data_loader.get_item_by_index(self.current_image_index)
        image = self.visualizer.to_drawn_image(item)
        self.current_original_image = image  # Store original for resizing
        
        # Get current label size
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()

        # Only resize if we have valid dimensions
        if label_width > 50 and label_height > 50 and label_width * label_height > 5000:
            image = self._resize_to_fit(image, label_width, label_height)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        else:
            self.image_label.image = None  # Clear image if label size is invalid
        
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

