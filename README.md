# WordleSim

WordleSim provides utilities for simulating a Wordle game. There are
three main classes that support the simulation:

1. WordPool
2. Puzzle
3. Robot

as well as these helper classes `WordScore` and `LetterScore`.


`WordPool` contains a list of possible 5-letter words. It provides
the method `pick`, which returns a random word from the pool.

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

```
import wordle_sim as w

word_pool = w.WordPool()
puzzle = w.Puzzle(sys.argv[1])
robot = w.Robot(word_pool)
robot.solve(puzzle, verbose=True)
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

The robot is not "smart". It doesn't imploy any strategy to find the
answer quickly. It doesn't look for common letter patterns, track
history from puzzle to puzzle, or choose words to eliminate as many
letters as possible. All it does is filter the word list based on the
knowledge it's gained, and choose a word from those possibilites.

Also note that since it doesn't remember knowledge from puzzle to
puzzle, it can be used to solve the same puzzle many times, each time
as if it's the first time it's seen it.