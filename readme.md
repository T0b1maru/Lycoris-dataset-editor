# Lycoris Dataset Editor

Lycoris Dataset Editor is a Python-based GUI application designed to facilitate editing of multiple text files in a selected directory. This tool is particularly useful for handling image dataset where each image is associated with a .txt file containing relevant prompts or keywords. The application provides features to replace, prepend, and append text in these files and save the changes directly.

## Features

- **Directory Drop:** Drag and drop a directory into the application to load all .txt files present in it.
- **Text Replacement:** Input the text to be replaced and its replacement in the provided fields. Press the "Replace Text" button to apply the changes to all loaded .txt files.
- **Prepend & Append:** Input text and select either "Prepend" or "Append" to add the text to the beginning or end of all loaded .txt files, respectively.
- **Live Editing and Saving:** Edit the contents of the text files directly in the application's interface and save the changes to the respective .txt files by pressing "Save Current".
- **Clear Interface:** Use the "Clear" button to remove all currently loaded files from the interface, allowing for a fresh start.

## Installation

Lycoris Dataset Editor requires Python 3.7+ to run. Clone this repository to your local machine and install the required dependencies with pip:

```
git clone https://github.com/T0b1maru/Lycoris-dataset-editor.git
cd lycoris-dataset-editor
pip install -r requirements.txt
```


## Usage

To start the application, run:

```
python main.py
```

