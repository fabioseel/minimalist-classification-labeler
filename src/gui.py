from collections import OrderedDict
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json
import matplotlib as mpl
import numpy as np
from enum import Enum

class COLORS(Enum):
    blue = "#0098cd"
    lightblue = "#cceaf5"
    pink ="#e01095"

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

        self.remain_label = tk.Label(root)
        self.remain_label.pack(fill="x",expand=False)
        # Create a label to display the image
        self.img_frame = tk.Frame(root)
        self.img_frame.pack(expand=True, fill="both")

        self.class_label = tk.Label(root)
        self.class_label.pack(fill="x",expand=False)

        self.prev_button = tk.Button(self.img_frame, text="<", command=lambda:self.inc_index(-1))
        self.prev_button.pack(side='left', fill="y")

        self.label = tk.Label(self.img_frame)
        self.label.pack(expand=True,side='left', fill="both")

        self.next_button = tk.Button(self.img_frame, text=">", command=lambda:self.inc_index(1))
        self.next_button.pack(side='left', fill="y")

        
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill="both")

        self.class_label.configure(bg=COLORS.lightblue.value)
        self.cmap = mpl.colors.LinearSegmentedColormap.from_list("hertie", [COLORS.blue.value, COLORS.lightblue.value, COLORS.pink.value])

        self.root.minsize(400, 400)

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        self.index = 0

    def __clean_gui__(self):
            if hasattr(self, "subdir_button"):
                self.subdir_button.destroy()
                self.__delattr__("subdir_button")

            if hasattr(self, "edit_classes_button"):
                self.edit_classes_button.destroy()
                self.__delattr__("edit_classes_button")

            if hasattr(self, "autoskip_button"):
                self.autolabels = {}
            
            for button in self.class_button_dict:
                self.class_button_dict[button].destroy()
            self.class_button_dict.clear()
            self.classes = []

            self.imgs = []
            self.load_image()


    def open_directory(self):
        # Open a file dialog to choose an image file
        new_home = filedialog.askdirectory(initialdir=self.home_dir)

        if new_home:
            self.home_dir = new_home
            self.__clean_gui__()

            self.classes = self.get_dirs(self.home_dir)
            if len(self.classes) > 0:
                self.subdir_button = tk.Button(self.menu_frame, text="Load Subdirectories", command=self.load_subdirs)
                self.subdir_button.pack(side='left', fill="both",expand=True)

            self.edit_classes_button = tk.Button(self.menu_frame, text="Edit Classes", command=self.edit_classes)
            self.edit_classes_button.pack(side='left', fill="both",expand=True)

            label_path = os.path.join(self.home_dir, "autolabels.json")
            self.load_labels(label_path)
            self.imgs = self.get_images_from_path(self.home_dir)
            if(self.num_imgs > 0):
                self.index = 0
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
        for dir in self.get_dirs(self.home_dir):
            full_path = os.path.join(self.home_dir, dir)
            self.imgs.extend(self.get_images_from_path(full_path))

            label_path = os.path.join(full_path, "autolabels.json")
            self.load_labels(label_path, join=True)

        self.load_image()
        self.subdir_button.destroy()
        self.__delattr__("subdir_button")

    @property
    def autolabels(self):
        if not hasattr(self, "_autolabels"):
            self._autolabels = {}
        return self._autolabels
    
    @autolabels.setter
    def autolabels(self, value):
        self._autolabels = value
        if len(value) > 0 and not hasattr(self, "autoskip_button"):
                self.autoskip_button = tk.Button(self.menu_frame, text="Skip correct", command=self.autoskip)
                self.autoskip_button.pack(side='left', fill="both",expand=True)
        elif len(value) == 0 and hasattr(self, "autoskip_button"):
            self.autoskip_button.destroy()
            self.__delattr__("autoskip_button")

    @staticmethod        
    def get_dirs(path):
        return sorted([ f.name for f in os.scandir(path) if f.is_dir() ])


    @staticmethod
    def get_images_from_path(path):
        imgs = []
        for file in os.listdir(path):
            if file.endswith(".png"):
                imgs.append(os.path.join(path, file))
        return imgs
    
    def load_labels(self, label_path, join = False):
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                new_labels = json.load(f)
                if join:
                    self.autolabels = self.autolabels | new_labels # Merge dictionaries
                else:
                    self.autolabels = new_labels

    def autoskip(self):
        num_auto_classes = len(next(iter(self.autolabels.values())))
        if len(self.classes) == num_auto_classes:
            remove_imgs = []
            for img in self.imgs:
                dir_path, img_name = os.path.split(img)
                if img_name in self.autolabels and dir_path != self.home_dir:
                    dir = os.path.split(dir_path)[1]
                    dir_label = self.classes.index(dir)
                    autolabel = np.argmax(self.autolabels[img_name])
                    if dir_label == autolabel:
                        remove_imgs.append(img)

            index_adjust = 0
            for img in remove_imgs:
                if self.imgs.index(img)-index_adjust < self.index:
                    index_adjust -=1
                self.imgs.remove(img)
            self.inc_index(index_adjust)
            self.load_image()
        else:
            pass #TODO: Implement error message

    @property
    def index(self):
        if not hasattr(self, "_index"):
            self._index=0
        return self._index
    
    @index.setter
    def index(self, value):
        if (self.num_imgs > 0):
            value = value % self.num_imgs
        else:
            value = 0
        self._index = value
        self.load_image()

    @property
    def num_imgs(self):
        return len(self.imgs) if hasattr(self, "imgs") else 0

    def load_image(self):
        if self.img_path != '':
            image = np.asarray(Image.open(self.img_path))
            image = (image-image.min())/(image.max()-image.min())
            image = np.round(255*image).astype(np.uint8)
            self.image = Image.fromarray(image)
            self.__display_image__()
            self.display_autolabels()
        else:
            self.__clear_image__()
        self.remain_label.config(text = "img: "+str(min(self.index+1, self.num_imgs))+"/"+str(self.num_imgs))

    def inc_index(self, diff):
        self.index += diff
    
    @property
    def img_path(self):
        if hasattr(self, "imgs") and len(self.imgs) > self.index:
            return self.imgs[self.index]
        else:
            return ""
        
    @property
    def img_class(self):
        _class = "None"
        path = self.img_path
        if len(path) > 0:
            _dir = os.path.split(path)[0]
            dirname = os.path.split(_dir)[1]
            if dirname in self.classes:
                _class = dirname
        return _class
    
    @property
    def img_name(self):
        if hasattr(self, "imgs"):
            return os.path.split(self.img_path)[1]
        else:
            return ""

    def display_autolabels(self):
        if self.img_name in self.autolabels.keys():
            label_values = self.autolabels[self.img_name]
            if len(label_values) == len(self.class_button_dict):
                for button, value in zip(self.class_button_dict, label_values):
                    color = np.round(np.array(self.cmap(value))[:3]*255).astype(int)
                    color = '#%02x%02x%02x' % (color[0],color[1],color[2])
                    fg = "white"# if value < 0.5 else "black"
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
            image = self.image.resize((width, height), Image.NEAREST)

            # Convert image to PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Update the label with the new image
            self.label.configure(image=photo)
            self.label.image = photo

            self.class_label.config(text=self.img_class)

    def __clear_image__(self):
        if hasattr(self, "image"):
            self.__delattr__("image")
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
            
            dest_path = os.path.join(class_dir, self.img_name)
            os.rename(self.img_path, dest_path)
            self.imgs.pop(self.index)
            self.load_image()


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Create an instance of the SimpleGUI class
    gui = SimpleGUI(root)

    # Start the GUI event loop
    root.mainloop()
