import tkinter as tk

class AvailabilityGrid:
    def __init__(self, root):
        self.root = root
        self.root.title("Group's Availability")
        self.selected_slots = {}  # Track which time slots are selected
        self.start_selection = None  # Track where the drag starts

        # Title and headers
        self.create_header()

        # Create time slot grid
        self.create_grid()

        # Bind mouse events for click-and-drag selection
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)

    def create_header(self):
        # Title
        title_label = tk.Label(self.root, text="s's Availability", font=('Arial', 14))
        title_label.grid(row=0, column=0, columnspan=6, pady=10)

        # Legend
        tk.Label(self.root, text="Unavailable", bg="light pink", width=10).grid(row=1, column=1)
        tk.Label(self.root, text="Available", bg="green", width=10).grid(row=1, column=4)

        # Instructions
        instructions = tk.Label(self.root, text="Click and Drag to Toggle; Saved Immediately")
        instructions.grid(row=2, column=0, columnspan=6, pady=10)

    def create_grid(self):
        days = ["Wed", "Thu", "Fri", "Sat"]
        times = ["9:00 AM", "9:15 AM", "9:30 AM", "9:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM",
                 "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM", "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM",
                 "1:00 PM", "1:15 PM", "1:30 PM", "1:45 PM", "2:00 PM", "2:15 PM", "2:30 PM", "2:45 PM",
                 "3:00 PM", "3:15 PM", "3:30 PM", "3:45 PM", "4:00 PM", "4:15 PM", "4:30 PM", "4:45 PM",
                 "5:00 PM"]

        # Create day headers
        for col, day in enumerate(days, start=1):
            tk.Label(self.root, text=day, font=('Arial', 12)).grid(row=3, column=col)

        # Create time headers
        for row, time in enumerate(times, start=4):
            tk.Label(self.root, text=time).grid(row=row, column=0)

        # Create a grid of buttons
        self.buttons = {}
        for row in range(4, len(times) + 4):  # Create rows based on the time increments
            for col in range(1, 5):  # 1 to 5 is the column index for days
                btn = tk.Button(self.root, width=10, height=2, bg='light pink')  # Default to unavailable (pink)
                btn.grid(row=row, column=col, padx=5, pady=5)
                self.buttons[(row, col)] = btn

    def toggle_slot(self, row, col):
        """Toggle a slot between available and unavailable, if necessary."""
        btn = self.buttons[(row, col)]
        if btn.cget("bg") == "light pink":
            btn.config(bg="green")  # Mark as available
            self.selected_slots[(row, col)] = True
        elif btn.cget("bg") == "green":
            btn.config(bg="light pink")  # Mark as unavailable
            self.selected_slots.pop((row, col), None)

    def on_click(self, event):
        """Handle mouse click event to start selection."""
        row, col = self.get_grid_position(event)
        if row and col:
            self.start_selection = (row, col)
            self.toggle_slot(row, col)

    def on_drag(self, event):
        """Handle mouse drag event for selecting multiple slots."""
        row, col = self.get_grid_position(event)
        if row and col and (row, col) != self.start_selection:
            self.toggle_slot(row, col)
            self.start_selection = (row, col)  # Update last position to prevent flickering

    def on_release(self, event):
        """Handle mouse release event to stop selection."""
        self.start_selection = None

    def get_grid_position(self, event):
        """Get the row and column of the grid based on mouse position."""
        for (row, col), btn in self.buttons.items():
            if btn == self.root.winfo_containing(event.x_root, event.y_root):
                return row, col
        return None, None


# Create the main window
root = tk.Tk()
app = AvailabilityGrid(root)
root.mainloop()
