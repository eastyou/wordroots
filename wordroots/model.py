"""英语词根词缀数据、检索、卡片与测验生成。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

KINDS = ("prefix", "root", "suffix")
KIND_LABELS = {"prefix": "前缀", "root": "词根", "suffix": "后缀"}
OPTION_LETTERS = "ABCDEF"


class WordRootError(ValueError):
    """词条、参数或题型不合法。"""


@dataclass(frozen=True)
class Affix:
    """一条词缀条目。"""

    text: str
    kind: str
    meaning: str
    examples: Tuple[str, ...]
    note: str = ""

    @property
    def display(self) -> str:
        if self.kind == "prefix":
            return self.text + "-"
        if self.kind == "suffix":
            return "-" + self.text
        return self.text

    @property
    def kind_label(self) -> str:
        return KIND_LABELS.get(self.kind, self.kind)


@dataclass(frozen=True)
class QuizQuestion:
    """一道词义选择题。"""

    entry: Affix
    options: Tuple[str, ...]
    answer_index: int

    @property
    def answer(self) -> str:
        return self.options[self.answer_index]

    @property
    def answer_letter(self) -> str:
        return OPTION_LETTERS[self.answer_index]


def _entry(text: str, kind: str, meaning: str, examples: Sequence[str], note: str = "") -> Affix:
    return Affix(text, kind, meaning, tuple(examples), note)


_RAW = (
    _entry("un", "prefix", "不、相反", ["unhappy", "unable", "unlock"]),
    _entry("re", "prefix", "再、重新", ["rewrite", "replay", "rebuild"]),
    _entry("pre", "prefix", "在前、预先", ["preview", "predict", "prepare"]),
    _entry("dis", "prefix", "否定、分开", ["disagree", "disappear", "disconnect"]),
    _entry("mis", "prefix", "错误地", ["mislead", "misspell", "misunderstand"]),
    _entry("sub", "prefix", "在下、次级", ["subway", "submarine", "subset"]),
    _entry("inter", "prefix", "在……之间", ["internet", "international", "interact"]),
    _entry("trans", "prefix", "跨越、转变", ["transport", "translate", "transform"]),
    _entry("anti", "prefix", "反对、抵抗", ["antibiotic", "antisocial", "antifreeze"]),
    _entry("auto", "prefix", "自己、自动", ["automatic", "autograph", "automobile"]),
    _entry("bio", "prefix", "生命", ["biology", "biography", "biodiversity"]),
    _entry("tele", "prefix", "远", ["telephone", "television", "telescope"]),
    _entry("port", "root", "携带、搬运", ["portable", "export", "transport"]),
    _entry("spect", "root", "看", ["inspect", "respect", "spectator"]),
    _entry("dict", "root", "说", ["predict", "dictionary", "contradict"]),
    _entry("scrib", "root", "写", ["describe", "prescribe", "scribble"]),
    _entry("struct", "root", "建造", ["structure", "construct", "instruct"]),
    _entry("tract", "root", "拉、拖", ["attract", "contract", "extract"]),
    _entry("form", "root", "形状", ["reform", "uniform", "transform"]),
    _entry("log", "root", "言语、学科", ["dialogue", "biology", "logic"]),
    _entry("graph", "root", "写、画", ["photograph", "autograph", "paragraph"]),
    _entry("cred", "root", "相信", ["credit", "incredible", "credential"]),
    _entry("duc", "root", "引导", ["produce", "reduce", "introduce"]),
    _entry("ject", "root", "投掷", ["project", "reject", "inject"]),
    _entry("tion", "suffix", "名词：行为或状态", ["action", "creation", "education"]),
    _entry("ment", "suffix", "名词：结果或过程", ["movement", "agreement", "enjoyment"]),
    _entry("able", "suffix", "形容词：能……的", ["readable", "comfortable", "valuable"]),
    _entry("less", "suffix", "形容词：没有……的", ["homeless", "careless", "endless"]),
    _entry("ful", "suffix", "形容词：充满……的", ["helpful", "careful", "wonderful"]),
    _entry("ly", "suffix", "副词：以……方式", ["quickly", "happily", "carefully"]),
    _entry("er", "suffix", "名词：做某事的人或物", ["teacher", "worker", "computer"]),
    _entry("ist", "suffix", "名词：从事……的人", ["scientist", "artist", "tourist"]),
    _entry("ology", "suffix", "名词：学科", ["biology", "psychology", "technology"]),
    _entry("scope", "suffix", "名词：观察仪器", ["microscope", "telescope", "periscope"]),
    _entry("ify", "suffix", "动词：使……", ["simplify", "beautify", "classify"]),
    _entry("ous", "suffix", "形容词：具有……性质的", ["famous", "dangerous", "nervous"]),
)


def load_entries() -> List[Affix]:
    """返回内置词条列表。"""
    return list(_RAW)


def normalize_term(text: str) -> str:
    """去掉空白和两端的连字符，转小写。"""
    if not isinstance(text, str):
        raise WordRootError("词条必须是字符串")
    cleaned = text.strip().lower().strip("-").strip()
    if not cleaned:
        raise WordRootError("词条不能为空")
    return cleaned


def check_kind(kind: str) -> str:
    if kind not in KINDS:
        raise WordRootError("类型必须是 prefix、root 或 suffix，收到 %r" % (kind,))
    return kind


def find(term: str, entries: Optional[Sequence[Affix]] = None) -> List[Affix]:
    """按词条精确查找，返回所有同形条目。"""
    target = normalize_term(term)
    source = list(entries) if entries is not None else load_entries()
    return [entry for entry in source if entry.text == target]


def filter_by_kind(kind: str, entries: Optional[Sequence[Affix]] = None) -> List[Affix]:
    """按前缀、词根、后缀筛选。"""
    check_kind(kind)
    source = list(entries) if entries is not None else load_entries()
    return [entry for entry in source if entry.kind == kind]


def search(keyword: str, entries: Optional[Sequence[Affix]] = None) -> List[Affix]:
    """在词条、释义、例词和类型名中搜索。"""
    if not isinstance(keyword, str):
        raise WordRootError("关键词必须是字符串")
    needle = keyword.strip().lower()
    if not needle:
        raise WordRootError("关键词不能为空")
    source = list(entries) if entries is not None else load_entries()
    results = []
    for entry in source:
        haystack = [entry.text, entry.meaning, entry.kind_label, entry.note]
        haystack.extend(entry.examples)
        if any(needle in item.lower() for item in haystack):
            results.append(entry)
    return results


def build_cards(
    count: int,
    kinds: Optional[Sequence[str]] = None,
    seed: Optional[int] = None,
    entries: Optional[Sequence[Affix]] = None,
) -> List[Affix]:
    """抽取一组互不相同的词条卡片。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise WordRootError("卡片数量必须是正整数")
    source = list(entries) if entries is not None else load_entries()
    if kinds:
        allowed = [check_kind(kind) for kind in kinds]
        source = [entry for entry in source if entry.kind in allowed]
    if not source:
        raise WordRootError("筛选后没有可用词条")
    if count > len(source):
        raise WordRootError("符合条件的词条只有 %d 条，无法生成 %d 张卡片" % (len(source), count))
    rng = random.Random(seed)
    return rng.sample(source, count)


