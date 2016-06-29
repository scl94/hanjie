# hanjie.py
# This module contains a class which represents a Hanjie puzzle, and is able to
# make logical deductions based on the available clues and the current state
# of the puzzle.

import copy
from PIL import Image

from linesolver import LineSolver

class Hanjie(object):
    """
    This class represents a standard Hanjie puzzle, including the clues and the
    current state of the board, and is able to make logical deductions in order
    to solve the puzzle.

    Currently, the only logical deductions that are able to be made by this
    solver are those which focus on a single line at a time - that is, when
    examining a single row or column, if there is a cell or cells which must
    be filled or must be unfilled, this solver can spot that, but it cannot
    make deductions based on interplay between two or more rows or columns
    simultaneously.
    """

    def __init__(self, row_clues, col_clues):
        """
        Initialise the puzzle with the set of clues defining it. The size of
        the grid can be inferred from the number of clues provided.
        """
        # Create an empty grid for the puzzle - we will let 0 represent an
        # undetermined cell, 1 represent a filled cell and -1 represent a cell
        # which is definitely unfilled.
        self._width = len(col_clues)
        self._height = len(row_clues)
        self._grid = [[0] * self._width for _ in xrange(self._height)]

        # Store off the clues for use when solving the puzzle.
        self._row_clues = copy.deepcopy(row_clues)
        self._col_clues = copy.deepcopy(col_clues)

        # Keep track of which lines are unchanged since the last time we
        # tried to deduce information about them
        self._rows_to_check = [True] * self._height
        self._cols_to_check = [True] * self._width

    def _check_consistency(self, line, clues):
        """
        Given the current state of a single line (row or column) and the clues
        associated with that line, check that there is no contradiction (that
        is, that there exists a solution to the line).

        Returns True if the line is consistent and False if inconsistent.
        """
        line_solver = LineSolver(line, clues)
        return line_solver.has_solution()

    def _make_deductions(self, line, clues):
        """
        Given the current state of a single line (row or column) and the clues
        associated with that line, firstly, check that no contradiction has
        arisen, and secondly, make any logical deductions possible from this
        line alone.

        Returns a list of deductions if the state of the line is consistent and
        False if there is an inconsistency.
        """
        # First establish consistency of the current state of the line
        if not self._check_consistency(line, clues):
            return False

        # Now iterate over each cell which is as yet undetermined, and check
        # whether the line remains consistent when that cell is filled or
        # unfilled.
        deductions = []
        for i in xrange(len(line)):
            if line[i] == 0:
                line[i] = 1
                if not self._check_consistency(line, clues):
                    deductions.append((i, -1))
                line[i] = -1
                if not self._check_consistency(line, clues):
                    deductions.append((i, 1))
                line[i] = 0

        return deductions

    def _single_pass_row(self, index):
        """
        Make a pass over the row with the given index, making any deductions
        which are possible. Returns True if no contradiction arose and False
        otherwise.
        """
        # Extract the line and the clues from the grid
        line = [self._grid[index][j] for j in xrange(self._width)]
        clues = self._row_clues[index]

        # Pull out any deductions that we can make
        deductions = self._make_deductions(line, clues)
        if deductions == False:
            return False
        
        # Apply the deductions to the grid and mark any intersecting columns
        # as requiring another pass
        for ix, val in deductions:
            self._grid[index][ix] = val
            self._cols_to_check[ix] = True
        self._rows_to_check[index] = False
        return True

    def _single_pass_col(self, index):
        """
        Make a pass over the column with the given index, making any deductions
        which are possible. Returns True if no contradiction arose and False
        otherwise.
        """
        # Extract the line and the clues from the grid
        line = [self._grid[j][index] for j in xrange(self._height)]
        clues = self._col_clues[index]

        # Pull out any deductions that we can make
        deductions = self._make_deductions(line, clues)
        if deductions == False:
            return False
        
        # Apply the deductions to the grid and mark any intersecting columns
        # as requiring another pass
        for ix, val in deductions:
            self._grid[ix][index] = val
            self._rows_to_check[ix] = True
        self._cols_to_check[index] = False
        return True

    def _pretty_print(self):
        """
        Display the current state of the grid.
        """
        sz = 7
        img = Image.new('RGB', (sz * self._width, sz * self._height), "red")
        pixels = img.load()

        for i in xrange(self._width):
            for j in xrange(self._height):
                if self._grid[j][i] == 1:
                    for ix in xrange(sz * i, sz * (i + 1)):
                        for jx in xrange(sz * j, sz * (j + 1)):
                            pixels[ix, jx] = (0, 0, 0)
                elif self._grid[j][i] == -1:
                    for ix in xrange(sz * i, sz * (i + 1)):
                        for jx in xrange(sz * j, sz * (j + 1)):
                            pixels[ix, jx] = (255, 255, 255)

        img.show()

    def solve(self):
        """
        Repeatedly make passes over rows and columns until no more deductions
        can be made.
        """
        while True:
            made_change = False
            for i, x in enumerate(self._rows_to_check):
                if x == True:
                    self._single_pass_row(i)
                    made_change = True
            for i, x in enumerate(self._cols_to_check):
                if x == True:
                    self._single_pass_col(i)
                    made_change = True
            if not made_change:
                break

        self._pretty_print()

