# coding: utf8
import re


BULLET = u'\u2022'


def parse_block(text):
    """
    >>> text = u"<p><strong>borissza </strong>(mn) <em>reg</em> "+BULLET+" antialkoholista, absztinens <em>val, </em>bornemissza <em>reg</em></p>"
    >>> parse_block(text)
    ((u'borissza', u'mn', u'reg', ''), [(u'antialkoholista', '', '', ''), (u'absztinens', '', u'val', ''), (u'bornemissza', '', u'reg', '')])

    >>> parse_block("<p>"+BULLET+"	[anyag]: elettelen, szervetlen</p>")
    (('', '', '', ''), [(u'elettelen', '', '', u'anyag'), (u'szervetlen', '', '', '')])

    >>> parse_block("<p><strong>atpartol</strong>&lt;vkihez, vhova&gt; (ige)"+ BULLET +"marad &lt;vhol&gt;, kitart &lt;vki mellett, vmi mellett&gt;, ragaszkodik &lt;vkihez&gt;</p>")
    ((u'atpartol', u'ige', '', u'vkihez, vhova'), [(u'marad', '', '', u'vhol'), (u'kitart', '', '', u'vki mellett, vmi mellett'), (u'ragaszkodik', '', '', u'vkihez')])
    
    >>> parse_block("<p><strong>orias II. </strong>(mn)<strong> "+ BULLET +" </strong>alacsony, kicsi, cseppnyi, paranyi</p>")
    ((u'orias II.', u'mn', '', ''), [(u'alacsony', '', '', ''), (u'kicsi', '', '', ''), (u'cseppnyi', '', '', ''), (u'paranyi', '', '', '')])
    
    >>> parse_block("<p><strong>parductestu "+ BULLET +" </strong>debella, macko <em>biz</em></p>")
    ((u'parductestu', '', '', ''), [(u'debella', '', '', ''), (u'macko', '', u'biz', '')])
    
    >>> parse_block('<p>' + BULLET + "	[vallalkozas, uzlet]: nyereseges, hasznos</p>")
    (('', '', '', ''), [(u'nyereseges', '', '', u'vallalkozas, uzlet'), (u'hasznos', '', '', '')])
    
    >>> parse_block('<p><strong>megfejthetetlen </strong>(mn) ' + BULLET + ' megfejtheto<strong>, </strong>kezenfekvo, nyilvanvalo, trivialis <em>reg</em></p>')
    ((u'megfejthetetlen', u'mn', '', ''), [(u'megfejtheto', '', '', ''), (u'kezenfekvo', '', '', ''), (u'nyilvanvalo', '', '', ''), (u'trivialis', '', u'reg', '')])
    
    >>> parse_block('<p><strong>disszonans </strong>(mn) ' + BULLET + ' <em>szak</em>: harmonikus, osszecsengo</p>')
    ((u'disszonans', u'mn', '', ''), [(u'harmonikus', '', u'szak', ''), (u'osszecsengo', '', '', '')])
    
    >>> parse_block('<p><strong>aradozik </strong>(ige)<em> </em>' + BULLET + '<em> </em>&lt;vkirol, vmirol&gt;: leszol, kritizal, ocsarol</p>')
    ((u'aradozik', u'ige', '', 'vkirol, vmirol'), [(u'leszol', '', '', ''), (u'kritizal', '', '', ''), (u'ocsarol', '', '', '')])
    """

    text = fix_errors(text)

    strong = parse_strong(text)
    antonyms = parse_antonyms(text)

    return strong, antonyms


def fix_errors(text):
    text = text.replace('<em> </em>', '')
    text = text.replace(', </em>', '</em>,')
    text = text.replace('<strong> </strong>', '')
    text = text.replace('<strong>\t</strong>', '')
    text = text.replace('<strong>, </strong>', ',')
    text = text.replace('<strong>&gt;</strong>', '&gt;')
    text = text.replace('<strong>&lt;</strong>', '&lt;')
    text = text.replace('<strong> '+ BULLET +' </strong>', BULLET)
    text = text.replace(BULLET +' </strong>', '</strong>' + BULLET)
    return text


def parse_antonyms(text):
    """
    >>> text = u"<p><strong>borissza </strong>(mn) <em>reg</em> "+BULLET+" antialkoholista, absztinens <em>val</em>, bornemissza <em>reg</em></p>"
    >>> parse_antonyms(text)
    [(u'antialkoholista', '', '', ''), (u'absztinens', '', u'val', ''), (u'bornemissza', '', u'reg', '')]

    >>> parse_antonyms("<p><strong>atpartol</strong>&lt;vkihez, vhova&gt; (ige)"+ BULLET +"marad &lt;vhol&gt;, kitart &lt;vki mellett, vmi mellett&gt;, ragaszkodik &lt;vkihez&gt;</p>")
    [(u'marad', '', '', u'vhol'), (u'kitart', '', '', u'vki mellett, vmi mellett'), (u'ragaszkodik', '', '', u'vkihez')]
   """

    if BULLET in text:
        pattern = (
            "<p>"
                "(.*)" +
                BULLET +
                "(.*)"
            "</p>"
        )
        antonyms_block = get_match(pattern, text, 2)

        return [parse_antonym(a) for a in split_antonyms(antonyms_block)]

    else:
        return []


