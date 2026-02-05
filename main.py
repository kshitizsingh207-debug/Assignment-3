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

    def blur(self, value):
        base = self.manager.original.copy()
        if value > 0:
            k = max(1, value * 2 + 1)  # kernel must be odd
            self.manager.current = cv2.GaussianBlur(base, (k, k), 0)
        else:
            self.manager.current = base.copy()

    def resize(self, scale_percent):
        if self.manager.current is not None:
            h, w = self.manager.current.shape[:2]
            new_w = max(1, int(w * scale_percent / 100))
            new_h = max(1, int(h * scale_percent / 100))
            self.manager.current = cv2.resize(
                self.manager.current, (new_w, new_h), interpolation=cv2.INTER_AREA
            )

class ImageEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor with Blur & Resize")
        self.root.geometry("1000x650")

        self.manager = ImageManager()
        self.processor = ImageProcessor(self.manager)
        self.scale_percent = 100

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

        # Grayscale & Edge
        tk.Button(panel, text="Grayscale (Toggle)", command=self.grayscale).pack(fill="x")
        tk.Button(panel, text="Edge Detection (Toggle)", command=self.edge).pack(fill="x")

        # Brightness
        tk.Label(panel, text="Brightness").pack(pady=(10,0))
        self.brightness_slider = tk.Scale(panel, from_=-100, to=100, orient="horizontal")
        self.brightness_slider.pack(fill="x")
        tk.Button(panel, text="Apply Brightness", command=self.brightness).pack(fill="x")

        # Contrast
        tk.Label(panel, text="Contrast").pack(pady=(10,0))
        self.contrast_slider = tk.Scale(panel, from_=0, to=100, orient="horizontal")
        self.contrast_slider.set(50)
        self.contrast_slider.pack(fill="x")
        tk.Button(panel, text="Apply Contrast", command=self.contrast).pack(fill="x")

        # Blur
        tk.Label(panel, text="Blur").pack(pady=(10,0))
        self.blur_slider = tk.Scale(panel, from_=0, to=10, orient="horizontal")
        self.blur_slider.pack(fill="x")
        tk.Button(panel, text="Apply Blur", command=self.blur).pack(fill="x")

        # Resize
        tk.Label(panel, text="Resize (%)").pack(pady=(10,0))
        resize_frame = tk.Frame(panel)
        resize_frame.pack(pady=(0,5))
        tk.Button(resize_frame, text="-", width=3, command=lambda: self.resize(-10)).grid(row=0, column=0, padx=5)
        tk.Label(resize_frame, text="Scale").grid(row=0, column=1)
        tk.Button(resize_frame, text="+", width=3, command=lambda: self.resize(10)).grid(row=0, column=2, padx=5)

    # File functions
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.png *.bmp")]
        )
        if path:
            self.manager.path = path
            self.manager.original = cv2.imread(path)
            self.manager.current = self.manager.original.copy()
            self.scale_percent = 100
            self.update_image()

    def save_image(self):
        if self.manager.current is not None:
            cv2.imwrite(self.manager.path, self.manager.current)
            messagebox.showinfo("Saved", "Image saved successfully")

    # Filters
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

    def blur(self):
        self.processor.blur(self.blur_slider.get())
        self.update_image()

    # Resize
    def resize(self, delta_percent):
        if self.manager.current is None:
            return
        self.scale_percent = max(1, self.scale_percent + delta_percent)
        self.processor.resize(self.scale_percent)
        self.update_image()

    # Update display
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

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()