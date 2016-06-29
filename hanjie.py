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
                    if not self._single_pass_row(i):
                        print "Puzzle is inconsistent"
                        return
                    made_change = True
            for i, x in enumerate(self._cols_to_check):
                if x == True:
                    if not self._single_pass_col(i):
                        print "Puzzle is inconsistent"
                        return
                    made_change = True
            if not made_change:
                break

        self._pretty_print()

if __name__ == "__main__":
    hanjie = Hanjie([[22,8,26],[19,16,22],[16,7,12,20],[15,8,6,6,19],[14,9,7,6,19],[13,1,9,6,7,17],[12,1,8,5,8,12],[12,1,8,7,9,10],[11,11,6,9,9],[10,11,6,10,7],[9,13,6,10,5],[7,13,7,13,4],[5,13,3,3,12,7,3],[4,13,5,20,2],[3,14,6,17,2,2],[2,13,6,22,1],[2,17,8,23,1],[1,4,13,5,19,3],[1,6,13,5,20,3],[1,6,14,5,20,1,4],[21,7,18,1,5],[25,7,17,5],[1,21,6,1,17,2,4],[2,20,6,1,19,2,3],[1,22,6,2,19,4,3],[1,20,1,9,21,4,3],[1,21,6,4,19,8],[29,3,1,19,8],[1,23,20,4,9],[22,18,4,7],[19,17,4,4,2],[17,16,4,3,2],[17,2,15,3,5,1],[17,3,14,4,7,2],[2,14,4,13,5,7,2],[2,14,4,11,13,2],[17,5,10,16],[17,4,9,12,4],[17,4,3,9,10,2,2],[17,3,9,18,2,1],[17,4,5,4,16,5],[16,2,3,5,14,6],[16,1,4,2,4,6,14,2,5],[16,8,5,4,4,3,9,2,5],[16,3,9,3,2,2,1,8,7],[16,2,6,4,4,3,1,1,7,7],[8,6,4,3,4,8,4,6,5],[8,6,5,2,4,1,3,5,8,5],[8,6,9,3,1,2,3,12],[8,5,7,2,1,2,3,9],[8,5,7,2,2,4,7],[6,6,4,2,3,9],[7,5,1,2,5,7],[5,5,2,2,13,1],[1,3,5,2,2,12,1],[1,2,6,2,3,2,12,2],[2,9,2,3,3,1,7,2],[4,9,3,3,3,1,3],[5,10,2,4,2,1,4],[5,9,3,5,2,1,1,5],[6,11,3,2,5,2,6],[6,5,3,10,6,9],[7,2,13,20],[8,10,2,1,1,18],[9,10,1,1,1,18],[11,10,1,2,1,18],[14,9,10,1,2,17],[19,5,7,3,2,4,17],[21,10,2,1,4,16],[22,5,9,3,15],[23,5,7,3,14],[23,5,1,2,13],[23,13,3,12],[23,6,3,11],[22,2,4,2,3,6],[21,4,3,3,2,4],[20,5,4,3,1,1],[19,3,3,4,2,2],[17,3,5,10,1],[16,4,4,2,6,2],[15,6,5,2,2],[14,6,7,4,2],[13,8,5,2,4,2],[11,9,7,2,2],[10,11,7,2,2],[9,12,5,4,2],[12,8,5,5,3],[9,10,5,2,4,5],[6,13,4,2,17],[5,6,3,2,1,2,2,13],[3,4,4,1,1,2,2],[1,4,5,2,1,2,3],[3,6,1,2,2,2],[3,6,2,2,1,3],[1,7,2,2,2,3]],[[20,10,38,2],[17,14,35,1],[15,17,34,2],[14,7,2,15,33,1],[13,3,1,23,32,2],[12,2,29,29,1,1],[12,34,26,2,1],[11,36,25,2,1],[11,36,24,2,2],[10,28,7,20,1,2,2],[9,30,1,7,19,1,2,3],[8,32,8,17,2,2,3],[6,3,32,4,17,1,2,2],[5,2,41,16,2,3,3],[4,3,43,14,2,2,2],[3,50,13,6,3],[2,30,15,12,6,2],[2,26,5,12,11,10],[2,25,6,8,8,11,9,1],[1,25,7,3,9,4,9,9,2],[1,25,8,2,7,5,1,8,9,3],[1,1,23,7,1,2,7,6,6,12],[1,24,5,4,5,6,4,11,1],[1,24,3,3,6,6,3],[26,8,6,5,9],[22,3,5,6,4,6,1],[17,2,2,2,1,1,1,8,3,14],[12,2,1,1,2,2,11,3,14],[10,1,1,2,4,14,3,10],[7,1,2,5,18,11],[5,3,16,6,6,11],[5,3,14,6,1,5,2,2,4],[3,1,1,3,8,2,6,2,2,3],[2,1,2,3,7,3,1,4,6,2,2,4],[2,19,3,4,7,2,2,1,2],[1,21,2,2,4,2,3,1,1,2,3],[1,22,1,2,3,2,1,3,2,2,5],[12,14,3,1,2,2,1,2,2,2,4],[12,3,5,2,5,2,2,2,1,2,1,3,2],[10,2,2,2,2,2,5,2,2,2,1,2,1,2],[6,1,2,3,4,2,2,2,1,2,2,2,2],[5,1,3,2,1,3,3,3,1,2,2],[5,3,2,2,2,3,2,1,2],[3,4,7,2,3,2,2,2],[3,2,6,2,1,2,1,1,2,2],[3,2,6,2,3,2,1,1,2],[4,1,1,2,10,1,2,2,1,2,2],[8,2,1,12,1,2,2,2,1,2],[13,19,2,3,2,2],[33,2,2,2,2],[34,1,2,1,2],[34,1,1,2,1],[34,1,2],[34,2,1],[1,34,2,1],[1,32,3,1],[1,32,4,2],[1,34,5,1],[2,38,3,2,2],[2,16,8,14,2,2],[3,16,5,5,3,7,7,2],[5,26,4,3,5,3,2],[5,32,3,5,5,2],[6,20,12,3,5,7,2],[6,19,12,1,3,4,8,2],[6,2,6,2,14,7,9,3],[6,2,5,16,7,9,3],[6,4,2,1,17,6,10,2],[7,3,1,7,25,11,1],[7,2,1,34,13],[8,3,1,33,12],[9,6,17,7,13],[9,6,4,6,4,4,13],[10,13,1,9,13],[10,13,6,1,7,15],[11,8,19,16],[12,2,10,18],[13,2,8,19],[15,8,21],[17,4,24]])
    hanjie.solve()
