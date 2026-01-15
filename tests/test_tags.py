import unittest
import glob
import json
import os
import xml.etree.ElementTree as ET

class TestTags(unittest.TestCase):
    def setUp(self):
        # Assuming tests are run from project root, but let's be safe and find data relative to this file
        # This file is in tests/, so data is in ../data
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.reactions_dir = os.path.join(self.base_dir, 'data', 'reactions')
        self.json_path = os.path.join(self.reactions_dir, 'tag_descriptions.json')

        # Load defined tags
        with open(self.json_path, 'r') as f:
            self.tag_data = json.load(f)
        self.defined_tags = set(self.tag_data.keys())

        # Find used tags in CML files
        self.used_tags = set()
        cml_files = glob.glob(os.path.join(self.reactions_dir, '*.cml'))
        
        for cml_file in cml_files:
            try:
                tree = ET.parse(cml_file)
                root = tree.getroot()
                for tag in root.findall('.//tag'):
                    if tag.text:
                        self.used_tags.add(tag.text.strip())
            except ET.ParseError as e:
                print(f"Error parsing {cml_file}: {e}")

    def test_missing_definitions(self):
        """Verify that all tags used in CML files are defined in tag_descriptions.json"""
        missing_definitions = self.used_tags - self.defined_tags
        error_msg = f"The following tags are used in CML files but not defined in tag_descriptions.json: {missing_definitions}"
        self.assertFalse(missing_definitions, error_msg)

    def test_unused_definitions(self):
        """Verify that all tags defined in tag_descriptions.json are used in CML files"""
        unused_definitions = self.defined_tags - self.used_tags
        error_msg = f"The following tags are defined in tag_descriptions.json but not used in any CML file: {unused_definitions}"
        self.assertFalse(unused_definitions, error_msg)

if __name__ == '__main__':
    unittest.main()
