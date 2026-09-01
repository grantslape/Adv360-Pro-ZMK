import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
KEYMAP_DTS = ROOT / "config" / "adv360.keymap"
KEYMAP_JSON = ROOT / "config" / "keymap.json"
MACROS = ROOT / "config" / "macros.dtsi"


def bindings_from_json():
    keymap = json.loads(KEYMAP_JSON.read_text())
    return {
        binding
        for layer in keymap["layers"]
        for binding in layer
    }


class KeymapConsistencyTests(unittest.TestCase):
    def test_editor_keymap_includes_all_mouse_bindings_in_firmware(self):
        firmware = KEYMAP_DTS.read_text()
        mouse_bindings = set(re.findall(r"&(?:mmv|mkp)\s+\w+", firmware))

        self.assertEqual(
            mouse_bindings,
            {
                "&mmv MOVE_UP",
                "&mmv MOVE_LEFT",
                "&mmv MOVE_DOWN",
                "&mmv MOVE_RIGHT",
                "&mkp MB1",
                "&mkp MB2",
            },
        )
        self.assertTrue(mouse_bindings <= bindings_from_json())

    def test_unused_pair_macros_are_not_defined(self):
        pair_macro_names = set(
            re.findall(
                r"^\s*(macro_(?:quotes|dquotes|braces|parens|brackets)):",
                MACROS.read_text(),
                re.MULTILINE,
            )
        )

        self.assertEqual(pair_macro_names, set())


if __name__ == "__main__":
    unittest.main()
