"""词根词缀卡片与测验的 HTML 渲染。"""

from __future__ import annotations

import html
from typing import Sequence

from .model import OPTION_LETTERS, Affix, QuizQuestion

STYLE = """
@page { size: A4 portrait; margin: 13mm 12mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1f2933;
  font-size: 11pt;
  line-height: 1.5;
}
h1 { font-size: 20pt; margin: 0 0 2mm; }
.sub { color: #6b7280; font-size: 10pt; margin: 0 0 6mm; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.card {
  border: 0.7pt dashed #9aa5b1;
  border-radius: 2mm;
  padding: 4mm 4.5mm;
  min-height: 34mm;
  page-break-inside: avoid;
}
.card .term {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 17pt;
  font-weight: 600;
  color: #0f4c81;
}
.card .kind {
  display: inline-block;
  margin-left: 2mm;
  padding: 0.3mm 1.8mm;
  border-radius: 1mm;
  background: #eef2f7;
  color: #52606d;
  font-size: 8.5pt;
  vertical-align: middle;
}
.card .meaning { margin-top: 1.8mm; font-size: 12pt; }
.card .examples { margin-top: 1.2mm; color: #6b7280; font-size: 9.5pt; }
ol.quiz { margin: 0; padding-left: 8mm; }
li.question { margin-bottom: 5mm; page-break-inside: avoid; }
.q-head { font-size: 12.5pt; margin-bottom: 1mm; }
.q-head .term { font-family: "SFMono-Regular", Consolas, monospace; font-weight: 600; }
.options { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6mm 6mm; }
.option { font-size: 10.5pt; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { columns: 2; column-gap: 10mm; padding-left: 8mm; }
.answers li { margin-bottom: 2mm; break-inside: avoid; }
.note { color: #6b7280; font-size: 9.5pt; }
@media print { .card, li.question, .answers li { break-inside: avoid; } }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_cards(entries: Sequence[Affix], title: str = "词根词缀卡片") -> str:
    """生成可裁剪的学习卡片。"""
    safe_title = _escape(title)
    cards = []
    for entry in entries:
        cards.append(
            '<div class="card">'
            '<span class="term">%s</span><span class="kind">%s</span>'
            '<div class="meaning">%s</div>'
            '<div class="examples">%s</div>'
            "</div>"
            % (
                _escape(entry.display),
                _escape(entry.kind_label),
                _escape(entry.meaning),
                _escape(" · ".join(entry.examples)),
            )
        )
    body = "".join(cards) or '<p class="note">暂无卡片。</p>'
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % safe_title,
            "<style>%s</style>" % STYLE,
            "</head>",
            "<body>",
            "<h1>%s</h1>" % safe_title,
            '<p class="sub">沿虚线剪开，正面看词条，背面写释义，自测更有效。</p>',
            '<div class="cards">%s</div>' % body,
            '<p class="note">共 %d 张卡片。</p>' % len(entries),
            "</body>",
            "</html>",
        ]
    )


def render_quiz(
    questions: Sequence[QuizQuestion],
    title: str = "词根词缀小测",
    include_answers: bool = False,
) -> str:
    """生成选择题小测；include_answers 为真时追加答案页。"""
    safe_title = _escape(title)
    items = []
    for index, question in enumerate(questions, start=1):
        option_html = "".join(
            '<div class="option">%s. %s</div>' % (OPTION_LETTERS[position], _escape(option))
            for position, option in enumerate(question.options)
        )
        items.append(
            '<li class="question">'
            '<div class="q-head">%d. <span class="term">%s</span> 的意思是？</div>'
            '<div class="options">%s</div>'
            "</li>" % (index, _escape(question.entry.display), option_html)
        )
    body = "".join(items) or '<p class="note">暂无题目。</p>'
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % safe_title,
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % safe_title,
        '<p class="sub">姓名：__________　得分：__________</p>',
        '<ol class="quiz">%s</ol>' % body,
    ]
    if include_answers:
        answers = "".join(
            "<li>%d. %s %s</li>"
            % (index, question.answer_letter, _escape(question.answer))
            for index, question in enumerate(questions, start=1)
        )
        parts.extend(
            [
                '<section class="answers">',
                "<h2>参考答案</h2>",
                "<ol>%s</ol>" % answers,
                "</section>",
            ]
        )
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)
