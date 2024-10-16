import cv2
import numpy as np
import pyautogui
import pydirectinput
import keyboard
import time
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

# Initialize toggle and running state
running = False
stop_script = False
clicked = False
center_x, center_y = None, None

# Function to upload an image
def upload_image():
    global template, h, w, file_name_label
    file_path = tk.filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        template = cv2.imread(file_path, cv2.IMREAD_COLOR)
        h, w = template.shape[:2]
        file_name_label.config(text=f"Selected File: {file_path.split('/')[-1]}")

# Create GUI using Tkinter
root = tk.Tk()
root.title("ImageCL")
root.configure(bg='#2e2e2e')  # Set dark grey background
root.geometry("300x150")

# Create a label to display the file name
file_name_label = ttk.Label(root, text="No file selected", background='#2e2e2e', foreground='white')
file_name_label.pack(pady=10)

# Create a button to upload an image
button_frame = tk.Frame(root, background='#2e2e2e')
button_frame.pack(pady=10)

upload_button = tk.Button(button_frame, text="Upload Image", command=upload_image, bg='#4a4a4a', fg='white')
upload_button.grid(row=0, column=0, padx=5)

start_button = tk.Button(button_frame, text="Toggle Scan(F1)", command=lambda: start_scan(), bg='#4a4a4a', fg='white')
start_button.grid(row=0, column=1, padx=5)

# Create a textbox to adjust threshold
threshold_label = tk.Label(button_frame, text="Threshold:", bg='#2e2e2e', fg='white')
threshold_label.grid(row=0, column=2, padx=5)

threshold_entry = tk.Entry(button_frame, width=5)
threshold_entry.insert(0, '0.8')  # Default value
threshold_entry.grid(row=0, column=3, padx=5)

# Warning label if user tries to change threshold while scanning
warning_label = ttk.Label(root, text='', background='#2e2e2e', foreground='red')
warning_label.pack()

# Create a button to start the scan
def start_scan():
    global running, template
    if 'template' not in globals():
        file_name_label.config(text="No file selected. Please upload an image before starting the scan.")
        return
    if running:
        running = False
        print("Script is now OFF")
        start_button.config(bg='#4a4a4a', fg='white')
        threshold_entry.config(state='normal')
        warning_label.config(text='')
    else:
        running = True
        print("Script is now ON")
        start_button.config(bg='#3cb043', fg='white')
        threshold_entry.config(state='disabled')  # Green color when running

# Set up toggle (F1) to start the scan
keyboard.add_hotkey('F1', start_scan)

# Set up quit (F2) to stop the script
keyboard.add_hotkey('F2', lambda: quit_script())

# Create a label to display the detection output
detection_image_label = ttk.Label(root, background='#2e2e2e')

# Quit function to stop the script
def quit_script():
    global stop_script
    stop_script = True
    root.quit()
    print("Script is now quitting")

# Main loop to run detection
def main_loop():
    global running, clicked, center_x, center_y, detection_image_label
    if running and not stop_script:
        # Take a screenshot and proceed with detection
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Convert the screenshot to grayscale
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Get the threshold value from the entry box
        try:
            threshold = float(threshold_entry.get())
            warning_label.config(text='')
        except ValueError:
            threshold = 0.8  # Default threshold if input is invalid
            threshold_entry.delete(0, tk.END)
            threshold_entry.insert(0, '0.8')
            warning_label.config(text='Invalid threshold value. Reverted to 0.8')

        # Template matching
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        if loc[0].size > 0:
            pt = list(zip(*loc[::-1]))[0]  # Only take the first detection
            if not clicked or (center_x != pt[0] + w // 2 or center_y != pt[1] + h // 2):
                cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)  # Highlight detected area in red
                center_x, center_y = pt[0] + w // 2, pt[1] + h // 2
                pydirectinput.moveTo(center_x, center_y, duration=0.01)  # Even faster movement
                time.sleep(0.005)  # Smaller delay before confirming position
                pydirectinput.moveTo(center_x + 1, center_y + 1, duration=0.005)  # Faster nudge to ensure position is registered
                pydirectinput.moveTo(center_x, center_y)
                print(f"Teleporting to ({center_x}, {center_y})")
                time.sleep(0.005)  # Further reduced delay for faster execution
                pydirectinput.mouseDown()
                time.sleep(0.005)  # Shorter delay for even quicker clicks
                pydirectinput.mouseUp()
                print(f"Clicked at ({center_x}, {center_y})")
                clicked = True
        else:
            clicked = False  # Reset clicked to False if no detection

        # Convert the screenshot to display in the GUI only when running and after detection
        if running and loc[0].size > 0:
            # Draw the red border on the detected area
            cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)  # Highlight detected area in red
            # Only update GUI with screenshot that includes the red border
            screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
            screenshot_pil = Image.fromarray(screenshot_rgb)
            screenshot_pil.thumbnail((400, 200))  # Resize for display in the GUI
            screenshot_tk = ImageTk.PhotoImage(screenshot_pil)

            # Update the detection image label with only the detected red border
            detection_image_label.config(image=screenshot_tk)
            detection_image_label.image = screenshot_tk
            root.geometry("300x350")
            detection_image_label.pack(pady=10)
    if not running:
        root.geometry("300x150")
        detection_image_label.pack_forget()

    root.after(10, main_loop)  # Run the main loop again after 10 ms

# Start the main loop
root.after(10, main_loop)
root.mainloop()

cv2.destroyAllWindows()
print("Script has exited cleanly")