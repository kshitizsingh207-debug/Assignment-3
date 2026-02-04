import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os

# Image Manager
class ImageManager:
    def __init__(self):
        self.original_image = None
        self.base_image = None
        self.current_image = None
        self.file_path = None

        self.is_grayscale = False
        self.color_backup = None
        self.is_edge = False
        self.edge_backup = None

        self.undo_stack = []
        self.redo_stack = []

    def load_image(self, path):
        self.file_path = path
        self.original_image = cv2.imread(path)
        self.base_image = self.original_image.copy()
        self.current_image = self.base_image.copy()

        self.is_grayscale = False
        self.color_backup = self.original_image.copy()
        self.is_edge = False
        self.edge_backup = None

        self.undo_stack.clear()
        self.redo_stack.clear()

    def save_state(self):
        if self.base_image is not None:
            self.undo_stack.append(self.base_image.copy())
            self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.base_image.copy())
            self.base_image = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.base_image.copy())
            self.base_image = self.redo_stack.pop()

# Image Processor
class ImageProcessor:
    def __init__(self, manager):
        self.manager = manager

    def toggle_grayscale(self):
        if not self.manager.is_grayscale:
            self.manager.color_backup = self.manager.base_image.copy()
            self.manager.base_image = cv2.cvtColor(
                self.manager.base_image, cv2.COLOR_BGR2GRAY
            )
            self.manager.is_grayscale = True
        else:
            self.manager.base_image = self.manager.color_backup.copy()
            self.manager.is_grayscale = False

    def toggle_edge_detection(self):
        if not self.manager.is_edge:
            self.manager.edge_backup = self.manager.base_image.copy()
            gray = cv2.cvtColor(self.manager.base_image, cv2.COLOR_BGR2GRAY)
            self.manager.base_image = cv2.Canny(gray, 100, 200)
            self.manager.is_edge = True
        else:
            self.manager.base_image = self.manager.edge_backup.copy()
            self.manager.is_edge = False

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

    def adjust_brightness(self, value):
        base = self.manager.original_image.copy()
        self.manager.base_image = cv2.convertScaleAbs(base, alpha=1, beta=value)

    def resize_proportional(self, scale_percent):
        if self.manager.base_image is not None:
            h, w = self.manager.base_image.shape[:2]
            new_w = max(1, int(w * scale_percent / 100))
            new_h = max(1, int(h * scale_percent / 100))
            self.manager.current_image = cv2.resize(
                self.manager.base_image, (new_w, new_h), interpolation=cv2.INTER_AREA
            )

# GUI
class ImageEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("1050x650")

        self.manager = ImageManager()
        self.processor = ImageProcessor(self.manager)
        self.scale_percent = 100

        self.create_menu()
        self.create_layout()

    # -------- MENU --------
    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

    # -------- LAYOUT --------
    def create_layout(self):
        self.image_label = tk.Label(self.root, bg="gray")
        self.image_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        panel = tk.Frame(self.root, width=250)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(panel, text="Grayscale (Toggle)", command=self.apply_grayscale).pack(fill="x", pady=5)
        tk.Button(panel, text="Edge Detection (Toggle)", command=self.apply_edge).pack(fill="x", pady=5)

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

        # Brightness
        tk.Label(panel, text="Brightness").pack(pady=(10,0))
        self.brightness_slider = tk.Scale(panel, from_=-100, to=100, orient="horizontal")
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill="x")
        tk.Button(panel, text="Apply Brightness", command=self.apply_brightness).pack(fill="x", pady=5)

        # Resize
        tk.Label(panel, text="Resize").pack(pady=(10,0))
        resize_frame = tk.Frame(panel)
        resize_frame.pack(pady=(0,5))
        tk.Button(resize_frame, text="-", width=3, command=lambda: self.resize_image(-10)).grid(row=0, column=0, padx=5)
        tk.Label(resize_frame, text="Scale").grid(row=0, column=1)
        tk.Button(resize_frame, text="+", width=3, command=lambda: self.resize_image(10)).grid(row=0, column=2, padx=5)

    # -------- FILE --------
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.bmp")])
        if path:
            self.manager.load_image(path)
            self.processor.resize_proportional(self.scale_percent)
            self.update_display()
            self.blur_slider.set(0)
            self.contrast_slider.set(50)
            self.brightness_slider.set(0)
            self.scale_percent = 100

    # -------- EDIT --------
    def undo(self):
        self.manager.undo()
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    def redo(self):
        self.manager.redo()
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    # -------- EFFECTS --------
    def apply_grayscale(self):
        self.manager.save_state()
        self.processor.toggle_grayscale()
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    def apply_edge(self):
        self.manager.save_state()
        self.processor.toggle_edge_detection()
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

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

    def apply_brightness(self):
        self.manager.save_state()
        self.processor.adjust_brightness(self.brightness_slider.get())
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    # -------- RESIZE --------
    def resize_image(self, delta_percent):
        if self.manager.base_image is None:
            return
        self.manager.save_state()
        self.scale_percent = max(1, self.scale_percent + delta_percent)
        self.processor.resize_proportional(self.scale_percent)
        self.update_display()

    # -------- DISPLAY --------
    def update_display(self):
        img = self.manager.current_image
        if img is None:
            return

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(img)
        img.thumbnail((750, 600))

        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

# RUN APPLICATION
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()
