import sys

from maliphors_inator_cli import main as cli_main
from maliphors_inator_ui import MaliphorsInatorApp

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise SystemExit(cli_main(sys.argv[1:]))

    app = MaliphorsInatorApp()
    app.run()