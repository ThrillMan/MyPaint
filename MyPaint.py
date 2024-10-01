import math
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageGrab
import sys

sys.setrecursionlimit(1500)
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
        self.points = []

        self.setup_ui()

    def setup_ui(self):
        self.root.rowconfigure(0, minsize=800, weight=1)
        self.root.columnconfigure(1, minsize=800, weight=1)

        self.frm_paint = tk.Canvas(self.root, takefocus=True)
        self.frm_buttons = tk.Frame(self.root, relief=tk.RAISED, bd=2)
        # self.frm_buttons.rowconfigure(1, weight=1)

        self.frm_control_buttons = tk.Frame(self.frm_buttons, relief=tk.RAISED, bd=1)
        self.frm_control_buttons.grid_columnconfigure(0, weight=1)
        self.btn_open = tk.Button(self.frm_control_buttons, text="Open", command=self.open_file)
        self.btn_save = tk.Button(self.frm_control_buttons, text="Save As...", command=self.save_file)
        self.btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.frm_paint_buttons = tk.Frame(self.frm_buttons, relief=tk.RAISED, bd=1, background="black")

        self.paints_color_box = tk.Listbox(self.frm_paint_buttons)
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

        self.paints_color_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.paints_color_box.yview)

        # Position Listbox and Scrollbar
        self.paints_color_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind color selection event
        self.paints_color_box.bind("<<ListboxSelect>>", self.on_color_select)


        self.frm_tool_buttons = tk.Frame(self.frm_buttons, relief=tk.RAISED, bd=1)
        self.frm_tool_buttons.grid_columnconfigure(0, weight=1)
        self.btn_drawing = tk.Button(self.frm_tool_buttons, text="Draw",
                                     command=lambda: self.set_current_activity("Drawing"))
        self.btn_color_pick = tk.Button(self.frm_tool_buttons, text="Pick Color",
                                        command=lambda: self.set_current_activity("Picking"))
        self.btn_drawing.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_color_pick.grid(row=1, column=0, sticky="ew", padx=5, pady=5)


        self.frm_control_buttons.grid(row=0, column=0, sticky="ew", padx=5)
        self.frm_paint_buttons.grid(row=1, column=0, sticky="ew", padx=5)
        self.frm_tool_buttons.grid(row=2, column=0, sticky="ew", padx=5)

        self.frm_buttons.grid(row=0, column=0, sticky="ns")
        self.frm_paint.grid(row=0, column=1, sticky="nsew")

        # self.frm_paint.bind('<Motion>', self.drawing)
        self.frm_paint.bind('<ButtonPress>', self.click_press)
        self.frm_paint.bind('<ButtonRelease>', self.click_release)
        # self.root.bind('<space>', self.fill_with_color)
        self.frm_paint.bind('<space>', self.fill_with_color)

        self.frm_paint.focus_set()

    def on_color_select(self, event):
        #Handles the selection of a color from the Listbox.
        selected_index = self.paints_color_box.curselection()
        if selected_index:
            selected_color = self.paints_color_box.get(selected_index)
            self.set_paint_color(selected_color)
    def set_paint_color(self, color):
        self.paintColor = color
        self.frm_paint_buttons.config(bg=self.paintColor)

    def drawing(self, event):
        # print("draw")
        self.mouseX = event.x
        self.mouseY = event.y
        if self.isPressed and self.isDrawing:
            if self.lastMouseX + self.lastMouseY > 0:
                self.interpolation(event)
            self.frm_paint.create_line(self.mouseX, self.mouseY, self.mouseX + 1, self.mouseY + 1, fill=self.paintColor)
            # self.draw_pixel(self.mouseX,self.mouseY)
            self.lastMouseX, self.lastMouseY = self.mouseX, self.mouseY
            # if abs(self.lastMouseX - self.mouseX)>3 or abs(self.lastMouseY - self.mouseY)>3:
            # self.interpolation()
        # print(f"Mouse position: ({event.x}, {event.y})")

    def draw_pixel(self, x, y):
        # print("draw pixel","x:",x,"y",y)
        # self.frm_paint.create_rectangle(x, y, x , y , fill=self.paintColor)
        self.frm_paint.create_line(x, y, x + 1, y + 1, fill=self.paintColor)

    def color_picker(self, event):
        # rint("color")
        # print("x:",event.x," y:",event.y)
        # print(self.frm_paint.winfo_width())
        if self.isPressed and self.isPickingColor:
            self.sourceX = event.x_root
            self.sourceY = event.y_root
            self.pic = ImageGrab.grab()
            self.r, self.g, self.b = self.pic.getpixel((self.sourceX, self.sourceY))
            self.hue = f"#{self.r:02x}{self.g:02x}{self.b:02x}"
            self.paintColor = self.hue
            print(self.hue)
            print(self.r, self.g, self.b)
            self.frm_paint_buttons.config(bg=self.paintColor)

    def find_color(self, x, y):
        self.sourceX = x
        self.sourceY = y
        # self.pic = ImageGrab.grab()

        x1 = self.frm_paint.winfo_rootx()
        y1 = self.frm_paint.winfo_rooty()

        # Get the width and height of the canvas
        x2 = x1 + self.frm_paint.winfo_width()
        y2 = y1 + self.frm_paint.winfo_height()

        # Capture only the canvas area
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        # self.r, self.g, self.b = self.pic.getpixel((self.sourceX , self.sourceY))
        self.r, self.g, self.b = screenshot.getpixel((self.sourceX, self.sourceY))
        self.hue = f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        # screenshot.show()
        return self.hue

    def set_current_activity(self, setActivity):
        if setActivity == 'Drawing':
            self.activity = "Drawing"
            self.isDrawing = True
            self.isPickingColor = False
        elif setActivity == 'Picking':
            self.activity = "Picking"
            self.isDrawing = False
            self.isPickingColor = True

    def activity_selector(self):
        if self.activity == 'Drawing':
            self.frm_paint.bind('<Motion>', self.drawing)
            # self.drawing(event)
        elif self.activity == 'Picking':

            self.frm_paint.bind('<Motion>', self.color_picker)
            # self.color_picker(event)

    def interpolation(self, event):
        # print(self.mouseX, self.lastMouseX,self.mouseY, self.lastMouseY)
        self.frm_paint.create_line(self.mouseX, self.mouseY, self.lastMouseX, self.lastMouseY, fill=self.paintColor,
                                   smooth=1)

    def fill_with_color(self, event):
        # print("fill")
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

        ogColor = arrImg[event.y][event.x]
        print("ogcolor:", ogColor, event.x, event.y)
        self.flood_fill(arrImg, event.x, event.y, self.paintColor)
        self.draw_pixel(event.x, event.y)

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

    # used for finding rectangles in floodfill algorithm
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

        print(len(pixels), len(rectCord))

        # solves issue of the last pixel not being properly colored
        self.draw_pixel(pixels[-1][0], pixels[-1][1])
        return rectCord

    def click_press(self, event):
        self.mousePressX = event.x
        self.mousePressY = event.y
        self.isPressed = True
        self.activity_selector()

    def click_release(self, event):
        self.mouseReleaseX = self.mouseX
        self.mouseReleaseY = self.mouseY
        self.lastMouseX, self.lastMouseY = 0, 0
        self.isPressed = False
        # print("Mouse released")

    def open_file(self):
        filename = askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filename:
            print(f"Opened file: {filename}")
            # Add logic to open and display the image on the canvas

    def save_file(self):
        filename = asksaveasfilename(defaultextension=".png",
                                     filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")])
        if filename:
            print(f"Saved file as: {filename}")
            # Add logic to save the canvas content as an image


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
