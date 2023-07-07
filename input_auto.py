import tkinter as tk
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

        self.available_devices = {'Mouse': False, 'Keyboard': False}
        self.checkboxes = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setup_source_section()
        
        self.record_button = tk.Button(self.root, text="Record", command=self.toggle_recording)
        self.record_button.pack(pady=10)
        
        self.text_area = tk.Text(self.root, height=10, width=50)
        self.text_area.pack(padx=10, pady=5)
        
    def setup_source_section(self):
        source_frame = tk.Frame(self.root)
        source_frame.pack(padx=10, pady=10)
        
        for index, (device, value) in enumerate(self.available_devices.items()):
            checkbox = tk.Checkbutton(source_frame, text=device, variable=self.available_devices[device], onvalue=True, offvalue=False)
            checkbox.grid(row=0, column=index, padx=5)
            self.checkboxes[device] = checkbox
        
    def toggle_recording(self):
        if not self.is_recording:
            self.record_button.config(text="Stop Recording")
            self.start_recording()
        else:
            self.record_button.config(text="Record")
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
        if self.is_recording and self.available_devices['Mouse']:
            pass
        
    def on_click(self, x, y, button, pressed):
        if self.is_recording and self.available_devices['Mouse']:
            action = "Click" if pressed else "Release"
            self.recorded_actions.append(f"{action} - {x}, {y}")
            self.update_text_area()
            
    def on_scroll(self, x, y, dx, dy):
        if self.is_recording and self.available_devices['Mouse']:
            action = "Scroll Up" if dy > 0 else "Scroll Down"
            self.recorded_actions.append(f"{action} - {x}, {y}")
            self.update_text_area()
            
    def on_key_press(self, key):
        if self.is_recording and self.available_devices['Keyboard']:
            if hasattr(key, 'char'):
                self.recorded_actions.append(f"Key Press - {key.char}")
            else:
                self.recorded_actions.append(f"Key Press - {key}")
            self.update_text_area()
            
    def update_text_area(self):
        self.text_area.delete('1.0', tk.END)
        for action in self.recorded_actions:
            self.text_area.insert(tk.END, action + '\n')

if __name__ == "__main__":
    root = tk.Tk()
    app = InputAutoGUI(root)
    root.mainloop()
