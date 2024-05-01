import random
import string
import copy
from itertools import accumulate
from numpy import searchsorted

source_file = "words_freq.txt"

### UTILITIES
# currently ignores frequency data
def read_word_data(file, get_freqs=False):
    data = []
    freqs = []
    with open(file) as f:
        for line in f.readlines():
            words = line.split()
            data.append(words[0])
            if get_freqs:
                freqs.append(float(words[1]))
    if get_freqs:
        return data, freqs
    else:
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

    def _set_word_list(self, wlist):
        self._word_list = wlist
        if len(wlist) > 0:
            self._word_len = len(self._get_word(wlist[0]))

    def _copy(self):
        local = self.__class__()
        local._set_word_list(copy.deepcopy(self._word_list))
        return local

    def _get_word(self, item):
        """Accessor to extra word from element of word_list"""
        # default is that item is the word itself
        return item

    def __iter__(self):
        self._iter = iter(self._word_list)
        return self
    
    def __next__(self):
        return self._get_word(next(self._iter))

    def name(self):
        return self.__class__.__name__

    def size(self):
        return len(self._word_list)
    
    def word_length(self):
        return self._word_len

    def word_list(self):
        return [self._get_word(item) for item in self._word_list]

    def pick(self):
        """Pick random word from list"""
        if len(self._word_list) == 0:
            raise ValueError("No words in pool!")
        return self._get_word(random.choice(self._word_list))

    def pick_n(self, n):
        """Pick `n` random words from list"""
        if len(self._word_list) < n:
            raise ValueError("Only {} words in pool, can't pick {}".format(len(self._word_list), n))
        return self._get_word(random.sample(self._word_list, n))

    def apply_filter(self, filter_func):
        """Return new pool that has been filtered by filter_func.

        'filter_func' should take a word and return True if the word is accepted."""
        new_pool = self.__class__(empty=True)
        new_pool._set_word_list([x for x in self._word_list if filter_func(self._get_word(x))])
        return new_pool

class SimpleWordPool(WordPool):
    def __init__(self, empty=False):
        if empty:
            WordPool.__init__(self)
        else:
            self._set_word_list(read_word_data(source_file))

class SyntheticWordPool(WordPool):
    """Create pool that's the same size as SimpleWordPool, but all words are random combinations of letters."""
    letters = string.ascii_lowercase
    def __init__(self, empty=False):
        if empty:
            WordPool.__init__(self)
        else:
            dict_words = read_word_data(source_file)
            self._word_len = len(dict_words[0])
            self._word_list = []
            for i in range(len(dict_words)):
                random_word = ''.join([random.choice(self.letters) for i in range(self._word_len)])
                self._word_list.append(random_word)

class ScrambledWordPool(SimpleWordPool):
    """Word pool based on Simple word pool, but with letters in each word scrambled"""
    def __init__(self, empty=False):
        SimpleWordPool.__init__(self, empty)
        for i in range(len(self._word_list)):
            chars = list(self._word_list[i])
            random.shuffle(chars)
            self._word_list[i] = ''.join(chars)

class WeightedWordPool(WordPool):
    """Create a pool of words where the 'pick' method is weighted towards common words."""
    def __init__(self, empty=False):
        if empty:
            WordPool.__init__(self)
        else:
            # word list is list of (word, freq) data
            words_and_freqs = read_word_data(source_file, get_freqs=True)
            self._set_word_list(list(zip(*words_and_freqs)))

    def _set_word_list(self, words_and_freqs):
        # call default method, then calculate cdf
        WordPool._set_word_list(self, words_and_freqs)
        if len(words_and_freqs) > 0:
            self._word_cdf = list(accumulate([x[1] for x in words_and_freqs]))
            self._cdf_max = self._word_cdf[-1]

    def _copy(self):
        local = WordPool._copy(self)
        print(local.__class__)
        local._word_cdf = copy.deepcopy(self._word_cdf)
        local._cdf_max = self._cdf_max
        return local

    def _get_word(self, item):
        # return the first element of the stored tuple
        return item[0]

    def pick(self):
        if len(self._word_list) == 0:
            raise ValueError("No words in pool!")
        rand = random.random() * self._cdf_max
        index = searchsorted(self._word_cdf, rand)
        return self._get_word(self._word_list[index])

    def pick_n(self, n):
        # algorithm:
        #   1) create local pool, initialized with self._word_list
        #   2) use `pick` to draw word
        #   3) set local pool to local._word_list with word removed
        #   4) repeat from (2) until we have the right number of words
        local_pool = self._copy()
        words = []
        while True:
            new_word = local_pool.pick()
            words.append(new_word)
            if len(words) == n:
                break
            local_pool._set_word_list(list(filter(lambda x: x[0] != new_word, local_pool._word_list)))
        return words

class CommonWordPool(SimpleWordPool):
    """Create a simple word pool with only common words."""
    num_words = 2000
    def __init__(self, empty=False):
        if empty:
            WordPool.__init__(self)
        else:
            full_sorted_list = sorted(read_word_data(source_file),
                                      key=lambda x: x[1],
                                      reverse=True)
            self._set_word_list(full_sorted_list[:self.num_words])
