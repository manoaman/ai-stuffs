#!/usr/bin/env python3

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Canvas, Toplevel
from PIL import Image, ImageTk
import threading
import json

CONFIG_FILE = "config.json"

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def run_script(image_dir, dry_run, progress_var, progress_bar, log_text):
    command = ["python3", "guess_and_rename_png_files.py", image_dir]
    if dry_run:
        command.append("--dry-run")
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    def read_output(pipe):
        for line in iter(pipe.readline, ''):
            log_text.insert(tk.END, line)
            log_text.see(tk.END)
            log_text.update_idletasks()
            if "Processing images" in line:
                total_files = int(line.split("/")[1].split()[0])
                progress_bar["maximum"] = total_files
            if "Renamed:" in line or "[DRY RUN] Would rename:" in line:
                progress_var.set(progress_var.get() + 1)
        pipe.close()

    threading.Thread(target=read_output, args=(process.stdout,), daemon=True).start()
    threading.Thread(target=read_output, args=(process.stderr,), daemon=True).start()
    
    process.wait()
    if process.returncode != 0:
        messagebox.showerror("Error", "An error occurred. Check logs for details.")
    else:
        messagebox.showinfo("Completed", "Processing completed.")

def list_images(image_dir, image_listbox):
    image_listbox.delete(0, tk.END)
    png_files = [f for f in os.listdir(image_dir) if f.lower().endswith(".png")]
    for filename in png_files:
        image_listbox.insert(tk.END, filename)

def toggle_list_frame():
    if list_frame.winfo_ismapped():
        list_frame.pack_forget()
    else:
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

def show_image_gallery(image_dir, gallery_frame):
    def enlarge_image(image_path):
        top = Toplevel()
        top.title("Image Viewer")
        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        panel = tk.Label(top, image=img)
        panel.image = img
        panel.pack()
        top.geometry(f"{img.width()}x{img.height()}")  # Set the size of the window to the image size

    for widget in gallery_frame.winfo_children():
        widget.destroy()
    
    canvas = Canvas(gallery_frame)
    scrollable_frame = tk.Frame(canvas)
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    canvas.pack(side="left", fill="both", expand=True)
    
    png_files = [f for f in os.listdir(image_dir) if f.lower().endswith(".png")]
    row, col = 0, 0
    max_cols = 10  # Adjust for layout to show 10 images per row
    for filename in png_files:
        image_path = os.path.join(image_dir, filename)
        img = Image.open(image_path)
        img.thumbnail((80, 80))  # Reduced thumbnail size
        img = ImageTk.PhotoImage(img)
        panel = tk.Label(scrollable_frame, image=img)
        panel.image = img
        panel.grid(row=row, column=col, padx=5, pady=5)
        panel.bind("<Button-1>", lambda e, path=image_path: enlarge_image(path))
        col += 1
        if col == max_cols:
            col = 0
            row += 1

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def main():
    global list_frame
    root = tk.Tk()
    root.title("PNG File Renamer")
    root.geometry("1000x1000")  # Adjusted size to make the gallery window taller and wider
    root.lift()
    root.attributes('-topmost', True)
    root.after(1000, lambda: root.attributes('-topmost', False))

    config = load_config()
    selected_dir = tk.StringVar(value=config.get("last_selected_dir", ""))

    def select_directory():
        image_dir = filedialog.askdirectory(initialdir=selected_dir.get() or "./")
        if image_dir:
            selected_dir.set(image_dir)
            config["last_selected_dir"] = image_dir
            save_config(config)
            list_images(image_dir, image_listbox)
            dry_run = dry_run_var.get()
            progress_var.set(0)
            log_text.delete(1.0, tk.END)
            threading.Thread(target=run_script, args=(image_dir, dry_run, progress_var, progress_bar, log_text), daemon=True).start()
        else:
            messagebox.showwarning("No Directory Selected", "No directory was selected. Exiting.")

    def select_directory_for_gallery():
        image_dir = filedialog.askdirectory(initialdir=selected_dir.get() or "./")
        if image_dir:
            selected_dir.set(image_dir)
            config["last_selected_dir"] = image_dir
            save_config(config)
            show_image_gallery(image_dir, gallery_frame)
        else:
            messagebox.showwarning("No Directory Selected", "No directory was selected. Exiting.")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=5, fill=tk.X)

    select_button = tk.Button(button_frame, text="Select Directory", command=select_directory)
    select_button.pack(side=tk.LEFT, padx=5, pady=2)

    gallery_button = tk.Button(button_frame, text="Show Image Gallery", command=select_directory_for_gallery)
    gallery_button.pack(side=tk.LEFT, padx=5, pady=2)

    toggle_list_button = tk.Button(button_frame, text="Toggle File List", command=toggle_list_frame)
    toggle_list_button.pack(side=tk.LEFT, padx=5, pady=2)

    dry_run_var = tk.BooleanVar(value=True)
    dry_run_check = tk.Checkbutton(button_frame, text="Dry Run", variable=dry_run_var)
    dry_run_check.pack(side=tk.LEFT, padx=5, pady=2)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, fill=tk.X)

    log_frame = tk.Frame(frame)
    log_frame.pack(pady=5, fill=tk.BOTH, expand=True)
    log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)  # Reduced height
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scroll = tk.Scrollbar(log_frame, command=log_text.yview)
    log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=log_scroll.set)

    list_frame = tk.Frame(frame)
    image_listbox = tk.Listbox(list_frame, height=8)  # Adjusted height
    image_listbox.pack(pady=5, fill=tk.BOTH, expand=True)
    
    gallery_frame = tk.Frame(frame)
    gallery_frame.pack(pady=5, fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
