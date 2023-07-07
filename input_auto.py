import tkinter as tk
from pynput.mouse import Listener, Button, Controller

class MouseAutoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Auto")
        
        self.is_recording = False
        self.record_button = None
        self.text_area = None
        self.recorded_actions = []
        
        self.setup_ui()
        
    def setup_ui(self):
        self.record_button = tk.Button(self.root, text="Record", command=self.toggle_recording)
        self.record_button.pack(pady=10)
        
        self.text_area = tk.Text(self.root, height=10, width=50)
        self.text_area.pack(padx=10, pady=5)
        
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
        
        with Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            listener.join()
            
    def stop_recording(self):
        self.is_recording = False
        
    def on_move(self, x, y):
        if self.is_recording:
            self.recorded_actions.append(f"Move - {x}, {y}")
            self.update_text_area()
            
    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            action = "Click" if pressed else "Release"
            self.recorded_actions.append(f"{action} - {x}, {y}")
            self.update_text_area()
            
    def on_scroll(self, x, y, dx, dy):
        if self.is_recording:
            action = "Scroll Up" if dy > 0 else "Scroll Down"
            self.recorded_actions.append(f"{action} - {x}, {y}")
            self.update_text_area()
            
    def update_text_area(self):
        self.text_area.delete('1.0', tk.END)
        for action in self.recorded_actions:
            self.text_area.insert(tk.END, action + '\n')

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseAutoGUI(root)
    root.mainloop()
