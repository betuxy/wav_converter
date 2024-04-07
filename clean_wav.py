from glob import glob
from os.path import basename, join as path_join
from subprocess import run, CalledProcessError
import tkinter as tk
from tkinter import filedialog
import threading


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

            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"{filename}\n")
            # output_text.update_idletasks()
            output_text.config(state=tk.DISABLED)

        except CalledProcessError as cpe:
            print(f"[ERROR] Failed processing file {filename}")
            print(f"stderr: {cpe.stderr.decode('utf-8')}\n")

    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "\n=== Finished Processing ===")
    output_text.insert(tk.END, f"Time spent: {default_timer() - start_time}")

    output_text.config(state=tk.DISABLED)


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

# Calculate the position to center the window on the screen
window_width = 1000
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2

# Set the window geometry and position
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Set padding for all widgets
padding = 5

# Set the font size for all text widgets and labels
font_style = ("Monaco", 18)

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
convert_button = tk.Button(root, text="Convert", command=convert_button, font=("Arial Rounded MT Bold", 20), width=20, height=2)
convert_button.pack(pady=10)

# Output text widget
output_text = tk.Text(root, font=font_style, state=tk.DISABLED)
output_text.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

# Start the GUI event loop
root.mainloop()
