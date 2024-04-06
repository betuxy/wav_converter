from glob import glob
from argparse import ArgumentParser
from pprint import pprint
from os.path import basename, expanduser, join as path_join
from subprocess import run, CalledProcessError
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import threading
import time


def convert_music(source_path, dest_path):
    incomplete_files = glob(path_join(source_path, '**', '*.download'), recursive=True)
    all_wav_files = glob(path_join(source_path, '**', '*.wav'), recursive=True)

    complete_wav_files = [
                x for x in all_wav_files if not any(x in string for string in incomplete_files)
            ]

    for file in complete_wav_files:
        filename = basename(file)

        try:
            res = run(
                [
                    "/opt/homebrew/bin/ffmpeg",
                    "-y", "-loglevel", "error",
                    "-i", file, f"{dest_path}/{filename}"
                ],
                shell=False, check=True, capture_output=True
            )

            output_text.insert(tk.END, f"{filename}\n")
            output_text.update_idletasks()

        except CalledProcessError as cpe:
            print(f"[ERROR] Failed processing file {filename}")
            print(f"stderr: {cpe.stderr.decode('utf-8')}\n")

    output_text.insert(tk.END, "\n\n=== Finished Processing ===")
    output_text.update_idletasks()


def browse_button(folder_var):
    folder_selected = filedialog.askdirectory()
    folder_var.set(folder_selected)


def convert_button():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    # Run the conversion process in a separate thread
    threading.Thread(target=convert_music, args=(input_folder, output_folder)).start()


# Create the main tkinter window
root = tk.Tk()
root.title("Music File Converter")

# Set the initial size of the window
root.geometry("1000x800")

# Set padding for all widgets
padding = 5

# Set the font size for all text widgets and labels
font_style = ("Arial", 18)

# Frame to contain input elements
input_frame = tk.Frame(root)
input_frame.pack(padx=padding, pady=padding)

# Input folder selection
input_folder_var = tk.StringVar()
input_folder_label = tk.Label(input_frame, text="Input Folder:", font=font_style)
input_folder_label.grid(row=0, column=0, sticky="w", padx=padding, pady=padding)
input_folder_entry = tk.Entry(input_frame, textvariable=input_folder_var, font=font_style, width=50)
input_folder_entry.grid(row=0, column=1, padx=padding, pady=padding)
input_folder_button = tk.Button(input_frame, text="Browse", command=lambda: browse_button(input_folder_var), font=font_style)
input_folder_button.grid(row=0, column=2, padx=padding, pady=padding)

# Output folder selection
output_folder_var = tk.StringVar()
output_folder_label = tk.Label(input_frame, text="Output Folder:", font=font_style)
output_folder_label.grid(row=1, column=0, sticky="w", padx=padding, pady=padding)
output_folder_entry = tk.Entry(input_frame, textvariable=output_folder_var, font=font_style, width=50)
output_folder_entry.grid(row=1, column=1, padx=padding, pady=padding)
output_folder_button = tk.Button(input_frame, text="Browse", command=lambda: browse_button(output_folder_var), font=font_style)
output_folder_button.grid(row=1, column=2, padx=padding, pady=padding)

# Convert button
convert_button = tk.Button(root, text="Convert", command=convert_button, font=font_style)
convert_button.pack(pady=padding)

# Output text widget
output_text = tk.Text(root, font=font_style)
output_text.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

# Start the GUI event loop
root.mainloop()
