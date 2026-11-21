"""模型层测试。"""

import unittest

from wordroots.model import (
    Affix,
    QuizQuestion,
    WordRootError,
    build_cards,
    build_quiz,
    check_kind,
    check_quiz,
    filter_by_kind,
    find,
    format_entry,
    load_entries,
    normalize_term,
    search,
)


class DatasetTest(unittest.TestCase):
    def test_size(self):
        self.assertEqual(len(load_entries()), 36)

    def test_kinds_are_valid(self):
        for entry in load_entries():
            self.assertIn(entry.kind, ("prefix", "root", "suffix"))

    def test_each_kind_has_twelve(self):
        for kind in ("prefix", "root", "suffix"):
            self.assertEqual(len(filter_by_kind(kind)), 12)

    def test_text_is_lowercase(self):
        for entry in load_entries():
            self.assertEqual(entry.text, entry.text.lower())
            self.assertNotIn("-", entry.text)

    def test_meaning_not_empty(self):
        for entry in load_entries():
            self.assertTrue(entry.meaning.strip())

    def test_at_least_three_examples(self):
        for entry in load_entries():
            self.assertGreaterEqual(len(entry.examples), 3)

    def test_examples_contain_affix(self):
        for entry in load_entries():
            for example in entry.examples:
                self.assertIn(entry.text, example, "%s 不含 %s" % (example, entry.text))

    def test_unique_text_and_kind(self):
        keys = [(entry.text, entry.kind) for entry in load_entries()]
        self.assertEqual(len(keys), len(set(keys)))

    def test_display_prefix(self):
        entry = find("tele")[0]
        self.assertEqual(entry.display, "tele-")

    def test_display_suffix(self):
        entry = find("tion")[0]
        self.assertEqual(entry.display, "-tion")

    def test_display_root(self):
        entry = find("port")[0]
        self.assertEqual(entry.display, "port")

    def test_kind_label(self):
        self.assertEqual(find("un")[0].kind_label, "前缀")


class NormalizeTest(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(normalize_term("PRE"), "pre")

    def test_strips_spaces_and_hyphens(self):
        self.assertEqual(normalize_term("  -tion-  "), "tion")

    def test_empty_rejected(self):
        with self.assertRaises(WordRootError):
            normalize_term(" - ")

    def test_non_string_rejected(self):
        with self.assertRaises(WordRootError):
            normalize_term(12)


class FindTest(unittest.TestCase):
    def test_exact(self):
        matches = find("tele")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].meaning, "远")

    def test_with_display_hyphen(self):
        self.assertEqual(find("un-")[0].meaning, "不、相反")

    def test_uppercase(self):
        self.assertEqual(len(find("MIS")), 1)

    def test_missing(self):
        self.assertEqual(find("zzz"), [])

    def test_custom_entries(self):
        custom = [Affix("xyz", "root", "测试", ("xyzzy",))]
        self.assertEqual(find("xyz", custom)[0].meaning, "测试")

    def test_invalid_kind(self):
        with self.assertRaises(WordRootError):
            check_kind("infix")


class FilterAndSearchTest(unittest.TestCase):
    def test_filter_prefix(self):
        entries = filter_by_kind("prefix")
        self.assertTrue(all(entry.kind == "prefix" for entry in entries))

    def test_filter_invalid(self):
        with self.assertRaises(WordRootError):
            filter_by_kind("infix")

    def test_search_by_term(self):
        results = search("tele")
        self.assertTrue(any(entry.text == "tele" for entry in results))

    def test_search_by_meaning(self):
        results = search("生命")
        self.assertTrue(any(entry.text == "bio" for entry in results))

    def test_search_by_example(self):
        results = search("teacher")
        self.assertTrue(any(entry.text == "er" for entry in results))

    def test_search_by_kind_label(self):
        self.assertEqual(len(search("后缀")), 12)

    def test_search_missing(self):
        self.assertEqual(search("不存在的关键词"), [])

    def test_search_empty_rejected(self):
        with self.assertRaises(WordRootError):
            search("  ")

    def test_search_non_string_rejected(self):
        with self.assertRaises(WordRootError):
            search(None)

    def test_format_entry(self):
        text = format_entry(find("tele")[0])
        self.assertIn("tele-", text)
        self.assertIn("前缀", text)
        self.assertIn("telephone", text)


class CardTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_cards(5, seed=1)), 5)

    def test_unique(self):
        cards = build_cards(12, seed=2)
        self.assertEqual(len(set(cards)), 12)

    def test_deterministic(self):
        first = [entry.text for entry in build_cards(6, seed=7)]
        second = [entry.text for entry in build_cards(6, seed=7)]
        self.assertEqual(first, second)

    def test_different_seed(self):
        first = [entry.text for entry in build_cards(6, seed=7)]
        second = [entry.text for entry in build_cards(6, seed=8)]
        self.assertNotEqual(first, second)

    def test_kind_filter(self):
        cards = build_cards(5, kinds=["root"], seed=3)
        self.assertTrue(all(entry.kind == "root" for entry in cards))

    def test_invalid_kind(self):
        with self.assertRaises(WordRootError):
            build_cards(2, kinds=["infix"])

    def test_too_many(self):
        with self.assertRaises(WordRootError):
            build_cards(13, kinds=["prefix"])

    def test_zero(self):
        with self.assertRaises(WordRootError):
            build_cards(0)

    def test_custom_entries(self):
        custom = [Affix("xyz", "root", "测试", ("xyzzy",))]
        self.assertEqual(len(build_cards(1, entries=custom)), 1)


class QuizTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_quiz(5, seed=1)), 5)

    def test_option_count(self):
        for question in build_quiz(5, seed=1):
            self.assertEqual(len(question.options), 4)

    def test_correct_option_present(self):
        for question in build_quiz(5, seed=1):
            self.assertIn(question.entry.meaning, question.options)

    def test_answer_index_points_to_correct(self):
        for question in build_quiz(5, seed=1):
            self.assertEqual(question.options[question.answer_index], question.entry.meaning)

    def test_options_unique(self):
        for question in build_quiz(8, seed=4):
            self.assertEqual(len(set(question.options)), len(question.options))

    def test_answer_letter(self):
        question = build_quiz(1, seed=4)[0]
        self.assertEqual(question.answer_letter, "ABCD"[question.answer_index])

    def test_distractors_share_kind(self):
        meanings = {
            kind: {entry.meaning for entry in filter_by_kind(kind)}
            for kind in ("prefix", "root", "suffix")
        }
        for question in build_quiz(6, seed=9):
            allowed = meanings[question.entry.kind]
            for option in question.options:
                self.assertIn(option, allowed)

    def test_check_quiz_true(self):
        question = build_quiz(1, seed=5)[0]
        self.assertTrue(check_quiz(question, question.answer_index))

    def test_check_quiz_false(self):
        question = build_quiz(1, seed=5)[0]
        wrong = (question.answer_index + 1) % len(question.options)
        self.assertFalse(check_quiz(question, wrong))

    def test_check_quiz_out_of_range(self):
        question = build_quiz(1, seed=5)[0]
        self.assertFalse(check_quiz(question, 99))
        self.assertFalse(check_quiz(question, -1))

    def test_check_quiz_non_integer(self):
        question = build_quiz(1, seed=5)[0]
        self.assertFalse(check_quiz(question, "0"))

    def test_deterministic(self):
        first = [(q.entry.text, q.options, q.answer_index) for q in build_quiz(5, seed=11)]
        second = [(q.entry.text, q.options, q.answer_index) for q in build_quiz(5, seed=11)]
        self.assertEqual(first, second)

    def test_custom_option_count(self):
        for question in build_quiz(3, seed=2, options=6):
            self.assertEqual(len(question.options), 6)

    def test_invalid_option_count(self):
        with self.assertRaises(WordRootError):
            build_quiz(2, options=1)
        with self.assertRaises(WordRootError):
            build_quiz(2, options=7)

    def test_too_many_questions(self):
        with self.assertRaises(WordRootError):
            build_quiz(37)

    def test_quiz_question_answer_property(self):
        question = QuizQuestion(
            Affix("un", "prefix", "不", ("unhappy",)),
            ("不", "远", "写", "看"),
            0,
        )
        self.assertEqual(question.answer, "不")


if __name__ == "__main__":
    unittest.main()
