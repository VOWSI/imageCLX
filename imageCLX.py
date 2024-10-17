import cv2
import numpy as np
import pyautogui
import pydirectinput
import keyboard
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import queue
import sys
import os

# Helper function to find resource files
def resource_path(relative_path):
    try:
        # If running in a PyInstaller bundle
        base_path = sys._MEIPASS
    except AttributeError:
        # If running directly as a script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Initialize toggle and running state
class ImageDetectionApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.display_on = True
        self.default_reset = True  # Default reset toggle to prevent repetitive resets
        self.stop_script = threading.Event()
        self.clicked = False
        self.center_x, self.center_y = None, None
        self.threshold = 0.8
        self.speed = 100
        self.template = None
        self.result_queue = queue.Queue(maxsize=1)
        self.lock = threading.Lock()  # Lock to prevent race conditions during toggle
        self.setup_gui()
        self.start_threads()

    def setup_gui(self):
        self.root.resizable(False, False)
        self.root.title("ImageCLX")
        self.root.configure(bg='#2e2e2e')
        self.root.geometry("400x210")
        self.root.iconbitmap(resource_path('mouse.ico'))  # Set custom icon for the top left corner

        self.file_name_label = ttk.Label(self.root, text="No file selected", background='#2e2e2e', foreground='white')
        self.file_name_label.pack(pady=10)

        control_frame = tk.Frame(self.root, background='#2e2e2e')
        control_frame.pack()

        upload_button = tk.Button(control_frame, text="Upload Image", command=self.upload_image, bg='#4a4a4a', fg='white')
        upload_button.grid(row=0, column=0, padx=10, pady=5)

        self.display_button = tk.Button(control_frame, text="Toggle Display", command=self.toggle_display, bg='#4a4a4a', fg='white')
        self.display_button.grid(row=0, column=1, padx=10, pady=5)

        threshold_label = tk.Label(control_frame, text="Threshold:", bg='#2e2e2e', fg='white')
        threshold_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')

        self.threshold_entry = tk.Entry(control_frame, width=5)
        self.threshold_entry.insert(0, '0.8')
        self.threshold_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        speed_label = tk.Label(control_frame, text="Speed (ms):", bg='#2e2e2e', fg='white')
        speed_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

        self.speed_entry = tk.Entry(control_frame, width=5)
        self.speed_entry.insert(0, '100')
        self.speed_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        self.start_button = tk.Button(self.root, text="Toggle Scan(F1)", command=self.start_scan, bg='#4a4a4a', fg='white')
        self.start_button.pack(pady=10)

        self.warning_label = tk.Label(self.root, text='', bg='#2e2e2e', fg='red')
        self.warning_label.pack()

        self.detection_image_label = ttk.Label(self.root, background='#2e2e2e')

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.template = cv2.imread(file_path, cv2.IMREAD_COLOR)
            self.template = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
            self.h, self.w = self.template.shape[:2]
            self.file_name_label.config(text=f"Selected File: {file_path.split('/')[-1]}")

    def start_scan(self):
        with self.lock:
            print("start_scan called")
            if self.template is None:
                self.file_name_label.config(text="No file selected. Please upload an image before starting the scan.")
                return

            try:
                self.threshold = float(self.threshold_entry.get())
                if self.threshold < 0 or self.threshold > 1:
                    raise ValueError
                self.warning_label.config(text='')
                print("Threshold set to:", self.threshold)
            except ValueError:
                self.threshold_entry.delete(0, tk.END)
                self.threshold_entry.insert(0, '0.8')
                self.warning_label.config(text='Threshold must be between 0 and 1. Reverted to 0.8')
                print("Threshold value error, reverted to 0.8")
                self.threshold = 0.8
                return

            try:
                self.speed = int(self.speed_entry.get())
                if self.speed <= 0:
                    raise ValueError
                self.warning_label.config(text='')
                print("Speed set to:", self.speed)
            except ValueError:
                self.speed_entry.delete(0, tk.END)
                self.speed_entry.insert(0, '100')
                self.warning_label.config(text='Speed must be an int > 0. Reverted to 100')
                print("Speed value error, reverted to 100")
                self.speed = 100
                return

            if self.running:
                self.running = False
                print("Script is now OFF")
                self.start_button.config(bg='#4a4a4a', fg='white')
                self.threshold_entry.config(state='normal')
                self.speed_entry.config(state='normal')
                self.default_reset = True
            else:
                self.running = True
                print("Script is now ON")
                self.start_button.config(bg='#3cb043', fg='white')
                self.threshold_entry.config(state='disabled')
                self.speed_entry.config(state='disabled')

    def reset_to_default(self):
        if self.default_reset:
            print("reset_to_default called")
            self.warning_label.config(text='')
            self.detection_image_label.pack_forget()
            self.detection_image_label.config(image='')
            self.root.geometry("400x210")
            self.result_queue = queue.Queue(maxsize=1)
            self.clicked = False
            self.center_x, self.center_y = None, None
            self.default_reset = False

    def toggle_display(self):
        self.display_on = not self.display_on
        print(f"toggle_display called, display_on is now {self.display_on}")
        if self.display_on:
            self.display_button.config(bg='#4a4a4a', fg='white')
        else:
            self.display_button.config(bg='#B22222', fg='white')
            self.reset_to_default()
        print(f"Display is now {'ON' if self.display_on else 'OFF'}")

    def quit_script(self):
        print("quit_script called")
        self.stop_script.set()
        self.running = False
        self.reset_to_default()
        self.root.quit()
        print("Script is now quitting")

    def run_detection(self):
        while not self.stop_script.is_set():
            if self.running:
                print("run_detection: main_loop running")
                self.main_loop()
            self.stop_script.wait(self.speed / 1000.0)

    def main_loop(self):
        if self.running and not self.stop_script.is_set():
            print("main_loop called")
            screenshot = pyautogui.screenshot()
            screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(screenshot_gray, self.template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= self.threshold)

            if loc[0].size > 0:
                pt = list(zip(*loc[::-1]))[0]
                if not self.result_queue.full():
                    self.result_queue.put((screenshot_bgr, pt))
                if not self.clicked or (self.center_x != pt[0] + self.w // 2 or self.center_y != pt[1] + self.h // 2):
                    self.center_x, self.center_y = pt[0] + self.w // 2, pt[1] + self.h // 2
                    if self.running and self.center_x is not None and self.center_y is not None:
                        try:
                            pydirectinput.moveTo(self.center_x, self.center_y, duration=0)
                            pydirectinput.moveTo(self.center_x + 1, self.center_y + 1, duration=0.0)
                            pydirectinput.moveTo(self.center_x, self.center_y)
                            pydirectinput.mouseDown()
                            pydirectinput.mouseUp()
                            print(f"Clicked at ({self.center_x}, {self.center_y})")
                            self.clicked = True
                        except TypeError:
                            print("Mouse movement error: center_x or center_y is None")
            else:
                self.clicked = False

    def update_gui(self):
        if self.display_on and not self.result_queue.empty() and self.running:
            try:
                screenshot_bgr, pt = self.result_queue.get_nowait()
                cv2.rectangle(screenshot_bgr, pt, (pt[0] + self.w, pt[1] + self.h), (0, 0, 255), 2)
                screenshot_rgb = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2RGB)
                screenshot_pil = Image.fromarray(screenshot_rgb)
                screenshot_pil.thumbnail((400, 200))
                screenshot_tk = ImageTk.PhotoImage(screenshot_pil)

                self.detection_image_label.config(image=screenshot_tk)
                self.detection_image_label.image = screenshot_tk
                self.root.geometry("400x410")
                self.detection_image_label.pack()
                self.warning_label.config(text='Last Match:')
                print("update_gui: Last Match displayed")
            except queue.Empty:
                pass
        elif self.default_reset:
            print("update_gui: reset_to_default called")
            self.reset_to_default()
        self.root.after(self.speed, self.update_gui)

    def start_threads(self):
        print("start_threads called")
        detection_thread = threading.Thread(target=self.run_detection)
        detection_thread.daemon = True
        detection_thread.start()
        self.root.after(10, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDetectionApp(root)
    keyboard.add_hotkey('F1', app.start_scan)
    keyboard.add_hotkey('F2', app.quit_script)
    root.mainloop()
    cv2.destroyAllWindows()
