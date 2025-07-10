# 📄 PDF Region Extractor

A modern desktop application to view PDF files, select a region of interest using a click-and-drag rectangle, and export that region as an image. Ideal for engineers, QA testers, document reviewers, or anyone needing quick content extractions from PDF documents.

Built with Python using `Tkinter` for GUI and `PyMuPDF` for PDF handling.

---

## 🖥 Features

- 📂 Load and render PDF documents.
- 🔍 Click and drag to select any rectangular region.
- 🖼 Export the selected region as a high-resolution image (`.png`).
- 🖨 Print the exported image directly.
- 🔄 Navigate between pages easily.
- ⚙ Auto-installs missing dependencies (like `PyMuPDF`) on first run.

---

## 📦 Dependencies

The following Python libraries are required:

| Module         | Purpose                                                                 |
|----------------|-------------------------------------------------------------------------|
| `tkinter`      | GUI components like windows, buttons, canvas, etc.                      |
| `filedialog`   | Opens a file browser to select PDFs.                                    |
| `messagebox`   | Displays user alerts and errors.                                        |
| `os` / `sys`   | Path and system-level operations.                                       |
| `datetime`     | For timestamping saved image files.                                     |
| `io`           | Handling byte streams from PDF image rendering.                         |
| `platform`     | Detect OS for native print support.                                     |
| `subprocess`   | Used to auto-install `PyMuPDF` if not found.                            |
| `fitz`         | The main interface from `PyMuPDF` for working with PDFs.                |
| `PIL.Image`    | For image manipulation and format conversion.                           |
| `PIL.ImageTk`  | Converts `PIL` images into `Tkinter`-compatible format for display.     |

🛠 **Note**: If `fitz` (PyMuPDF) is missing, the app auto-installs it using `pip`.

---

## 🚀 How to Run

1. **Install Python 3.8+**

2. **Install required packages** *(if not installed automatically)*:
   ```bash
   pip install PyMuPDF Pillow
