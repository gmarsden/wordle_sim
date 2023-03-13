from enum import Enum
import random

### Helper classes
class PositionFact(Enum):
    NO_INFO = 0
    HERE = 1
    NOT_HERE = 2
    
class LetterScore(Enum):
    BLACK = 0
    YELLOW = 1
    GREEN = 2
    UNKNOWN = -1

class WordScore:
    def __init__(self, size):
        self._score = [LetterScore.UNKNOWN] * size
    def __repr__(self):
        return "".join([x.name[0] for x in self._score])
    def _check_range(self, i):
        if i<0 or i>=len(self._score):
            raise Exception("Bad index for Score.get")
    def size(self):
        return len(self._score)
    def get(self, i):
        self._check_range(i)
        return self._score[i]
    def get_all(self):
        return self._score
    def set(self, i, value):
        self._check_range(i)
        self._score[i] = value
    
### UTILITIES
# currently ignores frequency data
def read_word_data(file):
    data = []
    with open(file) as f:
        for line in f.readlines():
            words = line.split()
            data.append(words[0])
    return data

## WordPool class provides random word from dictionary and iteration over full list
# check that:
#   - all words have the same length
#   - all letters are in [a-z]
## TO-DO:
##  - validate word list
##  - add biased selection to common words
class WordPool:
    _source_file = "words_freq.txt"
    def __init__(self, empty=False):
        # weird interface for now... fix up later
        if empty:
            self._set_word_list([])
        else:
            self._set_word_list(read_word_data(self._source_file))

    def _set_word_list(self, list):
        self._word_list = list
        if len(list) > 0:
            self._word_len = len(list[0])
        
    def __iter__(self):
        self._iter = iter(self._word_list)
        return self
    
    def __next__(self):
        return next(self._iter)
    
    def size(self):
        return len(self._word_list)
    
    def word_length(self):
        return self._word_len

    def pick(self):
        "Pick random word from list"
        return random.choice(self._word_list)
    
    def apply_filter(self, filter_func):
        """Return new pool that has been filtered by filter_func.

        Function should take a word a return True if the word is accepted."""
        new_pool = WordPool(empty=True)
        new_pool._word_list = [x for x in self._word_list if filter_func(x)]
        return new_pool

## A mini helper-class for counting letter occurrences
class LetterCount:
    def __init__(self, word=""):
        self._count = {}
        for l in word:
            self.add(l)
    def add(self, letter):
        self._count[letter] = self._count.get(letter, 0) + 1
    def get(self, letter):
        return self._count.get(letter, 0)
    
## Puzzle class lets player check a word
# a score is a N-length list where each element indicated correctness of letter:
#  - 0: letter is not found in puzzle (black)
#  - 1: letter is found in puzzle but not here (yellow)
#  - 2: letter is correct (green)

class Puzzle:
    def __init__(self, solution):
        self._solution = solution
        self._len = len(solution)
        self._letter_count = LetterCount(solution)

    def _score_guess(self, word):
        # we already know 'word' is the right length
        score = WordScore(self._len)
        this_letter_count = LetterCount()
        # first find letters in correct position
        # we need to do this to correctly score double-letters
        for i in range(self._len):
            if word[i] == self._solution[i]:
                score.set(i, LetterScore.GREEN)
                this_letter_count.add(word[i])
        # then fill in missed letters
        for i in range(self._len):
            # skip over letters we've already scored
            if score.get(i) != LetterScore.UNKNOWN:
                continue
            letter = word[i]
            this_letter_count.add(letter)
            if this_letter_count.get(letter) > self._letter_count.get(letter):
                score.set(i, LetterScore.BLACK)
            else:
                score.set(i, LetterScore.YELLOW)
        return score
            
    def guess(self, word):
        "Returns two values, whether or not the guess is correct and a word score"
        len(word) == self._len or error("guess is wrong length")
        result = (self._solution == word)
        return (result, self._score_guess(word))

## Knowledge about a letter
# contains facts about letter:
#   - count: minimum number of this letter in solution [int]
#   - limited: whether or not we know how many times this letter is in the solution [bool]
#   - positions: info about possible positions [list PositionFact]

