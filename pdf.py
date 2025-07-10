import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from datetime import datetime
import io
import platform
import subprocess

try:
    import fitz  # PyMuPDF
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMuPDF'])
    import fitz

from PIL import Image, ImageTk


class SimplePDFExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Region Extractor")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0F1E36")

        self.pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
        self.current_image = None
        self.saved_image_path = None

        self.setup_ui()
        self.update_status("Ready - Click 'Load PDF' to begin")

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg="#0A192F")
        top_frame.pack(fill='x')

        title_label = tk.Label(
            top_frame,
            text="PDF Extractor",
            font=("Segoe UI", 24, "bold"),
            fg="#00BFFF",
            bg="#0F1E36",
        )
        title_label.pack(side="left", padx=10, pady=10)

        toolbar = tk.Frame(self.root, bg="#0A192F")
        toolbar.pack(fill='x')

        btn_params = {'bg': '#007ACC', 'fg': 'white', 'activebackground': '#005A9E', 'activeforeground': 'white', 'font': ('Segoe UI', 10, 'bold')}

        tk.Button(toolbar, text="Load PDF", command=self.load_pdf, **btn_params).pack(side='left', padx=5, pady=5)
        tk.Button(toolbar, text="Prev", command=self.prev_page, **btn_params).pack(side='left', padx=5, pady=5)
        tk.Button(toolbar, text="Next", command=self.next_page, **btn_params).pack(side='left', padx=5, pady=5)
        tk.Button(toolbar, text="Save Selection as Image", command=self.save_selection_as_image, **btn_params).pack(side='left', padx=5, pady=5)
        tk.Button(toolbar, text="🖨️ Print Image", command=self.print_image, **btn_params).pack(side='left', padx=5, pady=5)

        self.page_label = tk.Label(toolbar, text="Page 0/0", bg="#0A192F", fg="white", font=('Segoe UI', 10, 'bold'))
        self.page_label.pack(side='left', padx=10)

        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.update_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        self.selection_info = tk.Label(self.root, text="Click and drag to select area", bg="#0F1E36", fg="white", font=('Segoe UI', 10))
        self.selection_info.pack(fill='x')

        self.status_label = tk.Label(self.root, text="Status", relief='sunken', anchor='w', bg="#0A192F", fg="white", font=('Segoe UI', 9))
        self.status_label.pack(fill='x')

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        try:
            self.pdf_doc = fitz.open(file_path)
            self.total_pages = len(self.pdf_doc)
            self.current_page = 0
            self.zoom_level = 1.0
            self.update_page_display()
            self.update_status(f"Loaded: {os.path.basename(file_path)} ({self.total_pages} pages)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_page_display(self):
        if not self.pdf_doc:
            return

        page = self.pdf_doc[self.current_page]
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("ppm")))
        self.current_image = img
        self.photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.page_label.config(text=f"Page {self.current_page + 1}/{self.total_pages}")
        self.clear_selection()

    def prev_page(self):
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()

    def next_page(self):
        if self.pdf_doc and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_display()

    def start_drag(self, event):
        self.clear_selection()
        self.start_point = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.selection_rect = self.canvas.create_rectangle(
            self.start_point[0], self.start_point[1],
            self.start_point[0], self.start_point[1],
            outline='red', width=2
        )

    def update_drag(self, event):
        if self.selection_rect:
            current_x, current_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self.canvas.coords(self.selection_rect, self.start_point[0], self.start_point[1], current_x, current_y)

    def end_drag(self, event):
        if self.selection_rect:
            self.end_point = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            w, h = abs(x2 - x1), abs(y2 - y1)
            self.selection_info.config(text=f"Selected area: {int(w)}x{int(h)} pixels")

    def clear_selection(self):
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
        self.selection_info.config(text="Click and drag to select area")

    def save_selection_as_image(self):
        if not self.pdf_doc or not self.start_point or not self.end_point:
            self.update_status("No selection to save")
            return

        try:
            x1 = min(self.start_point[0], self.end_point[0]) / self.zoom_level
            y1 = min(self.start_point[1], self.end_point[1]) / self.zoom_level
            x2 = max(self.start_point[0], self.end_point[0]) / self.zoom_level
            y2 = max(self.start_point[1], self.end_point[1]) / self.zoom_level

            rect = fitz.Rect(x1, y1, x2, y2)
            page = self.pdf_doc[self.current_page]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"selection_{timestamp}.png"
            with open(filename, "wb") as f:
                f.write(pix.tobytes("png"))

            self.saved_image_path = os.path.abspath(filename)
            self.update_status(f"Selection saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def print_image(self):
        if not self.saved_image_path or not os.path.exists(self.saved_image_path):
            messagebox.showwarning("Warning", "No image available to print")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(self.saved_image_path, "print")
            elif platform.system() == "Darwin":
                subprocess.run(["lp", self.saved_image_path])
            else:
                subprocess.run(["xdg-open", self.saved_image_path])
            self.update_status(f"Sent to printer: {self.saved_image_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {str(e)}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SimplePDFExtractor()
    app.run()
