import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw, ImageTk


class IconSelect:

    default_options = [("t.png", "Option 1"), ("t2.png", "Option 2"), ("t3.png", "Option 3")]

    def __init__(self, actors):
        self.options = self.get_available_options()
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
        # preserve order and remove duplicates while accepting both string values and grouped list pairs
        actor_values = []
        seen = set()
        for raw_value in actors.values():
            actor_name = raw_value[0] if isinstance(raw_value, (list, tuple)) else raw_value
            normalized_name = str(actor_name)
            if normalized_name not in seen:
                seen.add(normalized_name)
                actor_values.append([actor_name, self.options[0][1]])

        for idx, actor_entry in enumerate(actor_values):

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
            command=lambda: self.match_icons(actors, actor_values, root),
        )
        button.grid(column=2, row=rownum, columnspan=2, padx=10, pady=10)

        root.mainloop()

    def match_icons(self, actors, actorValues, root):
        for actor, actor_value in actors.items():
            lookup_value = actor_value[0] if isinstance(actor_value, (list, tuple)) else actor_value
            for av in actorValues:
                if lookup_value == av[0]:
                    actors[actor] = [av[0], av[1]]
                    break
        if root is not None:
            root.destroy()

    def _generate_fallback_icon(self, color):
        image = Image.new("RGBA", (20, 20), color)
        draw = ImageDraw.Draw(image)
        draw.rectangle((4, 4, 16, 16), outline=(255, 255, 255, 220), width=2)
        draw.line((6, 10, 14, 10), fill=(255, 255, 255, 220), width=2)
        draw.line((10, 6, 10, 14), fill=(255, 255, 255, 220), width=2)
        return image

    def get_available_options(self):
        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        # Prefer the organized `Actors` subfolder for icon options when present
        assets_dir = base / "assets" / "icons" / "Actors"
        if not assets_dir.exists():
            assets_dir = base / "assets" / "icons"
        assets_dir.mkdir(parents=True, exist_ok=True)

        found = []
        seen = set()
        # root icons folder (used by get_icons) — compute once so relative paths
        root_icons = base / "assets" / "icons"
        for image_path in sorted(assets_dir.rglob("*")):
            if not image_path.is_file():
                continue
            if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
                continue

            # make path relative to the top-level icons folder so get_icons can find it
            try:
                relative_path = image_path.relative_to(root_icons).as_posix()
            except Exception:
                # fallback to relative to scanned assets_dir
                relative_path = image_path.relative_to(assets_dir).as_posix()

            if relative_path.lower() in seen:
                continue
            seen.add(relative_path.lower())

            rel_noext = Path(relative_path).with_suffix("").as_posix()
            display_name = " ".join(
                rel_noext.replace("/", " ").replace("_", " ").replace("-", " ").split()
            ).title()
            found.append((relative_path, display_name))

        return found or self.default_options

    def get_icons(self):
        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        assets_dir = base / "assets" / "icons"
        assets_dir.mkdir(parents=True, exist_ok=True)

        images = []
        colors = [(79, 142, 247), (62, 182, 125), (240, 167, 68)]

        try:
            root = tk._default_root
        except AttributeError:
            root = None
        if root is None:
            temp_root = tk.Tk()
            temp_root.withdraw()
            root = temp_root

        for index, (relative_path, _) in enumerate(self.options):
            image_path = assets_dir / relative_path
            try:
                icon = Image.open(image_path).convert("RGBA")
            except (FileNotFoundError, OSError, ValueError):
                icon = self._generate_fallback_icon(colors[index % len(colors)])
            images.append(ImageTk.PhotoImage(icon.resize((20, 20)), master=root))

        if root is not None and getattr(root, "winfo_exists", lambda: False)() and root is not getattr(tk, "_default_root", None):
            root.destroy()
        return images