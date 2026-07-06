"""Unit tests for the --detail preset resolver (pure, no ffmpeg/network)."""
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from watch import DETAIL_PRESETS, UNCAPPED_MAX_FRAMES, resolve_detail_settings  # noqa: E402


def _resolve(detail, max_frames=None, no_scene=False, no_hook=False):
    return resolve_detail_settings(detail, max_frames, no_scene, no_hook)


class TestDetailModes(unittest.TestCase):

    def test_balanced_is_current_default(self):
        # REGRESSION GUARD: balanced == pre-flag default (max 80, scene on, hook on).
        r = _resolve("balanced")
        self.assertEqual(r["max_frames"], 80)
        self.assertFalse(r["no_scene_change"])
        self.assertFalse(r["no_hook_microscope"])
        self.assertTrue(r["extract_frames"])

    def test_transcript_no_frames(self):
        r = _resolve("transcript")
        self.assertFalse(r["extract_frames"])
        self.assertTrue(r["no_scene_change"])
        self.assertTrue(r["no_hook_microscope"])

    def test_efficient_uniform_capped_50(self):
        r = _resolve("efficient")
        self.assertTrue(r["extract_frames"])
        self.assertEqual(r["max_frames"], 50)
        self.assertTrue(r["no_scene_change"])   # uniform, not scene-change
        self.assertTrue(r["no_hook_microscope"])

    def test_token_burner_uncapped_scene_on(self):
        r = _resolve("token-burner")
        self.assertEqual(r["max_frames"], UNCAPPED_MAX_FRAMES)
        self.assertGreater(r["max_frames"], 100)
        self.assertFalse(r["no_scene_change"])
        self.assertFalse(r["no_hook_microscope"])

    def test_explicit_max_frames_beats_preset(self):
        self.assertEqual(_resolve("efficient", max_frames=25)["max_frames"], 25)
        self.assertEqual(_resolve("balanced", max_frames=30)["max_frames"], 30)

    def test_explicit_max_frames_capped_100_except_token_burner(self):
        # Every mode but token-burner keeps the 100 hard cap on explicit values.
        self.assertEqual(_resolve("balanced", max_frames=500)["max_frames"], 100)
        # token-burner honors the explicit number uncapped.
        self.assertEqual(_resolve("token-burner", max_frames=500)["max_frames"], 500)

    def test_explicit_no_scene_change_beats_preset(self):
        # balanced wants scene-change on; explicit flag forces it off.
        self.assertTrue(_resolve("balanced", no_scene=True)["no_scene_change"])

    def test_explicit_no_hook_beats_preset(self):
        # token-burner wants hook on; explicit flag forces it off.
        self.assertTrue(_resolve("token-burner", no_hook=True)["no_hook_microscope"])

    def test_all_modes_registered(self):
        self.assertEqual(
            set(DETAIL_PRESETS),
            {"transcript", "efficient", "balanced", "token-burner"},
        )


if __name__ == "__main__":
    unittest.main()
