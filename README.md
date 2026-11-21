# wordroots

[![CI](https://github.com/eastyou/wordroots/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/wordroots/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

英语词根词缀学习工具：36 条常用前缀、词根、后缀，支持查询、可裁剪 A4 卡片与词义选择题。

## 特性

- 内置 36 条词缀，每条含中文释义、三个例词与类型标签
- 精确查找忽略大小写与连字符，例如 `tele`、`tele-`、`UN` 都能命中
- 搜索覆盖词条、释义、例词与类型名
- 卡片按两栏排版，虚线方便裁剪
- 小测干扰项优先取自同一类型，题目与选项顺序可用种子复现
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
wordroots list
wordroots list --kind prefix
wordroots find tele
wordroots search 生命
wordroots cards --count 12 --seed 3 -o cards.html
wordroots quiz --count 10 --seed 3 --answers -o quiz.html
```

| 命令 | 说明 |
| --- | --- |
| `list` | 列出全部词条，可用 `--kind` 过滤 |
| `find` | 精确查找一个词条 |
| `search` | 在词条、释义、例词中搜索 |
| `cards` | 生成 A4 学习卡片 |
| `quiz` | 生成选择题小测，`--answers` 追加答案页 |

## 词条示例

| 词条 | 类型 | 释义 | 例词 |
| --- | --- | --- | --- |
| tele- | 前缀 | 远 | telephone、television、telescope |
| port | 词根 | 携带、搬运 | portable、export、transport |
| -tion | 后缀 | 名词：行为或状态 | action、creation、education |

## 示例

- [examples/wordroots-cards.html](examples/wordroots-cards.html)：12 张学习卡片
- [examples/wordroots-quiz.html](examples/wordroots-quiz.html)：10 题词义小测，带答案页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
