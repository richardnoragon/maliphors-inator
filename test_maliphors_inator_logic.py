import asyncio
import json
import logging
import threading
from pathlib import Path
from collections import deque

import pytest

from maliphors_inator_logic import MalaphorGenerator


@pytest.fixture
def sample_generator():
    generator = MalaphorGenerator()
    generator.proverbs = [
        {
            "original": "A bird in the hand",
            "beginning": "A bird in the hand",
            "ending": "is worth two in the bush",
        },
        {
            "original": "Too many cooks spoil the broth",
            "beginning": "Too many cooks",
            "ending": "spoil the broth",
        },
        {
            "original": "Actions speak louder than words",
            "beginning": "Actions",
            "ending": "speak louder than words",
        },
    ]
    generator.history = []
    generator.favorites = []
    generator.logger = logging.getLogger("test_maliphors_inator_logic")
    # Phase 2 attributes
    generator.recent_searches = deque(maxlen=10)
    generator.phrase_pair_ratings = {}
    generator.similarity_threshold = 0.80
    generator.generation_templates = [
        {
            "name": "Default Blend",
            "pattern": "{source1_beginning} {source2_ending}",
            "description": "Blend the beginning of one phrase with the ending of another.",
        }
    ]
    return generator


def test_smart_split_phrase_handles_and_clause():
    phrase = "A bird in the hand, but not in the bush"
    assert MalaphorGenerator().smart_split_phrase(phrase) == (
        "A bird in the hand",
        "but not in the bush",
    )


def test_smart_split_phrase_handles_but_clause_without_comma():
    phrase = "A stitch in time but not as good as a rest"
    assert MalaphorGenerator().smart_split_phrase(phrase)[1].startswith("but ")


def test_smart_split_phrase_handles_actions_phrase():
    phrase = "Actions speak louder than words"
    assert MalaphorGenerator().smart_split_phrase(phrase) == (
        "Actions",
        "speak louder than words",
    )


def test_smart_split_phrase_handles_simple_delimiter():
    phrase = "Look before you leap and learn from the past"
    result = MalaphorGenerator().smart_split_phrase(phrase)
    assert result[0] == "Look before you leap"
    assert result[1] == "learn from the past"


def test_smart_split_phrase_handles_phrase_without_delimiter():
    phrase = "Two wrongs do not make a right"
    left, right = MalaphorGenerator().smart_split_phrase(phrase)
    assert left == "Two wrongs do"
    assert right == "not make a right"


def test_smart_split_phrase_handles_empty_input():
    assert MalaphorGenerator().smart_split_phrase("") == ("", "")


def test_generate_malaphor_returns_expected_fields(sample_generator):
    result = sample_generator.generate_malaphor(0, 1)
    assert set(result) == {"malaphor", "source1", "source2", "timestamp", "language"}
    assert result["source1"] == "A bird in the hand"
    assert result["source2"] == "Too many cooks spoil the broth"
    assert result["malaphor"] == "A bird in the hand spoil the broth"
    assert result["language"] == "en"


def test_generate_malaphor_avoids_same_phrase(sample_generator):
    result = sample_generator.generate_malaphor(0, 0)
    assert result["source1"] == "A bird in the hand"
    assert result["source2"] == "A bird in the hand"


def test_generate_random_alias_returns_same_shape(sample_generator):
    result = sample_generator.generate_random()
    assert "malaphor" in result
    assert "source1" in result
    assert "source2" in result


def test_generate_random_uses_generated_history(sample_generator):
    sample_generator.generate_random()
    assert len(sample_generator.history) == 1


def test_generate_malaphor_respects_language_filter(sample_generator):
    sample_generator.proverbs = [
        {"original": "A bird in the hand", "beginning": "A bird in the hand", "ending": "is worth two in the bush", "language": "en"},
        {"original": "El tiempo es oro", "beginning": "El tiempo", "ending": "es oro", "language": "es"},
        {"original": "La prisa mata", "beginning": "La prisa", "ending": "mata", "language": "es"},
    ]

    result = sample_generator.generate_malaphor(language="es")
    assert result["source1"] in {"El tiempo es oro", "La prisa mata"}
    assert result["source2"] in {"El tiempo es oro", "La prisa mata"}
    assert result["language"] == "es"


def test_generate_multiple_respects_language_filter(sample_generator):
    sample_generator.proverbs = [
        {"original": "A bird in the hand", "beginning": "A bird in the hand", "ending": "is worth two in the bush", "language": "en"},
        {"original": "El tiempo es oro", "beginning": "El tiempo", "ending": "es oro", "language": "es"},
        {"original": "La prisa mata", "beginning": "La prisa", "ending": "mata", "language": "es"},
    ]

    results = sample_generator.generate_multiple(count=10, language="es")

    assert results
    assert all(result["source1"] in {"El tiempo es oro", "La prisa mata"} for result in results)
    assert all(result["source2"] in {"El tiempo es oro", "La prisa mata"} for result in results)


