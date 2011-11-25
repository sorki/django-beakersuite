import re
import pygments
from django import template
from pygments import lexers, filters, formatters


from pygments.lexer import RegexLexer, bygroups, using
from pygments.token import *

register = template.Library()
regex = re.compile(r'<code(.*?)>(.*?)</code>', re.DOTALL)

Logs = Token.Logs
LOGGER_TYPES = {
    Logs.Log     : 'lol',
    Logs.Warning : 'low',
    Logs.Pass    : 'lop',
    Logs.Fail    : 'lof',

    Logs.Host    : 'loh',
    Logs.Process : 'lor',
}

STANDARD_TYPES.update(LOGGER_TYPES)

# TODO: prefix
class RegexFilter(filters.Filter):
    def __init__(self, **options):
        self.regex = re.compile(options.get('regex', r''))
        self.new_type = options.get('new_type', Text)
        # TODO: prefix
        self.match_only = filters.get_list_opt(options, 'match_only', [])
        # TODO: prefix
        filters.Filter.__init__(self, **options)

    def filter(self, lexer, stream):
        for ttype, value in stream:
            if self.match_only and ttype not in self.match_only:
                yield ttype, value
            else:
                # TODO: prefix
                for sttype, svalue in pygments.filters._replace_special(ttype, value,
                    self.regex, self.new_type):
                    yield sttype, svalue


class BeakerLexer(RegexLexer):
    name = 'Beakerlib'
    aliases = ['beaker', 'beakerlib']
    filenames = ['*.bkr']

    tokens = {
        'root': [
            (r'[:]*\n', Text),
            (r':: \[\s*', Text, 'msg'),
            (r'(PURPOSE)( of )(.*)$', bygroups(Keyword, Text, String)),
            (r'(Description:)(.*)$', bygroups(Keyword, String)),
            (r'(Author:)(.*)$', bygroups(Keyword, String)),
            (r'.*\n', Text),
            ],
        'msg': [
            (r'LOG', Logs.Log),
            (r'INFO', Logs.Log),
            (r'WARN', Logs.Warning),
            (r'PASS', Logs.Pass),
            (r'FAIL', Logs.Fail),
            (r'\d\d:\d\d:\d\d', Logs.Log),
            (r'\s*\] :: ', Text, 'desc'),
            ],
        'desc': [
            (r' JOURNAL (XML|TXT)[^\n]*', Text),
            (r'[^:\n]+', Name.Attribute),
            (r'.*\n', Logs.Pass, '#pop:2'),
            ]
    }

class FailLexer(RegexLexer):
    name = 'Fail'

    tokens = {
        'root': [
            (r'(:: \[\s*)(.*\n)', bygroups(Text,
                using(BeakerLexer, state='msg'))),
            (r'(\d*)(:)', bygroups(Number, Punctuation)),
            (r'.*\n', Text),
            ]
    }

class DmesgLexer(RegexLexer):
    name = 'Dmesg'
    aliases = ['dmesg', 'kernel']

    tokens = {
        'root' : [
            (r'\[\s*', Text),
            (r'\d+', Number),
            (r'(.)(\d+)', bygroups(Punctuation, Number)),
            (r'\]\s*', Text),
            (r'.*\n', Logs.Log),
        ]
    }

class MessagesLexer(RegexLexer):
    name = 'messages'

    tokens = {
        'root' : [
            (r'([^\s]+ \d+ )(\d+:\d+:\d+ )', bygroups(Literal, Literal.Date)),
            (r'([^\s]+ )([^\s]+:)', bygroups(Logs.Host, Logs.Process)),
            (r'.*\n', Logs.Log),
        ]
    }


custom = {
    'beaker': BeakerLexer,
    'messages': MessagesLexer,
    'fail': FailLexer,
    'dmesg': DmesgLexer,
}

@register.filter
def pygmentize(value):
    last_end = 0
    to_return = ''
    found = 0
    for match_obj in regex.finditer(value):
        code_class = match_obj.group(1)
        code_string = match_obj.group(2)

        if code_class.find('class') != -1:
            language = re.split(r'"|\'', code_class)[1]
            if language in custom:
                lexer = custom[language]()
            else:
                lexer = lexers.get_lexer_by_name(language)
        else:
            try:
                lexer = lexers.guess_lexer(str(code_string))
            except ValueError:
                lexer = lexers.PythonLexer()

        if type(lexer) in [BeakerLexer, FailLexer]:
            lexer.add_filter(RegexFilter(regex=r'\((Expected[^\)]*)\)',
                new_type=Logs.Log))

        lexer.add_filter(RegexFilter(regex=r'\b(FAILED)\b',
            new_type=Logs.Fail))


        pygmented_string = pygments.highlight(code_string, lexer,
            formatters.HtmlFormatter(linenos=True, cssclass="source"))
        to_return = to_return + value[last_end:match_obj.start(0)] + pygmented_string
        last_end = match_obj.end(2)
        found = found + 1
    to_return = to_return + value[last_end:]
    return to_return