def build_quiz(
    count: int,
    seed: Optional[int] = None,
    entries: Optional[Sequence[Affix]] = None,
    options: int = 4,
) -> List[QuizQuestion]:
    """生成词义选择题，干扰项优先取自同一类型。"""
    if isinstance(options, bool) or not isinstance(options, int) or options < 2:
        raise WordRootError("选项数量至少为 2")
    if options > 6:
        raise WordRootError("选项数量最多为 6")
    source = list(entries) if entries is not None else load_entries()
    cards = build_cards(count, seed=seed, entries=source)
    rng = random.Random(None if seed is None else seed + 104729)
    questions = []
    for entry in cards:
        same_kind = [
            item.meaning
            for item in source
            if item.kind == entry.kind and item.meaning != entry.meaning
        ]
        others = [
            item.meaning
            for item in source
            if item.kind != entry.kind and item.meaning != entry.meaning
        ]
        same_pool = list(dict.fromkeys(same_kind))
        other_pool = list(dict.fromkeys(others))
        needed = options - 1
        if len(same_pool) + len(other_pool) < needed:
            raise WordRootError("题库中的释义不足以生成 %d 个选项" % options)
        take_same = min(needed, len(same_pool))
        distractors = rng.sample(same_pool, take_same)
        remaining = needed - take_same
        if remaining:
            distractors.extend(rng.sample(other_pool, remaining))
        choices = [entry.meaning] + distractors
        rng.shuffle(choices)
        questions.append(QuizQuestion(entry, tuple(choices), choices.index(entry.meaning)))
    return questions


def check_quiz(question: QuizQuestion, index: int) -> bool:
    """判断选项下标是否正确。"""
    if isinstance(index, bool) or not isinstance(index, int):
        return False
    if index < 0 or index >= len(question.options):
        return False
    return index == question.answer_index


def format_entry(entry: Affix) -> str:
    """终端里的一行展示。"""
    return "%s [%s] %s：%s" % (
        entry.display,
        entry.kind_label,
        entry.meaning,
        "、".join(entry.examples),
    )
