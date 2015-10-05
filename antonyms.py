# coding: utf8
import zipfile

from scrapy.selector import Selector


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
                print name
                yield root.read(name)


def split_by(text, before, after):
    if before in text:
        text, other = text.split(before)
        text = text.strip()
        other = other.replace(after, '').strip() or None
    else:
        text = text.strip()
        other = None
    return text, other


words = {}

for html in get_htmls():
    sel = Selector(text=html)
    current = None
    
    for p in sel.xpath('//p'):
        strongs = p.xpath('.//strong/text()').extract()
        if strongs:
            word = strongs[0].strip()
            for rep in ('II.', 'I.'):
                word = word.replace(rep, '').strip()

            text = p.extract()
            meta = text.split('</strong>')[1].split(u'•')[0]
            try:
                category, type = split_by(meta, '<em>', '</em>')
            except ValueError:
                category = type = None
            
            if u'•' in text:
                text = text.split(u'•')[1]
            else:
                text = text.split(u')')[1]

            if (word, category) in words:
                current = words[(word, category)]
            else:
                words[(word, category)] = current = Word(word, category, type)
        else:
            text = p.extract()
            if text == u'<p>\xa0</p>':
                continue
        
        for rep in ('<p>', u'•', '</p>', '<em> </em>', '\t&lt;vhova&gt;:'):
            text = text.replace(rep, '')
        
        for word in text.split(','):
            try:
                word, comment = split_by(word, '&lt;', '&gt;')
            except ValueError:
                comment = None
            
            word = word.replace('<em>szleng</em>:', '')
            
            word, type = split_by(word, '<em>', '</em>')
            word = word.strip()
            if (word, current.category) in words:
                antonym = words[(word, current.category)]
            else:
                words[(word, current.category)] = antonym = Word(word, current.category, type, comment)
            
            current.antonyms.append(antonym)
            antonym.antonyms.append(current)


with open('antonyms.txt', 'w') as f:
    for (word, category) in sorted(words.keys()):
        word = words[(word, category)]
        if word.category == '(mn)':
            f.write(u'\n[{}]\n'.format(word.word).encode('utf8'))
            for antonym in word.antonyms:
                f.write(u'{}\n'.format(antonym.word).encode('utf8'))


print len(words)
