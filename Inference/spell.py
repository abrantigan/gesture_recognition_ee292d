"""
Adapted by Hallie Dunham from:

Spelling Corrector in Python 3; see http://norvig.com/spell-correct.html

Copyright (c) 2007-2016 Peter Norvig
MIT license: www.opensource.org/licenses/mit-license.php
"""

################ Spelling Corrector 

import re
from collections import Counter
import serial
import inference

def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('big.txt').read()))
LETTERS = 'abcdefghijklmnopqrstuvwxyz'
LETTERS_SMALL = 'act'
SIMILARLETTERS = {'a':['h'],'b':['r','k','e','f'],'c':['o','g','q','l'],
                  'd':['r','p','v','x','y'],'e':['f','k','b','r'],'f':['e','k','r','b'],
                  'g':['c','o','q','s'],'h':['a'],'i':['z','j','l','t'],'j':['i','l'],
                  'k':['f','e','r','b'],'l':['z','i','j','c','u','s'],'m':['n','w'],
                  'n':['m','w'],'o':['c','g','q','u'],'p':['d','r'],'q':['s','o','g','c'],
                  'r':['f','k','b','e','d','p'],'s':['q','g','c','l','z'],
                  't':['f','x','z','i'],'u':['v'],'v':['x','y','u','d','w'],
                  'w':['n','m','v'],'x':['y','v','d'],'y':['x','v','d'],'z':['i','l','t','s']}
    

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    word = word.lower()
    print('Infered Word', word)
    print("Candidated Word: ", candidates(word))
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    # len2 = 0
    #len3 = 0
    # for w2 in edits2(word): len2+=1
    #for w3 in commonedits3(word): len3+=1
    # print(len2)
    #print(len3)
    
    known_word = known([word])
    if bool(known_word):
        return known_word
    edit1 = known(edits1(word))
    if bool(edit1):
        return edit1
    else:
        return (known(edits2(word)) or [word])
    
    #return (known([word]) or known(edits1(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one incorrect letter change away from `word`."
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    inserts    = [L + c + R               for L, R in splits for c in LETTERS_SMALL]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in LETTERS_SMALL]
    return (replaces + inserts)

def edits2(word): 
    "All edits that are two letter changes away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
    
def edits3(word):
    "All edits that are three letter changes away from `word`."
    return (e3 for e1 in edits1(word) for e2 in edits1(e1) for e3 in edits1(e2))
    
def commonedits1(word):
    "All edits that are one common letter change away from `word`."
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in SIMILARLETTERS[R[0]]]
    return replaces

def commonedits3(word):
    "All edits that are two letter changes plus one more common change away from `word`."
    return (e3 for e2 in edits2(word) for e3 in commonedits1(e2))

################ Test Code 

def unit_tests():
    assert words('This is a TEST.') == ['this', 'is', 'a', 'test']
    assert Counter(words('This is a test. 123; A TEST this is.')) == (
           Counter({'123': 1, 'a': 2, 'is': 2, 'test': 2, 'this': 2}))
    print(len(WORDS))
    print(sum(WORDS.values()))
    print(WORDS.most_common(10))
    assert 0.07 < P('the') < 0.08
    assert correction('korrectud') == 'corrected'           # replace 2
    assert correction('bycyclf') == 'bicycle'               # replace 2
    assert correction('hellp') == 'hello'                   # replace
    assert correction('word') == 'word'                     # known
    assert correction('womdedfol') == 'wonderful'           # replace 3
    assert P('quintessential') == 0
    assert correction('quintessential') == 'quintessential' # unknown
    return 'unit_tests pass'

def spelltest(tests, verbose=False):
    "Run correction(wrong) on all (right, wrong) pairs; report results."
    import time
    start = time.clock()
    good, unknown = 0, 0
    n = len(tests)
    for right, wrong in tests:
        w = correction(wrong)
        good += (w == right)
        if w != right:
            unknown += (right not in WORDS)
            if verbose:
                print('correction({}) => {} ({}); expected {} ({})'
                      .format(wrong, w, WORDS[w], right, WORDS[right]))
    dt = time.clock() - start
    print('{:.0%} of {} correct ({:.0%} unknown) at {:.0f} words per second '
          .format(good / n, n, unknown / n, n / dt))
    
def Testset(lines):
    "Parse 'right: wrong1 wrong2' lines into [('right', 'wrong1'), ('right', 'wrong2')] pairs."
    return [(right, wrong)
            for (right, wrongs) in (line.split(':') for line in lines)
            for wrong in wrongs.split()]

def read_char(arduinoData):
    while (arduinoData.inWaiting()==0): #Wait here until there is data
        pass #do nothing
    arduinoChar = arduinoData.read() #read the next char from the serial port
    arduinoChar = chr(arduinoChar)
    return arduinoChar 
    
## get next char version for on computer inference demo
def read_char_computer_inference():
    max_prob = 0
    ch = ' '
    probs = inference.inference()
    for letter, prob in probs.items():
        if prob > max_prob:
            ch = letter
            max_prob = prob
    return ch

if __name__ == '__main__':
    ##### Run this before starting data collection!
    #arduinoData = serial.Serial('/dev/tty.usbmodem14501', 9600) #Creating our serial object named arduinoData
    try:
        word = ''
        while True:
            ch = read_char_computer_inference()  
            print(ch)
            #ch = read_char(arduinoData) 
            #ch = input()  ##use this to test with computer letter input (no arduino)
            if(ch in LETTERS_SMALL or ch in LETTERS_SMALL.upper()):  
                word += ch
            else:
                if not word == '':
                    correction(word)
                    word = ''
                # print(ch)
                if ch == '.':
                    print('\n')
                    #arduinoData.close()
                    break
    except KeyboardInterrupt:
        if not word == '':
            print(correction(word))
        print('\n')
        #arduinoData.close()
    
    #print(unit_tests())
