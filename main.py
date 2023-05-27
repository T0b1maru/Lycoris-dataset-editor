import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Lycoris-dataset-editor")
        self.pack(fill=tk.BOTH, expand=True)

        self.configure(bg='black')

        self.directory = None
        self.files = []

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.editing_tab = tk.Frame(self.notebook, bg='black')
        self.notebook.add(self.editing_tab, text="Editing")
        self.create_editing_tab()  # Initialize editing tab

        self.training_tab = tk.Frame(self.notebook, bg='black')
        self.notebook.add(self.training_tab, text="Training")
        self.create_training_tab()  # Initialize training tab

    def create_editing_tab(self):
        self.directory = None
        self.files = []

        self.entry_frame = tk.Frame(self.editing_tab, bg='black')
        self.entry_frame.pack(fill=tk.X)

        self.search_and_replace_label = tk.Label(self.entry_frame, text="Search and Replace:", bg='black', fg='white', anchor='w')
        self.search_and_replace_label.pack(side=tk.LEFT, fill=tk.X)

        self.entry = tk.Entry(self.entry_frame, bg='#333333', fg='white', insertbackground='white')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.change_to_label = tk.Label(self.entry_frame, text="    change to    ", bg='black', fg='white')
        self.change_to_label.pack(side=tk.LEFT)

        self.replacement = tk.Entry(self.entry_frame, bg='#333333', fg='white', insertbackground='white')
        self.replacement.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.replace_button = tk.Button(self.entry_frame, text="Replace Text", command=self.replace_text, bg='#333333', fg='white')
        self.replace_button.pack(side=tk.LEFT, pady=5, padx=5)

        self.append_prepend_frame = tk.Frame(self.editing_tab, bg='black')
        self.append_prepend_frame.pack(fill=tk.X)

        self.prepend_append_label = tk.Label(self.append_prepend_frame, text="Prepend/Append:", bg='black', fg='white', anchor='w')
        self.prepend_append_label.pack(side=tk.LEFT, fill=tk.X)

        self.append_prepend_entry = tk.Entry(self.append_prepend_frame, bg='#333333', fg='white', insertbackground='white')
        self.append_prepend_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.prepend_button = tk.Button(self.append_prepend_frame, text="Prepend", command=self.prepend_text, bg='#333333', fg='white')
        self.prepend_button.pack(side=tk.LEFT, pady=5, padx=5)

        self.append_button = tk.Button(self.append_prepend_frame, text="Append", command=self.append_text, bg='#333333', fg='white')
        self.append_button.pack(side=tk.LEFT, pady=5, padx=5)

        self.save_clear_frame = tk.Frame(self.editing_tab, bg='black')
        self.save_clear_frame.pack(fill=tk.X)

        self.save_button = tk.Button(self.save_clear_frame, text='Save current', command=self.save_current, bg='#333333', fg='white')
        self.save_button.pack(side=tk.LEFT, pady=5, padx=5)

        self.clear_button = tk.Button(self.save_clear_frame, text='Clear', command=self.clear, bg='#333333', fg='white')
        self.clear_button.pack(side=tk.LEFT, pady=5, padx=5)

        self.drop_target = tk.Label(self.editing_tab, text='Drop directory here', relief='solid', bg='black', fg='white')
        self.drop_target.pack(fill=tk.BOTH, expand=True)
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind('<<Drop>>', self.drop)

        # This will store a reference to each text widget and the file it's related to
        self.text_widgets = {}

    def create_training_tab(self):
        # Create the main training frame
        self.training_frame = tk.Frame(self.training_tab, bg='black')
        self.training_frame.pack(fill=tk.BOTH, expand=True)

        # Create two frames, one for the left column and one for the right
        self.training_frame_left = tk.Frame(self.training_frame, bg='black')
        self.training_frame_right = tk.Frame(self.training_frame, bg='black')

        # Arrange the frames in a grid
        self.training_frame_left.grid(row=1, column=0, sticky='nsew')
        self.training_frame_right.grid(row=1, column=1, sticky='nsew')

        # Make the columns share any extra space equally
        self.training_frame.grid_columnconfigure(0, weight=1)
        self.training_frame.grid_columnconfigure(1, weight=1)

        # Create save/load controls at the top of the tab
        save_load_frame = tk.Frame(self.training_frame, bg='black', pady=10)
        save_load_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')

        # Save controls
        save_frame = tk.Frame(save_load_frame, bg='black')
        save_frame.pack(side=tk.LEFT, fill=tk.X)

        save_label = tk.Label(save_frame, text="Save As:", bg='black', fg='white')
        save_label.pack(side=tk.LEFT)

        self.save_entry = tk.Entry(save_frame, bg='#333333', fg='white', insertbackground='white')
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        save_button = tk.Button(save_frame, text="Save Config", command=self.save_config)
        save_button.pack(side=tk.LEFT)

        # Load controls
        load_frame = tk.Frame(save_load_frame, bg='black')
        load_frame.pack(side=tk.LEFT, fill=tk.X)

        load_label = tk.Label(load_frame, text="Load:", bg='black', fg='white')
        load_label.pack(side=tk.LEFT)

        self.load_combo = ttk.Combobox(load_frame)
        self.load_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        load_button = tk.Button(load_frame, text="Load Config", command=self.load_config)
        load_button.pack(side=tk.LEFT)

        self.update_config_list()

        labels = ["Lora Name", "Network (dim)", "Network (alpha)", "Conv (dim)",
                  "Conv (alpha)", "Batch size", "Epochs", "Bucket resolution", "Flip",
                  "Shuffle Captions"]

        entries = {}

        # Create the Lora type dropdown outside the loop
        lora_frame = tk.Frame(self.training_frame_left, bg='black')
        lora_frame.pack(fill=tk.X)  # Use tk.X here to fill horizontally within the parent frame
        lora_label = tk.Label(lora_frame, text="Lora Type:", bg='black', fg='white')
        lora_label.pack(side=tk.LEFT)

        self.lora_type = ttk.Combobox(lora_frame, values=["Kohya Locon", "LyCORIS/LoCon", "LyCORIS/LoHa"])
        self.lora_type.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lora_type.current(0)  # Set the first option as default

        for i, label in enumerate(labels):
            # Choose which frame to pack into based on the index
            parent_frame = self.training_frame_left if i < len(labels) / 2 else self.training_frame_right

            frame = tk.Frame(parent_frame, bg='black')
            frame.pack(fill=tk.X)  # Use tk.X here to fill horizontally within the parent frame

            # Create label
            label_widget = tk.Label(frame, text=f"{label}:", bg='black', fg='white')
            label_widget.pack(side=tk.LEFT)

            # Create entry
            entries[label] = tk.Entry(frame, bg='#333333', fg='white', insertbackground='white')
            entries[label].pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.training_entries = entries  # Save references to entry widgets

    def save_config(self):
        config_name = self.save_entry.get()
        if not config_name:
            return  # Don't save if there's no name

        # Serialize state
        state = {name: entry.get() for name, entry in self.training_entries.items()}
        state['lora_type'] = self.lora_type.get()

        # Save to a file
        with open(f"{config_name}.json", "w") as f:
            json.dump(state, f)

        self.update_config_list()

    def load_config(self):
        config_name = self.load_combo.get()
        if not config_name:
            return  # Don't load if there's no selected config

        # Load from a file
        with open(f"{config_name}.json", "r") as f:
            state = json.load(f)

        # Restore state
        for name, entry in self.training_entries.items():
            entry.delete(0, tk.END)  # Clear existing text
            entry.insert(0, state.get(name, ""))  # Restore saved text

        self.lora_type.set(state.get('lora_type', ""))  # Restore saved Lora type

    def update_config_list(self):
        configs = [file[:-5] for file in os.listdir() if file.endswith(".json")]
        self.load_combo['values'] = configs

    def drop(self, event):
        # event.data is a list of filenames (one directory in your case)
        # directories and filenames contain forward slashes regardless of the OS
        self.directory = event.data
        if not os.path.isdir(self.directory):
            self.directory = os.path.dirname(self.directory)
        self.files = [f for f in os.listdir(self.directory) if f.endswith('.txt')]

        # remove previous entries
        for widget in self.editing_tab.winfo_children():
            if isinstance(widget, tk.Entry) and widget not in [self.entry, self.replacement, self.append_prepend_entry]:
                widget.destroy()

        for file in self.files:
            with open(os.path.join(self.directory, file), 'r') as f:
                content = f.read()
            text_widget = tk.Entry(self.editing_tab, width=1, bg='#333333', fg='white', insertbackground='white')
            text_widget.insert(tk.END, content)
            text_widget.pack(fill=tk.X, padx=30)  # Add padding here

            # Associate text_widget with its file
            self.text_widgets[text_widget] = file
        self.drop_target.pack_forget()  # hide the drop target

    def refresh_fields(self):
        # Remove previous text widgets
        for widget in self.editing_tab.winfo_children():
            widget.destroy()

        # Create new text widgets
        for file in self.files:
            with open(os.path.join(self.directory, file), 'r') as f:
                content = f.read()
            text_widget = tk.Entry(self.editing_tab, width=1, bg='#333333', fg='white', insertbackground='white')
            text_widget.insert(tk.END, content)
            text_widget.pack(fill=tk.X)

            # Associate text_widget with its file
            self.text_widgets[text_widget] = file

        self.drop_target.pack_forget()  # Hide the drop target

    def clear(self):
        # Remove previous text widgets
        for widget in list(self.text_widgets.keys()):  # Iterate over a copy of the keys to avoid modification during iteration
            widget.destroy()
            del self.text_widgets[widget]

        # Hide the drop target
        self.drop_target.pack_forget()

        # Recreate the drop target
        self.drop_target = tk.Label(self.editing_tab, text='Drop directory here', relief='solid', bg='black', fg='white')
        self.drop_target.pack(fill=tk.BOTH, expand=True)
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind('<<Drop>>', self.drop)

        self.directory = None
        self.files = []


    def save_current(self):
        for widget, filename in self.text_widgets.items():
            with open(os.path.join(self.directory, filename), 'w') as f:
                f.write(widget.get())

    def replace_text(self):
        self.edit_text(self.entry.get(), self.replacement.get())
        self.refresh_fields()

    def prepend_text(self):
        self.edit_text("", self.append_prepend_entry.get() + "{content}")
        self.refresh_fields()

    def append_text(self):
        self.edit_text("", "{content}" + self.append_prepend_entry.get())
        self.refresh_fields()

    def edit_text(self, search_term, replacement):
        if not self.directory or not self.files:
            return

        for filename in self.files:
            with open(os.path.join(self.directory, filename), 'r') as file:
                text = file.read()
            new_text = text.replace(search_term, replacement) if "{content}" not in replacement else replacement.format(content=text)
            if text != new_text:  # Only write back if the text changed
                with open(os.path.join(self.directory, filename), 'w') as file:
                    file.write(new_text)

        self.update_display()  # Update the display without loading the files again

    def update_display(self):
        # remove previous entries
        for widget in self.editing_tab.winfo_children():
            if isinstance(widget, tk.Entry) and widget not in [self.entry, self.replacement, self.append_prepend_entry]:
                widget.destroy()

        for file in self.files:
            with open(os.path.join(self.directory, file), 'r') as f:
                content = f.read()
            text_widget = tk.Entry(self.editing_tab, width=1, bg='#333333', fg='white', insertbackground='white')
            text_widget.insert(tk.END, content)
            text_widget.pack(fill=tk.X)

root = TkinterDnD.Tk()
root.geometry("800x600")
app = Application(master=root)
app.mainloop()