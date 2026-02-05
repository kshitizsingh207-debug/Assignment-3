import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os

class ImageManager:
    def __init__(self):
        self.original = None
        self.current = None
        self.path = None

class ImageProcessor:
    def __init__(self, manager):
        self.manager = manager
        self.is_gray = False
        self.is_edge = False
        self.backup = None

    def toggle_grayscale(self):
        if not self.is_gray:
            self.backup = self.manager.current.copy()
            self.manager.current = cv2.cvtColor(
                self.manager.current, cv2.COLOR_BGR2GRAY
            )
            self.is_gray = True
        else:
            self.manager.current = self.backup.copy()
            self.is_gray = False

    def toggle_edge(self):
        if not self.is_edge:
            self.backup = self.manager.current.copy()
            gray = cv2.cvtColor(self.manager.current, cv2.COLOR_BGR2GRAY)
            self.manager.current = cv2.Canny(gray, 100, 200)
            self.is_edge = True
        else:
            self.manager.current = self.backup.copy()
            self.is_edge = False

    def brightness(self, value):
        self.manager.current = cv2.convertScaleAbs(
            self.manager.original, alpha=1, beta=value
        )

    def contrast(self, value):
        alpha = value / 50
        self.manager.current = cv2.convertScaleAbs(
            self.manager.original, alpha=alpha, beta=0
        )

class ImageEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Editor")
        self.root.geometry("900x600")

        self.manager = ImageManager()
        self.processor = ImageProcessor(self.manager)

        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        self.image_label = tk.Label(self.root, bg="gray")
        self.image_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        panel = tk.Frame(self.root, width=250)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(panel, text="Grayscale (Toggle)", command=self.grayscale).pack(fill="x")
        tk.Button(panel, text="Edge Detection (Toggle)", command=self.edge).pack(fill="x")

        tk.Label(panel, text="Brightness").pack(pady=(10,0))
        self.brightness_slider = tk.Scale(panel, from_=-100, to=100, orient="horizontal")
        self.brightness_slider.pack(fill="x")
        tk.Button(panel, text="Apply Brightness", command=self.brightness).pack(fill="x")

        tk.Label(panel, text="Contrast").pack(pady=(10,0))
        self.contrast_slider = tk.Scale(panel, from_=0, to=100, orient="horizontal")
        self.contrast_slider.set(50)
        self.contrast_slider.pack(fill="x")
        tk.Button(panel, text="Apply Contrast", command=self.contrast).pack(fill="x")

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.png *.bmp")]
        )
        if path:
            self.manager.path = path
            self.manager.original = cv2.imread(path)
            self.manager.current = self.manager.original.copy()
            self.update_image()

    def save_image(self):
        if self.manager.current is not None:
            cv2.imwrite(self.manager.path, self.manager.current)
            messagebox.showinfo("Saved", "Image saved successfully")

    def grayscale(self):
        self.processor.toggle_grayscale()
        self.update_image()

    def edge(self):
        self.processor.toggle_edge()
        self.update_image()

    def brightness(self):
        self.processor.brightness(self.brightness_slider.get())
        self.update_image()

    def contrast(self):
        self.processor.contrast(self.contrast_slider.get())
        self.update_image()

    def update_image(self):
        img = self.manager.current
        if img is None:
            return

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(img)
        img.thumbnail((600, 500))
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()
