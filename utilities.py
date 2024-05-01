import word_pool as wp
import wordle_sim as sim
import pickle

def build_word_score(score_string):
    """Build a WordScore from string listing b,g,y for each letter"""
    score = sim.WordScore(len(score_string))
    for i,s in enumerate(score_string):
        if s == "b":
            score.set(i, sim.LetterScore.BLACK)
        elif s == "y":
            score.set(i, sim.LetterScore.YELLOW)
        elif s == "g":
            score.set(i, sim.LetterScore.GREEN)
        else:
            raise ValueError("Unknown LetterScore type '"+s+"'")
    return score

def get_possible_words(word, score_string):
    wordlen = len(word)
    pool = wp.SimpleWordPool()
    kb = sim.KnowledgeBank(wordlen)
    kb.gain_knowledge(word, build_word_score(score_string))
    poss = pool.apply_filter(kb.make_filter())
    return poss.word_list()

def is_history_all_greens(history):
    """Analyze history returned by robot.Solve() to determine if there are any yellows"""
    for guess,is_correct,score in history:
        for letter_score in score.get_all():
            if letter_score == sim.LetterScore.YELLOW:
                return False
    return True

def run_puzzle(robot: sim.Robot, puzzle: sim.Puzzle, num_attempts):
    """
    Solve `puzzle` using `robot` `num_attempts` times.
    """
    stats = []
    for i in range(num_attempts):
        solved,history = robot.solve(puzzle)
        if not solved:
            raise ValueError("robot failed to solve puzzle!")
        stats.append((len(history), is_history_all_greens(history)))
    return stats

def run_simulation(robot: sim.Robot, pool: wp.WordPool, num_puzzles, num_attempts):
    """
    Draw `num_puzzles` words from `pool` and solve each `num_attempts` times using `robot`.
    Count how many times we achieve "all greens", that is a history with no yellow words.
    """
    data = []
    words = pool.pick_n(num_puzzles)
    for word_count,word in enumerate(words):
        puzzle = sim.Puzzle(word)
        print(f"Sim {word_count+1}/{num_puzzles}: {word}")
        stats = run_puzzle(robot, puzzle, num_attempts)
        data.append((word, stats))

    results = {
        "robot_pool": robot.poolName(),
        "pool": pool.name(),
        "words": words,
        "num_puzzles": num_puzzles,
        "num_attempts": num_attempts,
        "data": data
    }
    return results

def save_results(results, filetag="sim"):
    filename = f"wordlebot_{filetag}.pkl"
    with open(filename, 'wb') as fh:
        pickle.dump(results, fh)
    print(f"Saved results to '{filename}'")

def load_results(filename):
    with open(filename, 'rb') as fh:
        return pickle.load(fh)