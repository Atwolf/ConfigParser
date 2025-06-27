from __future__ import annotations

from typing import List

from ciscoconfparse2 import CiscoConfParse


class ConfigLine:
    """Represents a line of configuration and its children."""

    def __init__(self, text: str):
        self.text: str = text.strip()
        self.children: List[ConfigLine] = []

    def __repr__(self) -> str:
        return f"ConfigLine(text='{self.text}', children={len(self.children)})"


class ConfigParser:
    """A class to parse and manage hierarchical configurations."""

    def __init__(self):
        self.config: List[ConfigLine] = []

    def build_config(self, cisco_config: CiscoConfParse):
        """
        Build a hierarchical configuration from a CiscoConfParse object.

        This method iterates through the parent lines of the config object,
        initializes them as ConfigLine objects, and recursively processes
        their children using a DFS approach.
        """
        #^[^!\s].+"
        self.config = []
        for line in cisco_config.find_objects(r"^[^!\s].+"):
            new_config_line = ConfigLine(line.text)
            self.config.append(new_config_line)
            self._build_children_recursive(new_config_line, line)

    def _build_children_recursive(self, parent_config_line: ConfigLine, parent_cisco_line):
        for child_cisco_line in parent_cisco_line.children:
            child_config_line = ConfigLine(child_cisco_line.text)
            parent_config_line.children.append(child_config_line)
            self._build_children_recursive(child_config_line, child_cisco_line)

    def diff_configs(self, post_config_parser: ConfigParser) -> ConfigParser:
        """
        Compare two configurations and return the difference.

        This method compares the internal config (pre-config) with an external
        config (post-config) and returns a new ConfigParser object containing
        only the lines present in the post-config but not in the pre-config.
        """
        diffed_parser = ConfigParser()
        diffed_parser.config = self._diff_children(self.config, post_config_parser.config)
        return diffed_parser

    def _diff_children(self, pre_children: List[ConfigLine], post_children: List[ConfigLine]) -> List[ConfigLine]:
        diffed_children: List[ConfigLine] = []
        pre_children_map = {line.text: line for line in pre_children}

        for post_child in post_children:
            if post_child.text not in pre_children_map:
                diffed_children.append(post_child)
            else:
                pre_child = pre_children_map[post_child.text]
                grand_child_diff = self._diff_children(pre_child.children, post_child.children)
                if grand_child_diff:
                    diffed_parent = ConfigLine(post_child.text)
                    diffed_parent.children = grand_child_diff
                    diffed_children.append(diffed_parent)

        return diffed_children

    def flatten_config(self) -> List[str]:
        """
        Flatten the hierarchical configuration into a list of strings.

        This method traverses the configuration tree and returns a flat list
        of configuration lines, suitable for being sent to a device.
        """
        flattened: List[str] = []
        for line in self.config:
            self._flatten_recursive(line, flattened)
        return flattened

    def _flatten_recursive(self, line: ConfigLine, flattened_list: List[str]):
        flattened_list.append(line.text)
        for child in line.children:
            self._flatten_recursive(child, flattened_list)
