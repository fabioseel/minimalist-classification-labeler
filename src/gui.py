from collections import OrderedDict
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json
import matplotlib as mpl
import numpy as np

class ClassEditorWindow(tk.Toplevel):

    def __init__(self, parent, cur_classes):
        tk.Toplevel.__init__(self, parent)
        self.classes=cur_classes
        self.text = tk.Text(self, height=len(cur_classes))
        for i, cl in enumerate(cur_classes):
            self.text.insert('{}.0'.format(i+1), cl+'\n')
        self.text.pack(expand=True, fill='both', padx=50, pady=5)
        
        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
        self.ok_button.pack(expand=False, fill='x',)
        self.protocol("WM_DELETE_WINDOW", self.on_abort)

    def on_ok(self, event=None):
        self.classes = self.text.get('1.0','end').split("\n")
        self.destroy()

    def on_abort(self):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.classes

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimalist Classification Labeler")

        # Create buttons
        self.home_dir = "~"
        self.class_button_dict = OrderedDict()

        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(fill="both")
        self.dir_button = tk.Button(self.menu_frame, text="Open Directory", command=self.open_directory)
        self.dir_button.pack(side='left', fill="both",expand=True)

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

        self.cmap = mpl.colormaps['viridis']

        self.root.minsize(400, 400)

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        self.index = 0

    def open_directory(self):
        # Open a file dialog to choose an image file
        self.home_dir = filedialog.askdirectory(initialdir=self.home_dir)

        if not hasattr(self, "subdir_button"):
            self.subdir_button = tk.Button(self.menu_frame, text="Load Subdirectories", command=self.load_subdirs)
            self.subdir_button.pack(side='left', fill="both",expand=True)
        if not hasattr(self, "edit_classes_button"):
            self.edit_classes_button = tk.Button(self.menu_frame, text="Edit Classes", command=self.edit_classes)
            self.edit_classes_button.pack(side='left', fill="both",expand=True)

        self.classes = self.get_dirs(self.home_dir)

        if self.home_dir:
            label_path = os.path.join(self.home_dir, "autolabels.json")
            self.load_labels(label_path)
            self.imgs = self.get_all_images(self.home_dir)
            if(len(self.imgs) > 0):
                self.update_image(self.index)
            else:
                self.__clear_image__()

    @property
    def classes(self):
        return self._classes
    
    @classes.setter
    def classes(self, value):
        new_classes = [v for v in value if len(v)>0] # Validity check
        if not hasattr(self, "_classes") or self._classes != new_classes:
            self._classes = new_classes
            self.create_classifier_buttons()

    def edit_classes(self):
        self.classes = ClassEditorWindow(self.root, self.classes).show()

    def load_subdirs(self):
        pass

    @staticmethod        
    def get_dirs(path):
        return sorted([ f.name for f in os.scandir(path) if f.is_dir() ])


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
            if not hasattr(self, "autoskip_button"):
                self.autoskip_button = tk.Button(self.menu_frame, text="Skip correct", command=self.autoskip)
                self.autoskip_button.pack(side='left', fill="both",expand=True)

    def autoskip(self):
        pass

    def update_image(self, index):
        self.index = index
        # Load the chosen image
        self.image = Image.open(os.path.join(self.home_dir, self.imgs[index]))
        self.__display_image__()
        self.display_autolabels()
    
    def display_autolabels(self):
        if hasattr(self, "imgs") and self.imgs[self.index] in self.autolabels.keys():
            label_values = self.autolabels[self.imgs[self.index]]
            if len(label_values) == len(self.class_button_dict):
                for button, value in zip(self.class_button_dict, label_values):
                    color = np.round(np.array(self.cmap(value))[:3]*255).astype(int)
                    color = '#%02x%02x%02x' % (color[0],color[1],color[2])
                    fg = "white" if value < 0.5 else "black"
                    self.class_button_dict[button].configure(background=color, foreground=fg)

    def create_classifier_buttons(self):
        for button in self.class_button_dict:
            self.class_button_dict[button].destroy()

        self.class_button_dict = OrderedDict()
        for _class in self.classes: 
            if _class not in self.class_button_dict:
                # pass each button's text to a function 
                def action(x = _class):  
                    return self.classify_button_clicked(x) 
                    
                # create the buttons  
                self.class_button_dict[_class] = tk.Button(self.button_frame, text = _class, 
                                        command = action, height=10) 
                self.class_button_dict[_class].pack(side='left', fill="both",expand=True)
        self.display_autolabels()

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

    def __clear_image__(self):
        self.label.configure(image='')
        self.label.image = None

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
