import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ram_puzzle import RAMPuzzle
from src.game_data import load_challenge

class TestRAMPuzzle(unittest.TestCase):
    def test_clean_challenge_data_loads(self):
        challenge = load_challenge()
        self.assertEqual(challenge["challenge_id"], "RAM-001")
        self.assertTrue(challenge["hint_text"])

    def test_can_release_inactive_and_allocate_three(self):
        puzzle = RAMPuzzle()
        self.assertEqual(puzzle.release_block(0).status, "ok")
        self.assertEqual(puzzle.release_block(1).status, "ok")
        for block_id in (0, 1, 4):
            self.assertEqual(puzzle.allocate_block(block_id).status, "ok")
        self.assertEqual(puzzle.submit().status, "success")

    def test_cannot_release_active_memory(self):
        puzzle = RAMPuzzle()
        result = puzzle.release_block(2)
        self.assertEqual(result.status, "failure")
        self.assertIn("active program", result.message)

    def test_submit_too_few_fails(self):
        puzzle = RAMPuzzle()
        result = puzzle.submit()
        self.assertEqual(result.status, "failure")
        self.assertEqual(puzzle.status, "FAILURE")

    def test_reset_restores_puzzle(self):
        puzzle = RAMPuzzle()
        puzzle.release_block(2)
        puzzle.reset()
        self.assertEqual(puzzle.status, "PUZZLE")
        self.assertEqual(puzzle.blocks[2].owner, "System Monitor")

if __name__ == "__main__":
    unittest.main()
