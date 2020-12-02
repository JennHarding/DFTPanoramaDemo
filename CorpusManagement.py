# from music21 import converter
import music21 as m21

# demo_corpus = {'Harbison, Four Songs of Solitude, Movement 1' : 'Scores/HarbisonFourSongsofSolitude1.xml', 
#                'Messiaen, Theme and Variations, Theme' : 'Scores/MessiaenT&V_Theme.xml', 
#                'Mozart, K. 157, Movement 1, Exposition' : 'Scores/MozartK157_expo.xml', 
#                'Mozart, K. 465 (Dissonance), Movement 1, Exposition' : 'Scores/MozartK465_expo.xml'}

demo_corpus = {'Harbison, Four Songs of Solitude, Movement 1' : 'HarbisonFourSongsofSolitude1.xml', 
               'Messiaen, Theme and Variations, Theme' : 'MessiaenT&V_Theme.xml', 
               'Mozart, K. 157, Movement 1, Exposition' : 'MozartK157_expo.xml', 
               'Mozart, K. 465 (Dissonance), Movement 1, Exposition' : 'MozartK465_expo.xml'}

corpus_list = [x for x in demo_corpus.keys()]

def parse_score(score_name, measure_nums=None):
    working_score = m21.converter.parse(demo_corpus[score_name])
    if measure_nums == (0, 0):
        return working_score
    else:
        return working_score.measures(measure_nums[0], measure_nums[1])


