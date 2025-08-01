from tkinter import Tk, Label
# import sys; sys.path.insert(0, "")
# sys.path.append(".")


class App:
    def __init__(self, master: Tk):
        self.master = master
        self.master.title("Image Browser")
        self.master.geometry("800x600")
        self.master.resizable(width=False, height=False)
        self.master.attributes("-topmost", True)
        
        self.dummy_image = Label(master, text="Dummy Image", relief="solid", borderwidth=1)
        self.dummy_image.pack(pady=20)

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()

