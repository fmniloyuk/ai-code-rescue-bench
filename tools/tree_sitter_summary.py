from __future__ import annotations

import argparse
import json
from pathlib import Path

import tree_sitter_python
from tree_sitter import Language, Node, Parser


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


def main() -> None:
    parser_args = argparse.ArgumentParser()
    parser_args.add_argument("root", type=Path)
    parser_args.add_argument("--language", choices=["python"], required=True)
    args = parser_args.parse_args()

    language = Language(tree_sitter_python.language())
    parser = Parser(language)
    files = sorted(args.root.rglob("*.py"))
    summary: dict[str, object] = {"files": len(files), "functions": 0, "classes": 0, "parse_errors": 0}
    for path in files:
        source = path.read_bytes()
        tree = parser.parse(source)
        if tree.root_node.has_error:
            summary["parse_errors"] = int(summary["parse_errors"]) + 1
        for node in walk(tree.root_node):
            if node.type == "function_definition":
                summary["functions"] = int(summary["functions"]) + 1
            elif node.type == "class_definition":
                summary["classes"] = int(summary["classes"]) + 1
    print(json.dumps(summary, sort_keys=True))
    if summary["parse_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
