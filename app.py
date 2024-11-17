import pyautogui
import tkinter as tk
from tkinter import messagebox
from time import sleep as s
import threading
from pynput import keyboard
import random
import pyperclip

# Global variables to store mouse positions and comment position
click_positions = []
comment_position = None
recording = False

# Function to start recording mouse clicks
def start_recording():
    global recording
    recording = True
    click_positions.clear()  # Clear previous click positions
    record_button.config(state=tk.DISABLED)  # Disable start button
    stop_button.config(state=tk.NORMAL)      # Enable stop button
    instruction_label.config(text="Recording... Press 'C' to record a click, 'W' to select comment position, 'X' to stop.")
    
    # Start a separate thread to listen for keyboard inputs
    threading.Thread(target=listen_for_keypress).start()

# Function to stop recording mouse clicks
def stop_recording():
    global recording
    recording = False
    stop_button.config(state=tk.DISABLED)   # Disable stop button
    record_button.config(state=tk.NORMAL)   # Enable start button
    instruction_label.config(text="Recording stopped. Click 'Execute' to run automation.")
    
    # Show recorded clicks in the textbox
    recorded_text.delete(1.0, tk.END)
    for pos in click_positions:
        recorded_text.insert(tk.END, f"{pos[0]}, {pos[1]}\n")

# Function to listen for the 'C', 'W', and 'X' keypresses
def listen_for_keypress():
    global comment_position
    
    def on_press(key):
        global recording, comment_position
        try:
            if key.char == 'c':
                # Record mouse position when 'C' key is pressed
                x, y = pyautogui.position()
                click_positions.append((x, y))
                print(f"Recorded click at: {x}, {y}")
            elif key.char == 'w':
                # Record mouse position for the comment when 'W' key is pressed
                comment_position = pyautogui.position()
                print(f"Comment position recorded at: {comment_position}")
            elif key.char == 'x':
                # Stop recording when 'X' key is pressed
                stop_recording()
                return False  # Stop the listener
        except AttributeError:
            pass

    # Listen for keypresses
    with keyboard.Listener(on_press=on_press) as listener:
        while recording:
            s(0.1)  # Small sleep to allow other processes to run
        listener.stop()  # Stop the listener once recording is finished

# Function to simulate human-like mouse movement with adjustable speed
def move_mouse_smoothly(x, y, duration):
    start_x, start_y = pyautogui.position()
    steps = max(10, int(duration * 60))  # Number of steps based on duration, minimum steps set to 10 for fast speed
    for step in range(steps + 1):
        t = step / steps
        # Add some random jitter to make it human-like
        current_x = int(start_x + (x - start_x) * t + random.uniform(-2, 2))
        current_y = int(start_y + (y - start_y) * t + random.uniform(-2, 2))
        pyautogui.moveTo(current_x, current_y)
        s(duration / steps)
    
    # If very low duration is set, it should move faster
    if duration < 0.2:
        pyautogui.moveTo(x, y, duration=duration/5)  # Adjust for fast movement

# Function to set the clipboard text and paste it
def paste_comment(comment):
    pyperclip.copy(comment)  # Copy comment to clipboard
    pyautogui.hotkey('ctrl', 'v')  # Paste the clipboard content
    s(random.uniform(0.01, 0.03))  # Small random delay

# Function to execute the automation script
def execute_script():
    if not click_positions:
        messagebox.showwarning("Error", "No click positions recorded.")
        return

    if not comment_position:
        messagebox.showwarning("Error", "No position selected for the comment (Press 'W' to select a place).")
        return

    comment = "#RanilTheEducatedChoice"  # Fixed comment
    try:
        howmanytimes = int(times_entry.get())
    except ValueError:
        messagebox.showwarning("Error", "Please enter a valid number for how many times.")
        return
    
    try:
        delay = float(delay_entry.get())  # Get the delay value from the user
    except ValueError:
        messagebox.showwarning("Error", "Please enter a valid delay in seconds.")
        return
    
    mouse_speed = mouse_speed_slider.get() / 10.0  # Convert slider value to seconds
    
    # Perform the automated clicks and pasting
    for _ in range(howmanytimes):
        for pos in click_positions:
            move_mouse_smoothly(pos[0], pos[1], duration=mouse_speed)  # Move to recorded positions
            pyautogui.click()
            s(delay)  # Wait for the specified delay

        # Move to the comment position and paste the comment
        move_mouse_smoothly(comment_position[0], comment_position[1], duration=mouse_speed)
        pyautogui.click()
        s(delay)
        paste_comment(comment)
        pyautogui.press('enter')  # Assuming 'enter' submits the comment

# Creating the GUI
root = tk.Tk()
root.title("Automation Tool")

# Instruction label
instruction_label = tk.Label(root, text="Click 'Start' to begin recording mouse clicks.")
instruction_label.pack(pady=10)

# Button to start recording mouse clicks
record_button = tk.Button(root, text="Start Recording", command=start_recording)
record_button.pack(pady=5)

# Button to stop recording mouse clicks
stop_button = tk.Button(root, text="Stop Recording", state=tk.DISABLED, command=stop_recording)
stop_button.pack(pady=5)

# Text box to display recorded coordinates
recorded_text = tk.Text(root, height=10, width=40)
recorded_text.pack(pady=10)

# Entry for how many times to execute the action
tk.Label(root, text="How many times to comment:").pack(pady=5)
times_entry = tk.Entry(root, width=10)
times_entry.pack(pady=5)

# Entry for delay between actions
tk.Label(root, text="Delay between actions (seconds):").pack(pady=5)
delay_entry = tk.Entry(root, width=10)
delay_entry.pack(pady=5)

# Slider for mouse movement speed
tk.Label(root, text="Mouse movement speed (0.1s - 10s):").pack(pady=5)
mouse_speed_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, label="Mouse Speed")
mouse_speed_slider.set(10)  # Default value
mouse_speed_slider.pack(pady=5)

# Button to execute the automation script
execute_button = tk.Button(root, text="Execute", command=execute_script)
execute_button.pack(pady=10)

# Run the GUI event loop
root.mainloop()
