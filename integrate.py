
class Word:
    def __init__(self, word, antonyms):
        self.word = word
        self.antonyms = antonyms
        self.type = '?'


def read_words(path):
    with open(path) as f:
        return set(f.read().split())


def read_antonyms():
    with open('words/antonyms.txt') as f:
        text = f.read()

    for block in text.split('['):
        if block.strip():
            word, antonyms = block.split(']')
            yield word, antonyms.split()


positive = read_words('words/positive.txt')
negative = read_words('words/negative.txt')

words = {}
for word, antonyms in read_antonyms():
    words[word] = Word(word, antonyms)

for word in words.values():
    word.antonyms = [
        words[w] if w in words else Word(w, [])
        for w in word.antonyms
    ]


for word in words.values():
    if word.word in positive:
        word.type = '+'
    elif word.word in negative:
        word.type = '-'


for word in words.values():
    if word.type in '-+':
        print
        print '[{} {}]'.format(word.type, word.word)

        opposite = ('+' if word.type == '-' else '-')
        for a in word.antonyms:
            print a.type, a.word
