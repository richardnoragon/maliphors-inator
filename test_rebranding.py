"""Check that the renamed installation preserves existing daily-test state."""
from scripts.install_daily_test import preserve_daily_data


def test_rebrand_reuses_saved_data_and_session_lock(tmp_path):
    legacy = tmp_path / 'malaphors-inator-daily' / 'data'
    legacy.mkdir(parents=True)
    (legacy / 'favorites.json').write_text('{"favorites": ["Keep me"]}')
    (legacy / '.session.lock').touch()
    current = tmp_path / 'maliphors-inator-daily'
    current.mkdir()

    preserve_daily_data(tmp_path, current)
    preserve_daily_data(tmp_path, current)

    assert (current / 'data').resolve() == legacy
    assert (current / 'data' / '.session.lock').samefile(legacy / '.session.lock')
    assert (current / 'data' / 'favorites.json').read_text() == '{"favorites": ["Keep me"]}'


def test_rebrand_preserves_separate_existing_destination(tmp_path):
    legacy = tmp_path / 'malaphors-inator-daily' / 'data'
    legacy.mkdir(parents=True)
    current = tmp_path / 'maliphors-inator-daily'
    (current / 'data').mkdir(parents=True)
    (current / 'data' / 'favorites.json').write_text('existing destination')

    preserve_daily_data(tmp_path, current)

    assert not (current / 'data').is_symlink()
    assert (current / 'data' / 'favorites.json').read_text() == 'existing destination'


def test_fresh_install_does_not_link_missing_legacy_data(tmp_path):
    current = tmp_path / 'maliphors-inator-daily'
    current.mkdir()
    preserve_daily_data(tmp_path, current)
    assert not (current / 'data').is_symlink()
