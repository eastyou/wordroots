"""渲染层测试。"""

import unittest

from wordroots.model import Affix, QuizQuestion, build_cards, build_quiz, find
from wordroots.render import render_cards, render_quiz


class CardRenderTest(unittest.TestCase):
    def test_skeleton(self):
        html = render_cards(build_cards(3, seed=1))
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('<meta charset="utf-8">', html)
        self.assertIn('<html lang="zh-CN">', html)

    def test_card_count(self):
        html = render_cards(build_cards(6, seed=2))
        self.assertEqual(html.count('class="card"'), 6)

    def test_card_content(self):
        entry = find("tele")[0]
        html = render_cards([entry])
        self.assertIn("tele-", html)
        self.assertIn("前缀", html)
        self.assertIn("远", html)
        self.assertIn("telephone", html)

    def test_title_escaped(self):
        html = render_cards(build_cards(1, seed=1), title="<词根> & 卡片")
        self.assertIn("&lt;词根&gt; &amp; 卡片", html)

    def test_empty(self):
        html = render_cards([])
        self.assertIn("暂无卡片", html)

    def test_a4_style(self):
        html = render_cards(build_cards(1, seed=1))
        self.assertIn("size: A4", html)
        self.assertIn("@media print", html)

    def test_count_note(self):
        html = render_cards(build_cards(4, seed=3))
        self.assertIn("共 4 张卡片", html)


class QuizRenderTest(unittest.TestCase):
    def test_question_count(self):
        html = render_quiz(build_quiz(5, seed=1))
        self.assertEqual(html.count('class="question"'), 5)

    def test_option_letters(self):
        html = render_quiz(build_quiz(1, seed=1))
        self.assertIn("A. ", html)
        self.assertIn("B. ", html)
        self.assertIn("C. ", html)
        self.assertIn("D. ", html)

    def test_title_escaped(self):
        html = render_quiz(build_quiz(1, seed=1), title="<测验>")
        self.assertIn("&lt;测验&gt;", html)

    def test_answers_hidden(self):
        html = render_quiz(build_quiz(3, seed=1))
        self.assertNotIn("参考答案", html)

    def test_answers_included(self):
        questions = build_quiz(3, seed=1)
        html = render_quiz(questions, include_answers=True)
        self.assertIn("参考答案", html)
        self.assertIn(questions[0].answer, html)
        self.assertIn("1. " + questions[0].answer_letter, html)

    def test_empty(self):
        html = render_quiz([])
        self.assertIn("暂无题目", html)

    def test_print_style(self):
        html = render_quiz(build_quiz(1, seed=1))
        self.assertIn("size: A4", html)

    def test_custom_question(self):
        question = QuizQuestion(
            Affix("un", "prefix", "不、相反", ("unhappy", "unable")),
            ("不、相反", "远", "写", "看"),
            0,
        )
        html = render_quiz([question])
        self.assertIn("un-", html)
        self.assertIn("不、相反", html)


if __name__ == "__main__":
    unittest.main()
