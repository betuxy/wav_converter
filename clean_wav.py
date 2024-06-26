#!/usr/bin/env python3
"""
This program recursively searches for Waveform files from a given directory
and leverages ffmpeg to convert them to Waveform files that are readable by
Pioneer XDJs.
"""

from glob import glob
from os.path import basename, join as path_join
from subprocess import run, CalledProcessError
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from timeit import default_timer
from sys import exit as sys_exit
from os import remove


def delete_error_files(error_log, popup_window):
    """
    Delete files listed in the error log.

    Parameters:
    - error_log (list): A list containing dictionaries with 'file' key representing the file path.
    """
    for error in error_log:
        try:
            remove(error['file'])
        except Exception as e:
            output_text.insert(tk.END, f"Error deleting {error['file']}: {e}\n")
            output_text.see(tk.END)


def delete_error_files_popup(error_log):
    """
    Open a new window to confirm deleting files listed in the error log.

    Parameters:
    - error_log (list): A list containing dictionaries with 'file' key representing the file path.
    """
    # Create a new window for the confirmation
    popup_window = tk.Toplevel(root)
    popup_window.title("Confirmation")

    # Create a label to display the message
    message_label = tk.Label(popup_window, text="Do you want to remove the following files?", font=font_style)
    message_label.pack(padx=20, pady=10)

    # Construct the message to display
    files_to_delete = "\n".join([f["file"] for f in error_log])

    # Calculate the number of lines in the textbox
    num_lines = len(files_to_delete.split('\n'))

    # Calculate the width based on the length of the longest filename
    max_filename_length = max(len(line) for line in files_to_delete.split('\n'))
    _width = min(max_filename_length, 600)  # Adjust the width dynamically

    # Create a text box to display the list of files to be deleted
    files_textbox = tk.Text(popup_window, font=font_style, wrap=tk.WORD, height=num_lines, width=_width)
    files_textbox.insert(tk.END, files_to_delete)
    files_textbox.configure(state="disabled")
    files_textbox.pack(padx=20, pady=10)

    # Create a frame for buttons
    _button_frame = tk.Frame(popup_window)
    _button_frame.pack(pady=10)

    # Create "Yes" and "No" buttons
    yes_button = tk.Button(
        _button_frame, text="Yes", command=lambda: on_confirm_delete(popup_window, error_log),
        font=font_style, width=10, height=2
    )
    yes_button.grid(row=0, column=0, padx=10, pady=5)

    no_button = tk.Button(
        _button_frame, text="No", command=popup_window.destroy,
        font=font_style, width=10, height=2
    )
    no_button.grid(row=0, column=1, padx=10, pady=5)

    # Center the buttons within the window
    popup_window.update_idletasks()  # Update the window to get proper size


def on_confirm_delete(popup_window, error_log):
    """
    Callback function for confirming file deletion.

    Parameters:
    - popup_window (Tkinter.Toplevel): The popup window.
    - error_log (list): A list containing dictionaries with 'file' key representing the file path.
    """
    delete_error_files(error_log, popup_window)
    popup_window.destroy()


def convert_seconds(seconds):
    """
    Convert seconds into hours, minutes, seconds.
    :return: String representation of %H:%M:%S
    """
    hours = str(seconds // 3600) + "h"
    minutes = str((seconds % 3600) // 60) + "m"
    seconds = str(seconds % 60) + "s"

    if hours.startswith("0"):
        if minutes.startswith("0"):
            return f"{seconds}"

        return f"{minutes} {seconds}"

    return f"{hours:<3} {minutes:<3} {seconds:<3}"


def convert_music(source_path, dest_path):
    """
    Convert music files from source folder to destination folder.

    This function searches for WAV files in the specified source folder,
    converts them to another format using FFmpeg, and saves the converted files
    in the specified destination folder. The function also displays the progress
    and results of the conversion process in the output text widget.

    Parameters:
    - source_path (str): The path to the source folder containing WAV files.
    - dest_path (str): The path to the destination folder where converted files will be saved.
    """

    start_time = round(default_timer())
    convert_button.config(state=tk.DISABLED)
    num_errors = 0
    num_success = 0
    error_log = []

    incomplete_files = glob(path_join(source_path, '**', '*.download'), recursive=True)
    all_wav_files = glob(path_join(source_path, '**', '*.wav'), recursive=True)

    complete_wav_files = {}
    for x in all_wav_files:
        if not any(x in string for string in incomplete_files):
            complete_wav_files.setdefault(x.split('/')[-1], x)

    for file in sorted(complete_wav_files.values()):
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
            output_text.see(tk.END)
            output_text.config(state=tk.DISABLED)

        except CalledProcessError as cpe:
            num_errors += 1
            if 'Invalid data' in cpe.stderr.decode("utf-8"):
                error_log.append({"file": file, "msg": f"Invalid data: {filename}"})
            else:
                error_log.append(
                    {"file": file, "msg": f"{filename}: {cpe.stderr.decode("utf-8")}"}
                )
            continue

        num_success += 1

    end_time = round(default_timer())
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "\n=== Finished Processing ===\n")
    output_text.insert(tk.END, f"Time spent: {convert_seconds(end_time - start_time)}\n")
    output_text.insert(tk.END, f"Found files: {len(complete_wav_files)}\n")
    output_text.insert(tk.END, f"Successful: {num_success}\n")
    output_text.insert(tk.END, f"Failed: {num_errors}\n")

    if num_errors > 0:
        output_text.insert(tk.END, "\nFailed files:\n")
        output_text.insert(tk.END, "\n".join([x['msg'] for x in error_log]) + "\n")
        line_decoration = '=' * 70
        output_text.insert(
            tk.END,
            f"\n\n{line_decoration}\nTo delete the erroneous files,"
            f" click the 'Delete Error Files' button.\n{line_decoration}"
        )
        delete_button.config(state=tk.NORMAL)
        delete_button['command'] = lambda: delete_error_files_popup(error_log)
        output_text.see(tk.END)

        # output_text.insert(
        #     tk.END, "\nTo delete the erroneous files, execute this command in a terminal:\n"
        # )
        # output_text.insert(tk.END, "rm " + " ".join([x['file'] for x in error_log]))

    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)
    convert_button.config(state=tk.NORMAL)


