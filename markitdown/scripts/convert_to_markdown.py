#!/usr/bin/env python3
"""Safely convert local files to Markdown with Microsoft MarkItDown."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Iterable

from markitdown import MarkItDown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert local files to Markdown without silently overwriting outputs."
    )
    parser.add_argument("inputs", nargs="+", help="Local input file(s)")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument(
        "--output-dir", type=Path, help="Directory for generated .md files"
    )
    destination.add_argument(
        "--stdout", action="store_true", help="Write one conversion to stdout"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Replace existing output files"
    )
    parser.add_argument(
        "--enable-plugins",
        action="store_true",
        help="Enable installed third-party MarkItDown plugins",
    )
    args = parser.parse_args()
    if args.stdout and len(args.inputs) != 1:
        parser.error("--stdout accepts exactly one input")
    if args.stdout and args.overwrite:
        parser.error("--overwrite has no effect with --stdout")
    return args


def result_text(result: object) -> str:
    for attribute in ("markdown", "text_content"):
        value = getattr(result, attribute, None)
        if isinstance(value, str):
            return value
    raise RuntimeError("MarkItDown returned no Markdown text")


def convert_local(converter: MarkItDown, source: Path) -> str:
    method = getattr(converter, "convert_local", None)
    if callable(method):
        return result_text(method(str(source)))
    return result_text(converter.convert(str(source)))


def unique_output_path(output_dir: Path, source: Path, reserved: set[Path]) -> Path:
    candidate = output_dir / f"{source.stem}.md"
    index = 2
    while candidate in reserved:
        candidate = output_dir / f"{source.stem}-{index}.md"
        index += 1
    reserved.add(candidate)
    return candidate


def write_output(path: Path, text: str, overwrite: bool) -> None:
    if not overwrite:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return

    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_name = handle.name
            handle.write(text)
        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def validated_inputs(paths: Iterable[str]) -> list[Path]:
    validated: list[Path] = []
    for raw in paths:
        if "://" in raw:
            raise ValueError(f"remote URLs are not accepted: {raw}")
        resolved = Path(raw).expanduser().resolve(strict=True)
        if not resolved.is_file():
            raise ValueError(f"input is not a file: {resolved}")
        validated.append(resolved)
    return validated


def main() -> int:
    args = parse_args()
    try:
        sources = validated_inputs(args.inputs)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    converter = MarkItDown(enable_plugins=args.enable_plugins)

    if args.stdout:
        try:
            sys.stdout.write(convert_local(converter, sources[0]))
            return 0
        except Exception as exc:  # MarkItDown exposes format-specific failures.
            print(f"error: {sources[0]}: {exc}", file=sys.stderr)
            return 1

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    reserved: set[Path] = set()
    failures = 0

    for source in sources:
        target = unique_output_path(output_dir, source, reserved)
        try:
            markdown = convert_local(converter, source)
            if not markdown.strip():
                raise RuntimeError("conversion produced empty output")
            write_output(target, markdown, args.overwrite)
            print(f"OK\t{source}\t{target}")
        except Exception as exc:  # Continue so batch callers receive all failures.
            failures += 1
            print(f"ERROR\t{source}\t{exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