class Knowledge:
    def __init__(self, word_len):
        self._len = word_len
        self._count = 0
        self._limited = False
        self._positions = [PositionFact.NO_INFO] * word_len

    def __repr__(self):
        str = "Knowledge(count: {}, limited: {}, positions: {})"
        return str.format(self._count,
                          self._limited,
                          [x.name for x in self._positions])

    def add_fact(self, position, score):
        "Add a new fact to Knowledge. 'score' is LetterScore as reported by Puzzle"
        assert position >=0 and position < self._len
        if score == LetterScore.BLACK:
            self._limited = True
            self._positions[position] = PositionFact.NOT_HERE
        elif score == LetterScore.YELLOW:
            self._count += 1
            self._positions[position] = PositionFact.NOT_HERE
        elif score == LetterScore.GREEN:
            self._count += 1
            self._positions[position] = PositionFact.HERE
        else:
            raise Exception("Unknown LetterScore")

    def integrate_new_knowledge(self, new_knowledge):
        assert isinstance(new_knowledge, self.__class__)
        assert self._len == new_knowledge._len
        self._count = max(self._count, new_knowledge._count)
        self._limited = self._limited or new_knowledge._limited
        for i in range(self._len):
            if self._positions[i] == PositionFact.NO_INFO:
                self._positions[i] = new_knowledge._positions[i]
            else:
                # should already known, new knowledge should be unknown or should agree
                assert new_knowledge._positions[i] == PositionFact.NO_INFO or \
                    new_knowledge._positions[i] == self._positions[i]

    def apply_knowledge(self, letter, word):
        "Test knowledge on 'letter' in 'word'"
        assert len(word) == self._len
        result = True
        letter_count = word.count(letter)
        if self._limited and letter_count != self._count:
            result = False
        elif letter_count < self._count:
            result = False
        else:
            for l,p in zip(word, self._positions):
                if p == PositionFact.HERE and l != letter:
                    result = False
                    break;
                elif p == PositionFact.NOT_HERE and l == letter:
                    result = False
                    break;
        return result
                
## KnowledgeBank class tracks all information player has acquired
## KnowledgeBank is dictionary of Knowledge about letters
class KnowledgeBank:
    def __init__(self, length):
        self._bank = {}
        self._len = length

    def _build_new_knowledge(self, word, score):
        new_knowledge_bank = {}
        for index, (letter,fact) in enumerate(zip(word, score.get_all())):
            new_knowledge = new_knowledge_bank.get(letter, Knowledge(self._len))
            new_knowledge.add_fact(index, fact)
            new_knowledge_bank[letter] = new_knowledge
        return new_knowledge_bank

    def _integrate_new_knowledge_bank(self, new_knowledge_bank):
        for letter,new_knowledge in new_knowledge_bank.items():
            if letter in self._bank:
                self._bank[letter].integrate_new_knowledge(new_knowledge)
            else:
                self._bank[letter] = new_knowledge

    def gain_knowledge(self, word, score):
        # word and score should have same length as existing knowledge
        assert len(word) == score.size()
        assert score.size() == self._len
        new_knowledge_bank = self._build_new_knowledge(word, score)
        self._integrate_new_knowledge_bank(new_knowledge_bank)

    def _filter(self, word):
        return all([k.apply_knowledge(l, word) for l,k in self._bank.items()])
            
    def make_filter(self):
        "Return a filter for to apply Knowledge"
        return self._filter
        
## Robot (player) tries to solve a puzzle
# it will make guesses and gain knowledge
# has access to a pool of words
class Robot:
    def __init__(self, pool):
        self._pool = pool

    def _make_guess(self, puzzle, pool, bank):
        "Make a guess drawn from pool and gain knowledge"
        guess = pool.pick()
        result, score = puzzle.guess(guess)
        bank.gain_knowledge(guess, score)
        return (result, score)
        
    def solve(self, puzzle, verbose=False):
        knowledge_bank = KnowledgeBank(self._pool.word_length())
        word_pool = self._pool
        history = []
        while True:
            guess = word_pool.pick()
            if verbose:
                print("{} words in pool".format(word_pool.size()))
                print("Guess {}: '{}'".format(len(history)+1, guess))
            result, score = puzzle.guess(guess)
            if verbose: print("Result: {}, Score: {}".format(result, score))
            history.append((guess, result, score))
            if result:
                break
            if len(history) >= 100:
                raise Exception("Made 100 guesses. Aborting.")
            knowledge_bank.gain_knowledge(guess, score)
            word_pool = word_pool.apply_filter(knowledge_bank.make_filter())
        return (result, history)
