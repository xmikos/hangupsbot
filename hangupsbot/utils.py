import unicodedata

import hangups


def text_to_segments(text):
    """Create list of message segments from text"""
    # Replace two consecutive spaces with space and non-breakable space,
    # then split text to lines
    lines = text.replace('  ', ' \xa0').splitlines()
    if not lines:
        return []

    # Generate line segments
    segments = []
    for line in lines[:-1]:
        if line:
            segments.append(hangups.ChatMessageSegment(line))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    if lines[-1]:
        segments.append(hangups.ChatMessageSegment(lines[-1]))

    return segments


def word_in_text(word, text):
    """Return True if word is in text"""
    # Transliterate unicode characters to ASCII and make everything lowercase
    word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode().lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()

    # Replace delimiters in text with whitespace
    for delim in '.,:;!?':
        text = text.replace(delim, ' ')

    return True if word in text.split() else False
