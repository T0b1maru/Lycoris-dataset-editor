import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Lycoris-dataset-editor")
        self.pack(fill=tk.BOTH, expand=True)

        self.configure(bg='black')

        self.directory = None
        self.files = []

        self.entry_frame = tk.Frame(self, bg='black')
        self.entry_frame.pack(fill=tk.X)

        self.entry = tk.Entry(self.entry_frame, bg='#333333', fg='white', insertbackground='white')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.change_to_label = tk.Label(self.entry_frame, text="    change to    ", bg='black', fg='white')
        self.change_to_label.pack(side=tk.LEFT)

        self.replacement = tk.Entry(self.entry_frame, bg='#333333', fg='white', insertbackground='white')
        self.replacement.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.replace_button = tk.Button(self.entry_frame, text="Replace Text", command=self.replace_text, bg='#333333', fg='white')
        self.replace_button.pack(side=tk.LEFT)

        self.append_prepend_frame = tk.Frame(self, bg='black')
        self.append_prepend_frame.pack(fill=tk.X)

        self.append_prepend_entry = tk.Entry(self.append_prepend_frame, bg='#333333', fg='white', insertbackground='white')
        self.append_prepend_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.prepend_button = tk.Button(self.append_prepend_frame, text="Prepend", command=self.prepend_text, bg='#333333', fg='white')
        self.prepend_button.pack(side=tk.LEFT)

        self.append_button = tk.Button(self.append_prepend_frame, text="Append", command=self.append_text, bg='#333333', fg='white')
        self.append_button.pack(side=tk.LEFT)

        self.save_clear_frame = tk.Frame(self, bg='black')
        self.save_clear_frame.pack(fill=tk.X)

        self.save_button = tk.Button(self.save_clear_frame, text='Save current', command=self.save_current, bg='#333333', fg='white')
        self.save_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self.save_clear_frame, text='Clear', command=self.clear, bg='#333333', fg='white')
        self.clear_button.pack(side=tk.LEFT)

        self.drop_target = tk.Label(self, text='Drop directory here', relief='solid', bg='black', fg='white')
        self.drop_target.pack(fill=tk.BOTH, expand=True)
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind('<<Drop>>', self.drop)



        # This will store a reference to each text widget and the file it's related to
        self.text_widgets = {}


    def drop(self, event):
        # event.data is a list of filenames (one directory in your case)
        # directories and filenames contain forward slashes regardless of the OS
        self.directory = event.data
        if not os.path.isdir(self.directory):
            self.directory = os.path.dirname(self.directory)
        self.files = [f for f in os.listdir(self.directory) if f.endswith('.txt')]

        # remove previous entries
        for widget in self.winfo_children():
            if isinstance(widget, tk.Entry) and widget not in [self.entry, self.replacement, self.append_prepend_entry]:
                widget.destroy()

        for file in self.files:
            with open(os.path.join(self.directory, file), 'r') as f:
                content = f.read()
            text_widget = tk.Entry(self, width=1, bg='#333333', fg='white', insertbackground='white')
            text_widget.insert(tk.END, content)
            text_widget.pack(fill=tk.X)

            # Associate text_widget with its file
            self.text_widgets[text_widget] = file
        self.drop_target.pack_forget()  # hide the drop target

    def clear(self):
        # remove previous entries
        for widget in self.text_widgets.keys():
            widget.destroy()

        self.drop_target.pack(fill=tk.BOTH, expand=True)  # show the drop target

        self.text_widgets = {}  # reset the reference

    def save_current(self):
        for widget, filename in self.text_widgets.items():
            with open(os.path.join(self.directory, filename), 'w') as f:
                f.write(widget.get())

    def replace_text(self):
        self.edit_text(self.entry.get(), self.replacement.get())

    def prepend_text(self):
        self.edit_text("", self.append_prepend_entry.get() + "{content}")

    def append_text(self):
        self.edit_text("", "{content}" + self.append_prepend_entry.get())

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
        for widget in self.winfo_children():
            if isinstance(widget, tk.Entry) and widget not in [self.entry, self.replacement, self.append_prepend_entry]:
                widget.destroy()

        for file in self.files:
            with open(os.path.join(self.directory, file), 'r') as f:
                content = f.read()
            text_widget = tk.Entry(self, width=1, bg='#333333', fg='white', insertbackground='white')
            text_widget.insert(tk.END, content)
            text_widget.pack(fill=tk.X)

root = TkinterDnD.Tk()
root.geometry("800x600")
app = Application(master=root)
app.mainloop()