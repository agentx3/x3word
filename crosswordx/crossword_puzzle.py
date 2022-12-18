from typing import List, Dict, Any
from crosswordx.crossword_grid import CrosswordGrid, Word
import hashlib


def parse_word_list(word_list: Dict[str, List[List[str]]]) -> List[Word]:
    words = []
    direction_dict = {0: "r", 1: "d", 2: "l", 3: "u"}
    for word in word_list["words"]:
        try:
            words.append(Word(word[0], word[1], direction_dict[int(word[4])], (int(word[2]), int(word[3]))))
        except IndexError:
            raise IndexError("Invalid word list")
        except ValueError:
            raise ValueError("Invalid word list")
    return words


class CrosswordPuzzle:
    def __init__(self, word_list: Dict[str, List[List[str]]], metadata: Dict[str, Any] = None):
        self._word_list = parse_word_list(word_list)
        self.initialize_word_numbers()
        self._words: Dict[str, Dict[int, Word]] = self.initialize_word_dict()
        self._grid = CrosswordGrid(self.words)
        self._hash = hashlib.sha256(str(self._word_list).encode()).hexdigest()
        self.total_words = len(self._word_list)
        self.metadata: dict | None = word_list.get("metadata") or metadata
        self.guesses: Dict[str, Dict[int, Word]] = {"r": {}, "d": {}, "l": {}, "u": {}}

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def directions(self) -> List[str]:
        return self._grid.directions

    @property
    def words(self) -> Dict[str, Dict[int, Word]]:
        return self._words

    @property
    def grid(self) -> CrosswordGrid:
        return self._grid

    @property
    def correct_cnt(self) -> int:
        # TODO: There's probably a better way to do this than iterating through the entire list every time
        cnt = 0
        for direction in self.directions:
            cnt += len(self.correct_answers[direction])
        return cnt

    @property
    def correct_answers(self) -> Dict[str, Dict[int, Word]]:
        return self._grid.correct_answers

    def clear_correct(self, word: Word):
        self._grid.clear_correct(word)

    def get_word(self, word_num: int, direction: str) -> Word | None:
        if word_num < 0 or word_num > len(self._word_list):
            raise IndexError("Word index out of range")
        return self._words.get(direction, {}).get(word_num, None)

    def initialize_word_numbers(self):
        """Iterate through words and find ones that have the same start, and assign them the same word number"""
        word_list = self._word_list
        for word in word_list:
            if word.number is None:
                word.number = word_list.index(word) + 1
                for other_word in word_list[word.number - 1:]:
                    if other_word.number is None and other_word.start_pos == word.start_pos:
                        other_word.number = word.number
        return word_list

    def try_guess(self, word_num: int, direction: str, word: str) -> bool:
        # Validation should happen when submitting answers
        try:
            if self.words[direction][word_num].word.lower() == word.lower():
                return True
        except Exception as e:
            print(e, flush=True)
            return False
        return False

    def add_to_correct(self, word: Word):
        self._grid.add_to_correct(word)

    def initialize_word_dict(self):
        """Initialize a dictionary of words with the correct number of words"""
        word_dict = {"r": {}, "d": {}, "l": {}, "u": {}}
        for word in self._word_list:
            word_dict[word.direction].update({word.number: word})
        return word_dict
