from jinja2 import nodes, lexer
from jinja2.ext import Extension
import re


class LayoutExtension(Extension):
    tags = set(["use_layout"])

    def __init__(self, environment):
        super(LayoutExtension, self).__init__(environment)
        environment.extend(default_layout="layout.html",
                           default_layout_block="content",
                           disable_layout=False)

    def parse(self, parser):
        lineno = parser.stream.__next__().lineno
        template = None
        block_name = self.environment.default_layout_block
        if not parser.stream.current.test("block_end"):
            template = parser.parse_expression()
            if parser.stream.skip_if("comma"):
                block_name = parser.parse_expression().name

        if not template:
            template = nodes.Const(self.environment.default_layout)

        parser.stream.skip_if('comma')
        parser.stream.expect('block_end')
        # parse remaining tokens until EOF
        body = parser.subparse()
        # the parser expects a TOKEN_END_BLOCK after an
        # extension. fake this token and set the token
        # stream iterator with a single EOF token
        parser.stream.current = lexer.Token(1, lexer.TOKEN_BLOCK_END, "%}")
        parser.stream._iter = iter([lexer.Token(1, lexer.TOKEN_EOF, "")])

        blocks = []
        wrap_block = True
        wrap_nodes = []
        default_block = None
        # extracts blocks node out of the body
        for node in body:
            if isinstance(node, nodes.Block):
                if node.name == block_name:
                    wrap_block = False
                    default_block = node
                blocks.append(node)
            else:
                wrap_nodes.append(node)
        if wrap_block and wrap_nodes:
            # wrap nodes which were not wrapped in a block node
            default_block = nodes.Block(block_name, wrap_nodes, False, lineno=lineno)
            blocks.append(default_block)

        if self.environment.disable_layout:
            return default_block

        return [nodes.Extends(template, lineno=lineno)] + blocks
