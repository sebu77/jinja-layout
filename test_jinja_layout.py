import unittest
from jinja2 import Environment, FileSystemLoader
from jinja_layout import LayoutExtension
import os


templates_path = os.path.join(os.path.dirname(__file__), "test-templates")


class JinjaLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.env = Environment(loader=FileSystemLoader(templates_path))
        self.env.add_extension(LayoutExtension)
        self.env.default_layout = "base.html"

    def test_blocks(self):
        html = self.env.get_template("blocks.html").render()
        self.assertIn("title=foobar", html)
        self.assertIn("content=hello world", html)

    def test_mixed(self):
        html = self.env.get_template("mixed.html").render()
        self.assertIn("title=foobar", html)
        self.assertIn("content=\n\nhello world", html)

    def test_noblock(self):
        html = self.env.get_template("noblock.html").render()
        self.assertIn("data=\nhello world", html)

    def test_disable_layout(self):
        self.env.disable_layout = True
        html = self.env.get_template("blocks.html").render()
        self.assertEquals("hello world", html)

if __name__ == '__main__':
    unittest.main()