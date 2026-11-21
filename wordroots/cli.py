"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    WordRootError,
    build_cards,
    build_quiz,
    filter_by_kind,
    find,
    format_entry,
    load_entries,
    search,
)
from .render import render_cards, render_quiz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wordroots",
        description="英语词根词缀查询、卡片与测验",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="列出词条")
    list_parser.add_argument("--kind", choices=("prefix", "root", "suffix"), help="只看某一类")

    find_parser = subparsers.add_parser("find", help="精确查找词条")
    find_parser.add_argument("term", help="例如 tele 或 un-")

    search_parser = subparsers.add_parser("search", help="搜索词条、释义或例词")
    search_parser.add_argument("keyword", help="关键词")

    cards_parser = subparsers.add_parser("cards", help="生成可打印卡片")
    cards_parser.add_argument("--count", type=int, default=12, help="卡片数量，默认 12")
    cards_parser.add_argument("--kind", choices=("prefix", "root", "suffix"), help="限定类型")
    cards_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    cards_parser.add_argument("--title", default="词根词缀卡片", help="卡片标题")
    cards_parser.add_argument("-o", "--output", default=None, help="输出文件")

    quiz_parser = subparsers.add_parser("quiz", help="生成选择题小测")
    quiz_parser.add_argument("--count", type=int, default=10, help="题目数量，默认 10")
    quiz_parser.add_argument("--options", type=int, default=4, help="每题选项数，默认 4")
    quiz_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    quiz_parser.add_argument("--title", default="词根词缀小测", help="小测标题")
    quiz_parser.add_argument("--answers", action="store_true", help="追加答案页")
    quiz_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            entries = filter_by_kind(args.kind) if args.kind else load_entries()
            for entry in entries:
                print(format_entry(entry))
            return 0
        if args.command == "find":
            matches = find(args.term)
            if not matches:
                print("未找到 %s" % args.term, file=sys.stderr)
                return 1
            for entry in matches:
                print(format_entry(entry))
            return 0
        if args.command == "search":
            matches = search(args.keyword)
            if not matches:
                print("没有匹配 %s 的词条" % args.keyword, file=sys.stderr)
                return 1
            for entry in matches:
                print(format_entry(entry))
            return 0
        if args.command == "cards":
            kinds = [args.kind] if args.kind else None
            entries = build_cards(args.count, kinds, args.seed)
            _write_output(render_cards(entries, args.title), args.output)
            return 0
        questions = build_quiz(args.count, args.seed, options=args.options)
        _write_output(
            render_quiz(questions, args.title, include_answers=args.answers),
            args.output,
        )
        return 0
    except WordRootError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
