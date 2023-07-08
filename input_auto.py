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
        self.mouse_listener = None
        self.keyboard_listener = None

        self.available_devices = {'Mouse': tk.BooleanVar(), 'Keyboard': tk.BooleanVar()}
        self.checkboxes = {}
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        
    def setup_ui(self):
        source_frame = tk.Frame(self.root)
        source_frame.pack(padx=10, pady=10, anchor=tk.W, fill=tk.X)

        self.setup_source_section(source_frame)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, anchor=tk.W)

        self.record_button = tk.Button(button_frame, text="Record", command=self.toggle_recording, relief=tk.RAISED, compound=tk.LEFT)
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_actions, relief=tk.RAISED, compound=tk.LEFT)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.set_record_button_icon("record")

        self.text_area = tk.Text(self.root, height=10, width=50)
        self.text_area.pack(padx=10, pady=5, anchor=tk.W, fill=tk.X)

        # Add Loop section
        loop_section = tk.LabelFrame(self.root, text="Loop", padx=10, pady=10)
        loop_section.pack(padx=10, pady=10, anchor=tk.W, fill=tk.X)

        # Row 1: Numeric Input and Loop Button
        row1 = tk.Frame(loop_section)
        row1.pack(padx=10, pady=5, anchor=tk.W)

        self.count_var = tk.IntVar()
        count_entry = tk.Spinbox(row1, from_=1, to=50, width=3, textvariable=self.count_var)
        count_entry.pack(side=tk.LEFT, padx=5)

        loop_button = tk.Button(row1, text="Loop", command=self.start_loop)
        loop_button.pack(side=tk.LEFT, padx=5)

        # Row 2: Current Loop
        row2 = tk.Frame(loop_section)
        row2.pack(padx=10, pady=2, anchor=tk.W)
        self.current_loop_var = tk.IntVar()
        current_loop_label = tk.Label(row2, text="Current loop: ")
        current_loop_label.pack(side=tk.LEFT)
        current_loop_value = tk.Label(row2, textvariable=self.current_loop_var)
        current_loop_value.pack(side=tk.LEFT)

        # Row 3: Remaining Loops
        row3 = tk.Frame(loop_section)
        row3.pack(padx=10, pady=2, anchor=tk.W)
        self.remaining_loops_var = tk.IntVar()
        remaining_loops_label = tk.Label(row3, text="Remaining loops: ")
        remaining_loops_label.pack(side=tk.LEFT)
        remaining_loops_value = tk.Label(row3, textvariable=self.remaining_loops_var)
        remaining_loops_value.pack(side=tk.LEFT)
        
    def setup_source_section(self, frame):
        source_frame = tk.LabelFrame(frame, text="Source", padx=10, pady=10)
        source_frame.pack(padx=0, pady=0, anchor=tk.W, fill=tk.X)
        
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
        
        self.mouse_listener = Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
    def start_listener(self):
        with Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as mouse_listener, \
                KeyboardListener(on_press=self.on_key_press) as keyboard_listener:
            mouse_listener.join()
            keyboard_listener.join()
            
    def stop_recording(self):
        self.is_recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        
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

    def clear_actions(self):
        self.recorded_actions = []
        self.update_text_area()

    def update_text_area(self):
        self.text_area.delete('1.0', tk.END)
        for action in self.recorded_actions:
            self.text_area.insert(tk.END, action + '\n')

        # Update Current loop and Remaining loops values
        self.current_loop_var.set(current_loop_value)
        self.remaining_loops_var.set(remaining_loops_value)

    def start_loop(self):
        count = self.count_var.get()
        # Perform loop operation using the 'count' value

    def cleanup(self):
        if self.is_recording:
            self.stop_recording()
            self.mouse_listener.join()
            self.keyboard_listener.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InputAutoGUI(root)
    root.resizable(False, False)
    root.mainloop()
