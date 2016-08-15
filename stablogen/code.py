from jinja2 import nodes
from jinja2.ext import Extension

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
        lineno = next(parser.stream).lineno

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

        return nodes.CallBlock(self.call_method('_code_call', args), [], [], body).set_lineno(lineno)

    def _code_call(self, *args, **kw):
        language = args[0]
        filename = args[1]
        code = kw['caller']()

        result = '<pre>' + code + '</pre>'

        return result

from jinja2 import Environment, DictLoader
env = Environment(
loader = DictLoader(
{'index.html': 
'''This is the first line
{% code "python", "file.py" -%}
This is the code!
{%- endcode %}
'''}),
extensions=[CodeExtension]
)

import pdb, traceback, sys

try:
    result = env.get_template('index.html').render()
    print('RESULT')
    print(result)
except:
    type, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
