from unittest import TestCase
import os
import shutil
from os.path import join

import zero_readme
class Object(object): pass
zero_readme.opts = Object()
zero_readme.opts.rich = True

from zero_readme import main

class ReadmeTest(TestCase):
	def _clean(self):
		if os.path.exists(self.tmp):
			shutil.rmtree(self.tmp)

	def setUp(self):
		self.base = os.path.dirname(__file__)
		self.tmp = join(self.base, "tmp")
		self.original_dir = os.getcwd()
		self._clean()
		os.mkdir(self.tmp)
		os.chdir(self.tmp)
	
	def tearDown(self):
		os.chdir(self.original_dir)
		self._clean()

	def process(self, readme_text, xml, readme_filename):
		xml_path = "feed.xml"
		with open(xml_path, "w") as feed_file:
			feed_file.write("""<?xml version="1.0"?>
<interface xmlns="http://zero-install.sourceforge.net/2004/injector/interface">
%s
<group>
</group>
</interface>
			""" % (xml,))
		with open(readme_filename, "w") as readme_file:
			readme_file.write(readme_text + "\n")
		main(xml_path)
		with open(xml_path) as feed_file:
			contents = feed_file.read()
		contents = contents.replace("\t", "")
		return "\n".join(contents.splitlines()[2:-3])
	
class PlainTextReadmeTest(ReadmeTest):
	def process(self, *a):
		return super(PlainTextReadmeTest, self).process(*a, readme_filename='README')

	def test_should_add_description(self):
		output = self.process("README!", "")
		self.assertEquals(output, """<description>\nREADME!\n</description>""")

	def test_should_replace_description(self):
		output = self.process("README!", "<description>old</description>")
		self.assertEquals(output, """<description>\nREADME!\n</description>""")

	def test_should_escape_xml(self):
		output = self.process("<fancy>", "<description>old</description>")
		self.assertEquals(output, """<description>\n&lt;fancy&gt;\n</description>""")

	def test_should_remove_rich_description(self):
		output = self.process("plain", '<rich-description xmlns="http://gfxmonk.net/dist/0install">old</rich-description>')
		self.assertEquals(output, """<description>\nplain\n</description>""")


class RichTextReadmeTest(ReadmeTest):
	rich_example = """<description>
# README
</description>
<rich-description xmlns="http://gfxmonk.net/dist/0install" xmlns:h="http://www.w3.org/1999/xhtml">
<h:div id="readme">
<h:h1>README</h:h1>
</h:div>
</rich-description>"""

	def process(self, *a):
		return super(RichTextReadmeTest, self).process(*a, readme_filename='README.md')

	def test_should_add_both_descriptions(self):
		output = self.process("# README", "")
		self.assertEquals(output, self.rich_example)

	def test_should_update_both_descriptions(self):
		output = self.process("# README", """<description>OLD</description>
			<rich-description xmlns="http://gfxmonk.net/dist/0install" xmlns:h="http://www.w3.org/1999/xhtml">
				<h:div id="old">
					<h:h1>OLD</h:h1>
				</h:div>
			</rich-description>""")
		print output
		self.assertEquals(output, self.rich_example)
	
	def test_should_fall_back_to_only_plain_description_on_invalid_html(self):
		output = self.process("plain<a>foo", "")
		self.assertEquals(output, """<description>\nplain&lt;a&gt;foo\n</description>""")



