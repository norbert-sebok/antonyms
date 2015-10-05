# coding: utf8
import re


BULLET = u'\u2022'


def parse_block(text):
    """
    >>> text = u"<p><strong>borissza </strong>(mn) <em>reg</em> "+BULLET+" antialkoholista, absztinens <em>val, </em>bornemissza <em>reg</em></p>"
    >>> parse_block(text)
    ((u'borissza', u'mn', u'reg'), [(u'antialkoholista', '', '', ''), (u'absztinens', '', u'val', ''), (u'bornemissza', '', u'reg', '')])

    >>> parse_block("<p>"+BULLET+"	[anyag]: elettelen, szervetlen</p>")
    (('', '', ''), [(u'elettelen', '', '', u'anyag'), (u'szervetlen', '', '', '')])

    >>> parse_block("<p><strong>atpartol</strong>&lt;vkihez, vhova&gt; (ige)"+ BULLET +"marad &lt;vhol&gt;, kitart &lt;vki mellett, vmi mellett&gt;, ragaszkodik &lt;vkihez&gt;</p>")
    ((u'atpartol', u'ige', u'vkihez, vhova'), [(u'marad', '', '', 'vhol'), (u'kitart', '', '', 'vki mellett, vmi mellett'), (u'ragaszkodik', '', 'vkihez', '')])
    """

    text = fix_errors(text)

    strong = parse_strong(text)
    antonyms = parse_antonyms(text)

    return strong, antonyms


def fix_errors(text):
    text = text.replace('<em> </em>', '')
    text = text.replace(', </em>', '</em>,')
    text = text.replace('<strong> </strong>', '')
    text = text.replace('<strong>&gt;</strong>', '&gt;')
    text = text.replace('<strong>&lt;</strong>', '&lt;')
    return text


def parse_antonyms(text):
    """
    >>> text = u"<p><strong>borissza </strong>(mn) <em>reg</em> "+BULLET+" antialkoholista, absztinens <em>val</em>, bornemissza <em>reg</em></p>"
    >>> parse_antonyms(text)
    [(u'antialkoholista', '', '', ''), (u'absztinens', '', u'val', ''), (u'bornemissza', '', u'reg', '')]
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

        return [
            parse_antonym(antonym)
            for antonym in antonyms_block.split(',')
        ]

    else:
        return []


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
    """

    word, comment, meta = parse_word_comment_meta(text)
    category = parse_category(meta)
    type = parse_type(meta)

    return (word.strip(), category, type, comment)


def parse_strong(text):
    """
    >>> text = "<p><strong>borissza </strong>(mn) <em>reg</em> "+BULLET+" antialkoholista, absztinens <em>val, </em>bornemissza <em>reg</em></p>"
    >>> parse_strong(text)
    (u'borissza', u'mn', u'reg')

    >>> parse_strong('')
    ('', '', '')
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

        return word, category, type

    else:
        return ('', '', '')


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

        text = text.strip()

        if text:
            word = text.split()[0]
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