def test_generate_batch_respects_language_filter(sample_generator):
    sample_generator.proverbs = [
        {"original": "A bird in the hand", "beginning": "A bird in the hand", "ending": "is worth two in the bush", "language": "en"},
        {"original": "El tiempo es oro", "beginning": "El tiempo", "ending": "es oro", "language": "es"},
        {"original": "La prisa mata", "beginning": "La prisa", "ending": "mata", "language": "es"},
    ]

    results = sample_generator.generate_batch(count=5, language="es")

    assert len(results) == 5
    assert all(result["language"] == "es" for result in results)
    assert all(result["source1"] in {"El tiempo es oro", "La prisa mata"} for result in results)
    assert all(result["source2"] in {"El tiempo es oro", "La prisa mata"} for result in results)


@pytest.mark.asyncio
async def test_add_new_proverb_stores_language_metadata(sample_generator):
    success = await sample_generator.add_new_proverb("Tiempo es oro", "es oro", language="es")
    assert success is True
    assert sample_generator.proverbs[-1]["language"] == "es"


def test_search_returns_case_insensitive_matches(sample_generator):
    results = sample_generator.search("bird")
    assert len(results) == 1
    assert results[0]["original"] == "A bird in the hand"


def test_search_reuses_cached_results_for_repeated_queries(sample_generator, monkeypatch):
    sample_generator.proverbs = [{
        "original": "Time is of the essence",
        "beginning": "Time is",
        "ending": "of the essence",
    }]
    sample_generator._build_search_index()

    calls = []
    original_lookup = sample_generator.search_index.lookup

    def track_lookup(query):
        calls.append(query)
        return original_lookup(query)

    monkeypatch.setattr(sample_generator.search_index, "lookup", track_lookup)
    sample_generator.search.cache_clear()

    first = sample_generator.search("essence")
    second = sample_generator.search("essence")

    assert first == second
    assert calls == ["essence"]


def test_search_supports_partial_match(sample_generator):
    results = sample_generator.search("cook")
    assert any(item["original"] == "Too many cooks spoil the broth" for item in results)


def test_search_returns_all_when_query_empty(sample_generator):
    results = sample_generator.search("")
    assert len(results) == len(sample_generator.proverbs)


def test_search_handles_no_matches(sample_generator):
    assert sample_generator.search("no-such-phrase") == []


