import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
from PIL.ImageTk import PhotoImage
from pynput.mouse import Listener, Button, Controller
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, KeyCode, Key
import threading
import time

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

        self.run_loop_thread = None
        self.should_terminate = False
        
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

        # remove stop button click from recorded actions
        if self.recorded_actions[-1].startswith('Release'):
            self.recorded_actions.pop()
            self.recorded_actions.pop()
            self.update_text_area()
        
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

    def clear_actions(self):
        self.recorded_actions = []
        self.update_text_area()

        self.current_loop_var.set(0)
        self.remaining_loops_var.set(0)

    def update_text_area(self):
        self.text_area.delete('1.0', tk.END)
        for action in self.recorded_actions:
            self.text_area.insert(tk.END, action + '\n')

    def start_loop(self):
        count = self.count_var.get()
        
        self.current_loop_var.set(0)
        self.remaining_loops_var.set(count)
        self.root.update_idletasks()

        self.should_terminate = False  # Reset the termination flag
        self.run_loop_thread = threading.Thread(target=self.run_loop, args=(count,))
        self.run_loop_thread.start()

    def stop_loop(self):
        self.should_terminate = True

        # Terminate the run_loop thread if it is running
        if self.run_loop_thread is not None and self.run_loop_thread.is_alive():
            self.run_loop_thread.terminate()

        # Stop the keyboard listener if it is running
        if self.keyboard_listener is not None and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()

        if not self.run_loop_thread.is_alive():
            print("loop terminated")
            print("current loop:", self.current_loop_var.get())
            print("remaining loops:", self.remaining_loops_var.get())

            messagebox.showinfo("Information", "Input action loop terminated")

    def on_esc_key_press(self, key):
        print("command: escape input loop")
        if key == Key.esc:
            self.stop_loop()

    def run_loop(self, count):
        keyboard_listener = Listener(on_press=self.on_esc_key_press)
        keyboard_listener.start()

        messagebox.showwarning("Warning", "Starting input loop execution. Please avoid using input devices \
            until loop completion. Press the Escape (Esc) key to exit the loop.")

        print("executing loop")

        for i in range(count):
            time.sleep(1)
            if self.should_terminate:
                break
            self.current_loop_var.set(i + 1)
            self.remaining_loops_var.set(count - i - 1)
            self.root.update_idletasks()
            self.perform_recorded_steps()

        print("input action loop completed")

        messagebox.showinfo("Information", "Input action loop completed")

    def perform_recorded_steps(self):
        mouse = Controller()
        keyboard = KeyboardController()

        for action in self.recorded_actions:
            # Remove leading/trailing whitespace and split the action into components
            components = action.strip().split('-')

            if len(components) < 2:
                continue

            command = components[0].strip()
            args = components[1].strip()

            if command.startswith('\\'):
                # check and execute special command
                continue
            else:
                if command == 'Click':
                    x, y = map(int, args.split(','))
                    mouse.position = (x, y)
                    mouse.click(Button.left)
                elif command == 'Release':
                    x, y = map(int, args.split(','))
                    mouse.position = (x, y)
                    mouse.release(Button.left)
                elif command == 'Scroll Up':
                    x, y = map(int, args.split(','))
                    mouse.position = (x, y)
                    mouse.scroll(0, -1)
                elif command == 'Scroll Down':
                    x, y = map(int, args.split(','))
                    mouse.position = (x, y)
                    mouse.scroll(0, 1)
                elif command == 'Key Press':
                    print("key press -", args)
                    if args.startswith('<') and args.endswith('>'):
                        print("key press <>")
                        special_key = KeyCode.from_vk(int(args[1:-1]))
                        keyboard.press(special_key)
                        keyboard.release(special_key)
                    elif args.startswith('Key.'):
                        print("args")
                        keyboard.press(eval(args))
                        keyboard.release(eval(args))
                    # Add more special key cases as needed
                    else:
                        # Handle normal characters
                        try:
                            keyboard.type(args[1])
                        except Exception as e:
                            keyboard.type('-')

            time.sleep(0.1)

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
