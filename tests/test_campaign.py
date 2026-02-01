import unittest
import os
import sys

# Assume running from project root
sys.path.insert(0, os.path.abspath("."))
from libcml import Cml

class TestCampaign(unittest.TestCase):
    def test_all_levels_specified(self):
        campaign_path = os.path.join("data", "levels", "campaign.cml")
        levels_dir = os.path.join("data", "levels")
        
        if not os.path.exists(campaign_path):
             self.fail(f"Campaign file not found at {campaign_path}")

        # Load campaign using libcml
        campaign = Cml.Campaign()
        try:
            campaign.parse(campaign_path)
        except Exception as e:
            self.fail(f"Failed to parse campaign.cml with libcml: {e}")
            
        specified_levels = set()
        for page in campaign.pages:
            for biome in page:
                # biome is (name, icon, level_paths)
                # level_paths are absolute or relative paths as returned by parsing
                for lvl_path in biome[2]:
                    # The parser joins "data/levels" + fname
                    # But we want to match against file list in levels_dir
                    fname = os.path.basename(lvl_path)
                    specified_levels.add(fname)
            
        # List actual files
        actual_files = set()
        ignore_files = {"campaign.cml", "testlevel.cml"} 
        
        if os.path.exists(levels_dir):
            for f in os.listdir(levels_dir):
                if f.endswith(".cml") and f not in ignore_files:
                    actual_files.add(f)
        else:
            self.fail(f"Levels directory not found at {levels_dir}")
        
        # Check for matching sets
        missing_in_campaign = actual_files - specified_levels
        missing_on_disk = specified_levels - actual_files
        
        error_msg = ""
        if missing_in_campaign:
            error_msg += f"\nThe following levels are in {levels_dir} but not specified in {campaign_path}:\n" + "\n".join(sorted(missing_in_campaign))
            
        if missing_on_disk:
            error_msg += f"\nThe following levels are specified in {campaign_path} but do not exist in {levels_dir}:\n" + "\n".join(sorted(missing_on_disk))
            
        if error_msg:
            self.fail(error_msg)

if __name__ == '__main__':
    unittest.main()

