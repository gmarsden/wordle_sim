import random

### UTILITIES
# currently ignores frequency data
def read_word_data(file):
    data = []
    with open(file) as f:
        for line in f.readlines():
            words = line.split()
            data.append(words[0])
    return data

## WordPool base class
# Instantiating this directly will not be useful, since the pool is empty
## TO-DO:
##  - validate word list
##  - all letters are in [a-z]
##  - add biased selection to common words
class WordPool:
    _source_file = "words_freq.txt"
    def __init__(self, empty=False):
        self._set_word_list([])

    def _set_word_list(self, list):
        self._word_list = list
        if len(list) > 0:
            self._word_len = len(list[0])

    def _get_word(self, item):
        "Accessor to extra word from element of word_list"
        # default is that item is the word itself
        return item

    def __iter__(self):
        self._iter = iter(self._word_list)
        return self
    
    def __next__(self):
        return self._get_word(next(self._iter))
    
    def size(self):
        return len(self._word_list)
    
    def word_length(self):
        return self._word_len

    def pick(self):
        "Pick random word from list"
        return self._get_word(random.choice(self._word_list))
    
    def apply_filter(self, filter_func):
        """Return new pool that has been filtered by filter_func.

        'filter_func' should take a word and return True if the word is accepted."""
        new_pool = WordPool(empty=True)
        new_pool._word_list = [x for x in self._word_list if filter_func(self._get_word(x))]
        return new_pool

class SimpleWordPool(WordPool):
    _source_file = "words_freq.txt"
    def __init__(self, empty=False):
        # weird interface for now... fix up later
        if empty:
            self._set_word_list([])
        else:
            self._set_word_list(read_word_data(self._source_file))
