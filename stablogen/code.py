from jinja2 import nodes
from jinja2.ext import Extension

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

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
            self.call_method('_code_call', args),
            [], [], body
        ).set_lineno(lineno)

    def _code_call(self, *args, **kw):
        language = args[0]
        filename = args[1]
        code = kw['caller']()

        lexer = get_lexer_by_name(language, stripall=True)
        formatter = HtmlFormatter(linenos=True)
        result = filename + ':' + highlight(code, lexer, formatter)

        return result

from jinja2 import Environment, DictLoader
env = Environment(
loader = DictLoader(
{'index.html': 
'''
{% code "python", "file.py" -%}
#!/usr/bin/env python3
from sys import exit, argv

def do_something(*args, **kw):
    print("This is the program doing something")

if __name__ == "__main__":
    if len(argv) > 4:
        exit("Too many arguments")
    do_something()
{%- endcode %}
'''}),
extensions=[CodeExtension]
)

result = env.get_template('index.html').render()
print("<!DOCTYPE html>\n<html>\n<head>\n<style>")
print(HtmlFormatter().get_style_defs('.highlight'))
print("</style>\n</head>\n<body>")
print(result)
print("</body>\n</html>")
