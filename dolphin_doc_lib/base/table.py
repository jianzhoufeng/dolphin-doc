from enum import Enum
from typing import Dict, List, Optional, Any

from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.text import TextParagraph

_UNOCCUPIED_CELL = -1


class Direction(Enum):
    "Direction for movement"
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Cell(Rect[int]):
    "Class that represents a table cell."

    def __init__(self, rect: Rect[int]):
        self.parent: Optional["Table"] = None
        self._paragraphs: List[TextParagraph] = []
        Rect.__init__(self, rect.left(), rect.top(), rect.width(),
                      rect.height())

    def append_paragraph(self, paragraph: TextParagraph) -> "Cell":
        "Append a paragraph"
        if paragraph.parent:
            raise ValueError(
                "Should not append a paragraph that already has a parent")
        paragraph.parent = self
        self._paragraphs.append(paragraph)
        return self

    def move(self, direction: Direction) -> Optional["Cell"]:
        "Return the next Cell follow the direction. None if already reach the boundary."
        assert self.parent
        return self.parent.move(self, direction)

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {
            "type": "cell",
            "rect": super().to_dict(),
            "paragraphs": list(map(lambda p: p.to_dict(), self._paragraphs))
        }


class Table(Rect[int]):
    "Class that stores list of cells"
    parent: Optional[Any] = None
    _cells: List[Cell] = []

    _board: List[List[int]]
    _occupied_area: int

    def __init__(self, row_num: int, col_num: int):
        super().__init__(0, 0, col_num, row_num)
        self.parent = None
        self._cells = []
        self._occupied_area = 0
        self._board = [[_UNOCCUPIED_CELL for x in range(col_num)]
                       for y in range(row_num)]

    def _fill_board(self, cell: Cell, idx: int):
        for row in range(cell.top(), cell.bottom() + 1):
            for col in range(cell.left(), cell.right() + 1):
                self._board[row][col] = idx

        self._occupied_area += cell.area()

    def add_cell(self, cell: Cell) -> "Table":
        "Add a new cell to the table."
        if not self.contains(cell):
            raise ValueError("Cell is not inside the table")

        for row in range(cell.top(), cell.bottom() + 1):
            for col in range(cell.left(), cell.right() + 1):
                if self._board[row][col] != _UNOCCUPIED_CELL:
                    raise ValueError(
                        "Point (row = {}, col = {}) already occupied".format(
                            row, col))

        cell.parent = self
        self._cells.append(cell)
        self._cells.sort(key=lambda cell: (cell.top(), cell.left()))
        self._occupied_area = 0
        for i, _cell in enumerate(self._cells):
            self._fill_board(_cell, i)
        return self

    def ready_to_move(self) -> bool:
        "Return whether all the cells are added"
        return self._occupied_area == self.area()

    def move(self, cell: Cell, direction: Direction) -> Optional[Cell]:
        "Find the cell follow the direction. None if reach the boundary."
        assert self.ready_to_move()
        if cell.parent is not self:
            raise ValueError("The cell parent is not this table")
        x: int = 0
        y: int = 0
        if direction == Direction.UP:
            x, y = cell.left(), cell.top() - 1
        elif direction == Direction.DOWN:
            x, y = cell.left(), cell.bottom() + 1
        elif direction == Direction.LEFT:
            x, y = cell.left() - 1, cell.top()
        else:
            x, y = cell.right() + 1, cell.top()
        if self.contains_point(x, y):
            return self._cells[self._board[y][x]]
        return None

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {
            "type": "table",
            "cells": list(map(lambda cell: cell.to_dict(), self._cells))
        }