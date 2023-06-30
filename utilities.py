import word_pool as wp
import wordle_sim as ws

def build_word_score(score_string):
    'Build a WordScore from string listing b,g,y for each letter'
    score = ws.WordScore(len(score_string))
    for i,s in enumerate(score_string):
        if s == "b":
            score.set(i, ws.LetterScore.BLACK)
        elif s == "y":
            score.set(i, ws.LetterScore.YELLOW)
        elif s == "g":
            score.set(i, ws.LetterScore.GREEN)
        else:
            raise ValueError("Unknown LetterScore type '"+s+"'")
    return score

def get_possible_words(word, score_string):
    wordlen = len(word)
    pool = wp.SimpleWordPool()
    kb = ws.KnowledgeBank(wordlen)
    kb.gain_knowledge(word, build_word_score(score_string))
    poss = pool.apply_filter(kb.make_filter())
    return poss.word_list()
