"""Desktop entry point, retaining main.py CLI compatibility."""
import argparse
import os
import sys

from app_storage import StoreSession, resolve_data_dir, initialize_data, create_backup
from app_version import __version__


def desktop_main(argv=None):
    from maliphors_inator_ui import MaliphorsInatorApp
    parser = argparse.ArgumentParser(description='maliphors-inator desktop')
    parser.add_argument('--data-dir', help='Shared directory for saved JSON data')
    parser.add_argument('--smoke-test', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--version', action='version', version=__version__)
    args = parser.parse_args(argv)
    directory = resolve_data_dir(args.data_dir)
    try:
        with StoreSession(directory):
            initialize_data(directory, migrate=args.data_dir is None and not os.environ.get('MALIPHORS_INATOR_DATA_DIR'))
            create_backup(directory, reason='startup')
            app = MaliphorsInatorApp(data_dir=directory)
            app.root.title(f'maliphors-inator {__version__} — pre-alpha')
            if args.smoke_test:
                app.root.after(200, app.root.quit)
            try:
                app.run()
            finally:
                app.root.destroy()
        return 0
    except (OSError, ValueError) as exc:
        print(f'Could not start: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    cli_flags = {'--generate', '--search', '--import-file', '--export', '--backup',
                 '--restore', '--restore-preview', '--data-path', '--preview-import'}
    if any(flag in cli_flags for flag in sys.argv[1:]) or '--help' in sys.argv[1:]:
        from maliphors_inator_cli import main as cli_main
        raise SystemExit(cli_main(sys.argv[1:]))
    raise SystemExit(desktop_main())
