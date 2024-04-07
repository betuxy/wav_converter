from glob import glob
from os.path import basename, join as path_join
from subprocess import run, CalledProcessError
import tkinter as tk
from tkinter import filedialog
import threading
from timeit import default_timer


def convert_seconds(seconds):
    hours = str(seconds // 3600) + "h"
    minutes = str((seconds % 3600) // 60) + "m"
    seconds = str(seconds % 60) + "s"

    if hours.startswith("0"):
        if minutes.startswith("0"):
            return f"{seconds}"

        else:
            return f"{minutes} {seconds}"

    else:
        return f"{hours:<3} {minutes:<3} {seconds:<3}"


def convert_music(source_path, dest_path):
    start_time = round(default_timer())
    convert_button.config(state=tk.DISABLED)
    num_errors = 0
    num_success = 0
    error_log = []

    incomplete_files = glob(path_join(source_path, '**', '*.download'), recursive=True)
    all_wav_files = glob(path_join(source_path, '**', '*.wav'), recursive=True)

    complete_wav_files = [
                x for x in all_wav_files if not any(x in string for string in incomplete_files)
            ]

    for file in sorted(complete_wav_files):
        filename = basename(file)

        try:
            run(
                [
                    "/opt/homebrew/bin/ffmpeg",
                    "-y", "-loglevel", "error",
                    "-i", file, f"{dest_path}/{filename}"
                ],
                shell=False, check=True, capture_output=True
            )

            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"{filename}\n")
            output_text.config(state=tk.DISABLED)

        except CalledProcessError:
            num_errors += 1
            error_log.append(f"{filename}")
            continue

        except FileNotFoundError:
            num_errors += 1
            error_log.append(f"{filename}")
            continue

        num_success += 1

    end_time = round(default_timer())
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "\n=== Finished Processing ===\n")
    output_text.insert(tk.END, f"Time spent: {convert_seconds(end_time - start_time)}\n")
    output_text.insert(tk.END, f"Found files: {len(complete_wav_files)}\n")
    output_text.insert(tk.END, f"Successful: {num_success}\n")
    output_text.insert(tk.END, f"Erroneous: {num_errors}\n")

    if num_errors > 0:
        output_text.insert(tk.END, "\nFailed files:\n")
        output_text.insert(tk.END, "\n".join(error_log))
    output_text.config(state=tk.DISABLED)
    convert_button.config(state=tk.NORMAL)


def browse_button(folder_var):
    folder_selected = filedialog.askdirectory()
    folder_var.set(folder_selected)


def convert_button():
    # Clear the text in the output text widget
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.config(state=tk.DISABLED)

    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    # Run the conversion process in a separate thread
    threading.Thread(target=convert_music, args=(input_folder, output_folder)).start()


def exit_button():
    root.destroy()  # Close the Tkinter window
    exit(0)  # Exit the Python program


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

# Button frame to contain Convert and Exit buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=padding)

button_font = ("Arial Rounded MT Bold", 20)
button_width = 15
button_height = 1
button_padding_x = 30
button_padding_y = 15

# Convert button
convert_button = tk.Button(button_frame, text="Convert", command=convert_button, font=button_font, width=button_width, height=button_height)
convert_button.pack(side=tk.LEFT, padx=button_padding_x, pady=button_padding_y)

# Exit button
exit_button = tk.Button(button_frame, text="Exit", command=exit_button, font=button_font, width=button_width, height=button_height)
exit_button.pack(side=tk.LEFT, padx=button_padding_x, pady=button_padding_y)

# Output text widget
output_text = tk.Text(root, font=font_style)
output_text.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

# Start the GUI event loop
root.mainloop()
