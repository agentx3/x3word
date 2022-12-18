from typing import Dict, Tuple, List
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

FONT_PATH = os.path.join("x3word", "Ubuntu-Regular.ttf")


class Word:
    def __init__(self, word: str, hint: str, direction: str, start_pos: Tuple[int, int], number: int = None) -> None:
        self._word = word
        self._number = number
        self._hint = hint
        self._direction = direction
        self._length = len(word)
        self._start_pos = start_pos  # Row, Column
        self._is_guessed = False
        self._solver: int | None = None
        self._guess: str | None = None
        self._guesser: int | None = None

    def __repr__(self) -> str:
        return f"Word({self._word}, {self._hint}, {self._direction}, {self._start_pos}, {self._number})"

    @property
    def solver(self) -> int | None:
        return self._solver

    @solver.setter
    def solver(self, solver: int) -> None:
        self._solver = solver

    @property
    def guesser(self) -> int | None:
        return self._guesser

    @guesser.setter
    def guesser(self, guesser: int) -> None:
        self._guesser = guesser

    @property
    def word(self) -> str:
        return self._word

    @word.setter
    def word(self, word: str) -> None:
        self._word = word

    @property
    def guess(self) -> str:
        return self._guess

    @guess.setter
    def guess(self, guess: str) -> None:
        self._guess = guess

    @property
    def hint(self) -> str:
        return self._hint

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, number: int) -> None:
        self._number = number

    @property
    def direction(self) -> str:
        return self._direction

    @property
    def length(self) -> int:
        return self._length

    @property
    def start_pos(self) -> Tuple[int, int]:
        return self._start_pos

    @property
    def is_guessed(self) -> bool:
        return self._is_guessed

    @is_guessed.setter
    def is_guessed(self, is_guessed: bool) -> None:
        self._is_guessed = is_guessed

    @property
    def end_pos(self) -> Tuple[int, int]:
        match self.direction:
            case "r":
                return self.start_pos[0], self.start_pos[1] + self.length
            case "d":
                return self.start_pos[0] + self.length, self.start_pos[1]
            case "l":
                return self.start_pos[0], self.start_pos[1] - self.length
            case "u":
                return self.start_pos[0] - self.length, self.start_pos[1]
            case _:
                raise ValueError("Direction must be 'r', 'd', 'l', or 'u'")


