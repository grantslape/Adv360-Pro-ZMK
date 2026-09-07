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

    def test_qwerty_base_and_symbols_layers_preserve_requested_controls(self):
        keymap = json.loads(KEYMAP_JSON.read_text())
        self.assertEqual(
            keymap["layer_names"],
            ["base", "keypad", "fn", "mod", "qwerty", "qwerty_keypad"],
        )
        colemak, qwerty, qwerty_symbols = keymap["layers"][0], *keymap["layers"][4:6]

        self.assertEqual(colemak[6], "&to 4")
        self.assertEqual(qwerty[6], "&to 0")
        self.assertEqual([qwerty[index] for index in (29, 49, 50)], ["&kp A", "&kp C", "&kp V"])
        self.assertEqual(qwerty[48], "&kp X")
        self.assertEqual(qwerty[51], "&hm LG(B) B")
        self.assertEqual(qwerty[38], "&kp RCTRL")
        self.assertEqual(qwerty[54], "&mt RIGHT_GUI N")
        self.assertEqual(qwerty[62], "&caps_word")
        self.assertEqual([qwerty[index] for index in (60, 69)], ["&sl 5", "&sl 5"])

        self.assertEqual(qwerty_symbols[66], "&kp DEL")
        self.assertEqual(qwerty_symbols[35], "&kp LGUI")
        self.assertEqual(qwerty_symbols[37], "&kp LCTRL")
        self.assertEqual(qwerty_symbols[38], "&kp RIGHT_GUI")
        self.assertEqual(keymap["layers"][0][7], "&mo 3")
        self.assertEqual(
            [keymap["layers"][3][index] for index in (20, 21)],
            ["&bootloader", "&bootloader"],
        )
        self.assertIn("qwerty_layer", KEYMAP_DTS.read_text())
        self.assertIn("qwerty_keypad_layer", KEYMAP_DTS.read_text())


if __name__ == "__main__":
    unittest.main()
