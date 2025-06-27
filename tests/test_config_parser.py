import sys
import unittest
from pathlib import Path

# Add project root to the Python path to resolve imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ciscoconfparse2 import CiscoConfParse
from config_parser import ConfigParser, ConfigLine

TESTS_DIR = Path(__file__).parent
PRE_CONFIG_PATH = TESTS_DIR / "pre.conf"
POST_CONFIG_PATH = TESTS_DIR / "post.conf"
DIFF_CONFIG_PATH = TESTS_DIR / "diff.conf"


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        """Set up test objects before each test method."""
        cisco_pre_config = CiscoConfParse(str(PRE_CONFIG_PATH), syntax="ios")
        self.pre_parser = ConfigParser()
        self.pre_parser.build_config(cisco_pre_config)

        cisco_post_config = CiscoConfParse(str(POST_CONFIG_PATH), syntax="ios")
        self.post_parser = ConfigParser()
        self.post_parser.build_config(cisco_post_config)

        cisco_diff_config = CiscoConfParse(str(DIFF_CONFIG_PATH), syntax="ios")
        self.expected_diff_parser = ConfigParser()
        self.expected_diff_parser.build_config(cisco_diff_config)

    def test_build_config(self):
        """Test the build_config method."""
        self.assertEqual(len(self.pre_parser.config), 2)
        self.assertEqual(self.pre_parser.config[0].text, "interface GigabitEthernet1")
        self.assertEqual(len(self.pre_parser.config[0].children), 4)
        self.assertEqual(self.pre_parser.config[0].children[0].text, "description Mgmt")

        # Test nested children
        crypto_map_line = self.pre_parser.config[0].children[3]
        self.assertEqual(crypto_map_line.text, "crypto map MY_CRYPTO_MAP")
        self.assertEqual(len(crypto_map_line.children), 3)

    # def test_flatten_config(self):
    #     """Test the flatten_config method."""
    #     flattened_config = self.pre_parser.flatten_config()
    #     expected_flat_config = [
    #         "interface GigabitEthernet1",
    #         "description Mgmt",
    #         "ip address 10.0.0.1 255.255.255.0",
    #         "no shutdown",
    #         "crypto map MY_CRYPTO_MAP",
    #         "set peer 1.2.3.4",
    #         "set transform-set AES-256-SHA",
    #         "set transform-set AES-256-GCM",
    #         "router ospf 1",
    #         "router-id 1.1.1.1",
    #         "network 10.0.0.0 0.0.0.255 area 0",
    #         "area 0 authentication message-digest",
    #         "key-chain MY_KEY_CHAIN",
    #     ]
    #     self.assertEqual(flattened_config, expected_flat_config)

    def test_diff_configs(self):
        """Test the diff_configs method and save the output to diff.conf."""
        diff_parser = self.pre_parser.diff_configs(self.post_parser)
        flat_diff = diff_parser.flatten_config()

        # Create a new CiscoConfParse object from the diff and save it
        diff_cisco_config = CiscoConfParse(flat_diff)
        diff_cisco_config.save_as(str(DIFF_CONFIG_PATH))

        # Optionally, you can add an assertion to check if the file was created
        self.assertTrue(DIFF_CONFIG_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