def browse_button(folder_var):
    """
    Open a file dialog window to select a folder and
    update the given folder variable with the selected path.

    Parameters:
    - folder_var: A tkinter.StringVar object representing
                  the variable to store the selected folder path.
    """

    folder_selected = filedialog.askdirectory()
    folder_var.set(folder_selected)


def convert_button():
    """
    Start the music conversion process.

    This function retrieves the input and output folder paths from the corresponding Entry widgets,
    clears the output text widget, and starts the conversion process in a separate thread.
    """

    # Clear the text in the output text widget
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.config(state=tk.DISABLED)

    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    # Run the conversion process in a separate thread
    threading.Thread(target=convert_music, args=(input_folder, output_folder)).start()


def exit_button():
    """
    Close the application.

    This function destroys the tkinter root window, effectively closing the application.
    """

    root.destroy()  # Close the Tkinter window
    sys_exit(0)  # Exit the Python program


# Create the main tkinter window
root = tk.Tk()
root.title("Music File Converter")

# Calculate the position to center the window on the screen
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_coordinate = (screen_width - WINDOW_WIDTH) // 2
y_coordinate = (screen_height - WINDOW_HEIGHT) // 2

# Set the window geometry and position
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")

# Set PADDING for all widgets
PADDING = 5

# Set the font size for all text widgets and labels
font_style = ("Monaco", 18)

# Frame to contain input elements
input_frame = tk.Frame(root)
input_frame.pack(padx=PADDING, pady=PADDING)

# Input folder selection
input_folder_var = tk.StringVar()

input_folder_label = tk.Label(input_frame, text="Input Folder:", font=font_style)
input_folder_label.grid(row=0, column=0, sticky="w", padx=PADDING, pady=PADDING)

input_folder_entry = tk.Entry(input_frame, textvariable=input_folder_var, font=font_style, width=50)
input_folder_entry.grid(row=0, column=1, padx=PADDING, pady=PADDING)

input_folder_button = tk.Button(
    input_frame, text="Browse", command=lambda: browse_button(input_folder_var), font=font_style)
input_folder_button.grid(row=0, column=2, padx=PADDING, pady=PADDING)

# Output folder selection
output_folder_var = tk.StringVar()

output_folder_label = tk.Label(input_frame, text="Output Folder:", font=font_style)
output_folder_label.grid(row=1, column=0, sticky="w", padx=PADDING, pady=PADDING)

output_folder_entry = tk.Entry(
    input_frame, textvariable=output_folder_var, font=font_style, width=50
)
output_folder_entry.grid(row=1, column=1, padx=PADDING, pady=PADDING)

output_folder_button = tk.Button(
    input_frame, text="Browse", command=lambda: browse_button(output_folder_var), font=font_style)
output_folder_button.grid(row=1, column=2, padx=PADDING, pady=PADDING)

# Button frame to contain Convert and Exit buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=PADDING)

BUTTON_FONT = ("Arial Rounded MT Bold", 20)
BUTTON_WIDTH = 15
BUTTON_HEIGHT = 1
BUTTON_PADDING_X = 30
BUTTON_PADDING_Y = 15

# Convert button
convert_button = tk.Button(
    button_frame, text="Convert", command=convert_button,
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT
)
convert_button.pack(side=tk.LEFT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)

# Delete Error Files button
delete_button = tk.Button(
    button_frame, text="Delete Error Files", command=lambda: delete_error_files_popup([]),
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=1, state=tk.DISABLED
)
delete_button.pack(side=tk.LEFT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)

# Exit button
exit_button = tk.Button(
    button_frame, text="Exit", command=exit_button,
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT
)
exit_button.pack(side=tk.LEFT, padx=BUTTON_PADDING_X, pady=BUTTON_PADDING_Y)

# Output text widget
output_text = tk.Text(root, font=font_style)
output_text.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

# Start the GUI event loop
root.mainloop()
