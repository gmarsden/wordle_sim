# WordleSim

WordleSim provides utilities for simulating a Wordle game. It provides
two modules, `word_pool` and `wordle_sim`.

## word_pool

The `word_pool` module provides a base class `WordPool` and several
derived classes that implement the WordPool interface.

WordPool classes provide these methods:

| Method | Arguments | Description |
| ------ | --------- | ----------- |
| size | none | Return number of words in the pool |
| pick | none | Return a word from the pool |
| word_length | none | Return length of words in pool |
|apply_filter | function | Return a new WordPool based on `this` where the word list has been filtered by `function`. The function should take a word as input and return `True` or `False`, depending on whether or not the word should be included |

The class also supports iteration for listing all of the words in the
pool:

```
pool = SimpleWordPool()
for word in pool:
    print(word)
```

The available word pools are:

| Class | Description |
| ----- | ----------- |
| SimpleWordPool | A large list of 5-letter words. Words are chosen uniformly. |
| ScrambledWordPool | Same as SimpleWordPool but order of letters is scrambled. |
| SyntheticWordPool | A pool that is the same size as SimpleWordPool, but made of of random character strings. |
| WeightedWordPool | Like SimpleWordPool, but `pick()` weights towards common words |
| CommonWordPool | Like SimpleWordPool, but only the 2000 most common words |

## wordle_sim

The wordle_sim module provides two classes `Puzzle` and `Robot`, as
well as these helper classes `WordScore` and `LetterScore`.


`Puzzle` provides an instance of a Wordle puzzle. It is initialized
with a solution and provides the method `guess`, which takes a word
and returns the tuple `(result, score)`: `result` is boolean stating
whether the guessed word is correct, and `score` is an instance of the
helper class `WordScore`.

`Robot` is a player that can play Puzzles. It is initialize with a
WordPool and provides the method `solve`, which takes a Puzzle as
argument. `solve` uses WordPool.pick() to provide possible answers,
which it uses in calls to Puzzle.guess(). It then uses the returned
WordScore to build a knowledge base, which it then uses to filter down
the WordPool. `solve` returns the tuple `(result, history)`, where
`result` is the solution to the puzzle and `history` is a list of
tuples of the format `(guess, result, score)`.

`WordScore` is used to report the result of a guess. It provides a
printable view of the score, as well as providing the member functions
`get` (which takes an index `i`) and `get_all` (no arguments); the
former returns the LetterScore for the `i`th letter and the latter
returns an array of all LetterScores.

`LetterScore` provides the values `BLACK`, `YELLOW`, and `GREEN`,
which represent whether the guess is absent from the puzzle, present
but in a different location, and present and in the correct position,
respectively.

## Example

Here is a simple example using the simple word pool:

```
import word_pool as wp
import wordle_sim as sim

pool = wp.SimpleWordPool()
solution = pool.pick()
puzzle = sim.Puzzle(solution)
robot = sim.Robot(pool)
robot.solve(puzzle)
```

Here is a sample output:

```
(True, [('jutes', False, BBBGB),
        ('armed', False, BYBGB),
        ('inker', False, BYBGG),
	('never', False, GGBGG),
	('newer', True, GGGGG)])
```

## How the robot works

The robot is not "smart". It doesn't employ any strategy to find the
answer quickly. It doesn't look for common letter patterns, track
history from puzzle to puzzle, or choose words to eliminate as many
letters as possible. All it does is filter the word list based on the
knowledge it's gained, and choose a word from those possibilities.

Also note that since it doesn't remember knowledge from puzzle to
puzzle, it can be used to solve the same puzzle many times, each time
as if it's the first time it's seen it.

## All Greens

The purpose of writing this library was to investigate the observation that 
"all greens" -- that is, solutions where no yellows were ever found -- seem 
to be more common than would be expected. The "utilities" library includes a 
function `run_simulation` that uses the robot to run a number of simulations,
counting the number of times "all greens" occurred. One can then run 
simulations with a variety of word pools and determine whether the choice of 
pool has an effect on the frequency of occurrence. For example:

```commandline
import utilities as util

pool = wp.SimpleWordPool()
robot = sim.Robot(pool)
results = util.run_simulation(robot, pool, 10, 100)
```

This picks 10 words from the pool and has the robot solve each 100 times. 
The return value `results` will be a list of `(word, count)` tuples 10 items 
long indicating the word used and the number of times the "all greens" 
condition was found for each word.