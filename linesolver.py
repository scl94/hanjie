# linesolver.py
# This module contains a class which attempts to verify the consistency of a
# single line (row or column) of a Hanjie puzzle, given the cells already
# filled in.

import bisect
import copy

class LineSolver(object):
    """
    This class determines a single solution (if it exists) to a single line
    of a Hanjie puzzle, which is consistent with any cells which have already
    been filled in.

    It attempts to find a solution by placing blocks left-to-right and then
    applying a depth-first search to find solutions to the whole line.
    """
    def __init__(self, line, clues):
        """
        Initialise some data specific to the line being solved.
        """
        # Store the current state of the line and the clues associated with it.
        # For convenience, we actually append an extra cell to the end of the
        # line, and set this cell to empty.
        self._line = copy.deepcopy(line) + [-1]
        self._clues = copy.deepcopy(clues)
        self._length = len(self._line)

        # Additionally, some nodes on the search tree can be reached in more
        # than one way. Here, we keep track of the positions that have been
        # seen before, so as not to repeat work unnecessarily.
        self._seen_positions = set()

        # Calculate suffix-sums for the lengths of blocks required
        self._length_suffix = [sum([x + 1 for x in self._clues])]
        for x in self._clues:
            self._length_suffix.append(self._length_suffix[-1] - (x + 1))

        # Store the positions of the shaded cells in the line
        self._shaded_pos = [-1]
        for i, x in enumerate(self._line):
            if x == 1:
                self._shaded_pos.append(i)

    def _root(self):
        """
        Each node in the tree consists of a pair of numbers - the index of the
        first cell not yet reached by a block that we have attempted to place,
        and the index of the first clue corresponding to a block that we have
        not yet placed.

        Initially, at the root of the tree, these numbers are both 0.
        """
        return (0, 0)

    def _reject(self, node):
        """
        We should reject this node if there is insufficient space left in the 
        line to place the remaining blocks.

        If this situation ever arises, then due to the ordering of nodes in the
        tree (we always place in the leftmost available position first) this
        indicates that the entire row is inconsistent, and this should be
        raised all the way to the top of the tree.
        """
        # Extract the first unused block and the position in the line from
        # the node
        line_pos, first_block = node

        # Check that the space required for the remaining blocks is small
        # enough to fit in the remaining space in the line.
        if self._length_suffix[first_block] > self._length - line_pos:
            return True
        else:
            return False

    def _accept(self, node):
        """
        We should accept this node if all blocks have been placed successfully
        and there are no shaded blocks past the end of the last block.
        """
        line_pos, first_block = node
        if first_block == len(self._clues) and line_pos > self._shaded_pos[-1]:
            return True
        else:
            return False

    def _is_allowed(self, block_size, end_pos):
        """
        Determine if it is possible to place a block of the given size in the
        cells immediately preceeding the given end position.
        """
        return (self._line[end_pos] != 1 and 
                all(self._line[i] != -1 
                    for i in xrange(end_pos - block_size, end_pos)))

    def _children(self, node):
        """
        The only children worth considering are:

        0) The leftmost position for the next block.
        1) The leftmost position for the next block providing that it overlaps
           with one of the coming shaded blocks.
        2) The leftmost position for the next block providing that it overlaps
           with two of the coming shaded blocks.

        etc. It is easy to iterate over these possible placements.
        """
        # Extract the first unused block and the position in the line from the
        # node.
        line_pos, first_block = node
        
        # If we've used all the blocks, then there are no children
        if first_block == len(self._clues):
            return
        block_size = self._clues[first_block]

        # Find the position of the rightmost cell we can end at without
        # having skipped over any shaded cells.
        first_shaded_ix = bisect.bisect_left(self._shaded_pos, line_pos)
        if first_shaded_ix < len(self._shaded_pos):
            first_shaded_cell = self._shaded_pos[first_shaded_ix]
        else:
            first_shaded_cell = self._length
        last_cell = min(self._length - 1, first_shaded_cell + block_size)

        # Iterate over the coming shaded blocks to find the possible placements
        block_end = line_pos + block_size
        while block_end <= last_cell:
            while not self._is_allowed(block_size, block_end):
                block_end += 1
                if block_end > last_cell: return
            yield(block_end + 1, first_block + 1)
            while self._line[block_end] != 1:
                block_end += 1
                if block_end > last_cell: return
            block_end += 1

    def has_solution(self):
        """
        Iteratively search until a solution is found.
        """
        stack = [self._root()]
        while stack:
            node = stack.pop()
            if self._reject(node): return False
            if self._accept(node): return True

            children = []
            for next_node in self._children(node):
                children.append(next_node)
                for child in reversed(children):
                    stack.append(child)

        return False