if __name__ == "__main__":
    hanjie = Hanjie([[3,13,2,6,5,2],[5,10,2,2,3,2,3,5,3],[3,13,2,9,3,3],[2,9,1,2,2,7,3,4,2],[4,13,4,14,4],[3,3,11,1,5,12,4],[2,2,14,3,3,5,1,2],[4,3,13,3,5,1,3],[2,2,11,2,5,3],[2,2,11,2,3,2],[4,4,9,3,3,3],[2,4,8,3,3,4],[4,8,3,3,3],[5,9,4,3,2],[4,10,10,1],[3,11,12,1],[2,1,8,15,1],[2,1,8,5,12],[2,1,8,20],[3,1,8,6,3,2,3,9],[3,1,3,13,1,1,4,8],[5,3,11,2,4,8],[5,11,2,3,7],[4,4,4,3,1,6],[3,3,4,5,1,5],[4,3,5,2,4,2],[1,3,2,5,3,1],[3,3,5,4,1],[6,5,3,5],[1,7,4,3,3,5,1],[1,7,4,5,5,2],[1,6,4,7,7],[3,1,10,2,6,4],[3,1,2,11,2,9,5],[1,3,1,12,7,9,5],[5,1,4,2,3,3,3,15],[8,3,2,2,1,14,6],[1,1,2,3,2,4,9,5],[1,2,7,1,6,1,9,5],[1,2,1,3,7,10,4],[1,1,1,1,1,9,1,13,4],[1,2,1,3,11,17,4],[1,1,1,1,1,1,5,19,4,4],[1,1,3,5,19,4,2,1],[1,2,1,1,2,6,14,2,3,3,1],[1,2,1,1,5,3,4,7,1,3,3],[1,1,7,4,4,2,2,4,4],[1,2,9,5,2,1,4,1,2],[1,2,11,6,4,2,3],[1,14,8,5,3,2],[1,16,7,7,3,2],[13,6,3,2,1,4,2,2,2],[14,6,1,4,5,2,3,1],[10,3,3,3,1,1,3,1,2,3,1],[10,3,2,3,1,3,1,1,3,1,2,1],[10,4,2,2,2,2,1,7,2,2,1],[7,3,3,3,3,2,2,2,2,3,2,3],[7,3,3,2,3,3,2,3,2,3,3,2],[8,2,4,3,2,2,3,3,3,3,2,2],[8,3,3,3,3,3,3,5,3,2,2]],[[1,1,2,2,19,8],[1,2,2,2,4,2,5,2,9],[2,2,1,2,7,5,2,1,2,2,9],[1,1,2,2,3,10,3,2,2,2,2,10],[1,2,1,8,9,4,10],[2,1,11,3,5,1,9,11],[2,10,2,3,6,1,1,11],[1,4,4,3,12,2,3,1,1,1,8,2],[4,3,2,15,1,10],[4,4,11,9,8,13],[20,1,2,6,2,1,2,7,4],[29,7,6,10,1],[30,6,14],[38,15],[36,1,7,5],[23,8,12,2],[18,4,6,17],[3,12,6,6,6,13],[3,7,3,2,2,11,4,4],[1,1,5,4,2,3,12,4,2],[1,2,3,4,2,3,4,5,7],[2,1,2,3,1,9,5,7],[7,2,1,9,4,1,4],[3,3,3,14,3,1],[1,2,3,1,3,7,4,3],[2,1,2,2,4,7,4,1,4],[1,2,2,4,1,4,2,2,1,2,3],[2,3,3,2,2,1,4,4,3,1],[2,2,3,3,2,1,5,2,3],[4,4,7,2,5,2,3],[1,4,3,2,3,3,6,2,2],[7,4,1,1,3,3,6,2,1],[8,4,1,3,2,6,2],[1,10,2,1,2,2,2,6,2],[1,4,10,4,3,1,6,2],[2,4,11,12,6,1],[2,6,9,10,2,1,2,5],[11,6,17,4,5],[11,6,2,18,4,1,2],[6,13,19,5,4],[1,2,3,30,6,7],[1,2,3,19,18,6],[2,1,1,3,11,2,1,16,3,2],[2,1,3,13,2,1,11,7],[2,1,1,3,11,1,1,2,4,3,5],[1,2,1,1,2,7,1,5,10,3],[1,1,2,1,7,13,8],[2,2,2,15,8],[2,2,2,9,6,4],[2,2,2,11,8]])
    hanjie.solve()