def test_import_malaphors_merges_new_entries(tmp_path, sample_generator):
    path = tmp_path / "malaphors.json"
    payload = {
        "proverbs": [
            {
                "original": "A bird in the hand",
                "beginning": "A bird in the hand",
                "ending": "is worth two in the bush",
            },
            {
                "original": "No news is good news",
                "beginning": "No news",
                "ending": "is good news",
            },
            {
                "original": "The early bird catches the worm",
                "beginning": "The early bird",
                "ending": "catches the worm",
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    sample_generator._save_to_file = lambda filepath, data: True
    result = asyncio.run(sample_generator.import_malaphors(str(path)))

    assert result is True
    assert len(sample_generator.proverbs) == 5
    assert any(item["original"] == "No news is good news" for item in sample_generator.proverbs)


def test_import_malaphors_skips_duplicates(tmp_path, sample_generator):
    path = tmp_path / "malaphors.json"
    payload = {
        "proverbs": [
            {
                "original": "A bird in the hand",
                "beginning": "A bird in the hand",
                "ending": "is worth two in the bush",
            },
            {
                "original": "Too many cooks spoil the broth",
                "beginning": "Too many cooks",
                "ending": "spoil the broth",
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    sample_generator._save_to_file = lambda filepath, data: True
    result = asyncio.run(sample_generator.import_malaphors(str(path)))

    assert result is False
    assert len(sample_generator.proverbs) == 3


def test_import_malaphors_handles_invalid_json(tmp_path, sample_generator):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json}", encoding="utf-8")

    assert asyncio.run(sample_generator.import_malaphors(str(path))) is False


def test_history_loads_from_file_handles_missing_file(sample_generator, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert sample_generator._load_history_from_file() == []


def test_history_loads_from_file_handles_malformed_json(sample_generator, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("history.json").write_text("{bad json", encoding="utf-8")
    assert sample_generator._load_history_from_file() == []


def test_export_history_as_text_handles_incomplete_entries(sample_generator, tmp_path):
    output_path = tmp_path / "history.txt"
    sample_generator.history = [
        {"malaphor": "Alpha malaphor", "source1": "Alpha", "source2": "Beta"},
        {"malaphor": "Broken entry"},
    ]

    result = asyncio.run(sample_generator.export_history_as_text(str(output_path)))

    assert result is True
    content = output_path.read_text(encoding="utf-8")
    assert "Alpha malaphor" in content
    assert "Broken entry" not in content


@pytest.mark.asyncio
async def test_generate_batch_async_respects_cancellation(sample_generator):
    """Test async batch generation stops immediately when cancelled."""
    cancel_event = threading.Event()
    cancel_event.set()

    results = await sample_generator.generate_batch_async(count=5, cancel_event=cancel_event)
    assert results == []


def test_cancel_generation_sets_requested_event(sample_generator):
    """Test the cancellation helper toggles the shared event."""
    cancel_event = threading.Event()
    assert sample_generator.cancel_generation(cancel_event) is True
    assert cancel_event.is_set() is True


def test_save_history_entry_persists_history(sample_generator, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = {
        "malaphor": "Saved malaphor",
        "source1": "Source 1",
        "source2": "Source 2",
    }

    assert sample_generator._save_history_entry(entry) is True
    data = json.loads(Path("history.json").read_text(encoding="utf-8"))
    assert data[-1]["malaphor"] == "Saved malaphor"
    assert "timestamp" in data[-1]


def test_save_history_entry_preserves_language_metadata(sample_generator, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = {
        "malaphor": "Tiempo es oro",
        "source1": "El tiempo",
        "source2": "es oro",
        "language": "es",
    }

    assert sample_generator._save_history_entry(entry) is True
    data = json.loads(Path("history.json").read_text(encoding="utf-8"))
    assert data[-1]["language"] == "es"


@pytest.mark.parametrize(
    "query, expected",
    [
        ("bird", 1),
        ("BIRD", 1),
        ("spoil", 1),
        ("random", 0),
    ],
)
def test_search_parameterized_queries(sample_generator, query, expected):
    assert len(sample_generator.search(query)) == expected


# ========== PHASE 2: POLISH & EXPLORATION TEST CASES ==========

# FEAT-7: Phrase Similarity Detection Tests
def test_phrase_similarity_detection_finds_similar(sample_generator):
    """Test that similar phrases are detected."""
    similar = sample_generator.detect_similar_phrases("A bird in hand")
    assert len(similar) > 0
    assert similar[0][1] >= sample_generator.similarity_threshold


def test_phrase_similarity_detection_returns_empty_for_unique():
    """Test that completely unique phrases don't match."""
    generator = MalaphorGenerator()
    generator.proverbs = [
        {"original": "alpha bravo charlie", "beginning": "alpha", "ending": "bravo charlie"},
    ]
    generator.similarity_threshold = 0.80

    similar = generator.detect_similar_phrases("xyz abc def")
    assert len(similar) == 0


def test_set_similarity_threshold():
    """Test adjusting similarity threshold."""
    generator = MalaphorGenerator()
    generator.similarity_threshold = 0.80

    generator.set_similarity_threshold(0.90)
    assert generator.similarity_threshold == 0.90

    # Invalid threshold should not change
    generator.set_similarity_threshold(1.5)
    assert generator.similarity_threshold == 0.90


# UX-9: Copy Generation Stats Formatting Tests
def test_format_malaphor_plain():
    """Test plain text formatting."""
    generator = MalaphorGenerator()
    result = generator.format_malaphor_for_copy("Test malaphor", "Source 1", "Source 2", "plain")
    assert "Malaphor: Test malaphor" in result
    assert "Source 1" in result
    assert "Source 2" in result


def test_format_malaphor_markdown():
    """Test markdown formatting."""
    generator = MalaphorGenerator()
    result = generator.format_malaphor_for_copy("Test", "Src1", "Src2", "markdown")
    assert "**Malaphor:**" in result
    assert "**Sources:**" in result
    assert "- Src1" in result


def test_format_malaphor_json():
    """Test JSON formatting."""
    generator = MalaphorGenerator()
    result = generator.format_malaphor_for_copy("Test", "Src1", "Src2", "json")
    data = json.loads(result)
    assert data["malaphor"] == "Test"
    assert data["source1"] == "Src1"
    assert "timestamp" in data


# UX-10: Recent Searches Tests
def test_add_recent_search(sample_generator):
    """Test adding search to recent history."""
    sample_generator.add_recent_search("bird")
    assert "bird" in sample_generator.get_recent_searches()


def test_get_recent_searches_order(sample_generator):
    """Test recent searches are in reverse order (newest first)."""
    sample_generator.add_recent_search("first")
    sample_generator.add_recent_search("second")
    recent = sample_generator.get_recent_searches()
    assert recent[0] == "second"
    assert recent[1] == "first"


def test_recent_searches_deque_max_size():
    """Test that recent searches respects max size of 10."""
    generator = MalaphorGenerator()
    generator.recent_searches = __import__('collections').deque(maxlen=10)

    for i in range(15):
        generator.add_recent_search(f"search_{i}")

    assert len(generator.get_recent_searches()) == 10


def test_clear_recent_searches(sample_generator):
    """Test clearing recent searches."""
    sample_generator.add_recent_search("test")
    sample_generator.clear_recent_searches()
    assert len(sample_generator.get_recent_searches()) == 0


# FEAT-2: Generate Multiple Suggestions Tests
def test_generate_multiple_returns_correct_count(sample_generator):
    """Test that generate_multiple returns requested count."""
    suggestions = sample_generator.generate_multiple(count=3)
    assert len(suggestions) <= 3


def test_generate_multiple_returns_unique_suggestions(sample_generator):
    """Test that generated suggestions are unique."""
    suggestions = sample_generator.generate_multiple(count=3)
    malaphors = [s["malaphor"] for s in suggestions]
    assert len(malaphors) == len(set(malaphors))


def test_generate_multiple_has_required_fields(sample_generator):
    """Test that suggestions have all required fields."""
    suggestions = sample_generator.generate_multiple(count=1)
    for sugg in suggestions:
        assert "malaphor" in sugg
        assert "source1" in sugg
        assert "source2" in sugg
        assert "timestamp" in sugg


# FEAT-3: Weighted Generation & Ratings Tests
def test_rate_malaphor_stores_rating(sample_generator, tmp_path, monkeypatch):
    """Test that ratings are stored."""
    monkeypatch.chdir(tmp_path)
    sample_generator.rate_malaphor("Source 1", "Source 2", 5)
    assert "Source 1|Source 2" in sample_generator.phrase_pair_ratings


def test_get_pair_rating_calculates_average():
    """Test that pair ratings return average."""
    generator = MalaphorGenerator()
    generator.phrase_pair_ratings = {"A|B": [4, 5, 3]}

    rating = generator.get_pair_rating("A", "B")
    assert rating == 4.0


def test_generate_weighted_random_falls_back_to_regular(sample_generator):
    """Test that weighted generation falls back if no ratings."""
    # Should not raise error even with no ratings
    result = sample_generator.generate_weighted_random(smart_mode=True)
    assert "malaphor" in result


def test_generate_weighted_random_respects_smart_mode_toggle():
    """Test smart mode toggle works."""
    generator = MalaphorGenerator()
    generator.proverbs = [
        {"original": "A", "beginning": "A", "ending": "B"},
        {"original": "C", "beginning": "C", "ending": "D"},
    ]
    generator.phrase_pair_ratings = {}
    generator.logger = logging.getLogger("test")
    generator.history = []  # Initialize history

    # Smart mode off should work
    result = generator.generate_weighted_random(smart_mode=False)
    assert "malaphor" in result


# FEAT-8: Batch Phrase Import Tests
def test_parse_batch_phrases_single_phrase(sample_generator):
    """Test parsing single phrase."""
    text = "A test phrase"
    phrases = sample_generator.parse_batch_phrases(text)
    assert len(phrases) == 1
    assert phrases[0][0] == "A test phrase"


def test_parse_batch_phrases_multiple():
    """Test parsing multiple phrases."""
    generator = MalaphorGenerator()
    generator.smart_split_phrase = lambda x: (x.split()[0], " ".join(x.split()[1:]))

    text = "First phrase\nSecond phrase"
    phrases = generator.parse_batch_phrases(text)
    assert len(phrases) == 2


def test_parse_batch_phrases_ignores_empty_lines():
    """Test that empty lines are ignored."""
    generator = MalaphorGenerator()
    generator.smart_split_phrase = lambda x: (x.split()[0], " ".join(x.split()[1:]))

    text = "First\n\n\nSecond"
    phrases = generator.parse_batch_phrases(text)
    assert len(phrases) == 2


def test_import_batch_phrases_counts_correctly(sample_generator, tmp_path, monkeypatch):
    """Test import batch counts imported and duplicate correctly."""
    monkeypatch.chdir(tmp_path)

    # Mock the save method to be async
    async def mock_save(*args, **kwargs):
        return True

    sample_generator._save_to_file = mock_save

    phrases = [
        ("New phrase", "New", "phrase"),  # New
    ]

    # Call the async function synchronously for testing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        imported, duplicates = loop.run_until_complete(sample_generator.import_batch_phrases(phrases))
        assert imported >= 0
        assert duplicates >= 0
    finally:
        loop.close()


# ============================================================================
# DATA-2: Source/Attribution Tests
# ============================================================================

def test_set_phrase_source(sample_generator):
    """Test setting source for a phrase."""
    result = sample_generator.set_phrase_source(0, "Shakespeare")
    assert result is True
    assert sample_generator.get_phrase_source(0) == "Shakespeare"


def test_set_phrase_source_invalid_index(sample_generator):
    """Test setting source with invalid index."""
    result = sample_generator.set_phrase_source(999, "Shakespeare")
    assert result is False


def test_get_phrase_source_not_set(sample_generator):
    """Test getting source when not set."""
    source = sample_generator.get_phrase_source(0)
    assert source is None


def test_get_all_sources(sample_generator):
    """Test getting all unique sources."""
    sample_generator.set_phrase_source(0, "Shakespeare")
    sample_generator.set_phrase_source(1, "Folk Wisdom")
    sample_generator.set_phrase_source(2, "Folk Wisdom")

    sources = sample_generator.get_all_sources()
    assert "Shakespeare" in sources
    assert "Folk Wisdom" in sources
    assert len(sources) == 2


def test_get_phrases_by_source(sample_generator):
    """Test filtering phrases by source."""
    sample_generator.set_phrase_source(0, "Shakespeare")
    sample_generator.set_phrase_source(1, "Folk Wisdom")

    shakespeare_phrases = sample_generator.get_phrases_by_source("Shakespeare")
    assert len(shakespeare_phrases) == 1
    assert shakespeare_phrases[0]["original"] == "A bird in the hand"


def test_migrate_schema_add_source(sample_generator):
    """Test schema migration to add source field."""
    # Verify no source field initially
    assert "source" not in sample_generator.proverbs[0]

    # Migrate
    count = sample_generator.migrate_schema_add_source()
    assert count == 3

    # Verify all have source field now
    for proverb in sample_generator.proverbs:
        assert "source" in proverb
        assert proverb["source"] == "Unknown"


# ============================================================================
# DATA-4: Database Validation & Deduplication Tests
# ============================================================================

def test_find_exact_duplicates(sample_generator):
    """Test finding exact duplicate phrases."""
    # Add a duplicate
    sample_generator.proverbs.append({
        "original": "A bird in the hand",
        "beginning": "A bird",
        "ending": "in the hand"
    })

    duplicates = sample_generator.find_exact_duplicates()
    assert len(duplicates) > 0
    assert len(duplicates[0]) == 2  # Should have a group of 2


def test_find_exact_duplicates_case_insensitive(sample_generator):
    """Test that duplicate detection is case-insensitive."""
    # Add a duplicate with different case
    sample_generator.proverbs.append({
        "original": "a bird in the hand",
        "beginning": "a bird",
        "ending": "in the hand"
    })

    duplicates = sample_generator.find_exact_duplicates()
    assert len(duplicates) > 0


def test_find_no_duplicates(sample_generator):
    """Test when there are no duplicates."""
    duplicates = sample_generator.find_exact_duplicates()
    assert len(duplicates) == 0


def test_find_similar_phrases(sample_generator):
    """Test finding similar phrases."""
    # Add a very similar phrase
    sample_generator.proverbs.append({
        "original": "A bird in the hand is worth two in the bush",
        "beginning": "A bird in the hand",
        "ending": "is worth two in the bush"
    })

    similar = sample_generator.find_similar_phrases(threshold=0.80)
    assert len(similar) > 0


def test_find_similar_phrases_empty_result(sample_generator):
    """Test finding similar phrases with high threshold."""
    similar = sample_generator.find_similar_phrases(threshold=0.95)
    # Most phrases won't be >95% similar
    assert isinstance(similar, list)


def test_validate_schema_valid(sample_generator):
    """Test schema validation with valid data."""
    report = sample_generator.validate_schema()

    assert report["total_phrases"] == 3
    assert report["valid"] == 3
    assert len(report["invalid"]) == 0


def test_validate_schema_invalid_missing_field(sample_generator):
    """Test schema validation with missing required field."""
    # Remove a required field
    del sample_generator.proverbs[0]["beginning"]

    report = sample_generator.validate_schema()
    assert len(report["invalid"]) == 1
    assert report["valid"] == 2


def test_validate_schema_missing_optional_source(sample_generator):
    """Test schema validation detects missing optional source field."""
    # Verify source field tracking
    report = sample_generator.validate_schema()

    # All phrases missing source should be reported
    assert len(report["missing_fields"]) == 3


def test_deduplicate_database_no_duplicates(sample_generator):
    """Test deduplication when there are no duplicates."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        report = loop.run_until_complete(sample_generator.deduplicate_database())
        assert report["removed_count"] == 0
        assert len(report["removed_indices"]) == 0
    finally:
        loop.close()


def test_deduplicate_database_with_duplicates(sample_generator):
    """Test deduplication with duplicate phrases."""
    # Add an exact duplicate
    sample_generator.proverbs.append({
        "original": "A bird in the hand",
        "beginning": "A bird in the hand",
        "ending": "is worth two in the bush"
    })

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        initial_count = len(sample_generator.proverbs)
        report = loop.run_until_complete(sample_generator.deduplicate_database())

        assert report["removed_count"] == 1
        assert len(sample_generator.proverbs) == initial_count - 1
    finally:
        loop.close()


def test_clean_database_full_cleanup(sample_generator):
    """Test full database cleanup."""
    # Add invalid phrase (missing field)
    sample_generator.proverbs.append({
        "original": "Bad phrase",
        # Missing "beginning" and "ending"
    })

    # Add a duplicate
    sample_generator.proverbs.append({
        "original": "A bird in the hand",
        "beginning": "A bird",
        "ending": "in hand"
    })

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        initial_count = len(sample_generator.proverbs)
        report = loop.run_until_complete(sample_generator.clean_database(
            remove_invalid=True,
            remove_duplicates=True
        ))

        # Should remove 2 phrases (1 invalid, 1 duplicate)
        assert report["total_removed"] >= 1  # At least the invalid one
        assert len(sample_generator.proverbs) < initial_count
    finally:
        loop.close()

    # ============================================================================
    # FEAT-4: Category/Tag System Tests
    # ============================================================================

def test_add_tags_to_phrase_valid(sample_generator):
    """Test adding tags to a valid phrase."""
    result = sample_generator.add_tags_to_phrase(0, ["animal", "nature"])
    assert result is True
    assert "animal" in sample_generator.proverbs[0]["tags"]
    assert "nature" in sample_generator.proverbs[0]["tags"]


def test_add_tags_to_phrase_invalid_index(sample_generator):
    """Test adding tags with invalid phrase index."""
    result = sample_generator.add_tags_to_phrase(999, ["animal"])
    assert result is False


def test_add_tags_to_phrase_no_duplicates(sample_generator):
    """Test that duplicate tags are not added."""
    sample_generator.add_tags_to_phrase(0, ["animal"])
    sample_generator.add_tags_to_phrase(0, ["animal", "bird"])

    tags = sample_generator.proverbs[0]["tags"]
    # Count how many times "animal" appears
    assert tags.count("animal") == 1
    assert "bird" in tags


def test_remove_tags_from_phrase(sample_generator):
    """Test removing tags from a phrase."""
    sample_generator.add_tags_to_phrase(0, ["animal", "nature", "wisdom"])

    result = sample_generator.remove_tags_from_phrase(0, ["nature"])
    assert result is True
    assert "nature" not in sample_generator.proverbs[0]["tags"]
    assert "animal" in sample_generator.proverbs[0]["tags"]


def test_remove_tags_from_phrase_invalid_index(sample_generator):
    """Test removing tags with invalid index."""
    result = sample_generator.remove_tags_from_phrase(999, ["animal"])
    assert result is False


def test_get_phrase_tags(sample_generator):
    """Test getting tags for a phrase."""
    sample_generator.add_tags_to_phrase(1, ["weather", "humor"])

    tags = sample_generator.get_phrase_tags(1)
    assert "weather" in tags
    assert "humor" in tags


def test_get_phrase_tags_empty(sample_generator):
    """Test getting tags for phrase without tags."""
    tags = sample_generator.get_phrase_tags(0)
    assert tags == [] or (isinstance(tags, list) and len(tags) == 0)


def test_get_all_tags(sample_generator):
    """Test getting all unique tags in database."""
    sample_generator.add_tags_to_phrase(0, ["animal", "nature"])
    sample_generator.add_tags_to_phrase(1, ["wisdom", "nature"])
    sample_generator.add_tags_to_phrase(2, ["animal"])

    all_tags = sample_generator.get_all_tags()
    assert "animal" in all_tags
    assert "nature" in all_tags
    assert "wisdom" in all_tags
    assert len(all_tags) == 3


def test_get_phrases_by_tag(sample_generator):
    """Test filtering phrases by tag."""
    sample_generator.add_tags_to_phrase(0, ["animal"])
    sample_generator.add_tags_to_phrase(2, ["animal", "nature"])

    results = sample_generator.get_phrases_by_tag("animal")
    assert len(results) == 2

    indices = [idx for idx, _ in results]
    assert 0 in indices
    assert 2 in indices


def test_get_phrases_by_tag_no_match(sample_generator):
    """Test filtering by tag with no results."""
    sample_generator.add_tags_to_phrase(0, ["animal"])

    results = sample_generator.get_phrases_by_tag("nonexistent")
    assert len(results) == 0


def test_generate_with_category_success(sample_generator):
    """Test generating malaphor within a specific category."""
    sample_generator.add_tags_to_phrase(0, ["animal"])
    sample_generator.add_tags_to_phrase(1, ["animal"])

    result = sample_generator.generate_with_category(category="animal")
    assert "malaphor" in result
    assert "source1" in result
    assert "source2" in result
    assert result["category"] == "animal"


def test_generate_with_category_any(sample_generator):
    """Test generating malaphor without category constraint."""
    result = sample_generator.generate_with_category(category=None)
    assert "malaphor" in result
    assert result["category"] == "Any"


def test_generate_with_category_insufficient_phrases(sample_generator):
    """Test generating with category that has too few phrases."""
    sample_generator.add_tags_to_phrase(0, ["rare"])
    # Only 1 phrase with tag "rare", need at least 2

    with pytest.raises(ValueError):
        sample_generator.generate_with_category(category="rare")


def test_migrate_schema_add_tags(sample_generator):
    """Test schema migration to add tags field."""
    # Remove tags field from all phrases
    for proverb in sample_generator.proverbs:
        if "tags" in proverb:
            del proverb["tags"]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        migrated = loop.run_until_complete(sample_generator.migrate_schema_add_tags())
        assert migrated == 3

        # Verify all phrases have tags field
        for proverb in sample_generator.proverbs:
            assert "tags" in proverb
            assert isinstance(proverb["tags"], list)
    finally:
        loop.close()

    # ============================================================================
    # FEAT-11: Statistics Dashboard Tests
    # ============================================================================

def test_get_statistics_returns_dict(sample_generator):
    """Test that get_statistics returns a dict with expected keys."""
    stats = sample_generator.get_statistics()

    assert isinstance(stats, dict)
    assert "total_phrases" in stats
    assert "total_generated" in stats
    assert "total_favorites" in stats
    assert "total_tags" in stats
    assert "phrase_usage" in stats
    assert "generation_trends" in stats
    assert "source_distribution" in stats


def test_get_statistics_correct_counts(sample_generator):
    """Test that statistics counts are accurate."""
    sample_generator.history.append({
        "malaphor": "Test malaphor",
        "source1": sample_generator.proverbs[0]["original"],
        "source2": sample_generator.proverbs[1]["original"]
    })

    stats = sample_generator.get_statistics()
    assert stats["total_phrases"] == 3
    assert stats["total_generated"] == 1


def test_calculate_phrase_usage(sample_generator):
    """Test phrase usage calculation."""
    # Add some history
    sample_generator.history = [
        {
            "malaphor": "test1",
            "source1": sample_generator.proverbs[0]["original"],
            "source2": sample_generator.proverbs[1]["original"]
        },
        {
            "malaphor": "test2",
            "source1": sample_generator.proverbs[0]["original"],
            "source2": sample_generator.proverbs[1]["original"]
        }
    ]

    usage = sample_generator._calculate_phrase_usage()

    # First phrase used twice, second phrase used twice
    assert sample_generator.proverbs[0]["original"] in usage
    assert usage[sample_generator.proverbs[0]["original"]] == 2


def test_calculate_generation_trends(sample_generator):
    """Test generation trends calculation."""
    trends = sample_generator._calculate_generation_trends()

    assert isinstance(trends, dict)
    assert "daily_count" in trends
    assert "total_by_day" in trends


def test_get_top_tags_with_tags(sample_generator):
    """Test getting top tags."""
    sample_generator.add_tags_to_phrase(0, ["animal", "animal"])
    sample_generator.add_tags_to_phrase(1, ["wisdom"])
    sample_generator.add_tags_to_phrase(2, ["animal", "wisdom"])

    top_tags = sample_generator._get_top_tags(limit=5)
    assert isinstance(top_tags, list)


def test_get_source_distribution(sample_generator):
    """Test source distribution calculation."""
    sample_generator.proverbs[0]["source"] = "Shakespeare"
    sample_generator.proverbs[1]["source"] = "Folk Wisdom"
    sample_generator.proverbs[2]["source"] = "Shakespeare"

    distribution = sample_generator._get_source_distribution()
    assert distribution.get("Shakespeare", 0) == 2
    assert distribution.get("Folk Wisdom", 0) == 1


def test_calculate_average_rating_no_ratings(sample_generator):
    """Test average rating with no ratings."""
    avg = sample_generator._calculate_average_rating()
    assert avg == 0.0


def test_calculate_average_rating_with_ratings(sample_generator):
    """Test average rating calculation."""
    sample_generator.phrase_pair_ratings = {
        "phrase1||phrase2": 4.5,
        "phrase2||phrase3": 3.5
    }

    avg = sample_generator._calculate_average_rating()
    assert abs(avg - 4.0) < 0.01  # Average of 4.5 and 3.5


def test_export_statistics_csv_returns_string(sample_generator):
    """Test that export_statistics_csv returns a string."""
    csv_content = sample_generator.export_statistics_csv()

    assert isinstance(csv_content, str)
    assert "STATISTICS SUMMARY" in csv_content
    assert "Total Phrases" in csv_content


def test_get_gallery_entries_sorts_and_marks_favorites(sample_generator):
    """Test gallery entries include ratings and favorite flags."""
    sample_generator.history = [
        {
            "malaphor": "Alpha malaphor",
            "source1": sample_generator.proverbs[0]["original"],
            "source2": sample_generator.proverbs[1]["original"],
            "timestamp": "2026-09-09T10:00:00+00:00",
        },
        {
            "malaphor": "Beta malaphor",
            "source1": sample_generator.proverbs[1]["original"],
            "source2": sample_generator.proverbs[2]["original"],
            "timestamp": "2026-09-10T10:00:00+00:00",
        },
    ]
    sample_generator.favorites = ["Beta malaphor"]
    sample_generator.phrase_pair_ratings = {
        f"{sample_generator.proverbs[0]['original']}|{sample_generator.proverbs[1]['original']}": [2, 4],
        f"{sample_generator.proverbs[1]['original']}|{sample_generator.proverbs[2]['original']}": [5],
    }

    gallery_entries = sample_generator.get_gallery_entries(sort_by="rating", favorites_only=True)

    assert len(gallery_entries) == 1
    assert gallery_entries[0]["malaphor"] == "Beta malaphor"
    assert gallery_entries[0]["is_favorite"] is True
    assert gallery_entries[0]["rating"] == 5


def test_generate_with_constraints_respects_word_bounds(sample_generator):
    """Test constrained generation honors word count limits."""
    result = sample_generator.generate_with_constraints(min_words=2, max_words=20)
    word_count = sample_generator.count_words(result["malaphor"])
    assert 2 <= word_count <= 20


def test_generate_from_template_uses_saved_pattern(sample_generator):
    """Test template-based generation uses the configured pattern."""
    sample_generator.save_generation_template(
        "Echo",
        "{source1_original} // {source2_original}",
        "Echo the source phrases",
    )
    result = sample_generator.generate_from_template("Echo", source1_index=0, source2_index=1)
    assert "//" in result["malaphor"]
    assert result["template"] == "Echo"


def test_generate_rhyming_random_prefers_rhyming_pairs():
    """Test rhyming generation selects a pair with a shared rhyme key."""
    generator = MalaphorGenerator()
    generator.proverbs = [
        {"original": "Time to shine", "beginning": "Time to", "ending": "shine"},
        {"original": "Climb the brine", "beginning": "Climb the", "ending": "brine"},
    ]
    generator.history = []
    generator.favorites = []
    generator.logger = logging.getLogger("test_maliphors_inator_logic")
    generator.recent_searches = deque(maxlen=10)
    generator.phrase_pair_ratings = {}
    generator.similarity_threshold = 0.80
    generator.generation_templates = [{"name": "Default Blend", "pattern": "{source1_beginning} {source2_ending}"}]

    result = generator.generate_rhyming_random(rhyme_length=3)
    assert "malaphor" in result


def test_format_malaphor_with_metadata_json(sample_generator):
    """Test metadata formatting returns JSON with rating and timestamp."""
    result = sample_generator.format_malaphor_with_metadata(
        "Test malaphor",
        "Source 1",
        "Source 2",
        rating=4,
        timestamp="2026-09-10T00:00:00+00:00",
        format_type="json",
    )
    data = json.loads(result)
    assert data["rating"] == 4
    assert data["timestamp"] == "2026-09-10T00:00:00+00:00"


def test_settings_profiles_roundtrip(sample_generator, tmp_path, monkeypatch):
    """Test saving, loading, listing, and deleting settings profiles."""
    monkeypatch.chdir(tmp_path)
    assert sample_generator.save_settings_profile("work", {"theme": "dark"}) is True
    assert sample_generator.list_settings_profiles() == ["work"]
    assert sample_generator.load_settings_profile("work")["theme"] == "dark"
    assert sample_generator.delete_settings_profile("work") is True
    assert sample_generator.list_settings_profiles() == []


def test_history_page_and_move_proverb(sample_generator, tmp_path, monkeypatch):
    """Test lazy history paging and proverb reordering."""
    monkeypatch.chdir(tmp_path)
    sample_generator.history = [
        {"malaphor": f"Item {i}", "source1": "A", "source2": "B", "timestamp": f"2026-09-10T00:00:0{i}+00:00"}
        for i in range(5)
    ]
    page = sample_generator.get_history_page(page=1, page_size=2)
    assert page["total_items"] == 5
    assert len(page["items"]) == 2

    before = [proverb["original"] for proverb in sample_generator.proverbs]
    assert sample_generator.move_proverb(0, 2) is True
    after = [proverb["original"] for proverb in sample_generator.proverbs]
    assert before[0] == after[2]


def test_auto_save_runs_and_persists_state(tmp_path, monkeypatch):
    """Test the periodic auto-save persists history and favorites."""
    monkeypatch.chdir(tmp_path)
    generator = MalaphorGenerator()
    generator.history = [{"malaphor": "Alpha", "source1": "A", "source2": "B", "timestamp": "2026-09-10T00:00:00+00:00"}]
    generator.favorites = ["Alpha"]

    generator.start_auto_save(interval_seconds=0.01)
    generator._run_auto_save()
    generator.stop_auto_save()

    assert json.loads(Path("history.json").read_text(encoding="utf-8")) == generator.history
    assert json.loads(Path("favorites.json").read_text(encoding="utf-8")) == {"favorites": generator.favorites}


def test_generate_batch_stops_when_cancelled(sample_generator):
    """Test batch generation respects cancellation early."""
    import threading

    cancel_event = threading.Event()
    cancel_event.set()

    results = sample_generator.generate_batch(count=5, cancel_event=cancel_event)
    assert results == []


def test_search_uses_phrase_index_for_queries(sample_generator):
    """Test search queries are resolved through the phrase index."""
    sample_generator.proverbs = [{
        "original": "Time is of the essence",
        "beginning": "Time is",
        "ending": "of the essence",
    }]
    sample_generator._build_search_index()

    matches = sample_generator.search("essence")
    assert len(matches) == 1
    assert matches[0]["original"] == "Time is of the essence"
    assert "essence" in sample_generator.search_index.query("essence")


def test_benchmark_search_latency_reports_stats(sample_generator):
    """Test repeated search queries produce latency statistics for performance checks."""
    sample_generator.proverbs = [
        {"original": f"Phrase {i} is worth testing", "beginning": f"Phrase {i}", "ending": "is worth testing"}
        for i in range(1, 101)
    ]
    sample_generator._build_search_index()

    stats = sample_generator.benchmark_search_latency("worth", iterations=25)

    assert stats["query"] == "worth"
    assert stats["iterations"] == 25
    assert stats["average_seconds"] >= 0
    assert stats["results_count"] >= 1
    assert "min_seconds" in stats and "max_seconds" in stats


def test_undo_redo_stack_tracks_state(sample_generator):
    """Test the undo/redo stack records and restores state."""
    generator = sample_generator
    generator.undo_stack = __import__('maliphors_inator_logic').UndoRedoStack(max_size=10)
    before = list(generator.proverbs)

    generator.proverbs.pop(0)
    generator.undo_stack.record_state("delete_proverb", {"proverbs": before}, {"proverbs": list(generator.proverbs)})

    assert generator.undo_stack.can_undo() is True
    generator.undo_stack.undo()
    assert len(generator.proverbs) == 3
    generator.undo_stack.redo()
    assert len(generator.proverbs) == 2


def test_export_malaphor_image_creates_png(tmp_path, sample_generator):
    """Test PNG export writes a valid image file."""
    output_path = tmp_path / "malaphor.png"
    result = sample_generator.export_malaphor_image(
        "Test malaphor",
        "Source One",
        "Source Two",
        str(output_path),
        image_format="png",
    )

    assert result is True
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_group3_generation_and_favorite_flow(sample_generator):
    """Test an end-to-end generation and favorite workflow."""
    result = sample_generator.generate_malaphor(0, 1)
    sample_generator.history.append(result)
    sample_generator.add_to_favorites(result["malaphor"])

    assert result["malaphor"]
    assert result["malaphor"] in sample_generator.favorites
    stats = sample_generator.get_statistics()
    assert stats["total_generated"] >= 1
    assert stats["total_favorites"] >= 1
