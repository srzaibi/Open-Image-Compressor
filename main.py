import os
import sys
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Entry, Scale, StringVar, IntVar, Toplevel,
    filedialog, messagebox, ttk, BOTH, X, Y, LEFT, RIGHT, TOP, BOTTOM,
    W, E, N, S, HORIZONTAL, DISABLED, NORMAL
)
from PIL import Image
import multiprocessing

# ====================== WORKER FUNCTION (must be top-level for ProcessPool) ======================
def compress_one_image(args):
    filepath, resize_mode, percent, max_w, max_h, quality, overwrite = args
    try:
        path = Path(filepath)
        img = Image.open(path)

        # Convert for JPEG if needed
        if path.suffix.lower() in {".jpg", ".jpeg"} and img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # Resize
        if resize_mode == "percentage":
            percent = percent / 100.0
            new_size = (max(1, int(img.width * percent)), max(1, int(img.height * percent)))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        # Output path
        if overwrite:
            out_path = path
        else:
            compressed_dir = path.parent / "Compressed"
            compressed_dir.mkdir(exist_ok=True)
            out_path = compressed_dir / path.name

        # Save
        save_kwargs = {"optimize": True}
        ext = out_path.suffix.lower()

        if ext in {".jpg", ".jpeg"}:
            save_kwargs["quality"] = quality
            save_kwargs["progressive"] = True
        elif ext == ".webp":
            save_kwargs["quality"] = quality
            save_kwargs["method"] = 6
        elif ext == ".png":
            # PNG compress_level 0-9 (higher = more compression)
            save_kwargs["compress_level"] = max(0, min(9, 9 - (quality // 11)))

        img.save(out_path, **save_kwargs)
        return True, str(out_path)
    except Exception as e:
        return False, str(e)

# ====================== MAIN APP ======================
class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OPEN IMAGE COMPRESSOR")
        self.root.geometry("780x680")
        self.root.minsize(700, 640)
        self.root.configure(bg="#f0f2f5")

        self.files = []
        self.is_running = False
        self.output_dirs = set()

        self.setup_ui()

    def setup_ui(self):
        # ========== HEADER ==========
        header = Frame(self.root, bg="#1a252f", height=85)
        header.pack(fill=X)
        header.pack_propagate(False)

        Label(
            header, text="OPEN IMAGE COMPRESSOR",
            font=("Segoe UI", 18, "bold"), bg="#1a252f", fg="#ffffff"
        ).pack(pady=(10, 0))

        Label(
            header,
            text="Developed By Shahzaib Rasool from Pakistan  |  Email: srzaibi@gmail.com",
            font=("Segoe UI", 9), bg="#1a252f", fg="#a0aec0"
        ).pack(pady=(2, 10))

        # ========== Selection Frame ==========
        select_frame = Frame(self.root, bg="#f0f2f5", pady=12)
        select_frame.pack(fill=X, padx=20)

        Button(
            select_frame, text="Select Images", command=self.select_files,
            font=("Segoe UI", 10), bg="#3498db", fg="white",
            activebackground="#2980b9", relief="flat", padx=14, pady=7
        ).pack(side=LEFT, padx=(0, 10))

        Button(
            select_frame, text="Select Folder", command=self.select_folder,
            font=("Segoe UI", 10), bg="#9b59b6", fg="white",
            activebackground="#8e44ad", relief="flat", padx=14, pady=7
        ).pack(side=LEFT, padx=(0, 10))

        Button(
            select_frame, text="Clear", command=self.clear_selection,
            font=("Segoe UI", 10), bg="#e74c3c", fg="white",
            activebackground="#c0392b", relief="flat", padx=14, pady=7
        ).pack(side=LEFT)

        self.file_count_label = Label(
            select_frame, text="No images selected", font=("Segoe UI", 10),
            bg="#f0f2f5", fg="#555"
        )
        self.file_count_label.pack(side=LEFT, padx=15)

        # ========== Options Frame ==========
        options = Frame(self.root, bg="white", bd=1, relief="solid")
        options.pack(fill=X, padx=20, pady=8)

        # --- Resize Mode ---
        Label(
            options, text="Resize Mode", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#2c3e50"
        ).grid(row=0, column=0, columnspan=4, sticky=W, padx=15, pady=(14, 6))

        self.resize_mode = StringVar(value="percentage")

        ttk.Radiobutton(
            options, text="Percentage", variable=self.resize_mode,
            value="percentage", command=self.toggle_resize_inputs
        ).grid(row=1, column=0, sticky=W, padx=15, pady=4)

        ttk.Radiobutton(
            options, text="Max Width / Height", variable=self.resize_mode,
            value="max", command=self.toggle_resize_inputs
        ).grid(row=1, column=1, sticky=W, padx=10, pady=4)

        # Percentage Slider
        self.percent_frame = Frame(options, bg="white")
        self.percent_frame.grid(row=2, column=0, columnspan=4, sticky=W+E, padx=15, pady=6)

        Label(self.percent_frame, text="Resize Percentage:", bg="white", font=("Segoe UI", 10)).pack(side=LEFT)

        self.percent_var = IntVar(value=80)
        self.percent_scale = Scale(
            self.percent_frame, from_=10, to=200, orient=HORIZONTAL,
            variable=self.percent_var, length=320,
            bg="white", highlightthickness=0, troughcolor="#ddd",
            activebackground="#3498db", font=("Segoe UI", 9),
            command=self.update_percent_label
        )
        self.percent_scale.pack(side=LEFT, padx=10)

        self.percent_label = Label(
            self.percent_frame, text="80%", bg="white",
            font=("Segoe UI", 11, "bold"), fg="#2980b9", width=5
        )
        self.percent_label.pack(side=LEFT)

        # Max size inputs
        self.max_frame = Frame(options, bg="white")
        self.max_frame.grid(row=3, column=0, columnspan=4, sticky=W, padx=15, pady=6)

        Label(self.max_frame, text="Max Width:", bg="white", font=("Segoe UI", 10)).pack(side=LEFT)
        self.max_w_var = StringVar(value="1920")
        Entry(self.max_frame, textvariable=self.max_w_var, width=8, font=("Segoe UI", 10)).pack(side=LEFT, padx=6)

        Label(self.max_frame, text="Max Height:", bg="white", font=("Segoe UI", 10)).pack(side=LEFT, padx=(18, 0))
        self.max_h_var = StringVar(value="1080")
        Entry(self.max_frame, textvariable=self.max_h_var, width=8, font=("Segoe UI", 10)).pack(side=LEFT, padx=6)
        Label(self.max_frame, text="(keeps aspect ratio)", bg="white", fg="#777", font=("Segoe UI", 9)).pack(side=LEFT, padx=8)

        # --- Quality ---
        Label(
            options, text="Compression Quality", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#2c3e50"
        ).grid(row=4, column=0, columnspan=4, sticky=W, padx=15, pady=(16, 4))

        Label(
            options, text="0% = Maximum Compression (smallest size)     |     100% = Best Quality",
            bg="white", fg="#666", font=("Segoe UI", 9)
        ).grid(row=5, column=0, columnspan=4, sticky=W, padx=15)

        self.quality_var = IntVar(value=75)
        self.quality_scale = Scale(
            options, from_=0, to=100, orient=HORIZONTAL,
            variable=self.quality_var, length=420,
            bg="white", highlightthickness=0, troughcolor="#ddd",
            activebackground="#27ae60", font=("Segoe UI", 9)
        )
        self.quality_scale.grid(row=6, column=0, columnspan=4, sticky=W, padx=15, pady=(2, 14))

        # --- Save Option ---
        Label(
            options, text="Save Option", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#2c3e50"
        ).grid(row=7, column=0, columnspan=4, sticky=W, padx=15, pady=(4, 6))

        self.save_mode = StringVar(value="folder")

        ttk.Radiobutton(
            options, text="Create 'Compressed' folder (recommended)",
            variable=self.save_mode, value="folder"
        ).grid(row=8, column=0, columnspan=2, sticky=W, padx=15, pady=2)

        ttk.Radiobutton(
            options, text="Overwrite original files",
            variable=self.save_mode, value="overwrite"
        ).grid(row=9, column=0, columnspan=2, sticky=W, padx=15, pady=(2, 16))

        # ========== Progress & Status ==========
        progress_frame = Frame(self.root, bg="#f0f2f5")
        progress_frame.pack(fill=X, padx=20, pady=(12, 5))

        self.progress = ttk.Progressbar(progress_frame, orient=HORIZONTAL, mode="determinate")
        self.progress.pack(fill=X)

        self.status_label = Label(
            progress_frame, text="Ready — using all CPU cores for maximum speed",
            font=("Segoe UI", 10), bg="#f0f2f5", fg="#555", anchor=W
        )
        self.status_label.pack(fill=X, pady=(6, 0))

        # ========== Start Button ==========
        btn_frame = Frame(self.root, bg="#f0f2f5")
        btn_frame.pack(fill=X, padx=20, pady=18)

        self.start_btn = Button(
            btn_frame, text="Start Compression", command=self.start_compression,
            font=("Segoe UI", 12, "bold"), bg="#27ae60", fg="white",
            activebackground="#219a52", relief="flat", padx=24, pady=11
        )
        self.start_btn.pack(side=LEFT)

        # Initialize visibility
        self.toggle_resize_inputs()

    def update_percent_label(self, value):
        self.percent_label.config(text=f"{int(float(value))}%")

    def toggle_resize_inputs(self):
        if self.resize_mode.get() == "percentage":
            self.percent_frame.grid()
            self.max_frame.grid_remove()
        else:
            self.percent_frame.grid_remove()
            self.max_frame.grid()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                ("All files", "*.*")
            ]
        )
        if files:
            self.files = list(files)
            self.file_count_label.config(text=f"{len(self.files)} image(s) selected")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder containing images")
        if folder:
            extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
            self.files = [
                str(p) for p in Path(folder).rglob("*")
                if p.suffix.lower() in extensions and p.is_file()
            ]
            self.file_count_label.config(text=f"{len(self.files)} image(s) found in folder")

    def clear_selection(self):
        self.files = []
        self.file_count_label.config(text="No images selected")
        self.progress["value"] = 0
        self.status_label.config(text="Ready — using all CPU cores for maximum speed")
        self.output_dirs.clear()

    def start_compression(self):
        if not self.files:
            messagebox.showwarning("No Images", "Please select images or a folder first.")
            return
        if self.is_running:
            return

        # Validate
        try:
            quality = int(self.quality_var.get())
            if not (0 <= quality <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quality", "Quality must be between 0 and 100.")
            return

        if self.resize_mode.get() == "percentage":
            percent = self.percent_var.get()
            if percent < 10 or percent > 200:
                messagebox.showerror("Invalid Percentage", "Percentage must be between 10 and 200.")
                return
            max_w = max_h = 0
        else:
            try:
                max_w = int(self.max_w_var.get())
                max_h = int(self.max_h_var.get())
                if max_w < 1 or max_h < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Size", "Max Width and Height must be positive integers.")
                return
            percent = 0

        self.is_running = True
        self.start_btn.config(state=DISABLED)
        self.progress["value"] = 0
        self.status_label.config(text="Starting multi-core compression...")
        self.output_dirs.clear()

        # Prepare arguments for workers
        quality_pil = max(1, min(95, quality))
        overwrite = self.save_mode.get() == "overwrite"
        resize_mode = self.resize_mode.get()

        args_list = [
            (f, resize_mode, percent, max_w, max_h, quality_pil, overwrite)
            for f in self.files
        ]

        # Run in background thread so GUI stays responsive
        thread = threading.Thread(
            target=self.run_multiprocessing,
            args=(args_list,),
            daemon=True
        )
        thread.start()

    def run_multiprocessing(self, args_list):
        total = len(args_list)
        success = 0
        failed = 0
        first_output = None

        # Use all available CPU cores
        max_workers = multiprocessing.cpu_count()

        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(compress_one_image, args): args for args in args_list}

                for i, future in enumerate(as_completed(futures), 1):
                    ok, result = future.result()
                    if ok:
                        success += 1
                        if first_output is None:
                            first_output = result
                        # Collect output directories
                        out_path = Path(result)
                        self.output_dirs.add(str(out_path.parent))
                    else:
                        failed += 1
                        print(f"Failed: {result}")

                    # Update progress
                    progress_value = (i / total) * 100
                    self.root.after(0, self.update_progress, progress_value, i, total)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed:\n{e}"))
            self.root.after(0, self.finish_processing, 0, total)
            return

        self.root.after(0, self.finish_processing, success, failed, first_output)

    def update_progress(self, value, current, total):
        self.progress["value"] = value
        self.status_label.config(text=f"Processing {current}/{total} images  •  Using all CPU cores")

    def finish_processing(self, success, failed, first_output=None):
        self.is_running = False
        self.start_btn.config(state=NORMAL)
        self.progress["value"] = 100

        msg = f"Done!  {success} succeeded"
        if failed:
            msg += f",  {failed} failed"
        self.status_label.config(text=msg)

        # Custom completion dialog with Open Folder button
        self.show_completion_dialog(success, failed, first_output)

    def show_completion_dialog(self, success, failed, first_output):
        dialog = Toplevel(self.root)
        dialog.title("Compression Complete")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 210
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 110
        dialog.geometry(f"+{x}+{y}")

        Label(
            dialog, text="✓ Compression Finished",
            font=("Segoe UI", 14, "bold"), bg="white", fg="#27ae60"
        ).pack(pady=(20, 8))

        info = f"{success} image(s) compressed successfully"
        if failed:
            info += f"\n{failed} failed"
        Label(
            dialog, text=info, font=("Segoe UI", 10), bg="white", fg="#333",
            justify="center"
        ).pack(pady=5)

        btn_frame = Frame(dialog, bg="white")
        btn_frame.pack(pady=20)

        def open_folder():
            if first_output:
                folder = str(Path(first_output).parent)
                if sys.platform == "win32":
                    os.startfile(folder)
                elif sys.platform == "darwin":
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')
            dialog.destroy()

        if first_output and success > 0:
            Button(
                btn_frame, text="Open Folder", command=open_folder,
                font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white",
                activebackground="#2980b9", relief="flat", padx=18, pady=8
            ).pack(side=LEFT, padx=8)

        Button(
            btn_frame, text="Close", command=dialog.destroy,
            font=("Segoe UI", 10), bg="#95a5a6", fg="white",
            activebackground="#7f8c8d", relief="flat", padx=18, pady=8
        ).pack(side=LEFT, padx=8)

if __name__ == "__main__":
    # Required for Windows multiprocessing
    multiprocessing.freeze_support()
    root = Tk()
    app = ImageCompressorApp(root)
    root.mainloop()