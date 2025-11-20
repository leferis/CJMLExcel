from tkinter import Image, PhotoImage
import tkinter as tk
from PIL import Image, ImageTk


class IconSelect:

    options = [("t.png", "Option 1"), ("t2.png", "Option 2"), ("t3.png", "Option 3")]

    def __init__(self, actors):
        root = tk.Tk()
        rownum = 1
        text = tk.Label(
            root,
            text="Select Icons for actor",
            anchor=tk.CENTER,
            font=("Arial", 22, "bold"),
        )
        text.grid(column=2, row=0, columnspan=2, padx=10, pady=10)
        root.title("Dropdown with Icons")

        images = self.get_icons()
        # keep references to images so they aren't garbage-collected
        self.images = images

        current_index = tk.IntVar(value=0)
        # preserve order and remove duplicates, initialize selected option to first option name
        actorValues = [[v, self.options[0][1]] for v in dict.fromkeys(actors.values())]
        for idx, actor_entry in enumerate(actorValues):

            label = tk.Label(
                root, text=actor_entry[0], anchor=tk.CENTER, font=("Arial", 12, "bold")
            )

            label.grid(column=0, row=rownum, columnspan=3)
            menubutton = tk.Menubutton(root, relief="raised", compound="left")
            menubutton.grid(column=3, row=rownum, padx=10, pady=10)
            rownum = rownum + 1

            # bind the specific menubutton and actor_entry into the callback so each button updates its own value
            def select_option(index, mb=menubutton, av=actor_entry):
                current_index.set(index)
                mb.config(text=self.options[index][1], image=self.images[index])
                av[1] = self.options[index][1]

            # initialize button to first option
            select_option(0)

            menu = tk.Menu(menubutton, tearoff=False)
            for opt_idx, (img, name) in enumerate(zip(self.images, [n for _, n in self.options])):
                menu.add_command(
                    label=name,
                    image=img,
                    compound="left",
                    command=lambda i=opt_idx, fn=select_option: fn(i),
                )
            menubutton.config(menu=menu)

        button = tk.Button(
            root,
            text="Submit",
            command=lambda: self.match_icons(actors, actorValues, root),
        )
        button.grid(column=2, row=rownum, columnspan=2, padx=10, pady=10)

        root.mainloop()

    def match_icons(self, actors, actorValues, root):
        for actor, value in actors.items():
            for av in actorValues:
                if value == av[0]:
                    actors[actor] = av
                    break
        root.destroy()

    def get_icons(self):

        images = [
            ImageTk.PhotoImage(Image.open(path).resize((20, 20)))
            for path, _ in self.options
        ]
        return images