def split_antonyms(text):
    """
    >>> split_antonyms(' antialkoholista, absztinens <em>val</em>, bornemissza <em>reg</em>')
    ['antialkoholista', 'absztinens <em>val</em>', 'bornemissza <em>reg</em>']

    >>> split_antonyms('marad &lt;vhol&gt;, kitart &lt;vki mellett, vmi mellett&gt;, ragaszkodik &lt;vkihez&gt;')
    ['marad &lt;vhol&gt;', 'kitart &lt;vki mellett, vmi mellett&gt;', 'ragaszkodik &lt;vkihez&gt;']

    >>> split_antonyms("	[vallalkozas, uzlet]: nyereseges, hasznos")
    ['[vallalkozas, uzlet]: nyereseges', 'hasznos']
    """

    antonyms = []

    in_meta = False
    last_i = 0
    for i, ch in enumerate(text):
        if text[i:].startswith(('&lt;', '[', '(')):
            in_meta = True
        elif text[i:].startswith(('&gt;', ']', ')')):
            in_meta = False

        if ch == ',' and not in_meta:
            antonym = text[last_i:i].strip()
            antonyms.append(antonym)
            last_i = i+1

    antonym = text[last_i:].strip()
    antonyms.append(antonym)

    return antonyms


def parse_antonym(text):
    """
    >>> parse_antonym("antialkoholista")
    ('antialkoholista', '', '', '')
    >>> parse_antonym("absztinens <em>val</em>")
    ('absztinens', '', 'val', '')
    >>> parse_antonym("bornemissza <em>reg</em>")
    ('bornemissza', '', 'reg', '')
    >>> parse_antonym("bornemissza (mn)")
    ('bornemissza', 'mn', '', '')

    >>> parse_antonym("	[anyag]: elettelen")
    ('elettelen', '', '', 'anyag')

    >>> parse_antonym("	ragaszkodik &lt;vkihez&gt;")
    ('ragaszkodik', '', '', 'vkihez')
    
    >>> parse_antonym(' <em>szak</em>: harmonikus')
    ('harmonikus', '', 'szak', '')
    """

    word, comment, meta = parse_word_comment_meta(text)
    category = parse_category(meta)
    type = parse_type(meta)

    return (word.strip(), category, type, comment)


def parse_strong(text):
    """
    >>> text = "<p><strong>borissza </strong>(mn) <em>reg</em> "+BULLET+" antialkoholista, absztinens <em>val, </em>bornemissza <em>reg</em></p>"
    >>> parse_strong(text)
    (u'borissza', u'mn', u'reg', '')

    >>> parse_strong('')
    ('', '', '', '')

    >>> parse_strong("<p><strong>atpartol</strong>&lt;vkihez, vhova&gt; (ige)"+ BULLET +"</p>")
    (u'atpartol', u'ige', '', u'vkihez, vhova')
    """

    pattern = (
        "<p>"
            "<strong>"
                "(.*)"
            "</strong>"
            "(.*)" +
            BULLET +
            "(.*)"
        "</p>"
    )
    m = re.match(pattern, text)

    if m:
        word = m.group(1).strip()
        meta = m.group(2).strip()

        category = parse_category(meta)
        type = parse_type(meta)
        comment = parse_comment(meta)

        return word, category, type, comment

    else:
        return ('', '', '', '')


def parse_category(text):
    """
    >>> parse_category('(mn) <em>reg</em>')
    'mn'
    """

    pattern = (
        "(.*)"
        "\("
            "(.*)"
        "\)"
        "(.*)"
    )
    return get_match(pattern, text, 2)


def parse_type(text):
    """
    >>> parse_type('(mn) <em>reg</em>')
    'reg'
    """

    pattern = (
        "(.*)"
        "<em>"
            "(.*)"
        "</em>"
        "(.*)"
    )
    return get_match(pattern, text, 2)


def parse_comment(text):
    """
    >>> parse_comment('&lt;vkihez, vhova&gt; (ige)')
    'vkihez, vhova'
    """

    pattern = (
        "(.*)"
        "&lt;"
            "(.*)"
        "&gt;"
        "(.*)"
    )
    return get_match(pattern, text, 2)


def parse_word_comment_meta(text):
    """
    >>> parse_word_comment_meta("antialkoholista")
    ('antialkoholista', '', '')
    >>> parse_word_comment_meta("absztinens <em>val</em>")
    ('absztinens', '', '<em>val</em>')
    >>> parse_word_comment_meta("bornemissza <em>reg</em>")
    ('bornemissza', '', '<em>reg</em>')
    >>> parse_word_comment_meta("bornemissza (mn)")
    ('bornemissza', '', '(mn)')

    >>> parse_word_comment_meta('	[anyag]: elettelen')
    ('elettelen', 'anyag', '')

    >>> parse_word_comment_meta('')
    ('', '', '')

    >>> parse_word_comment_meta("	ragaszkodik &lt;vkihez&gt;")
    ('ragaszkodik', 'vkihez', '')
    """

    text = text.strip()

    if text:
        word = meta = comment = ''

        if ']:' in text:
            comment, text = text.split(']:')
            comment = comment.replace('[', '').strip()
        elif '&lt;' in text:
            text, comment = text.split('&lt;')[:2]
            comment = comment.replace('&gt;', '').strip()
        elif '</em>:' in text:
            meta, text = text.split(':')

        text = text.strip()

        if text:
            word = text.split()[0]
        if text and not meta:
            meta = text[len(word)+1:].strip()

        return word.strip(), comment, meta

    else:
        return '', '', ''


def get_match(pattern, text, group):
    m = re.match(pattern, text)

    if m:
        return m.group(group)
    else:
        return ''


if __name__ == '__main__':
    import doctest
    if not doctest.testmod().failed:
        print 'doctest passed'
