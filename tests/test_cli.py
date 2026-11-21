"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from wordroots.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class ListCommandTest(unittest.TestCase):
    def test_lists_all(self):
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 36)

    def test_lists_prefix_only(self):
        code, out, _ = run_cli(["list", "--kind", "prefix"])
        self.assertEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 12)
        self.assertTrue(all("前缀" in line for line in lines))


class FindCommandTest(unittest.TestCase):
    def test_find_tele(self):
        code, out, _ = run_cli(["find", "tele"])
        self.assertEqual(code, 0)
        self.assertIn("tele-", out)
        self.assertIn("远", out)

    def test_find_with_hyphen(self):
        code, out, _ = run_cli(["find", "--", "-tion"])
        self.assertEqual(code, 0)
        self.assertIn("-tion", out)

    def test_missing_returns_one(self):
        code, _, err = run_cli(["find", "zzz"])
        self.assertEqual(code, 1)
        self.assertIn("未找到", err)


class SearchCommandTest(unittest.TestCase):
    def test_search_example(self):
        code, out, _ = run_cli(["search", "teacher"])
        self.assertEqual(code, 0)
        self.assertIn("teacher", out)
        self.assertIn("[后缀]", out)

    def test_search_meaning(self):
        code, out, _ = run_cli(["search", "生命"])
        self.assertEqual(code, 0)
        self.assertIn("bio-", out)

    def test_no_match_returns_one(self):
        code, _, err = run_cli(["search", "没有这个词"])
        self.assertEqual(code, 1)
        self.assertIn("没有匹配", err)


class CardsCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "cards.html")
            code, out, _ = run_cli(["cards", "--count", "5", "--seed", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                html = handle.read()
            self.assertEqual(html.count('class="card"'), 5)

    def test_stdout(self):
        code, out, _ = run_cli(["cards", "--count", "2", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_kind_filter(self):
        code, out, _ = run_cli(["cards", "--count", "3", "--kind", "suffix", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertIn("后缀", out)

    def test_zero_count_returns_two(self):
        code, _, err = run_cli(["cards", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_directory_created(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "cards.html")
            code, _, _ = run_cli(["cards", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class QuizCommandTest(unittest.TestCase):
    def test_stdout(self):
        code, out, _ = run_cli(["quiz", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="question"'), 3)

    def test_answers_flag(self):
        code, out, _ = run_cli(["quiz", "--count", "3", "--seed", "1", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "quiz.html")
            code, _, _ = run_cli(["quiz", "--count", "4", "--seed", "4", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))

    def test_too_many_returns_two(self):
        code, _, err = run_cli(["quiz", "--count", "40"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_options_returns_two(self):
        code, _, err = run_cli(["quiz", "--count", "2", "--options", "7"])
        self.assertEqual(code, 2)
        self.assertIn("选项", err)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_cards_help(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["cards", "--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
