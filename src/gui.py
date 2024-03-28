from collections import OrderedDict
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json
import matplotlib as mpl
import numpy as np


class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimalist Classification Labeler")

        # Create buttons
        self.home_dir = "~"
        self.dir_button = tk.Button(root, text="Open Directory", command=self.open_directory)
        self.dir_button.pack()

        # Create a label to display the image
        self.img_frame = tk.Frame(root)
        self.img_frame.pack(expand=True, fill="both")

        self.prev_button = tk.Button(self.img_frame, text="<", command=lambda:self.update_image(self.index-1))
        self.prev_button.pack(side='left', fill="y")

        self.label = tk.Label(self.img_frame)
        self.label.pack(expand=True,side='left', fill="both")

        self.next_button = tk.Button(self.img_frame, text=">", command=lambda:self.update_image(self.index+1))
        self.next_button.pack(side='left', fill="y")

        
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill="both")

        self.classes = ['center_surround', 'color', 'gabor', 'mult_freq', 'noise', 'simple_edge', 'unclassifiable']
        self.create_classifier_buttons()

        self.cmap = mpl.colormaps['viridis']

        self.root.minsize(400, 400)

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        self.index = 0

    def open_directory(self):
        # Open a file dialog to choose an image file
        self.home_dir = filedialog.askdirectory(initialdir=self.home_dir)

        if self.home_dir:
            label_path = os.path.join(self.home_dir, "autolabels.json")
            self.load_labels(label_path)
            self.imgs = self.get_all_images(self.home_dir)
            self.update_image(self.index)

    @staticmethod
    def get_all_images(path):
        imgs = []
        for file in os.listdir(path):
            if file.endswith(".png"):
                imgs.append(file)
        return imgs
    
    def load_labels(self, label_path):
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                self.autolabels = json.load(f)

    def update_image(self, index):
            self.index = index
            # Load the chosen image
            self.image = Image.open(os.path.join(self.home_dir, self.imgs[index]))
            self.__display_image__()
            self.display_autolabels()
    
    def display_autolabels(self):
        if self.imgs[self.index] in self.autolabels.keys():
            label_values = self.autolabels[self.imgs[self.index]]
            for button, value in zip(self.button_dict, label_values):
                color = np.round(np.array(self.cmap(value))[:3]*255).astype(int)
                color = '#%02x%02x%02x' % (color[0],color[1],color[2])
                fg = "white" if value < 0.5 else "black"
                self.button_dict[button].configure(background=color, foreground=fg)

    def create_classifier_buttons(self):
        self.button_dict = OrderedDict()
        for _class in self.classes: 
            
            # pass each button's text to a function 
            def action(x = _class):  
                return self.classify_button_clicked(x) 
                
            # create the buttons  
            self.button_dict[_class] = tk.Button(self.button_frame, text = _class, 
                                    command = action, height=10) 
            self.button_dict[_class].pack(side='left', fill="both",expand=True) 

    def __display_image__(self):
        if hasattr(self, "image"):
            # Resize image to fit within window
            width, height = self.label.winfo_width()-50, self.label.winfo_height()-50
            old_width, old_height = self.image.width, self.image.height
            factor = old_width/old_height
            new_factor = width/height
            if new_factor > factor:
                width=int(round(height/factor,0))
            else:
                height=int(round(width*factor,0))
            self.image = self.image.resize((width, height), Image.NEAREST)

            # Convert image to PhotoImage
            photo = ImageTk.PhotoImage(self.image)

            # Update the label with the new image
            self.label.configure(image=photo)
            self.label.image = photo

    def on_window_resize(self, event):
        # Resize and display the image when the window is resized
        self.__display_image__()

    def classify_button_clicked(self, _class):
        if self.image:
            class_dir = os.path.join(self.home_dir, _class)
            if not os.path.exists(class_dir):
                os.mkdir(class_dir)
            
            src_path = os.path.join(self.home_dir, self.imgs[self.index])
            dest_path = os.path.join(class_dir, self.imgs[self.index])
            os.rename(src_path, dest_path)
            self.imgs.pop(self.index)
            self.update_image(self.index)


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Create an instance of the SimpleGUI class
    gui = SimpleGUI(root)

    # Start the GUI event loop
    root.mainloop()
