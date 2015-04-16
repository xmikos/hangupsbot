from reparser import Parser, Token, MatchGroup
from hangups import ChatMessageSegment, SegmentType


# Regex patterns used by token definitions
markdown_re = r'(^|\s)(?P<start>{tag})(?P<text>\S.+?\S)(?P<end>{tag})(\s|$)'
markdown_link_re = r'(?P<start>\[)(?P<text>.+?)\]\((?P<url>.+?)(?P<end>\))'
html_re = r'(?P<start><{tag}>)(?P<text>.+?)(?P<end></{tag}>)'
html_link_re = r'(?P<start><a href=[\'"](?P<url>.+?)[\'"]>)(?P<text>.+?)(?P<end></a>)'
html_newline_re = r'(?P<text><br([\s]*/)?>)'
newline_re = r'(?P<text>\n|\r\n)'

# URL regex pattern by John Gruber (http://gist.github.com/gruber/249502)
auto_link_re = (r'(?i)\b(?P<text>(?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
                r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'
                r'(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')


class Tokens:
    """Groups of tokens to be used by ChatMessageParser"""
    basic = [
        Token(auto_link_re, link_target=MatchGroup('text')),
        Token(newline_re, segment_type=SegmentType.LINE_BREAK)
    ]

    markdown = [
        Token(markdown_re.format(tag=r'\*\*\*'), is_bold=True, is_italic=True),
        Token(markdown_re.format(tag=r'___'), is_bold=True, is_italic=True),
        Token(markdown_re.format(tag=r'\*\*'), is_bold=True),
        Token(markdown_re.format(tag=r'__'), is_bold=True),
        Token(markdown_re.format(tag=r'\*'), is_italic=True),
        Token(markdown_re.format(tag=r'_'), is_italic=True),
        Token(markdown_re.format(tag=r'~~'), is_strikethrough=True),
        Token(markdown_re.format(tag=r'=='), is_underline=True),
        Token(markdown_link_re, link_target=MatchGroup('url')),
    ]

    html = [
        Token(html_re.format(tag=r'b'), is_bold=True),
        Token(html_re.format(tag=r'strong'), is_bold=True),
        Token(html_re.format(tag=r'i'), is_italic=True),
        Token(html_re.format(tag=r'em'), is_italic=True),
        Token(html_re.format(tag=r's'), is_strikethrough=True),
        Token(html_re.format(tag=r'strike'), is_strikethrough=True),
        Token(html_re.format(tag=r'del'), is_strikethrough=True),
        Token(html_re.format(tag=r'u'), is_underline=True),
        Token(html_re.format(tag=r'ins'), is_underline=True),
        Token(html_re.format(tag=r'mark'), is_underline=True),
        Token(html_link_re, link_target=MatchGroup('url')),
        Token(html_newline_re, segment_type=SegmentType.LINE_BREAK)
    ]


class ChatMessageParser(Parser):
    """Chat message parser"""
    def __init__(self, tokens=Tokens.markdown + Tokens.html + Tokens.basic):
        super().__init__(tokens)

    def preprocess(self, text):
        """Preprocess text before parsing"""
        # Replace two consecutive spaces with space and non-breakable space
        # (this is how original Hangouts client does it to preserve multiple spaces)
        return text.replace('  ', ' \xa0')

    def parse(self, text):
        """Parse text to obtain list of ChatMessageSegments"""
        segment_list = super().parse(text)
        return [ChatMessageSegment(segment.text, **segment.params) for segment in segment_list]
