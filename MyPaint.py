import math
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageGrab, Image, ImageTk
from collections import deque


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing App")

        self.mouseX = 0
        self.mouseY = 0
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.mousePressX = 0
        self.mousePressY = 0
        self.mouseReleaseX = 0
        self.mouseReleaseY = 0
        self.paintColor = 'black'
        self.activity = None
        self.isPressed = False
        self.isDrawing = False
        self.isPickingColor = False
        self.isFillingColor = False
        self.points = []
        # used for storing recent versions
        self.versions = []
        self.isFirstUndo = True
        self.setup_ui()

    def setup_ui(self):
        self.root.rowconfigure(0, minsize=800, weight=1)
        self.root.columnconfigure(1, minsize=800, weight=1)

        self.frm_paint = tk.Canvas(self.root, takefocus=True, bg="white")
        self.frm_buttons = tk.Frame(self.root, relief=tk.RAISED, bd=2)
        # self.frm_buttons.rowconfigure(1, weight=1)

        self.frm_control_buttons = tk.Frame(self.frm_buttons, relief=tk.RAISED, bd=1)
        self.frm_control_buttons.grid_columnconfigure(0, weight=1)
        self.btn_open = tk.Button(self.frm_control_buttons, text="Open", command=self.open_file)
        self.btn_save = tk.Button(self.frm_control_buttons, text="Save As...", command=self.save_file)
        self.btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.frm_paint_buttons = tk.Frame(self.frm_buttons, relief=tk.RAISED, bd=1, background="black")
        self.frm_paint_buttons.grid_columnconfigure(0, weight=1)

        self.paints_color_box = tk.Listbox(self.frm_paint_buttons, activestyle="none")

        self.paints_color_box.grid(row=0, column=0, sticky="ew", padx=5, pady=5)  # Add Listbox to grid

        # Create scrollbar for the Listbox
        self.scrollbar = tk.Scrollbar(self.frm_paint_buttons, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0, column=1, sticky="ns")  # Add Scrollbar to grid

        color_names = [
            "red", "green", "blue", "yellow", "black", "white",
            "orange", "purple", "pink", "brown"
        ]
        # Insert color names into the Listbox
        for color in color_names:
            self.paints_color_box.insert(tk.END, color)
        # sets the list selection to black color, where it should be
        self.paints_color_box.select_set(4)

        self.paints_color_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.paints_color_box.yview)

        # Position Listbox and Scrollbar
        self.paints_color_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.frm_tool_buttons = tk.Frame(self.frm_buttons, relief=tk.RAISED, bd=1)
        self.frm_tool_buttons.grid_columnconfigure(0, weight=1)
        self.btn_drawing = tk.Button(self.frm_tool_buttons, text="Draw",
                                     command=lambda: self.set_current_activity("Drawing"))
        self.btn_color_pick = tk.Button(self.frm_tool_buttons, text="Pick Color",
                                        command=lambda: self.set_current_activity("Picking"))
        self.btn_color_fill = tk.Button(self.frm_tool_buttons, text="Fill With Color",
                                        command=lambda: self.set_current_activity("ColorFilling"))
        self.pencil_size_value = tk.IntVar()
        self.pencil_size_slider = tk.Scale(self.frm_tool_buttons, from_=1, to=10,
                                           orient=tk.HORIZONTAL, variable=self.pencil_size_value)
        self.pencil_size_text = tk.Label(self.frm_tool_buttons, text="Pencil Size")

        self.undo_btn = tk.Button(self.frm_tool_buttons, text="Undo",
                                  command=lambda: self.undo())

        self.btn_drawing.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_color_pick.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.btn_color_fill.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.pencil_size_slider.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.pencil_size_text.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        self.undo_btn.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

        self.frm_control_buttons.grid(row=0, column=0, sticky="ew", padx=5)
        self.frm_paint_buttons.grid(row=1, column=0, sticky="ew", padx=5)
        self.frm_tool_buttons.grid(row=2, column=0, sticky="ew", padx=5)

        self.frm_buttons.grid(row=0, column=0, sticky="ns")
        self.frm_paint.grid(row=0, column=1, sticky="nsew")

        # Bind color selection event
        self.paints_color_box.bind("<<ListboxSelect>>", self.on_color_select)
        self.frm_paint.bind('<ButtonPress-1>', self.click_press)
        self.frm_paint.bind('<ButtonRelease-1>', self.click_release)

    def on_color_select(self, event):
        # Handles the selection of a color from the Listbox.
        selected_index = self.paints_color_box.curselection()
        if selected_index:
            selected_color = self.paints_color_box.get(selected_index)
            self.set_paint_color(selected_color)

    def color_to_hex(self, color_name):
        # Get the RGB values in the range of 0 to 65535
        rgb_tuple = self.root.winfo_rgb(color_name)

        # Normalize the RGB values to the range 0 to 255 and convert to hexadecimal
        r = int(rgb_tuple[0] / 256)
        g = int(rgb_tuple[1] / 256)
        b = int(rgb_tuple[2] / 256)

        # Format the hex color string and return it
        return f"#{r:02x}{g:02x}{b:02x}"

    def set_paint_color(self, color):
        self.paintColor = color
        self.frm_paint_buttons.config(bg=self.paintColor)

        # Update the selection in the Listbox
        color_list = self.paints_color_box.get(0, tk.END)  # Get all items from the Listbox
        isInTheList = False
        for index, item in enumerate(color_list):
            if self.color_to_hex(item) == color:
                isInTheList = True
                self.paints_color_box.selection_clear(0, tk.END)  # Clear any previous selection
                self.paints_color_box.selection_set(index)  # Select the matching color
                self.paints_color_box.activate(index)  # Set it as the active item
                break

        # if picked color is not on the list then deselect currently active element
        if not isInTheList and self.isPickingColor:
            self.paints_color_box.selection_clear(0, tk.END)

    def undo(self):
        if len(self.versions) == 0:
            self.isFirstUndo = False
            # self.save_action()
            return
        # function for undoing action
        if len(self.versions) == 1 or not self.isFirstUndo:
            image = self.versions.pop(len(self.versions) - 1)
        else:
            self.versions.pop(len(self.versions) - 1)
            image = self.versions.pop(len(self.versions) - 1)
        # making the image usable for tkinter
        self.isFirstUndo = False

        self.tk_image = ImageTk.PhotoImage(image)

        self.frm_paint.delete("all")
        self.frm_paint.create_image(0, 0, image=self.tk_image, anchor=tk.NW)

    def save_action(self):
        # Get the bounding box (position and size) of the canvas
        x1 = self.frm_paint.winfo_rootx()
        y1 = self.frm_paint.winfo_rooty()
        x2 = x1 + self.frm_paint.winfo_width()
        y2 = y1 + self.frm_paint.winfo_height()

        # Capture the canvas area as an image using ImageGrab
        canvas_image = ImageGrab.grab(bbox=(x1, y1, x2 - 2, y2 - 2))
        self.versions.append(canvas_image)

    def drawing(self, event):
        self.mouseX = event.x
        self.mouseY = event.y

        # makes sure there is no space between paint brush if it is moved quickly
        if self.isDrawing:
            if self.lastMouseX + self.lastMouseY > 0:
                self.interpolation(event)

            self.draw_pixel(self.mouseX, self.mouseY)
            self.lastMouseX, self.lastMouseY = self.mouseX, self.mouseY

    def interpolation(self, event):
        size = self.pencil_size_value.get()
        dx = self.mouseX - self.lastMouseX
        dy = self.mouseY - self.lastMouseY
        distance = math.sqrt(dx ** 2 + dy ** 2)

        steps = int(distance / size) * 2

        if steps == 0:
            # If the points are close enough, just draw a single square
            self.draw_pixel(self.mouseX, self.mouseY)
            return

        # Calculate the step increments for x and y
        x_step = dx / steps
        y_step = dy / steps

        # Draw squares at each interpolated step
        for i in range(steps):
            x = self.lastMouseX + i * x_step
            y = self.lastMouseY + i * y_step
            self.draw_pixel(x, y)

        self.draw_pixel(self.mouseX, self.mouseY)

    def draw_pixel(self, x, y):
        size = self.pencil_size_value.get()
        self.frm_paint.create_rectangle(x, y, x + size, y + size, fill=self.paintColor, outline="")

    def color_picker(self, event):
        if self.isPickingColor:
            sourceX = event.x_root
            sourceY = event.y_root
            pic = ImageGrab.grab()
            r, g, b = pic.getpixel((sourceX, sourceY))
            hue = f"#{r:02x}{g:02x}{b:02x}"
            self.set_paint_color(hue)
            self.frm_paint_buttons.config(bg=self.paintColor)

    def find_color(self, x, y):
        sourceX = x
        sourceY = y

        x1 = self.frm_paint.winfo_rootx()
        y1 = self.frm_paint.winfo_rooty()

        # Get the width and height of the canvas
        x2 = x1 + self.frm_paint.winfo_width()
        y2 = y1 + self.frm_paint.winfo_height()

        # Capture only the canvas area
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        r, g, b = screenshot.getpixel((sourceX, sourceY))
        hue = f"#{r:02x}{g:02x}{b:02x}"
        # screenshot.show()
        return hue

    def set_current_activity(self, setActivity):
        # important for undo tool, without it initial white frame wont be saved in activities
        if self.activity is None:
            self.save_action()

        if setActivity == 'Drawing':
            self.activity = "Drawing"
            self.isDrawing = True
            self.isPickingColor = False
            self.isFillingColor = False

            self.btn_drawing.config(bg='grey')
            self.btn_color_pick.config(bg='SystemButtonFace')
            self.btn_color_fill.config(bg='SystemButtonFace')

        elif setActivity == 'Picking':
            self.activity = "Picking"
            self.isDrawing = False
            self.isPickingColor = True
            self.isFillingColor = False

            self.btn_drawing.config(bg='SystemButtonFace')
            self.btn_color_pick.config(bg='grey')
            self.btn_color_fill.config(bg='SystemButtonFace')

        elif setActivity == 'ColorFilling':
            self.activity = "ColorFilling"
            self.isDrawing = False
            self.isPickingColor = False
            self.isFillingColor = True

            self.btn_drawing.config(bg='SystemButtonFace')
            self.btn_color_pick.config(bg='SystemButtonFace')
            self.btn_color_fill.config(bg='grey')

        self.activity_selector()

    def activity_selector(self):
        if self.activity == 'Drawing':
            self.frm_paint.unbind("<Button-1>")

            self.frm_paint.bind('<B1-Motion>', self.drawing)
            self.frm_paint.bind('<Button-1>', self.click_press)

        elif self.activity == 'Picking':
            self.frm_paint.bind('<Button-1>', self.color_picker)

        elif self.activity == 'ColorFilling':
            self.frm_paint.bind("<Button-1>", self.fill_with_color)
            # self.frm_paint.bind("<Button-1>", self.fill_with_color, add=True)

    def fill_with_color(self, event):
        if self.isFillingColor:
            self.sourceX = event.x
            self.sourceY = event.y

            x1 = self.frm_paint.winfo_rootx()
            y1 = self.frm_paint.winfo_rooty()

            # Get the width and height of the canvas
            x2 = x1 + self.frm_paint.winfo_width()
            y2 = y1 + self.frm_paint.winfo_height()

            # Capture only the canvas area
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            arrImg = []
            for y in range(self.frm_paint.winfo_height()):
                tempXArr = []
                for x in range(self.frm_paint.winfo_width()):
                    self.r, self.g, self.b = screenshot.getpixel((x, y))
                    self.hue = f"#{self.r:02x}{self.g:02x}{self.b:02x}"
                    tempXArr.append(self.hue)
                arrImg.append(tempXArr)

            self.flood_fill(arrImg, event.x, event.y, self.paintColor)
            self.draw_pixel(event.x, event.y)

            # ensures filled color is registered in self.versions = []
            root.update_idletasks()

    def flood_fill(self, img, x, y, newColor):
        q = deque()

        # Rows and columns of the display
        m = self.frm_paint.winfo_height()  # y-axis (rows)
        n = self.frm_paint.winfo_width()  # x-axis (columns)
        prevColor = img[y][x]  # Get the initial color
        if prevColor == newColor:
            return

        q.append((x, y))
        img[y][x] = newColor
        pixels_to_update = [(x, y)]  # Collect all pixels to update in a list

        while q:
            x, y = q.popleft()

            # Check if the adjacent pixels are valid and enqueue
            if x + 1 < n and img[y][x + 1] == prevColor:
                img[y][x + 1] = newColor
                pixels_to_update.append((x + 1, y))
                q.append((x + 1, y))

            if x - 1 >= 0 and img[y][x - 1] == prevColor:
                img[y][x - 1] = newColor
                pixels_to_update.append((x - 1, y))
                q.append((x - 1, y))

            if y + 1 < m and img[y + 1][x] == prevColor:
                img[y + 1][x] = newColor
                pixels_to_update.append((x, y + 1))
                q.append((x, y + 1))

            if y - 1 >= 0 and img[y - 1][x] == prevColor:
                img[y - 1][x] = newColor
                pixels_to_update.append((x, y - 1))
                q.append((x, y - 1))

        self.find_rect(sorted(pixels_to_update))

        lines = self.find_rect(sorted(pixels_to_update))
        for line in lines:
            self.frm_paint.create_line(line[0], line[1], line[2], line[3] + 1, fill=self.paintColor, width=1)

    # used for finding lines in floodfill algorithm
    def find_rect(self, pixels):

        rectCord = []
        # Outer loop using indices
        i = 0
        while i < len(pixels) - 1:
            x_1 = pixels[i][0]  # Access first element of the tuple at index i
            y_1 = pixels[i][1]  # Access second element of the tuple at index i

            j = i  # Start the inner loop from the next element

            # find bottom right corner
            y_2 = y_1

            # so that we always access the next X in pixels list
            numOfRemovedPixels = 0
            while pixels[j][0] == x_1 and j < len(pixels) - 1:
                numOfRemovedPixels += 1

                # in the case if there is a separation in the vertical line
                if pixels[j][1] - y_2 > 1:
                    rectCord.append((x_1, y_1, x_1, y_2))
                    y_1 = pixels[j][1]
                    y_2 = y_1
                    j += 1  # Increment inner loop index
                    continue

                y_2 = max(y_2, pixels[j][1])
                j += 1  # Increment inner loop index

            i += numOfRemovedPixels

            rectCord.append((x_1, y_1, x_1, y_2))

        # solves issue of the last pixel not being properly colored
        self.frm_paint.create_rectangle(pixels[-1][0], pixels[-1][1], pixels[-1][0] + 1, pixels[-1][1] + 1,
                                        fill=self.paintColor, outline="")
        return rectCord

    def click_press(self, event):
        self.isPressed = True
        if self.activity is not None and self.isFirstUndo == False:
            self.isFirstUndo = True
            self.save_action()
        if self.isDrawing:
            # Draws the initial pixel which would otherwise be drawn because of how binding works
            self.draw_pixel(event.x, event.y)
        # self.activity_selector()

    def click_release(self, event):

        self.mouseReleaseX = self.mouseX
        self.mouseReleaseY = self.mouseY
        self.lastMouseX, self.lastMouseY = 0, 0
        self.isPressed = False
        if self.activity is not None:
            self.isFirstUndo = True
            self.save_action()

    def open_file(self):
        filename = askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filename:
            # loading the image
            image = Image.open(filename)

            # making the image usable for tkinter
            self.tk_image = ImageTk.PhotoImage(image)

            self.frm_paint.delete("all")
            self.frm_paint.create_image(0, 0, image=self.tk_image, anchor=tk.NW)

    def save_file(self):
        filename = asksaveasfilename(defaultextension=".png",
                                     filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")])
        if filename:
            # Get the bounding box (position and size) of the canvas
            x1 = self.frm_paint.winfo_rootx()
            y1 = self.frm_paint.winfo_rooty()
            x2 = x1 + self.frm_paint.winfo_width()
            y2 = y1 + self.frm_paint.winfo_height()

            # Capture the canvas area as an image using ImageGrab
            canvas_image = ImageGrab.grab(bbox=(x1 + 2, y1 + 2, x2 - 2, y2 - 2))

            # Save the captured image to the file
            canvas_image.save(filename)

            print(f"Saved file as: {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
