from jinja2 import nodes
from jinja2.ext import Extension

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

class CodeStyle(Style):
    default_style = ""
    styles = {
        Comment:                'italic #7CAFC2',
        Keyword:                'bold #DC9656',
        Name:                   '#BA8BAF',
        Name.Function:          '#F7CA88',
        Name.Class:             '#A16946',
        String:                 '#AB4642'
    }

formatter = HtmlFormatter(
    style = CodeStyle,
    nobackground = True,
)

def code_highlight(language, filename, code):
    lexer = get_lexer_by_name(language, stripall=True)
    return (
        '<div class="codebox">{0}'
        '<button class="code-copy-btn">'
        '<i class="fa fa-clipboard" aria-hidden="true"></i>'
        '</button><hr><div class="code-copy">{1}</div></div>'
    ).format(
        filename,
        highlight(code, lexer, formatter),
        code,
    )

def output_code_style(path):
    path.write_text(formatter.get_style_defs('.highlight'))


def parse_expr_if(parser):
    if parser.stream.skip_if('comma'):
        return parser.parse_expression()
    else:
        return nodes.Const(None)

class CodeExtension(Extension):
    tags = set(['code'])

    def __init__(self, environment):
        super().__init__(environment)
        environment.extend(
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno # I honestly dont really know
                                            # what this does
        if parser.stream.current.test('string'): # Is there a string argument?
            args = [
                parser.parse_expression(), # Get First Argument (No Comma)
                parse_expr_if(parser), # Get Second Argument (Comma in front)
            ]
        else: # Else skip to 'block_end' and set Arguments to None
            while True:
                if not parser.stream.current.test('block_end'):
                    parser.stream.skip()
                else:
                    break
            args = [
                nodes.Const(None),
                nodes.Const(None),
            ]

        body = parser.parse_statements(['name:endcode'], drop_needle=True)

        return nodes.CallBlock(
            self.call_method('_code_highlight_call', args),
            [], [], body
        ).set_lineno(lineno)

    def _code_highlight_call(self, *args, **kw):
        return code_highlight(args[0], args[1], kw['caller']())