class CrosswordGrid:
    def __init__(self, word_dict: Dict[str, Dict[int, Word]], **kwargs):
        self.words = word_dict
        self.font_size = kwargs.get("font_size", 36)
        self.number_font_size = kwargs.get("number_font_size", 15)
        self.font_path = kwargs.get("font_path", FONT_PATH)
        self.cell_size = kwargs.get("cell_size", 60)
        self.padding = kwargs.get("padding", 10)
        self.cell_fill = kwargs.get("cell_fill", (255, 255, 255, 255))
        self.cell_stroke_color = kwargs.get("cell_stroke_color", (0, 0, 0, 255))
        self.cell_stroke_width = kwargs.get("cell_stroke_width", 1)
        self.background_color = kwargs.get("background_color", (210, 70, 58))
        self.font_color = kwargs.get("font_color", (0, 0, 0, 255))
        self.number_color = kwargs.get("number_color", (0, 0, 0, 255))
        self._correct_answers = {"r": {}, "d": {}, "l": {}, "u": {}}
        self._directions = ["r", "d", "l", "u"]
        self._grid_size: Tuple[int, int] = self.get_grid_size()
        self._grid: Image = self.generate_initial_grid()
        self._drawn_words = {"r": {}, "d": {}, "l": {}, "u": {}} # Words that have been drawn

    @property
    def grid_size(self) -> Tuple[int, int]:
        return self._grid_size

    @property
    def font(self) -> ImageFont:
        return ImageFont.truetype(self.font_path, self.font_size)

    @property
    def number_font(self) -> ImageFont:
        return ImageFont.truetype(self.font_path, self.number_font_size)

    @property
    def text_offset_y(self) -> float:
        return self.font_size / 2 - self.cell_size * 0.1 + self.padding

    @property
    def text_offset_x(self) -> float:
        return self.font_size / 2 + self.padding

    @property
    def grid(self) -> Image:
        return self._grid

    @property
    def directions(self) -> list[str]:
        return self._directions

    @property
    def correct_answers(self) -> Dict[str, Dict[int, Word]]:
        return self._correct_answers

    def add_to_correct(self, word: Word):
        self._correct_answers[word.direction][word.number] = word

    def clear_correct(self, word: Word):
        return self._correct_answers[word.direction].pop(word.number, False)

    def refresh(self):
        for direction in self.directions:
            for word in self._drawn_words[direction].values():
                self.draw_word(word)

    def generate_initial_grid(self) -> Image:
        """Generate a blank grid with the correct size with boxes for the words"""
        grid = Image.new(
            "RGBA",
            (
                self._grid_size[1] * self.cell_size + self.padding * 2,
                self._grid_size[0] * self.cell_size + self.padding * 2
            ),
            self.background_color
        )
        draw = ImageDraw.Draw(grid)
        for direction in self.directions:

            for word in self.words[direction].values():
                for i in range(word.length):
                    # Draw the borders
                    x_shift: int = {"r": i, "l": -i, "d": 0, "u": 0}[direction]
                    y_shift: int = {"r": 0, "l": 0, "d": i, "u": -i}[direction]
                    draw.rectangle(
                        (
                            (word.start_pos[1] + x_shift) * self.cell_size + self.padding,
                            (word.start_pos[0] + y_shift) * self.cell_size + self.padding,
                            (word.start_pos[1] + x_shift + 1) * self.cell_size + self.padding,
                            (word.start_pos[0] + y_shift + 1) * self.cell_size + self.padding
                        ),
                        outline=self.cell_stroke_color,
                        width=self.cell_stroke_width,
                        fill=self.cell_fill
                    )
                # Draw numbers
                draw.text(
                    (
                        (word.start_pos[1] + 0) * self.cell_size + self.cell_size * 0.1 + self.padding,
                        (word.start_pos[0] + 0) * self.cell_size + self.cell_size * 0.05 + self.padding
                    ),
                    str(word.number),
                    font=self.number_font,
                    fill=self.number_color
                )
        return grid

    def add_to_drawn(self, word: Word):
        self._drawn_words[word.direction][word.number] = word

    def draw(self):
        for direction in self.directions:
            for word in self._drawn_words[direction].values():
                self.draw_word(word)

    def draw_word(self, word: Word) -> None:
        """Draw a word on the grid"""
        draw = ImageDraw.Draw(self._grid)
        for i in range(word.length):
            x_shift: int = {"r": i, "l": -i, "d": 0, "u": 0}[word.direction]
            y_shift: int = {"r": 0, "l": 0, "d": i, "u": -i}[word.direction]
            draw.rectangle(
                (
                    (word.start_pos[1] + x_shift) * self.cell_size + self.padding,
                    (word.start_pos[0] + y_shift) * self.cell_size + self.padding,
                    (word.start_pos[1] + x_shift + 1) * self.cell_size + self.padding,
                    (word.start_pos[0] + y_shift + 1) * self.cell_size + self.padding
                ),
                outline=self.cell_stroke_color,
                width=self.cell_stroke_width,
                fill=self.cell_fill
            )
            # Letter
            draw.text(
                (
                    (word.start_pos[1] + x_shift) * self.cell_size + self.text_offset_x,
                    (word.start_pos[0] + y_shift) * self.cell_size + self.text_offset_y
                ),
                word.word[i].upper(),
                font=self.font,
                fill=self.font_color
            )
        self.add_to_drawn(word)
        self.draw_all_numbers()

    def draw_all_numbers(self):
        """Used because otherwise the cell fill would cover the numbers"""
        draw = ImageDraw.Draw(self._grid)
        for direction in self.directions:
            for word in self.words[direction].values():
                draw.text(
                    (
                        (word.start_pos[1] + 0) * self.cell_size + self.cell_size * 0.1 + self.padding,
                        (word.start_pos[0] + 0) * self.cell_size + self.cell_size * 0.05 + self.padding
                    ),
                    str(word.number),
                    font=self.number_font,
                    fill=self.number_color
                )

    def write(self, filename: str) -> None:
        """Write the grid to a file"""
        with open(filename, "wb") as f:
            self._grid.save(f, "PNG")
        f.close()

    def get_bytes_image(self) -> BytesIO:
        img = BytesIO()
        self._grid.save(img, format="PNG")
        img.seek(0)
        return img

    def get_grid_size(self):
        max_row = 0
        max_col = 0
        for direction in self.directions:
            for word in self.words[direction].values():
                if word.start_pos[0] > max_row:
                    max_row = word.start_pos[0]
                if word.end_pos[0] > max_row:
                    max_row = word.end_pos[0]
                if word.start_pos[1] > max_col:
                    max_col = word.start_pos[1]
                if word.end_pos[1] > max_col:
                    max_col = word.end_pos[1]
        return max_row, max_col
