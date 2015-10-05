# coding: utf8
from parse import parse_block
from scrapy.selector import Selector
import zipfile


EPUB_PATH = 'TAMOP-4_2_5-09_Ellentetes_jelentesu_szavak_adatbazisa.epub'


class Word(object):
    def __init__(self, word, category, type, comment=None):
        self.word = word
        self.category = category
        self.type = type
        self.comment = comment
        self.antonyms = []


def get_htmls():
    root = zipfile.ZipFile(EPUB_PATH, "r")

    for name in sorted(root.namelist()):
        if name.startswith('OEBPS/text/content'):
            if name >= 'OEBPS/text/content0006.xhtml':
                print 'processing', name
                yield root.read(name)


words = {}

for html in get_htmls():
    sel = Selector(text=html)
    current = None

    for p in sel.xpath('//p'):
        text = p.extract()
        (word, category, type), antonyms = parse_block(text)

        if word:
            if (word, category) in words:
                current = words[(word, category)]
            else:
                words[(word, category)] = current = Word(word, category, type)

        for (word, category, type, comment) in antonyms:
            if (word, current.category) in words:
                antonym = words[(word, current.category)]
            else:
                words[(word, current.category)] = antonym = Word(word, current.category, type, comment)

            current.antonyms.append(antonym)
            antonym.antonyms.append(current)


with open('antonyms.txt', 'w') as f:
    for (word, category) in sorted(words.keys()):
        word = words[(word, category)]
        if word.category == 'mn':
            f.write(u'\n[{}]\n'.format(word.word).encode('utf8'))
            for antonym in word.antonyms:
                f.write(u'{}\n'.format(antonym.word).encode('utf8'))


print len(words)
