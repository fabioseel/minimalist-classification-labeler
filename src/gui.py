import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimalist Classification Labeler")

        # Create buttons
        self.button1 = tk.Button(root, text="Open Directory", command=self.open_directory)
        self.button1.pack()

        # Create a label to display the image
        self.label = tk.Label(root)
        self.label.pack(expand=True, fill="both")

        self.button2 = tk.Button(root, text="Button 2", command=self.button2_clicked)
        self.button2.pack()
        self.root.minsize(400, 400)

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def open_directory(self):
        # Open a file dialog to choose an image file
        dir_path = filedialog.askdirectory(initialdir="~")

        if dir_path:
            img_path = os.listdir(dir_path)[0]
            # Load the chosen image
            self.image = Image.open(os.path.join(dir_path, img_path))
            self.display_image()

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

    def button2_clicked(self):
        print("Button 2 clicked")

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Create an instance of the SimpleGUI class
    gui = SimpleGUI(root)

    # Start the GUI event loop
    root.mainloop()
