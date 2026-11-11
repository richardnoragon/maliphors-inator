"""Build a wheel plus a versioned Linux installer archive (requires build)."""
from pathlib import Path
import argparse
import subprocess
import sys
import tarfile
import tempfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from app_version import __version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-isolation', action='store_true', help='Use installed setuptools/wheel when ensurepip is unavailable')
    args = parser.parse_args()
    out = REPO / 'dist'
    out.mkdir(exist_ok=True)
    subprocess.run([sys.executable, '-m', 'build', '--wheel', '--outdir', str(out)] + (['--no-isolation'] if args.no_isolation else []), cwd=REPO, check=True)
    wheel = out / f'maliphors_inator-{__version__}-py3-none-any.whl'
    archive = out / f'maliphors-inator-{__version__}-linux.tar.gz'
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary) / f'maliphors-inator-{__version__}'
        folder.mkdir()
        import shutil
        for source in (wheel, REPO / 'LICENSE', REPO / 'README.md', REPO / 'scripts/install_linux.sh'):
            shutil.copyfile(source, folder / source.name)
        (folder / 'install_linux.sh').chmod(0o755)
        with tarfile.open(archive, 'w:gz') as tar:
            tar.add(folder, arcname=folder.name)
    print(archive)


if __name__ == '__main__':
    main()
