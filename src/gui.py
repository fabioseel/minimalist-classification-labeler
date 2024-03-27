import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimalist Classification Labeler")

        # Create buttons
        self.home_dir = "~"
        self.button1 = tk.Button(root, text="Open Directory", command=self.open_directory)
        self.button1.pack()

        # Create a label to display the image
        self.label = tk.Label(root)
        self.label.pack(expand=True, fill="both")

        
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill="both")

        self.classes = ['center_surround', 'color', 'gabor', 'mult_freq', 'noise', 'simple_edge', 'unclassifiable']
        self.create_classifier_buttons()

        self.root.minsize(400, 400)

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def open_directory(self):
        # Open a file dialog to choose an image file
        self.home_dir = filedialog.askdirectory(initialdir=self.home_dir)

        if self.home_dir:
            self.display_next_image()

    @staticmethod
    def get_next_image(path):
        for file in os.listdir(path):
            if file.endswith(".png"):
                return file
        return ""
    
    def display_next_image(self):
        img_name = self.get_next_image(self.home_dir)
        self.update_image(img_name)

    def update_image(self, img_name):
            self.img_name = img_name
            # Load the chosen image
            self.image = Image.open(os.path.join(self.home_dir, self.img_name))
            self.display_image()

    def create_classifier_buttons(self):
        button_dict = {} 
        for _class in self.classes: 
            
            # pass each button's text to a function 
            def action(x = _class):  
                return self.classify_button_clicked(x) 
                
            # create the buttons  
            button_dict[_class] = tk.Button(self.button_frame, text = _class, 
                                    command = action, height=10) 
            button_dict[_class].pack(side='left', fill="both",expand=True) 

    def display_image(self):
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
        self.display_image()

    def classify_button_clicked(self, _class):
        if self.image:
            class_dir = os.path.join(self.home_dir, _class)
            if not os.path.exists(class_dir):
                os.mkdir(class_dir)
            
            src_path = os.path.join(self.home_dir, self.img_name)
            dest_path = os.path.join(class_dir, self.img_name)
            os.rename(src_path, dest_path)
            self.display_next_image()


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Create an instance of the SimpleGUI class
    gui = SimpleGUI(root)

    # Start the GUI event loop
    root.mainloop()
