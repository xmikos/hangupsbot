import re

from hangups import ChatMessageSegment, SegmentType


class ParserSegment:
    """Segment of parsed text"""
    def __init__(self, text, match=None, **params):
        self.text = text
        self.params = params
        if match:
            self.update_params(match)

    def update_params(self, match):
        """Update dict of params from regex match"""
        for k, v in self.params.items():
            if isinstance(v, ParserMatchGroup):
                try:
                    self.params[k] = match.group(v.group)
                except IndexError:
                    self.params[k] = ''


class ParserToken:
    """Definition of token which should be parsed from text"""
    def __init__(self, pattern, text_group='text', start_group='start', end_group='end', **params):
        self.regex = re.compile(pattern, re.DOTALL)
        self.params = params
        self.text_group = text_group
        self.start_group = start_group
        self.end_group = end_group


class ParserMatchGroup:
    """Name of regex group which should be replaced by its value when token is parsed"""
    def __init__(self, group):
        self.group = group


class ChatMessageParser:
    """Chat message parser"""
    def __init__(self, tokens):
        self.tokens = tokens

    def preprocess(self, text):
        """Preprocess text before parsing"""
        # Replace two consecutive spaces with space and non-breakable space
        # (this is how original Hangouts client does it to preserve multiple spaces)
        return text.replace('  ', ' \xa0')

    def find_tokens(self, token, segment):
        """Find tokens in ParserSegment"""
        segment_list = []
        last_pos = 0

        for match in token.regex.finditer(segment.text):
            # Append previous (non-matched) text
            try:
                start_pos = match.start(token.start_group)
            except IndexError:
                start_pos = match.start(token.text_group)

            if start_pos != last_pos:
                segment_list.append(ParserSegment(segment.text[last_pos:start_pos], **segment.params))

            # Append matched text
            params = segment.params.copy()
            params.update(token.params)
            segment_list.append(ParserSegment(match.group(token.text_group), match=match, **params))

            # Move last position pointer after matched text
            try:
                last_pos = match.end(token.end_group)
            except IndexError:
                last_pos = match.end(token.text_group)

        # Append anything that's left
        if last_pos != len(segment.text):
            segment_list.append(ParserSegment(segment.text[last_pos:], **segment.params))

        return segment_list

    def parse(self, text):
        """Parse text to obtain list of ChatMessageSegments"""
        segment_list = [ParserSegment(self.preprocess(text))]
        for token in self.tokens:
            new_segment_list = []
            for segment in segment_list:
                new_segment_list.extend(self.find_tokens(token, segment))
            segment_list = new_segment_list
        return [ChatMessageSegment(segment.text, **segment.params) for segment in segment_list]


# Regex patterns used by token definitions
inline_re = r'(^|\s)(?P<start>{tag})(?P<text>\S.+?\S)(?P<end>{tag})(\s|$)'
inline_link_re = r'(?P<start>\[)(?P<text>.+?)\]\((?P<url>.+?)(?P<end>\))'
newline_re = r'(?P<text>\n|\r\n)'

# URL regex pattern by John Gruber (http://gist.github.com/gruber/249502)
auto_link_re = (r'(?i)\b(?P<text>(?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
                r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'
                r'(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')

# Tokens for parsing simplified Markdown-like language
tokens = [
    ParserToken(inline_re.format(tag=r'\*\*\*'), is_bold=True, is_italic=True),
    ParserToken(inline_re.format(tag=r'___'), is_bold=True, is_italic=True),
    ParserToken(inline_re.format(tag=r'\*\*'), is_bold=True),
    ParserToken(inline_re.format(tag=r'__'), is_bold=True),
    ParserToken(inline_re.format(tag=r'\*'), is_italic=True),
    ParserToken(inline_re.format(tag=r'_'), is_italic=True),
    ParserToken(inline_re.format(tag=r'~~'), is_strikethrough=True),
    ParserToken(inline_re.format(tag=r'=='), is_underline=True),
    ParserToken(inline_re.format(tag=r'=='), is_underline=True),
    ParserToken(inline_link_re, link_target=ParserMatchGroup('url')),
    ParserToken(auto_link_re, link_target=ParserMatchGroup('text')),
    ParserToken(newline_re, segment_type=SegmentType.LINE_BREAK)
]
