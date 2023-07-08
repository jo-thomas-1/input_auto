import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
from PIL.ImageTk import PhotoImage
from pynput.mouse import Listener, Button, Controller
from pynput.keyboard import Listener as KeyboardListener, KeyCode
import threading

class InputAutoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Input Auto")

        self.is_recording = False
        self.record_button = None
        self.text_area = None
        self.recorded_actions = []

        self.available_devices = {'Mouse': tk.BooleanVar(), 'Keyboard': tk.BooleanVar()}
        self.checkboxes = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        source_frame = tk.Frame(self.root)
        source_frame.pack(padx=10, pady=10, anchor=tk.W)

        self.setup_source_section(source_frame)
        
        self.record_button = tk.Button(self.root, text="Record", command=self.toggle_recording, relief=tk.RAISED, compound=tk.LEFT)
        self.record_button.pack(pady=10, padx=10, anchor=tk.W)
        self.set_record_button_icon("record")
        
        self.text_area = tk.Text(self.root, height=10, width=50)
        self.text_area.pack(padx=10, pady=5, anchor=tk.W)
        
    def setup_source_section(self, frame):
        source_frame = tk.LabelFrame(frame, text="Source", padx=10, pady=10)
        source_frame.pack(padx=0, pady=0, anchor=tk.W)
        
        for index, (device, value) in enumerate(self.available_devices.items()):
            checkbox = tk.Checkbutton(source_frame, text=device, variable=value, onvalue=True, offvalue=False)
            checkbox.grid(row=0, column=index, padx=5, sticky=tk.W)
            self.checkboxes[device] = checkbox
        
    def toggle_recording(self):
        if not self.is_recording:
            if any(value.get() for value in self.available_devices.values()):
                self.record_button.config(text="Stop Recording", relief=tk.SUNKEN)
                self.set_record_button_icon("stop")
                self.start_recording()
            else:
                self.show_error_message("Please select at least one input source.")
        else:
            self.record_button.config(text="Record", relief=tk.RAISED)
            self.set_record_button_icon("record")
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.recorded_actions = []
        self.text_area.delete('1.0', tk.END)
        
        threading.Thread(target=self.start_listener).start()
        
    def start_listener(self):
        with Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as mouse_listener, \
                KeyboardListener(on_press=self.on_key_press) as keyboard_listener:
            mouse_listener.join()
            keyboard_listener.join()
            
    def stop_recording(self):
        self.is_recording = False
        
    def on_move(self, x, y):
        if self.is_recording and self.available_devices['Mouse'].get():
            self.recorded_actions.append(f"Move - {x}, {y}")
            self.update_text_area()
        
    def on_click(self, x, y, button, pressed):
        if self.is_recording and self.available_devices['Mouse'].get():
            action = "Click" if pressed else "Release"
            self.recorded_actions.append(f"{action} - {x}, {y}")
            self.update_text_area()
            
    def on_scroll(self, x, y, dx, dy):
        if self.is_recording and self.available_devices['Mouse'].get():
            action = "Scroll Up" if dy > 0 else "Scroll Down"
            self.recorded_actions.append(f"{action} - {x}, {y}")
            self.update_text_area()
            
    def on_key_press(self, key):
        if self.is_recording and self.available_devices['Keyboard'].get():
            if hasattr(key, 'char'):
                self.recorded_actions.append(f"Key Press - {key.char}")
            else:
                self.recorded_actions.append(f"Key Press - {key}")
            self.update_text_area()
            
    def update_text_area(self):
        self.text_area.delete('1.0', tk.END)
        for action in self.recorded_actions:
            self.text_area.insert(tk.END, action + '\n')
            
    def show_error_message(self, message):
        messagebox.showerror("Error", message)
        
    def set_record_button_icon(self, icon):
        if icon == "record":
            image = Image.open("record.png")
            self.record_button.config(text="Record")
        elif icon == "stop":
            image = Image.open("stop.png")
            self.record_button.config(text="Stop")
        else:
            return
        
        image = ImageOps.fit(image, (15, 15), Image.Resampling.LANCZOS)
        photo = PhotoImage(image)
        self.record_button.config(image=photo, compound=tk.LEFT, padx=5)
        self.record_button.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = InputAutoGUI(root)
    root.mainloop()
