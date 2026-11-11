import json

import pytest

import maliphors_inator_cli


class DummyGenerator:
    instances = []

    def __init__(self):
        self.__class__.instances.append(self)
        self.search_calls = []
        self.import_path = None
        self.export_path = None
        self.export_text_path = None
        self.last_language = None

    def generate_malaphor(self, language=None):
        self.last_language = language
        return {
            "malaphor": "Generated malaphor",
            "source1": "Source A",
            "source2": "Source B",
        }

    def _save_history_entry(self, entry):
        return True

    def generate_multiple(self, count=5, exclude_pairs=None, language=None):
        self.last_language = language
        return [
            {
                "malaphor": f"Generated {index}",
                "source1": "Source A",
                "source2": "Source B",
            }
            for index in range(count)
        ]

    def generate_with_category(self, category):
        return {
            "malaphor": f"Category {category}",
            "source1": "Source A",
            "source2": "Source B",
        }

    def generate_weighted_random(self, smart_mode=True):
        return {
            "malaphor": "Smart malaphor",
            "source1": "Source A",
            "source2": "Source B",
        }

    def search(self, query):
        self.search_calls.append(query)
        return [{"original": "Bird in the hand"}]

    async def import_malaphors(self, path):
        self.import_path = path
        return True

    async def export_malaphors(self, path):
        self.export_path = path
        return True

    async def export_malaphors_as_text(self, path):
        self.export_text_path = path
        return True


@pytest.fixture
def dummy_generator(monkeypatch):
    instance = DummyGenerator()
    monkeypatch.setattr(maliphors_inator_cli, "MalaphorGenerator", lambda: instance)
    return instance


def test_cli_generate_prints_output(dummy_generator, capsys):
    exit_code = maliphors_inator_cli.main(["--generate", "--count", "2", "--output-format", "plain"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Generated 0" in output
    assert "Generated 1" in output


def test_cli_generate_passes_language_to_generator(dummy_generator, capsys):
    exit_code = maliphors_inator_cli.main(["--generate", "--language", "es", "--output-format", "json"])

    assert exit_code == 0
    assert dummy_generator.last_language == "es"
    assert "Generated malaphor" in capsys.readouterr().out


def test_cli_search_outputs_json(dummy_generator, capsys):
    exit_code = maliphors_inator_cli.main(["--search", "bird", "--output-format", "json"])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["original"] == "Bird in the hand"


def test_cli_import_and_export(dummy_generator, tmp_path, capsys):
    import_path = tmp_path / "incoming.json"
    export_path = tmp_path / "out.json"
    import_path.write_text("{}", encoding="utf-8")

    import_exit = maliphors_inator_cli.main(["--import-file", str(import_path)])
    export_exit = maliphors_inator_cli.main(["--export", str(export_path), "--export-format", "text"])
    output = capsys.readouterr().out

    assert import_exit == 0
    assert export_exit == 0
    assert dummy_generator.import_path == str(import_path)
    assert dummy_generator.export_text_path == str(export_path)
    assert "Imported" in output
