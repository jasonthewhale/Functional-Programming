import tkinter as tk
from tkinter import filedialog

Box = tuple[int, int]
Coordinate = tuple[int, int]

class Model():
    def __init__(self) -> None:
        self._board = [[None for _ in range(9)] for _ in range(9)] #: self._Board
        self._fixed = []

    def get(self, row: int, col: int) -> None | int:
        """
        Return None when off the grid.
        """
        if 0 <= row < 9 and 0 <= col < 9:
            return self._board[row][col]
        return None

    def delete(self, row: int, col: int) -> None:
        if not self.isFixed(row, col):
            self._board[row][col] = None

    def setter(self, row: int, col: int, number: int, fixed=False) -> None:
        """
        Sets the grid if legal setting and legal position
        """
        if 0 <= row < 9 and 0 <= col < 9 and 1 <= number < 10:
            self._board[row][col] = number

            if fixed:
                self._fixed.append((row, col))

    def isFixed(self, row: int, col: int) -> bool:
        return (row, col) in self._fixed

    def duplicate(self, row: int, col: int) -> bool:
        """Return true if number at <row, col> is duplicate in <row>, <col>
        or grid where <row>, <col> resides.
        """
        val = self.get(row, col)
        
        xs = self._rows()[row]
        if sum(val == x for x in xs) > 1:
            return True
        
        xs = self._columns()[col]
        if sum(val == x for x in xs) > 1:
            return True

        xs = self._grids()[row//3*3 + col//3]
        if sum(val == x for x in xs) > 1:
            return True

        return False

    def _check(self, xs: list[None | int]) -> bool:
        """
        Check xs contains ALL numbers 1 through 9.
        """
        for k in range(1,10):
            if k not in xs:
                return False
        return True

    def _rows(self) -> list[list[None | int]]:
        """
        Returns a list of all rows of the self._board as lists.
        """
        return self._board

    def _columns(self) -> list[list[None | int]]:
        """
        Returns a list of all columns of the self._board as lists.
        """
        columns = []
        for col in range(0,9):
            column = []
            for row in range(0,9):
                column.append(self._board[row][col])
            columns.append(column)
        return columns

    def _grids(self) -> list[list[None | int]]:
        """
        Returns a list of all grids of the self._board as lists.
        """
        ans = []
        for k in range(0,9,3):
            for ell in range(0, 9, 3):
                g = self._board[k][ell:ell+3] + self._board[k+1][ell:ell+3] + self._board[k+2][ell:ell+3]
                ans.append(g)
        return ans

    def has_won(self) -> bool:
        
        # check all rows
        for row in self._rows():
            if not self._check(row):
                return False
        
        # check all cols
        for col in self._columns():
            if not self._check(col):
                return False

        # check all grids
        for grid in self._grids():
            if not self._check(grid):
                return False

        return True

class View(tk.Canvas):
    """
    View for main Controller grid.
    """
    _SIDE_LENGTH = 40     # size of single box
    _OUTTER_PADDING = 10  # padding the Controller self._board

    def __init__(self, master: tk.Tk, model: Model, signal: tk.IntVar, **kwargs) -> None:
        self._board_side = 2*self._OUTTER_PADDING + 9*self._SIDE_LENGTH
        super().__init__(
            master, 
            width=self._board_side,
            height=self._board_side,
            **kwargs)

        self._model = model
        self._signal = signal

        self.bind("<Button>", self._click_handler)
        self._active_box = None # : Box

        self.bind_all("<Key>", self._keypress_handler)

        self.flash()

    def _keypress_handler(self, event):
        print(f"{event.char}")
        abox   = self._active_box
        
        if event.char == 'x':
            self._model.delete(*abox)
            self.flash()

        try:
            number = int(event.char)
            if abox and not self._model.isFixed(*abox):
                self._model.setter(*abox, number)
                self._signal.set(1)  # send signal back to controller
                self.flash()
        except ValueError:
            return None

    def _click_handler(self, event):
        """What to do when canvas is clicked
        """
        coord = (event.x, event.y)
        self._active_box = self._cordinate_to_box(coord)
        self.flash()
        print(f"{coord} {self._active_box}")

    def _bbox(self, box: Box) -> Coordinate:
        """
        Bounding box for <box>
        """
        row, col = box
        x_min = self._OUTTER_PADDING + col*self._SIDE_LENGTH
        y_min = self._OUTTER_PADDING + row*self._SIDE_LENGTH

        x_max = x_min + self._SIDE_LENGTH
        y_max = y_min + self._SIDE_LENGTH

        return (x_min, y_min), (x_max, y_max)

    def _get_midpoint(self, box: Box) -> Coordinate:
        """Return the Coordinateinate of the middle of <box>
        """
        (x_min, y_min), _ = self._bbox(box)
        return (x_min + self._SIDE_LENGTH//2, y_min + self._SIDE_LENGTH//2)

    def _draw_box(self, box: Box) -> None:
        """Draw a <box>
        """
        self.create_rectangle(
            *self._bbox(box), 
            fill="light blue" if self._model.isFixed(*box) else "white",
            outline="black",
            width=1)
        self._draw_number(box)
    
    def _draw_active_box(self) -> None:
        """Highlight active box.
        """
        if self._active_box:
            self.create_rectangle(
                *self._bbox(self._active_box), 
                outline="red",
                width=4)

    def _cordinate_to_box(self, coord: Coordinate) -> None | Box:
        """
        """
        x, y = coord[0] - self._OUTTER_PADDING, coord[1] - self._OUTTER_PADDING
        row, col = y//self._SIDE_LENGTH, x//self._SIDE_LENGTH
        if row in range(9) and col in range(9):
            return (row, col)
        return None

    def flash(self) -> None:
        """Redraw the screen.
        """
        # background (so red lines at border are overwritten)
        self.create_rectangle(
            0, 0, self._board_side, self._board_side,
            fill="gray")

        for row in range(0, 9):
            for col in range(0, 9):
                self._draw_box((row, col))

        # grid lines
        grid_lines = []
        (x0, y0), _ = self._bbox((0, 3))
        (x1, _), (_, y1) = self._bbox((8, 3))
        grid_lines.append( (x0, y0, x1, y1) )

        (x0, y0), _ = self._bbox((0, 6))
        (x1, _), (_, y1) = self._bbox((8, 6))
        grid_lines.append( (x0, y0, x1, y1) )

        (x0, y0), _ = self._bbox((3, 0))
        (_, y1), (x1, _) = self._bbox((3, 8))
        grid_lines.append( (x0, y0, x1, y1) )

        (x0, y0), _ = self._bbox((6, 0))
        (_, y1), (x1, _) = self._bbox((6, 8))
        grid_lines.append( (x0, y0, x1, y1) )

        for line in grid_lines:
            self.create_line(*line, fill="black", width=3)

        self._draw_active_box()

    def _draw_number(self, box: Box) -> None:
        """
        """
        if self._model.get(*box):
            colour = "black"
            if self._model.isFixed(*box):
                colour = "blue"
            if self._model.duplicate(*box):
                colour = "red"

            self.create_text(
                *self._get_midpoint(box),
                text = f"{self._model.get(*box)}", 
                fill = colour, 
                font = (f'Helvetica 20 bold'))

class Controller():
    def __init__(self, master: tk.Tk) -> None:
        signal = tk.IntVar()
        self._model  = Model()
        self._view = View(master, self._model, signal)
        self._view.pack()
        self._load_board("board_one.txt")
        self._view.flash()

        while True:
            self._view.wait_variable(signal)  # wait for valid number entry
            
            if self._model.has_won():
                print("You have won")
                break

        master.destroy()
        return

    def _load_board(self, filename: str) -> None:
        """ 
        """
        board = ""
        with filedialog.askopenfile(mode='r') as file:
            for line in file:
                if not line.startswith('-'):
                    line = line.replace("|","")
                    line = line.replace("\n","") # BW file.readlines() should do this
                    board += line
        
        for k, char in enumerate(board):
            number = None if char == " " else int(char)
            print(f"{k} {k//3} {k%3}")
            if number != None:
                self._model.setter(k//9, k%9, number, fixed=True)


def main():
    """ Entry-point for Suduko. """
    root = tk.Tk()
    controller = Controller(root)
    root.mainloop()

if __name__ == '__main__':
    main()