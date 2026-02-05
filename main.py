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

<<<<<<< HEAD
    def brightness(self, value):
        self.manager.current = cv2.convertScaleAbs(
            self.manager.original, alpha=1, beta=value
        )

    def contrast(self, value):
        alpha = value / 50
        self.manager.current = cv2.convertScaleAbs(
            self.manager.original, alpha=alpha, beta=0
        )
=======
    def blur(self, value):
        base = self.manager.original_image.copy()
        if value > 0:
            k = max(1, value * 2 + 1)
            self.manager.base_image = cv2.GaussianBlur(base, (k, k), 0)
        else:
            self.manager.base_image = base.copy()

    def adjust_contrast(self, value):
        base = self.manager.original_image.copy()
        alpha = value / 50  # 50 is default
        self.manager.base_image = cv2.convertScaleAbs(base, alpha=alpha, beta=0)

    def resize_proportional(self, scale_percent):
        if self.manager.base_image is not None:
            h, w = self.manager.base_image.shape[:2]
            new_w = max(1, int(w * scale_percent / 100))
            new_h = max(1, int(h * scale_percent / 100))
            self.manager.current_image = cv2.resize(
                self.manager.base_image, (new_w, new_h), interpolation=cv2.INTER_AREA
            )
>>>>>>> 5eb328aa2fe3bdd4367107c1b04453dd4c7cba95

class ImageEditorGUI:
    def __init__(self, root):
        self.root = root
<<<<<<< HEAD
        self.root.title("Simple Image Editor")
        self.root.geometry("900x600")
=======
        self.root.title("Image Editor")
        self.root.geometry("1000x650")
>>>>>>> 5eb328aa2fe3bdd4367107c1b04453dd4c7cba95

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

<<<<<<< HEAD
=======
        # Blur
        tk.Label(panel, text="Blur").pack(pady=(10,0))
        self.blur_slider = tk.Scale(panel, from_=0, to=10, orient="horizontal")
        self.blur_slider.pack(fill="x")
        tk.Button(panel, text="Apply Blur", command=self.apply_blur).pack(fill="x", pady=5)

        # Contrast
        tk.Label(panel, text="Contrast").pack(pady=(10,0))
        self.contrast_slider = tk.Scale(panel, from_=0, to=100, orient="horizontal")
        self.contrast_slider.set(50)
        self.contrast_slider.pack(fill="x")
        tk.Button(panel, text="Apply Contrast", command=self.apply_contrast).pack(fill="x", pady=5)

    # -------- FILE --------
>>>>>>> 5eb328aa2fe3bdd4367107c1b04453dd4c7cba95
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.png *.bmp")]
        )
        if path:
<<<<<<< HEAD
            self.manager.path = path
            self.manager.original = cv2.imread(path)
            self.manager.current = self.manager.original.copy()
            self.update_image()
=======
            self.manager.load_image(path)
            self.processor.resize_proportional(self.scale_percent)
            self.update_display()
            self.blur_slider.set(0)
            self.contrast_slider.set(50)
>>>>>>> 5eb328aa2fe3bdd4367107c1b04453dd4c7cba95

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

<<<<<<< HEAD
    def brightness(self):
        self.processor.brightness(self.brightness_slider.get())
        self.update_image()

    def contrast(self):
        self.processor.contrast(self.contrast_slider.get())
        self.update_image()

    def update_image(self):
        img = self.manager.current
=======
    def apply_blur(self):
        self.manager.save_state()
        self.processor.blur(self.blur_slider.get())
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    def apply_contrast(self):
        self.manager.save_state()
        self.processor.adjust_contrast(self.contrast_slider.get())
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    # -------- DISPLAY --------
    def update_display(self):
        img = self.manager.current_image
>>>>>>> 5eb328aa2fe3bdd4367107c1b04453dd4c7cba95
        if img is None:
            return

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(img)
<<<<<<< HEAD
        img.thumbnail((600, 500))
=======
        img.thumbnail((750, 600))

>>>>>>> 5eb328aa2fe3bdd4367107c1b04453dd4c7cba95
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()
