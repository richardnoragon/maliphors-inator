"""Command-line entrypoints for maliphors-inator."""

import argparse
import asyncio
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List

from maliphors_inator_logic import MalaphorGenerator
from app_storage import StoreSession, resolve_data_dir, initialize_data, create_backup, preview_restore, restore_backup
from app_version import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="maliphors-inator CLI")
    parser.add_argument('--data-dir', help='Shared data directory (also MALIPHORS_INATOR_DATA_DIR)')
    parser.add_argument('--data-path', action='store_true', help='Print the resolved data directory')
    parser.add_argument('--backup', metavar='ZIP', help='Create a verified backup ZIP')
    parser.add_argument('--restore-preview', metavar='ZIP', help='Validate and list backup contents without restoring')
    parser.add_argument('--restore', metavar='ZIP', help='Restore a backup; requires --confirm-restore')
    parser.add_argument('--confirm-restore', action='store_true', help='Approve replacement after inspecting --restore-preview')
    parser.add_argument('--preview-import', metavar='JSON', help='Print import row statuses without changing the library')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument("--generate", action="store_true", help="Generate malaphors and print them")
    parser.add_argument("--count", type=int, default=1, help="Number of malaphors to generate")
    parser.add_argument("--category", help="Optional tag/category filter for generation")
    parser.add_argument("--language", help="Generate using phrases from a specific language code, such as en or es")
    parser.add_argument("--smart", action="store_true", help="Use weighted generation when available")
    parser.add_argument("--search", help="Search the phrase database")
    parser.add_argument("--import-file", dest="import_file", help="Import malaphors from a JSON file")
    parser.add_argument("--export", dest="export_path", help="Export the phrase database to a file")
    parser.add_argument(
        "--export-format",
        choices=["json", "text"],
        default="json",
        help="Export format when using --export",
    )
    parser.add_argument(
        "--output-format",
        choices=["plain", "markdown", "json"],
        default="plain",
        help="Format used when printing generated malaphors",
    )
    return parser


def _print_generated(results: List[dict], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    for index, item in enumerate(results, start=1):
        if output_format == "markdown":
            print(f"## Malaphor {index}")
            print(f"**Malaphor:** {item['malaphor']}")
            print(f"**Sources:** {item['source1']} | {item['source2']}")
        else:
            print(f"Malaphor {index}: {item['malaphor']}")
            print(f"From: {item['source1']} + {item['source2']}")
        print()


def _print_search(results: Iterable[dict], output_format: str) -> None:
    results_list = list(results)
    if output_format == "json":
        print(json.dumps(results_list, indent=2, ensure_ascii=False))
        return

    for item in results_list:
        print(item.get("original", ""))


def main(argv: List[str] | None = None) -> int:
    """Run a CLI command and return an exit code."""
    args = build_parser().parse_args(argv)
    try:
        actions = [args.generate, args.search, args.import_file, args.export_path,
                   args.backup, args.restore, args.restore_preview, args.data_path, args.preview_import]
        if sum(bool(value) for value in actions) > 1:
            raise ValueError('Choose one action per invocation')
        if args.restore and not args.confirm_restore:
            raise ValueError('Inspect --restore-preview first, then use --restore ZIP --confirm-restore')
        directory = resolve_data_dir(args.data_dir)
        if args.data_path:
            print(directory)
            return 0
        with StoreSession(directory):
            initialize_data(directory, migrate=args.data_dir is None and not os.environ.get('MALIPHORS_INATOR_DATA_DIR'))
            create_backup(directory, reason='startup')
            return _run_command(args)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _run_command(args) -> int:
    generator = MalaphorGenerator(data_dir=args.data_dir) if args.data_dir else MalaphorGenerator()
    directory = resolve_data_dir(args.data_dir)
    if args.backup:
        print(create_backup(directory, args.backup) or 'No data to back up')
        return 0
    if args.restore_preview:
        files = preview_restore(args.restore_preview)
        print(json.dumps({name: len(content) for name, content in files.items()}, indent=2))
        return 0
    if args.restore:
        print(json.dumps(restore_backup(directory, args.restore), indent=2))
        return 0
    if args.preview_import:
        from library_workflows import preview_import
        print(json.dumps(preview_import(args.preview_import, generator.proverbs), indent=2, ensure_ascii=False))
        return 0

    if args.search:
        _print_search(generator.search(args.search), args.output_format)
        return 0

    if args.import_file:
        imported = asyncio.run(generator.import_malaphors(args.import_file))
        print("Imported" if imported else "No new malaphors imported")
        return 0 if imported else 1

    if args.export_path:
        export_path = Path(args.export_path)
        if args.export_format == "text":
            success = asyncio.run(generator.export_malaphors_as_text(str(export_path)))
        else:
            success = asyncio.run(generator.export_malaphors(str(export_path)))
        print(f"Exported to {export_path}" if success else f"Export failed: {export_path}")
        return 0 if success else 1

    if args.generate:
        results: List[dict] = []
        count = max(1, args.count)
        if args.category:
            for _ in range(count):
                if args.language:
                    results.append(generator.generate_malaphor(language=args.language))
                else:
                    results.append(generator.generate_with_category(args.category))
        elif args.smart:
            for _ in range(count):
                results.append(generator.generate_weighted_random(smart_mode=True))
        elif count > 1:
            results = generator.generate_multiple(count=count, language=args.language)
            for result in results:
                if not generator._save_history_entry(result):
                    raise OSError("Could not save history.json. Check the destination and permissions.")
        else:
            results = [generator.generate_malaphor(language=args.language)]
        _print_generated(results, args.output_format)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())