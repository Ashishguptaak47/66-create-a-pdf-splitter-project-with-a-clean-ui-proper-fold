import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PyPDF2 import PdfReader, PdfWriter

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class PDFSplitterLogic:
    @staticmethod
    def parse_ranges(range_str, total_pages):
        pages = set()
        parts = range_str.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                sub_parts = part.split('-')
                if len(sub_parts) != 2:
                    raise ValueError(f"Invalid range format: {part}")
                start, end = int(sub_parts[0]), int(sub_parts[1])
                if start > end:
                    raise ValueError(f"Start cannot be greater than end in range: {part}")
                for p in range(start, end + 1):
                    if 1 <= p <= total_pages:
                        pages.add(p - 1)
                    else:
                        raise ValueError(f"Page {p} out of range (1-{total_pages})")
            else:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.add(p - 1)
                else:
                    raise ValueError(f"Page {p} out of range (1-{total_pages})")
        return sorted(list(pages))

    @staticmethod
    def split_pdf(input_path, output_dir, mode, range_str=""):
        if not input_path or not os.path.exists(input_path):
            raise FileNotFoundError("Please select a valid PDF file.")

        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            raise ValueError("The selected PDF has no pages.")

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        created_files = []

        if mode == "every":
            for i in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                out_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                with open(out_path, "wb") as f:
                    writer.write(f)
                created_files.append(out_path)

        elif mode == "custom":
            page_indices = PDFSplitterLogic.parse_ranges(range_str, total_pages)
            if not page_indices:
                raise ValueError("No valid pages specified for extraction.")
            writer = PdfWriter()
            for idx in page_indices:
                writer.add_page(reader.pages[idx])
            out_path = os.path.join(output_dir, f"{base_name}_custom_split.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)
            created_files.append(out_path)

        return created_files


class PDFSplitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern PDF Splitter")
        self.geometry("600"), "450"
        self.resizable(False, False)

        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "output_splits"))
        self.split_mode = tk.StringVar(value="every")

        self._create_widgets()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(self, text="PDF Splitter Tool", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=15)

        # File Selection Frame
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(fill="x", padx=20, pady=10)

        self.file_entry = ctk.CTkEntry(file_frame, textvariable=self.file_path, width=400, placeholder_text="Select PDF file...")
        self.file_entry.pack(side="left", padx=10, pady=10)

        browse_btn = ctk.CTkButton(file_frame, text="Browse", width=100, command=self._browse_file)
        browse_btn.pack(side="right", padx=10, pady=10)

        # Mode Frame
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=20, pady=10)

        self.radio_every = ctk.CTkRadioButton(mode_frame, text="Split into individual pages", variable=self.split_mode, value="every", command=self._toggle_mode)
        self.radio_every.pack(anchor="w", padx=15, pady=10)

        self.radio_custom = ctk.CTkRadioButton(mode_frame, text="Extract specific pages/ranges", variable=self.split_mode, value="custom", command=self._toggle_mode)
        self.radio_custom.pack(anchor="w", padx=15, pady=(0, 10))

        self.range_entry = ctk.CTkEntry(mode_frame, placeholder_text="e.g., 1-3, 5, 7-10", width=540)
        self.range_entry.pack(padx=15, pady=(0, 15))
        self.range_entry.configure(state="disabled")

        # Action Frame
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=15)

        self.split_btn = ctk.CTkButton(action_frame, text="Split PDF", fg_color="green", hover_color="darkgreen", height=40, font=("Helvetica", 14, "bold"), command=self._execute_split)
        self.split_btn.pack(fill="x")

    def _browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filename:
            self.file_path.set(filename)

    def _toggle_mode(self):
        if self.split_mode.get() == "custom":
            self.range_entry.configure(state="normal")
        else:
            self.range_entry.configure(state="disabled")

    def _execute_split(self):
        path = self.file_path.get()
        mode = self.split_mode.get()
        range_str = self.range_entry.get()
        out_dir = self.output_dir.get()

        try:
            created = PDFSplitterLogic.split_pdf(path, out_dir, mode, range_str)
            messagebox.showinfo("Success", f"Successfully created {len(created)} file(s)\nSaved in: {out_dir}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = PDFSplitterApp()
    app.mainloop()
