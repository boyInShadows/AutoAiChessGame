import tempfile
import unittest
from pathlib import Path

from flask import render_template

from chess_log_viewer import app, get_agent_stats, get_emotion_color, parse_game_log


class LogParserTests(unittest.TestCase):
    def test_indented_move_fields_are_preserved(self):
        log = """Date: 2026-10-30 12:00:00
White: DemoWhite
Black: DemoBlack
Mode: COLLABORATIVE
Move 1 - DemoWhite (analytical):
  Move: e2e4
  Reasoning: Synthetic center-control example
  Time taken: 0.1s
  Feeling: focused
  Subgoal: Develop pieces
  Dialogue: Synthetic commentary
  Question: Synthetic question
  Answer: Synthetic answer
  Reflection: Synthetic reflection
  Mode: collaborative
  Board Image: move_001.svg
"""
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "agent_chess_log_fixture.txt"
            filename.write_text(log, encoding="utf-8")
            game = parse_game_log(filename)

        self.assertEqual(game["white_agent"], "DemoWhite")
        self.assertEqual(len(game["moves"]), 1)
        self.assertEqual(game["moves"][0], {
            "move_number": 1,
            "agent_name": "DemoWhite",
            "personality": "analytical",
            "move": "e2e4",
            "reasoning": "Synthetic center-control example",
            "time_taken": "0.1s",
            "feeling": "focused",
            "subgoal": "Develop pieces",
            "dialogue": "Synthetic commentary",
            "question": "Synthetic question",
            "answer": "Synthetic answer",
            "reflection": "Synthetic reflection",
            "game_mode": "collaborative",
            "svg_file": "move_001.svg",
        })

    def test_missing_log_returns_an_error_record(self):
        with tempfile.TemporaryDirectory() as directory:
            result = parse_game_log(Path(directory) / "missing.txt")
        self.assertEqual(result["filename"], "missing.txt")
        self.assertIn("Failed to parse log file", result["error"])

    def test_generated_reflection_and_feedback_are_escaped(self):
        game = {
            "filename": "synthetic.txt", "date": "2026-10-30",
            "white_agent": "DemoWhite", "black_agent": "DemoBlack",
            "moves": [], "game_mode": "COLLABORATIVE", "final_result": None,
        }
        payload = '<script>syntheticUnsafeContent()</script>\nSecond line'
        for field in ("final_reflections", "personality_evolution", "human_feedback"):
            game[field] = payload
        with app.test_request_context():
            html = render_template("game.html", game=game,
                                   stats=get_agent_stats(game),
                                   get_emotion_color=get_emotion_color)
        self.assertFalse('<script>syntheticUnsafeContent()</script>' in html,
                         "Generated content must remain escaped text")
        self.assertEqual(html.count('&lt;script&gt;syntheticUnsafeContent()&lt;/script&gt;'), 3)
