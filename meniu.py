import tkinter as tk
from tkinter import messagebox


class Meniu:

    def __init__(self, change_variable):
        root = tk.Tk()
        text = tk.Label(root, text="Data parsing was successful", font=(32))

        group = tk.Button(
            text="Group actors",
            width=20,
            master=root,
            command=lambda: close(change_variable, "group", root),
        )
        icons = tk.Button(
            text="Assign Icons",
            width=20,
            master=root,
            command=lambda: close(change_variable, "icons", root),
        )
        sort = tk.Button(
            text="Sort actors",
            width=20,
            master=root,
            command=lambda: close(change_variable, "sort", root),
        )
        skip = tk.Button(
            text="Generate xCJML 3.0",
            width=30,
            font=("Arial", 10, "bold"),
            master=root,
            command=lambda: close(change_variable, "skip", root),
        )
        text.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        skip.grid(row=1, column=2, padx=10, pady=10)
        optional = tk.Label(root, text="Optional choices")
        optional.grid(row=2, column=1, columnspan=3, pady=5)
        group.grid(row=3, column=1, padx=10, pady=10)
        icons.grid(row=3, column=2, padx=10, pady=10)
        sort.grid(row=3, column=3, padx=10, pady=10)
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
        root.lift()
        root.focus_force()
        root.attributes('-topmost', True)
        root.update()
        root.attributes('-topmost', False)
        root.mainloop()


def close(function, action, root):
    function(action)
    root.destroy()


def on_closing(root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
