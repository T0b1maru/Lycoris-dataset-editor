import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk
import tkinter.messagebox as messagebox
import shutil
import subprocess

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Lycoris-dataset-editor")
        self.pack(fill=tk.BOTH, expand=True)

        self.dir_path = "/run/media/t0b1maru/2TB_Drive/Pictures/Scraped"

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

        # New "Prepare" tab
        self.prepare_tab = tk.Frame(self.notebook, bg='black')
        self.notebook.add(self.prepare_tab, text="Prepare")
        self.create_prepare_tab()
        
    def get_folders_list(self):
        return sorted([folder for folder in os.listdir(self.dir_path) if os.path.isdir(os.path.join(self.dir_path, folder))])


    def copy_files(self, foldername):
        try:
            src_dir = os.path.join(self.dir_path, foldername, 'input')
            dest_dir = os.path.join(self.dir_path, foldername, f'img/1_{foldername}')

            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            files_in_src = os.listdir(src_dir)

            for filename in files_in_src:
                src_path = os.path.join(src_dir, filename)
                dest_path = os.path.join(dest_dir, filename)

                # Check if .txt file already exists
                output_filename = os.path.splitext(filename)[0] + '.txt'
                output_path = os.path.join(dest_dir, output_filename)
                if os.path.exists(output_path):
                    continue  # skip if .txt file already exists

                if os.path.isfile(src_path) and os.access(src_path, os.R_OK):
                    if os.path.exists(dest_dir) and os.access(dest_dir, os.W_OK):
                        shutil.copy2(src_path, dest_path)

                        # Run the deepdanbooru command for the copied image
                        cmd = ["python", "deepdanbooru.py", "--image", dest_path, "--threshold", "0.7", "--ignore", "rating:explicit,rating:safe,rating:questionable,uncensored"]
                        result = subprocess.run(cmd, capture_output=True, text=True)

                        # Modify the output by adding the foldername to each line
                        modified_output = "\n".join([f"{foldername}, {line}" for line in result.stdout.strip().split("\n")])

                        # Save the output to a .txt file
                        with open(output_path, 'w') as output_file:
                            output_file.write(modified_output)
                    else:
                        print(f"Can't write to the destination: {dest_dir}")
                else:
                    print(f"Source file does not exist or is not readable: {src_path}")
            
            # Display the 'done' popup
            messagebox.showinfo("Info", "Done!")
        except Exception as e:
            print(f"Error during copy: {e}")



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

        labels = ["Lora Name", "Network (dim)", "Network (alpha)", "Conv (dim)", "Conv (alpha)", "Batch size", "Epochs", "Bucket resolution"]

        entries = {}

        # Create the Lora type dropdown outside the loop
        lora_frame = tk.Frame(self.training_frame_left, bg='black')
        lora_frame.pack(fill=tk.X)  # Use tk.X here to fill horizontally within the parent frame
        lora_label = tk.Label(lora_frame, text="Lora Type:", bg='black', fg='white')
        lora_label.pack(side=tk.LEFT)

        self.lora_type = ttk.Combobox(lora_frame, values=["Kohya Locon", "LyCORIS/LoCon", "LyCORIS/LoHa"])
        self.lora_type.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lora_type.current(0)  # Set the first option as default

        right_side_started = False
        for i, label in enumerate(labels):
            # Check if we have reached the label "Conv (dim)" and set the flag to True
            if label == "Batch size":
                right_side_started = True
            # Choose which frame to pack into based on the flag
            parent_frame = self.training_frame_right if right_side_started else self.training_frame_left

            frame = tk.Frame(parent_frame, bg='black')
            frame.pack(fill=tk.X)  # Use tk.X here to fill horizontally within the parent frame

            # Create label
            label_widget = tk.Label(frame, text=f"{label}:", bg='black', fg='white')
            label_widget.pack(side=tk.LEFT)

            # Create entry
            entries[label] = tk.Entry(frame, bg='#333333', fg='white', insertbackground='white')
            entries[label].pack(side=tk.LEFT, fill=tk.X, expand=True)


        # Create flip label and button
        flip_frame = tk.Frame(self.training_frame_right, bg='black')
        flip_frame.pack(fill=tk.X)

        flip_label = tk.Label(flip_frame, text="Flip:", bg='black', fg='white')
        flip_label.pack(side=tk.LEFT)

        self.flip_var = tk.BooleanVar()
        flip_button = tk.Checkbutton(flip_frame, variable=self.flip_var, bg='black')
        flip_button.pack(side=tk.LEFT)

        # Create shuffle label and button
        shuffle_frame = tk.Frame(self.training_frame_right, bg='black')
        shuffle_frame.pack(fill=tk.X)

        shuffle_label = tk.Label(shuffle_frame, text="Shuffle Captions:", bg='black', fg='white')
        shuffle_label.pack(side=tk.LEFT)

        self.shuffle_var = tk.BooleanVar()
        shuffle_button = tk.Checkbutton(shuffle_frame, variable=self.shuffle_var, bg='black')
        shuffle_button.pack(side=tk.LEFT)

        self.training_entries = entries  # Save references to entry widgets

    def create_prepare_tab(self):
        # New Section
        new_label = ttk.Label(self.prepare_tab, text="New")
        new_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
        
        self.new_param_entry = ttk.Entry(self.prepare_tab)
        self.new_param_entry.grid(row=1, column=0, padx=20, pady=10, sticky='w')
        
        self.new_proceed_button = ttk.Button(self.prepare_tab, text="Generate", command=self.prepare_generate_action)
        self.new_proceed_button.grid(row=1, column=1, padx=20, pady=10)
        
        # Folder Display and Update Section

        folder_label = ttk.Label(self.prepare_tab, text="Current Folder:")
        folder_label.grid(row=0, column=2, padx=20, pady=10, sticky='w')
        
        self.folder_display = ttk.Label(self.prepare_tab, text=self.dir_path)  # Using dir_path variable
        self.folder_display.grid(row=1, column=2, padx=20, pady=10, sticky='w')
        
        update_button = ttk.Button(self.prepare_tab, text="Update", command=self.update_folder_path)
        update_button.grid(row=2, column=2, padx=20, pady=10)

        # Dropdown for selecting loraname
        self.loraname_var = tk.StringVar()
        self.loraname_dropdown = ttk.Combobox(self.prepare_tab, textvariable=self.loraname_var, values=self.get_folders_list())
        self.loraname_dropdown.grid(row=3, column=2, padx=20, pady=5, sticky='w')


        # Button to initiate copy
        self.deepdanbooru_button = tk.Button(self.prepare_tab, text="deepdanbooru", command=lambda: self.copy_files(self.loraname_var.get()))
        self.deepdanbooru_button.grid(row=4, column=2, padx=20, pady=10)

        
    def update_folder_path(self):
        # Use filedialog to select a new folder
        new_folder = filedialog.askdirectory(title="Select Folder")
        if new_folder:
            self.dir_path = new_folder
            self.folder_display.config(text=self.dir_path)
            # Update any internal variable storing the folder path if needed

    def prepare_generate_action(self):
        folder_name = self.new_param_entry.get()  # Taking the folder name from the correct text field
        if not folder_name:
            messagebox.showerror("Error", "Folder name is empty!")
            return

        mainfolder = os.path.join(self.dir_path, folder_name)
        imgfolder = os.path.join(mainfolder, "img")
        specific_imgfolder = os.path.join(imgfolder, "1_" + folder_name)

        # Creating the folders
        try:
            os.makedirs(os.path.join(mainfolder, "input"), exist_ok=True)
            os.makedirs(specific_imgfolder, exist_ok=True)
            messagebox.showinfo("Success", f"Directories created at: {mainfolder}")
        except Exception as e:
            messagebox.showerror("Error", str(e))



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
        # Update the content of auto-generated text fields
        for file in self.files:
            with open(os.path.join(self.directory, file), 'r') as f:
                content = f.read()
            if file in self.text_widgets:  # Check if the text field exists
                text_widget = self.text_widgets[file]
                text_widget.delete(0, tk.END)
                text_widget.insert(tk.END, content)

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
            text_widget.pack(fill=tk.X, padx=30)  # Add padding here

            # Associate text_widget with its file
            self.text_widgets[text_widget] = file

        self.drop_target.pack_forget()  # Hide the drop target



root = TkinterDnD.Tk()
root.geometry("800x600")
app = Application(master=root)
app.mainloop()