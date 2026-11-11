import json
import os
import stat
import tempfile
import random
import tkinter.messagebox
import re
import difflib
import threading
import time
import statistics
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import asyncio
import logging
from typing import List, Dict, Optional, Tuple, Set, Any
from collections import defaultdict, deque
from copy import deepcopy


def atomic_write_json(filepath, data):
    """Replace one JSON file only after serialization and a flushed write succeed."""
    path = Path(filepath).resolve()
    content = json.dumps(data, indent=2, ensure_ascii=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = None
    if path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)
        # Atomic replacement must still respect an explicitly read-only target.
        if not mode & 0o222 or not os.access(path, os.W_OK):
            raise PermissionError(f"Cannot write {path}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class PhraseIndex:
    """A lightweight inverted index for quick phrase search lookups."""

    def __init__(self, phrases: Optional[List[Dict[str, str]]] = None):
        self.phrases: List[Dict[str, str]] = []
        self.index: Dict[str, Set[int]] = defaultdict(set)
        if phrases:
            self.build(phrases)

    @staticmethod
    def _normalize_text(value: Any) -> str:
        text = "" if value is None else str(value)
        return re.sub(r"[^\w\u00C0-\uFFFF]+", " ", text.lower()).strip()

    def _tokenize(self, value: Any) -> List[str]:
        normalized = self._normalize_text(value)
        return [token for token in normalized.split() if token]

    def build(self, phrases: List[Dict[str, str]]) -> None:
        self.phrases = list(phrases)
        self.index = defaultdict(set)
        for idx, phrase in enumerate(self.phrases):
            for field in (phrase.get("original", ""), phrase.get("beginning", ""), phrase.get("ending", "")):
                for token in self._tokenize(field):
                    self.index[token].add(idx)

    def add_phrase(self, phrase: Dict[str, str]) -> None:
        self.phrases.append(phrase)
        for field in (phrase.get("original", ""), phrase.get("beginning", ""), phrase.get("ending", "")):
            for token in self._tokenize(field):
                self.index[token].add(len(self.phrases) - 1)

    def remove_phrase(self, index: int) -> None:
        if 0 <= index < len(self.phrases):
            phrase = self.phrases.pop(index)
            for field in (phrase.get("original", ""), phrase.get("beginning", ""), phrase.get("ending", "")):
                for token in self._tokenize(field):
                    self.index.get(token, set()).discard(index)
                    if not self.index.get(token):
                        self.index.pop(token, None)

    def query(self, query: str) -> Set[str]:
        tokens = self._tokenize(query)
        if not tokens:
            return set()
        return {token for token in tokens if token in self.index}

    def lookup(self, query: str) -> List[Dict[str, str]]:
        tokens = self._tokenize(query)
        if not tokens:
            return list(self.phrases)

        matched_indexes: Set[int] = set()
        for token in tokens:
            matched_indexes |= self.index.get(token, set())
        return [self.phrases[index] for index in sorted(matched_indexes)]


class UndoRedoStack:
    """Manage undo/redo history for destructive operations."""

    def __init__(self, owner: Optional[Any] = None, max_size: int = 20):
        self.owner = owner
        self.max_size = max_size
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []

    def attach(self, owner: Any) -> None:
        """Attach the stack to an object whose attributes will be restored."""
        self.owner = owner

    def record_state(self, operation: str, before_state: Dict[str, Any], after_state: Dict[str, Any], target: Optional[Any] = None) -> None:
        """Record an operation and its state transition."""
        entry = {
            "operation": operation,
            "before_state": before_state,
            "after_state": after_state,
            "target": target or self.owner,
        }
        self.undo_stack.append(entry)
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        return bool(self.undo_stack)

    def can_redo(self) -> bool:
        return bool(self.redo_stack)

    def _apply_snapshot(self, state: Dict[str, Any], target: Any) -> bool:
        if target is None:
            return False
        for key, value in state.items():
            if hasattr(target, key):
                setattr(target, key, deepcopy(value))
        return True

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        entry = self.undo_stack.pop()
        self.redo_stack.append(entry)
        return self._apply_snapshot(entry["before_state"], entry["target"])

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        entry = self.redo_stack.pop()
        self.undo_stack.append(entry)
        return self._apply_snapshot(entry["after_state"], entry["target"])


class MalaphorGenerator:
    """Generate and manage malaphors from combinations of phrases."""

    def __setattr__(self, name, value):
        if name == "undo_stack" and isinstance(value, UndoRedoStack):
            value.attach(self)
        super().__setattr__(name, value)

    def __init__(self):
        """Initialize the MalaphorGenerator with phrases from JSON file."""
        self._persistence_lock = threading.RLock()
        self.load_errors = {}
        self.proverbs = []
        self.history = []
        self.favorites = []
        self.logger = logging.getLogger('maliphors_inator')
        self.recent_searches = deque(maxlen=10)  # Track last 10 searches
        self.phrase_pair_ratings = {}  # Track ratings for phrase pairs (FEAT-3)
        self.similarity_threshold = 0.80  # 80% similarity threshold (FEAT-7)
        self.search_index = PhraseIndex()
        self.undo_stack = UndoRedoStack(owner=self, max_size=20)
        self.generation_templates = self._load_generation_templates()
        self._load_data()
        self.history = self._load_history_from_file()
        self._load_ratings()
        self._build_search_index()

    def _build_search_index(self) -> PhraseIndex:
        """Rebuild the phrase lookup index from the current proverb set."""
        self.search_index = PhraseIndex(self.proverbs)
        return self.search_index

    def start_auto_save(self, interval_seconds: float = 300.0) -> bool:
        """Start a background thread that periodically saves history and favorites."""
        self.stop_auto_save()
        self._auto_save_interval = max(1.0, float(interval_seconds))
        self._auto_save_stop_event = threading.Event()
        self._auto_save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self._auto_save_thread.start()
        return True

    def stop_auto_save(self) -> None:
        """Stop the background auto-save thread if it is running."""
        stop_event = getattr(self, "_auto_save_stop_event", None)
        if stop_event is not None:
            stop_event.set()
        thread = getattr(self, "_auto_save_thread", None)
        if thread is not None and thread.is_alive():
            thread.join(timeout=0.5)

    def _run_auto_save(self) -> bool:
        """Persist the latest history and favorites without blocking the UI."""
        history_ok = self._save_history_entry()
        favorites_ok = self._save_favorites_sync()
        if history_ok and favorites_ok:
            self.logger.info("Auto-saved history and favorites.")
            return True
        return False

    def _auto_save_loop(self) -> None:
        """Run the periodic save loop until stopped."""
        while not getattr(self, "_auto_save_stop_event", threading.Event()).is_set():
            if self._auto_save_stop_event.wait(self._auto_save_interval):
                break
            self._run_auto_save()

    def _protect_unreadable_file(self, filepath, error):
        path = Path(filepath).resolve()
        self.load_errors[path] = str(error)
        self.logger.error("Cannot load %s: %s. Writes are blocked; restore a backup and restart.", path, error)

    def _write_json(self, filepath, data):
        with self._persistence_lock:
            try:
                if Path(filepath).resolve() in self.load_errors:
                    raise OSError(f"{filepath} could not be loaded. Restore a backup and restart before saving.")
                atomic_write_json(filepath, data)
                return True
            except (OSError, ValueError, TypeError) as exc:
                self.logger.error("Could not save %s: %s", filepath, exc)
                return False

    def _save_favorites_sync(self) -> bool:
        with self._persistence_lock:
            return self._write_json("favorites.json", {"favorites": self.favorites})

    def _load_data(self) -> None:
        """Load malaphors, favorites, and history from JSON files."""
        try:
            self._load_malaphors()
            self._load_favorites()
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def _load_history_from_file(self) -> List[Dict[str, str]]:
        """Load valid records, protecting unreadable/partly invalid files from overwrite."""
        path = Path("history.json")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entries = data.get("history") if isinstance(data, dict) else data
            if not isinstance(entries, list):
                raise ValueError("Expected a history list")
            normalized = []
            for item in entries:
                if not isinstance(item, dict) or any(
                    not isinstance(item.get(key), str) or not item[key]
                    for key in ("malaphor", "source1", "source2")
                ) or (item.get("timestamp") is not None and not isinstance(item["timestamp"], str)):
                    self._protect_unreadable_file(path, "Invalid history record")
                    continue
                record = dict(item)
                record["timestamp"] = item.get("timestamp") or datetime.now(timezone.utc).isoformat()
                normalized.append(record)
            return normalized
        except FileNotFoundError:
            return []
        except (OSError, ValueError, TypeError) as exc:
            self._protect_unreadable_file(path, exc)
            return []

    def _save_history_entry(self, entry: Optional[Dict[str, str]] = None) -> bool:
        """Commit new history only after its file has been saved."""
        with self._persistence_lock:
            updated = list(self.history)
            if entry is not None:
                record = dict(entry)
                record["timestamp"] = entry.get("timestamp") or datetime.now(timezone.utc).isoformat()
                if not all(record.get(key) for key in ("malaphor", "source1", "source2")):
                    return False
                updated.append(record)
            if not self._write_json("history.json", updated):
                return False
            self.history = updated
            return True

    def _load_malaphors(self) -> None:
        try:
            data = json.loads(Path("malaphors.json").read_text(encoding="utf-8"))
            phrases = data.get("proverbs") if isinstance(data, dict) else None
            if not isinstance(phrases, list) or any(
                not isinstance(item, dict)
                or any(not isinstance(item.get(key), str) or not item[key].strip()
                       for key in ("original", "beginning", "ending"))
                or any(key in item and not isinstance(item[key], str) for key in ("language", "source"))
                or ("tags" in item and (not isinstance(item["tags"], list)
                    or any(not isinstance(tag, str) for tag in item["tags"])))
                for item in phrases
            ):
                raise ValueError("Expected a proverbs list with original, beginning, and ending strings")
            self.proverbs = phrases
        except FileNotFoundError:
            self.logger.warning("malaphors.json not found; starting with an empty collection.")
        except (OSError, ValueError, TypeError) as exc:
            self._protect_unreadable_file("malaphors.json", exc)

    def _load_favorites(self) -> None:
        try:
            data = json.loads(Path("favorites.json").read_text(encoding="utf-8"))
            favorites = data.get("favorites") if isinstance(data, dict) else None
            if not isinstance(favorites, list) or any(not isinstance(item, str) for item in favorites):
                raise ValueError("Expected a favorites list of strings")
            self.favorites = favorites
        except FileNotFoundError:
            pass
        except (OSError, ValueError, TypeError) as exc:
            self._protect_unreadable_file("favorites.json", exc)

    @lru_cache(maxsize=128)
    def _get_split_points(self, phrase: str) -> Tuple[str, str]:
        """Cache split points for phrases to avoid recomputing."""
        return self.smart_split_phrase(phrase)

    def smart_split_phrase(self, phrase: str) -> Tuple[str, str]:
        """Split a phrase into beginning and ending parts."""
        # Special case for 'but' since it should start the second part
        if ", but " in phrase:
            parts = phrase.split(", but ", 1)
            return parts[0].strip(), "but " + parts[1].strip()
        elif " but " in phrase:
            parts = phrase.split(" but ", 1)
            return parts[0].strip(), "but " + parts[1].strip()

        # Special case for "Actions speak louder than words" pattern
        parts = phrase.split(" speak ", 1)
        if len(parts) == 2 and parts[0].strip() == "Actions":
            return "Actions", "speak " + parts[1].strip()

        # Other common delimiters
        delimiters = [', and ', ' and ', ', ', '; ', ': ']
        for delimiter in delimiters:
            if delimiter in phrase:
                parts = phrase.split(delimiter, 1)
                return parts[0].strip(), parts[1].strip()

        # If no delimiter found, split at closest word to middle
        words = phrase.split()
        mid = len(words) // 2
        return ' '.join(words[:mid]), ' '.join(words[mid:])

    async def _save_to_file(self, filepath: str, data: dict) -> bool:
        """Commit without a cancellation point between disk and caller state updates."""
        return self._write_json(filepath, data)

    def generate_malaphor(
        self,
        source1_index: Optional[int] = None,
        source2_index: Optional[int] = None,
        language: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate a malaphor by combining parts of two phrases."""
        candidate_proverbs = list(self.proverbs)
        if language:
            language_key = str(language).lower()
            candidate_proverbs = [
                proverb for proverb in candidate_proverbs
                if str(proverb.get("language", "en")).lower() == language_key
            ]

        if len(candidate_proverbs) < 2:
            raise ValueError("Not enough proverbs to generate a malaphor")

        proverb1 = candidate_proverbs[source1_index] if source1_index is not None else random.choice(candidate_proverbs)
        if source2_index is not None:
            proverb2 = candidate_proverbs[source2_index]
            if source1_index is None:
                alternatives = [p for p in candidate_proverbs if p != proverb2]
                if not alternatives:
                    raise ValueError("Not enough distinct proverbs to generate a malaphor")
                proverb1 = random.choice(alternatives)
        else:
            alternatives = [p for p in candidate_proverbs if p != proverb1]
            if not alternatives:
                raise ValueError("Not enough distinct proverbs to generate a malaphor")
            proverb2 = random.choice(alternatives)

        new_malaphor = f"{proverb1['beginning']} {proverb2['ending']}"

        result = {
            "malaphor": new_malaphor,
            "source1": proverb1["original"],
            "source2": proverb2["original"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "language": str(proverb1.get("language", language or "en")).lower(),
        }

        if not self._save_history_entry(result):
            raise OSError("Could not save history.json. Check the destination and permissions.")
        return result

    def generate_random(self, source1_index: Optional[int] = None, source2_index: Optional[int] = None, language: Optional[str] = None) -> Dict[str, str]:
        """Compatibility wrapper for random malaphor generation."""
        return self.generate_malaphor(source1_index, source2_index, language=language)

    def generate_batch(
        self,
        count: int = 5,
        cancel_event: Optional[Any] = None,
        category: Optional[str] = None,
        template_name: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Generate a batch of malaphors until the request count is reached or cancellation is requested."""
        results: List[Dict[str, str]] = []
        if cancel_event is not None and cancel_event.is_set():
            return results

        for _ in range(max(0, int(count))):
            if cancel_event is not None and cancel_event.is_set():
                break
            if template_name:
                try:
                    result = self.generate_from_template(template_name, category=category, language=language)
                except ValueError:
                    result = self.generate_malaphor(language=language)
            else:
                result = self.generate_malaphor(language=language)
            results.append(result)
        return results

    async def generate_batch_async(
        self,
        count: int = 5,
        cancel_event: Optional[Any] = None,
        category: Optional[str] = None,
        template_name: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Async wrapper for batch generation that exits early if a cancellation signal is set."""
        if cancel_event is not None and cancel_event.is_set():
            return []

        results = []
        for _ in range(max(0, int(count))):
            await asyncio.sleep(0)
            if cancel_event is not None and cancel_event.is_set():
                break
            results.extend(self.generate_batch(count=1, cancel_event=cancel_event,
                                              category=category, template_name=template_name, language=language))
        return results

    def cancel_generation(self, cancel_event: Optional[Any] = None) -> bool:
        """Set a cancellation event if one is supplied."""
        if cancel_event is None:
            return False
        cancel_event.set()
        return True

    async def add_new_proverb(self, phrase_or_beginning: str, ending: str = None, language: Optional[str] = None) -> bool:
        """Add a new proverb to the collection."""
        try:
            if ending:
                beginning = phrase_or_beginning
            else:
                beginning, ending = self._get_split_points(phrase_or_beginning)

            if not beginning.strip() or not ending.strip():
                return False
            new_proverb = {
                "original": f"{beginning} {ending}",
                "beginning": beginning,
                "ending": ending,
                "language": str(language or "en").lower(),
            }

            updated = self.proverbs + [new_proverb]
            if not await self._save_to_file("malaphors.json", {"proverbs": updated}):
                return False
            self.proverbs = updated
            self._build_search_index()
            self.search.cache_clear()
            return True
        except Exception as e:
            self.logger.error(f"Error adding new proverb: {str(e)}")
            return False

    def add_to_favorites(self, malaphor: str) -> bool:
        """Add a favorite only when it can be saved."""
        if malaphor in self.favorites:
            return True
        with self._persistence_lock:
            previous = self.favorites
            self.favorites = self.favorites + [malaphor]
            if not self._save_favorites_sync():
                self.favorites = previous
                return False
            return True

    async def _save_favorites_async(self) -> bool:
        """Save favorite malaphors to a JSON file."""
        return self._save_favorites_sync()

    def save_favorites(self):
        """Save favorite malaphors to a JSON file."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._save_favorites_async())
        return loop.create_task(self._save_favorites_async())

    async def export_malaphors(self, filepath: str) -> bool:
        """Export all original malaphors to a JSON file."""
        return await self._save_to_file(filepath, {"proverbs": self.proverbs})

    async def export_favorites(self, filepath: str) -> bool:
        """Export favorites to a JSON file."""
        return await self._save_to_file(filepath, {"favorites": self.favorites})

    async def export_history(self, filepath: str) -> bool:
        """Export generated malaphor history to a JSON file."""
        return await self._save_to_file(filepath, {"history": self.history})

    async def export_malaphors_as_text(self, filepath: str) -> bool:
        """Export all original malaphors to a text file."""
        try:
            text = '\n'.join(proverb['original'] for proverb in self.proverbs)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Path(filepath).write_text(text, encoding='utf-8')
            )
            return True
        except Exception as e:
            self.logger.error(f"Error exporting malaphors as text: {str(e)}")
            return False

    async def export_history_as_text(self, filepath: str) -> bool:
        """Export generated malaphor history to a text file."""
        try:
            lines = []
            for item in self.history:
                if not isinstance(item, dict):
                    continue
                malaphor = item.get("malaphor") or ""
                source1 = item.get("source1") or ""
                source2 = item.get("source2") or ""
                if not malaphor or not source1 or not source2:
                    continue
                lines.extend([
                    f"Malaphor: {malaphor}",
                    "Created from:",
                    f"1. {source1}",
                    f"2. {source2}\n"
                ])
            text = '\n'.join(lines)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Path(filepath).write_text(text, encoding='utf-8')
            )
            return True
        except Exception as e:
            self.logger.error(f"Error exporting history as text: {str(e)}")
            return False

    async def export_favorites_as_text(self, filepath: str) -> bool:
        """Export favorites to a text file."""
        try:
            text = '\n\n'.join(self.favorites)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Path(filepath).write_text(text, encoding='utf-8')
            )
            return True
        except Exception as e:
            self.logger.error(f"Error exporting favorites as text: {str(e)}")
            return False

    async def import_malaphors(self, filepath: str) -> bool:
        """Validate and save an import before changing the active library."""
        self.last_import_error = None
        self.last_import_count = 0
        try:
            content = await asyncio.get_running_loop().run_in_executor(
                None, lambda: Path(filepath).read_text(encoding="utf-8")
            )
            data = json.loads(content)
            if not isinstance(data, dict) or not isinstance(data.get("proverbs"), list):
                raise ValueError("Expected a JSON object containing a proverbs list.")
            for index, phrase in enumerate(data["proverbs"], start=1):
                if not isinstance(phrase, dict) or any(
                    not isinstance(phrase.get(key), str) or not phrase[key].strip()
                    for key in ("original", "beginning", "ending")
                ):
                    raise ValueError(f"Phrase {index} needs non-empty original, beginning, and ending strings.")
                for key in ("language", "source"):
                    if key in phrase and not isinstance(phrase[key], str):
                        raise ValueError(f"Phrase {index}: {key} must be a string.")
                if "tags" in phrase and (
                    not isinstance(phrase["tags"], list)
                    or any(not isinstance(tag, str) for tag in phrase["tags"])
                ):
                    raise ValueError(f"Phrase {index}: tags must be a list of strings.")

            existing = {p["original"] for p in self.proverbs}
            additions = []
            for phrase in data["proverbs"]:
                if phrase["original"] not in existing:
                    additions.append(phrase)
                    existing.add(phrase["original"])
            if not additions:
                self.logger.info("No new malaphors to import.")
                return False

            merged = self.proverbs + additions
            save_result = self._save_to_file("malaphors.json", {"proverbs": merged})
            save_ok = await save_result if hasattr(save_result, "__await__") else bool(save_result)
            if not save_ok:
                raise OSError("Could not save malaphors.json. Check the destination and permissions.")
            self.proverbs = merged
            self._build_search_index()
            self.search.cache_clear()
            self.last_import_count = len(additions)
            self.logger.info("Successfully imported %s new malaphors.", len(additions))
            return True
        except (OSError, ValueError, TypeError) as exc:
            self.last_import_error = str(exc)
            self.logger.error("Error importing malaphors: %s", exc)
            return False

    async def edit_proverb(self, index: int, beginning: str, ending: str) -> bool:
        if not 0 <= index < len(self.proverbs) or not beginning.strip() or not ending.strip():
            return False
        updated = deepcopy(self.proverbs)
        updated[index].update(original=f"{beginning} {ending}", beginning=beginning, ending=ending)
        if not await self._save_to_file("malaphors.json", {"proverbs": updated}):
            return False
        self.proverbs = updated
        self._build_search_index()
        self.search.cache_clear()
        return True

    async def delete_proverb(self, index: int) -> bool:
        if not 0 <= index < len(self.proverbs):
            return False
        before = deepcopy(self.proverbs)
        updated = self.proverbs[:index] + self.proverbs[index + 1:]
        if not await self._save_to_file("malaphors.json", {"proverbs": updated}):
            return False
        self.proverbs = updated
        self._build_search_index()
        self.search.cache_clear()
        self.undo_stack.record_state("delete_proverb", {"proverbs": before}, {"proverbs": deepcopy(updated)})
        return True

    def _restore_action(self, redo=False):
        stack = self.undo_stack.redo_stack if redo else self.undo_stack.undo_stack
        if not stack:
            return False
        entry = stack[-1]
        state = entry["after_state" if redo else "before_state"]
        # Each supported deletion affects exactly one collection/file.
        if len(state) != 1 or entry["target"] is not self:
            return False
        key, value = next(iter(state.items()))
        files = {"proverbs": "malaphors.json", "history": "history.json", "favorites": "favorites.json"}
        if key not in files:
            return False
        with self._persistence_lock:
            if not self._write_json(files[key], value if key == "history" else {key: value}):
                return False
            result = self.undo_stack.redo() if redo else self.undo_stack.undo()
            self._build_search_index()
            self.search.cache_clear()
            return result

    def undo_last_action(self) -> bool:
        return self._restore_action()

    def redo_last_action(self) -> bool:
        return self._restore_action(redo=True)

    def get_all_proverbs(self) -> List[Dict[str, str]]:
        """Return all proverbs."""
        return self.proverbs

    def _delete_saved_item(self, key, index):
        with self._persistence_lock:
            items = getattr(self, key)
            if not 0 <= index < len(items):
                return False
            updated = items[:index] + items[index + 1:]
            if not self._write_json(f"{key}.json", updated if key == "history" else {key: updated}):
                return False
            setattr(self, key, updated)
            self.undo_stack.record_state(f"delete_{key}", {key: deepcopy(items)}, {key: deepcopy(updated)})
            return True

    def delete_from_history(self, index: int) -> bool:
        return self._delete_saved_item("history", index)

    def delete_from_favorites(self, index: int) -> bool:
        return self._delete_saved_item("favorites", index)

    @lru_cache(maxsize=32)
    def search(self, query: str) -> List[Dict[str, str]]:
        """Search formatted proverbs by original, beginning, or ending text."""
        query = (query or "").strip()
        if not query:
            return list(self.proverbs)

        if not hasattr(self, "search_index") or not self.search_index.index:
            self._build_search_index()
        matches = self.search_index.lookup(query)
        if not matches:
            query_lower = query.lower()
            matches = []
            for proverb in self.proverbs:
                haystacks = [
                    proverb.get("original", ""),
                    proverb.get("beginning", ""),
                    proverb.get("ending", "")
                ]
                if any(query_lower in value.lower() for value in haystacks if isinstance(value, str)):
                    matches.append(proverb)
        return matches

    def benchmark_search_latency(self, query: str, iterations: int = 25) -> Dict[str, Any]:
        """Benchmark repeated search latency and summarize the timing statistics."""
        iterations = max(1, int(iterations))
        query = (query or "").strip()
        self.search.cache_clear()

        durations: List[float] = []
        result_count = 0
        for _ in range(iterations):
            start = time.perf_counter()
            matches = self.search(query)
            end = time.perf_counter()
            durations.append(end - start)
            result_count = len(matches)

        return {
            "query": query,
            "iterations": iterations,
            "average_seconds": statistics.fmean(durations) if durations else 0.0,
            "min_seconds": min(durations) if durations else 0.0,
            "max_seconds": max(durations) if durations else 0.0,
            "results_count": result_count,
        }

    @lru_cache(maxsize=32)
    def search_history(self, query: str) -> List[Tuple[int, Dict[str, str]]]:
        """Search history items for a query string."""
        query = query.lower()
        return [
            (i, item) for i, item in enumerate(self.history)
            if query in item["malaphor"].lower() or
               query in item["source1"].lower() or
               query in item["source2"].lower()
        ]

    @lru_cache(maxsize=32)
    def search_favorites(self, query: str) -> List[Tuple[int, str]]:
        """Search favorites for a query string."""
        query = query.lower()
        return [
            (i, item) for i, item in enumerate(self.favorites)
            if query in item.lower()
        ]

    # ========== PHASE 2: POLISH & EXPLORATION FEATURES ==========

    # FEAT-7: Phrase Similarity Detection
    def detect_similar_phrases(self, phrase: str, threshold: Optional[float] = None) -> List[Tuple[Dict[str, str], float]]:
        """Detect phrases similar to the input (>80% match). Returns [(phrase, similarity_score)]."""
        if threshold is None:
            threshold = self.similarity_threshold

        phrase_normalized = phrase.lower().strip()
        similar = []

        for proverb in self.proverbs:
            original_normalized = proverb.get("original", "").lower().strip()
            if original_normalized == phrase_normalized:
                continue  # Don't match itself

            # Use a stronger score when one phrase fully contains the other.
            if phrase_normalized in original_normalized or original_normalized in phrase_normalized:
                ratio = 1.0
            else:
                ratio = difflib.SequenceMatcher(None, phrase_normalized, original_normalized).ratio()
            if ratio >= threshold:
                similar.append((proverb, ratio))

        # Sort by similarity score descending
        return sorted(similar, key=lambda x: x[1], reverse=True)

    def set_similarity_threshold(self, threshold: float) -> None:
        """Set the similarity detection threshold (0.0 - 1.0)."""
        if 0.0 <= threshold <= 1.0:
            self.similarity_threshold = threshold

    # UX-9: Copy Generation Stats Formatting
    def format_malaphor_for_copy(self, malaphor: str, source1: str, source2: str,
                                 format_type: str = "plain") -> str:
        """Format a malaphor with source phrases for copying. Formats: plain, markdown, json."""
        if format_type == "markdown":
            return f"**Malaphor:** {malaphor}\n\n**Sources:**\n- {source1}\n- {source2}"
        elif format_type == "json":
            return json.dumps({
                "malaphor": malaphor,
                "source1": source1,
                "source2": source2,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, indent=2)
        else:  # plain
            return f"Malaphor: {malaphor}\nFrom: {source1} + {source2}"

    # UX-10: Recent Searches
    def add_recent_search(self, query: str) -> None:
        """Add a search query to recent searches."""
        query = query.strip()
        if query:
            # Remove if already exists (to avoid duplicates in deque)
            if query in self.recent_searches:
                self.recent_searches.remove(query)
            self.recent_searches.appendleft(query)

    def get_recent_searches(self) -> List[str]:
        """Get list of recent searches."""
        return list(self.recent_searches)

    def clear_recent_searches(self) -> None:
        """Clear recent searches history."""
        self.recent_searches.clear()

    # FEAT-2: Generate Multiple Suggestions Without Duplicates
    def generate_multiple(self, count: int = 5, exclude_pairs: Optional[Set[Tuple[int, int]]] = None, language: Optional[str] = None) -> List[Dict[str, str]]:
        """Generate N unique malaphors. Returns list of malaphor dicts."""
        candidate_proverbs = list(self.proverbs)
        if language:
            language_key = str(language).lower()
            candidate_proverbs = [
                proverb for proverb in candidate_proverbs
                if str(proverb.get("language", "en")).lower() == language_key
            ]

        if len(candidate_proverbs) < 2:
            raise ValueError("Not enough proverbs to generate malaphors")

        if exclude_pairs is None:
            exclude_pairs = set()

        suggestions = []
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops

        while len(suggestions) < count and attempts < max_attempts:
            idx1 = random.randint(0, len(candidate_proverbs) - 1)
            idx2 = random.randint(0, len(candidate_proverbs) - 1)

            # Avoid same phrase and duplicates
            if idx1 != idx2 and (idx1, idx2) not in exclude_pairs:
                # Check if this combination would produce a unique malaphor
                proverb1 = candidate_proverbs[idx1]
                proverb2 = candidate_proverbs[idx2]
                new_malaphor = f"{proverb1['beginning']} {proverb2['ending']}"

                # Check if we already have this one
                if not any(s['malaphor'] == new_malaphor for s in suggestions):
                    result = {
                        "malaphor": new_malaphor,
                        "source1": proverb1["original"],
                        "source2": proverb2["original"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "language": str(proverb1.get("language", language or "en")).lower(),
                    }
                    suggestions.append(result)
                    exclude_pairs.add((idx1, idx2))

            attempts += 1

        return suggestions

    # FEAT-3: Weighted Random Generation (Rating-based)
    def _load_ratings(self) -> None:
        try:
            data = json.loads(Path("ratings.json").read_text(encoding="utf-8"))
            ratings = data.get("ratings") if isinstance(data, dict) else None
            if not isinstance(ratings, dict) or any(
                not isinstance(values, list) or any(type(rating) is not int or not 1 <= rating <= 5 for rating in values)
                for values in ratings.values()
            ):
                raise ValueError("Expected ratings lists containing integers from 1 to 5")
            self.phrase_pair_ratings = ratings
        except FileNotFoundError:
            pass
        except (OSError, ValueError, TypeError) as exc:
            self._protect_unreadable_file("ratings.json", exc)

    def _save_ratings(self) -> bool:
        return self._write_json("ratings.json", {"ratings": self.phrase_pair_ratings})

    def rate_malaphor(self, source1: str, source2: str, rating: int) -> None:
        """Rate a malaphor pair (1-5 stars). Used to train weighted generation."""
        if not (1 <= rating <= 5):
            return

        key = f"{source1}|{source2}"
        if key not in self.phrase_pair_ratings:
            self.phrase_pair_ratings[key] = []

        self.phrase_pair_ratings[key].append(rating)
        self._save_ratings()

    def get_pair_rating(self, source1: str, source2: str) -> Optional[float]:
        """Get average rating for a phrase pair."""
        key = f"{source1}|{source2}"
        ratings = self.phrase_pair_ratings.get(key, [])
        return sum(ratings) / len(ratings) if ratings else None

    def generate_weighted_random(self, smart_mode: bool = True) -> Dict[str, str]:
        """Generate malaphor with optional weighting by ratings."""
        if not smart_mode or not self.phrase_pair_ratings:
            # Fall back to regular generation if no ratings
            return self.generate_malaphor()

        # Calculate weights for each phrase pair based on ratings
        weighted_pairs = []
        for i, proverb1 in enumerate(self.proverbs):
            for j, proverb2 in enumerate(self.proverbs):
                if i != j:
                    key = f"{proverb1['original']}|{proverb2['original']}"
                    ratings = self.phrase_pair_ratings.get(key, [])
                    avg_rating = sum(ratings) / len(ratings) if ratings else 2.5  # Default neutral
                    # Weight increases exponentially with rating
                    weight = (avg_rating / 5.0) ** 2
                    weighted_pairs.append((i, j, weight))

        if not weighted_pairs:
            return self.generate_malaphor()

        # Select based on weights
        _, _, weights = zip(*weighted_pairs)
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        idx = random.choices(range(len(weighted_pairs)), weights=weights, k=1)[0]
        i, j, _ = weighted_pairs[idx]

        return self.generate_malaphor(i, j)

    def export_malaphor_image(self, malaphor: str, source1: str, source2: str, filepath: str, image_format: str = "png") -> bool:
        """Export a malaphor to PNG or SVG format."""
        fmt = (image_format or "png").lower()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "svg":
            safe_malaphor = (malaphor or "Malaphor").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe_source1 = str(source1 or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe_source2 = str(source2 or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='700'>
  <rect width='1200' height='700' fill='#111827'/>
  <rect x='40' y='40' width='1120' height='620' rx='24' fill='#1f2937' stroke='#60a5fa' stroke-width='3'/>
  <text x='60' y='180' fill='#f9fafb' font-family='DejaVu Sans, Arial, sans-serif' font-size='42' font-weight='bold'>Malaphor</text>
  <text x='60' y='260' fill='#fef3c7' font-family='DejaVu Sans, Arial, sans-serif' font-size='38'>{safe_malaphor}</text>
  <text x='60' y='420' fill='#cbd5e1' font-family='DejaVu Sans, Arial, sans-serif' font-size='24'>Source 1: {safe_source1}</text>
  <text x='60' y='470' fill='#cbd5e1' font-family='DejaVu Sans, Arial, sans-serif' font-size='24'>Source 2: {safe_source2}</text>
</svg>"""
            path.write_text(svg, encoding='utf-8')
            return True

        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self.logger.error("Pillow is required for PNG export.")
            return False

        width, height = 1200, 700
        image = Image.new("RGBA", (width, height), (17, 24, 39, 255))
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle((40, 40, 1160, 660), radius=30, fill=(31, 41, 55, 255), outline=(96, 165, 250, 255), width=4)
        draw.rounded_rectangle((80, 80, 1120, 620), radius=24, fill=(17, 24, 39, 255))

        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
        source_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)

        draw.text((95, 110), "Malaphor", fill=(249, 250, 251, 255), font=title_font)

        wrapped_lines = []
        current = ""
        for word in str(malaphor).split():
            candidate = f"{current} {word}".strip()
            if len(candidate) <= 36:
                current = candidate
            else:
                wrapped_lines.append(current)
                current = word
        if current:
            wrapped_lines.append(current)

        body_top = 180
        for line in wrapped_lines[:5]:
            draw.text((95, body_top), line, fill=(254, 243, 199, 255), font=body_font)
            body_top += 52

        draw.text((95, 490), f"Source 1: {str(source1 or '')[:90]}", fill=(203, 213, 225, 255), font=source_font)
        draw.text((95, 530), f"Source 2: {str(source2 or '')[:90]}", fill=(203, 213, 225, 255), font=source_font)

        image.save(path, format="PNG")
        return True

    # FEAT-8: Batch Phrase Import with Auto-Splitting
    def parse_batch_phrases(self, text: str) -> List[Tuple[str, str, str]]:
        """Parse batch text and auto-detect splits. Returns [(original, beginning, ending)]."""
        lines = text.strip().split('\n')
        results = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            beginning, ending = self.smart_split_phrase(line)
            results.append((line, beginning, ending))

        return results

    async def import_batch_phrases(self, phrases: List[Tuple[str, str, str]]) -> Tuple[int, int]:
        """Import batch of phrases. Returns (imported_count, duplicate_count)."""
        existing = {p["original"] for p in self.proverbs}
        imported = 0
        duplicates = 0

        for original, beginning, ending in phrases:
            if original not in existing:
                new_proverb = {
                    "original": original,
                    "beginning": beginning,
                    "ending": ending
                }
                self.proverbs.append(new_proverb)
                existing.add(original)
                imported += 1
            else:
                duplicates += 1

        if imported > 0:
            await self._save_to_file("malaphors.json", {"proverbs": self.proverbs})

        return imported, duplicates

    # ============================================================================
    # DATA-2: Source/Attribution Management
    # ============================================================================

    def set_phrase_source(self, phrase_index: int, source: str) -> bool:
        """Set the source for a phrase. Returns True if successful."""
        if 0 <= phrase_index < len(self.proverbs):
            self.proverbs[phrase_index]["source"] = source
            return True
        return False

    def get_phrase_source(self, phrase_index: int) -> Optional[str]:
        """Get the source for a phrase. Returns None if not set."""
        if 0 <= phrase_index < len(self.proverbs):
            return self.proverbs[phrase_index].get("source", None)
        return None

    def get_all_sources(self) -> Set[str]:
        """Get all unique sources in the database."""
        sources = set()
        for proverb in self.proverbs:
            if "source" in proverb and proverb["source"]:
                sources.add(proverb["source"])
        return sources

    def get_phrases_by_source(self, source: str) -> List[Dict[str, str]]:
        """Get all phrases from a specific source."""
        return [p for p in self.proverbs if p.get("source") == source]

    def migrate_schema_add_source(self) -> int:
        """Migrate database schema to add source field if missing. Returns count of added fields."""
        count = 0
        for proverb in self.proverbs:
            if "source" not in proverb:
                proverb["source"] = "Unknown"
                count += 1
        return count

    # ============================================================================
    # DATA-4: Database Validation & Deduplication
    # ============================================================================

    def find_exact_duplicates(self) -> List[List[int]]:
        """Find exact duplicate phrases (same original text).

        Returns: List of groups, where each group is a list of indices with same original.
        """
        seen = {}
        duplicates = []

        for idx, proverb in enumerate(self.proverbs):
            original = proverb.get("original", "").strip().lower()
            if original:
                if original in seen:
                    # Add to existing group or create new one
                    found = False
                    for group in duplicates:
                        if seen[original] in group:
                            group.append(idx)
                            found = True
                            break
                    if not found:
                        duplicates.append([seen[original], idx])
                else:
                    seen[original] = idx

        return duplicates

    def find_similar_phrases(self, threshold: float = 0.85) -> List[List[int]]:
        """Find similar phrase pairs using string similarity.

        Args:
            threshold: Similarity threshold (0.0-1.0), default 0.85

        Returns: List of groups, where each group is a list of similar indices.
        """
        similar_groups = []
        checked = set()

        for i, proverb1 in enumerate(self.proverbs):
            if i in checked:
                continue

            group = [i]
            original1 = proverb1.get("original", "").lower()

            for j in range(i + 1, len(self.proverbs)):
                if j in checked:
                    continue

                proverb2 = self.proverbs[j]
                original2 = proverb2.get("original", "").lower()

                # Calculate similarity with a containment shortcut for longer variants.
                if original1 in original2 or original2 in original1:
                    similarity = 1.0
                else:
                    similarity = difflib.SequenceMatcher(None, original1, original2).ratio()

                if similarity >= threshold:
                    group.append(j)
                    checked.add(j)

            if len(group) > 1:
                similar_groups.append(group)
                checked.add(i)

        return similar_groups

    def validate_schema(self) -> Dict[str, any]:
        """Validate database schema. Returns validation report."""
        report = {
            "total_phrases": len(self.proverbs),
            "valid": 0,
            "invalid": [],
            "missing_fields": [],
            "warnings": []
        }

        required_fields = ["original", "beginning", "ending"]
        optional_fields = ["source"]

        for idx, proverb in enumerate(self.proverbs):
            issues = []

            # Check required fields
            for field in required_fields:
                if field not in proverb or not str(proverb[field]).strip():
                    issues.append(f"Missing or empty '{field}'")

            # Check for empty strings
            for field in required_fields:
                if field in proverb and not str(proverb[field]).strip():
                    issues.append(f"Field '{field}' is empty")

            if issues:
                report["invalid"].append({"index": idx, "issues": issues})
            else:
                report["valid"] += 1

            # Check optional fields
            for field in optional_fields:
                if field not in proverb:
                    report["missing_fields"].append({"index": idx, "field": field})

        return report

    async def deduplicate_database(self, keep_first: bool = True) -> Dict[str, any]:
        """Deduplicate database by removing exact duplicates.

        Args:
            keep_first: If True, keep first occurrence; if False, keep last

        Returns: Report of changes made
        """
        duplicates = self.find_exact_duplicates()

        report = {
            "removed_count": 0,
            "removed_indices": [],
            "changes": []
        }

        if not duplicates:
            return report

        # Sort indices in reverse to remove from end first (preserves earlier indices)
        indices_to_remove = []
        for group in duplicates:
            group_sorted = sorted(group, reverse=True)
            # Keep first/last, remove others
            keep_idx = group_sorted[-1] if keep_first else group_sorted[0]
            remove_indices = [idx for idx in group_sorted if idx != keep_idx]
            indices_to_remove.extend(remove_indices)

            report["changes"].append({
                "original": self.proverbs[keep_idx].get("original"),
                "kept_index": keep_idx,
                "removed_indices": remove_indices
            })

        # Remove duplicates (in reverse order to preserve indices)
        for idx in sorted(set(indices_to_remove), reverse=True):
            removed = self.proverbs.pop(idx)
            report["removed_indices"].append(idx)
            report["removed_count"] += 1

        # Save updated database
        if report["removed_count"] > 0:
            await self._save_to_file("malaphors.json", {"proverbs": self.proverbs})

        return report

    async def clean_database(self, remove_invalid: bool = True, remove_duplicates: bool = True) -> Dict[str, any]:
        """Full database cleanup: validate, remove invalid, deduplicate.

        Returns: Combined report of all cleanup operations
        """
        report = {
            "validation": self.validate_schema(),
            "deduplication": {},
            "total_removed": 0
        }

        if remove_invalid:
            # Remove phrases with missing required fields
            indices_to_remove = [item["index"] for item in report["validation"]["invalid"]]
            for idx in sorted(indices_to_remove, reverse=True):
                self.proverbs.pop(idx)
            report["total_removed"] += len(indices_to_remove)

        if remove_duplicates:
            dedup_report = await self.deduplicate_database(keep_first=True)
            report["deduplication"] = dedup_report
            report["total_removed"] += dedup_report["removed_count"]

        # Save if any changes made
        if report["total_removed"] > 0:
            await self._save_to_file("malaphors.json", {"proverbs": self.proverbs})

        return report

    # ============================================================================
    # FEAT-4: Category/Tag System for Phrases
    # ============================================================================

    PRESET_TAGS = [
        "animal", "food", "emotion", "wisdom", "nature", "weather",
        "body", "color", "time", "place", "action", "object",
        "historical", "modern", "literary", "proverbial", "humorous", "wisdom"
    ]

    def add_tags_to_phrase(self, phrase_index: int, tags: List[str]) -> bool:
        """Add tags to a phrase (creates tags field if missing).

        Args:
            phrase_index: Index of phrase in database
            tags: List of tag strings to add

        Returns: True if successful, False if index invalid
        """
        if not (0 <= phrase_index < len(self.proverbs)):
            return False

        if "tags" not in self.proverbs[phrase_index]:
            self.proverbs[phrase_index]["tags"] = []

        # Add new tags without duplicates
        existing = set(self.proverbs[phrase_index]["tags"])
        for tag in tags:
            if tag.lower() not in existing:
                self.proverbs[phrase_index]["tags"].append(tag.lower())

        return True

    def remove_tags_from_phrase(self, phrase_index: int, tags: List[str]) -> bool:
        """Remove tags from a phrase.

        Args:
            phrase_index: Index of phrase in database
            tags: List of tag strings to remove

        Returns: True if successful, False if index invalid
        """
        if not (0 <= phrase_index < len(self.proverbs)):
            return False

        if "tags" not in self.proverbs[phrase_index]:
            return True

        tags_lower = {tag.lower() for tag in tags}
        self.proverbs[phrase_index]["tags"] = [
            t for t in self.proverbs[phrase_index]["tags"]
            if t not in tags_lower
        ]

        return True

    def get_phrase_tags(self, phrase_index: int) -> List[str]:
        """Get tags for a specific phrase.

        Args:
            phrase_index: Index of phrase in database

        Returns: List of tags, or empty list if none exist
        """
        if not (0 <= phrase_index < len(self.proverbs)):
            return []

        return self.proverbs[phrase_index].get("tags", [])

    def get_all_tags(self) -> Set[str]:
        """Get all unique tags used in database.

        Returns: Set of all tags used across all phrases
        """
        all_tags = set()
        for proverb in self.proverbs:
            tags = proverb.get("tags", [])
            all_tags.update(tags)
        return all_tags

    def get_phrases_by_tag(self, tag: str) -> List[Tuple[int, Dict[str, any]]]:
        """Find all phrases with a specific tag.

        Args:
            tag: Tag to search for

        Returns: List of (index, phrase) tuples
        """
        tag_lower = tag.lower()
        results = []
        for idx, proverb in enumerate(self.proverbs):
            tags = proverb.get("tags", [])
            if tag_lower in [t.lower() for t in tags]:
                results.append((idx, proverb))
        return results

    def generate_with_category(self, category: Optional[str] = None,
                              source1_index: Optional[int] = None,
                              source2_index: Optional[int] = None) -> Dict[str, str]:
        """Generate malaphor with optional category/tag filter.

        Args:
            category: If provided, both phrases must have this tag
            source1_index: Specific phrase index for source1 (optional)
            source2_index: Specific phrase index for source2 (optional)

        Returns: Generated malaphor dict with category info
        """
        if len(self.proverbs) < 2:
            raise ValueError("Not enough proverbs to generate a malaphor")

        # Filter phrases by category if specified
        if category:
            category_lower = category.lower()
            filtered_indices = [
                i for i, p in enumerate(self.proverbs)
                if category_lower in [t.lower() for t in p.get("tags", [])]
            ]
            if len(filtered_indices) < 2:
                raise ValueError(f"Not enough phrases with tag '{category}' to generate malaphor")
        else:
            filtered_indices = list(range(len(self.proverbs)))

        left = source1_index if source1_index in filtered_indices else random.choice(filtered_indices)
        if source2_index in filtered_indices:
            right = source2_index
            if source1_index not in filtered_indices:
                alternatives = [i for i in filtered_indices if self.proverbs[i] != self.proverbs[right]]
                if not alternatives:
                    raise ValueError("Not enough distinct phrases in this category")
                left = random.choice(alternatives)
        else:
            alternatives = [i for i in filtered_indices if self.proverbs[i] != self.proverbs[left]]
            if not alternatives:
                raise ValueError("Not enough distinct phrases in this category")
            right = random.choice(alternatives)
        proverb1, proverb2 = self.proverbs[left], self.proverbs[right]

        new_malaphor = f"{proverb1['beginning']} {proverb2['ending']}"

        result = {
            "malaphor": new_malaphor,
            "source1": proverb1["original"],
            "source2": proverb2["original"],
            "category": category or "Any",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if not self._save_history_entry(result):
            raise OSError("Could not save history.json. Check the destination and permissions.")
        return result

    async def migrate_schema_add_tags(self) -> int:
        """Add tags field to phrases that don't have it.

        Returns: Number of phrases migrated
        """
        migrated = 0
        for proverb in self.proverbs:
            if "tags" not in proverb:
                proverb["tags"] = []
                migrated += 1

        if migrated > 0:
            await self._save_to_file("malaphors.json", {"proverbs": self.proverbs})

        return migrated

    # ============================================================================
    # FEAT-11: Statistics Dashboard
    # ============================================================================

    def get_statistics(self) -> Dict[str, any]:
        """Generate comprehensive statistics for dashboard.

        Returns: Dict with statistics including counts, trends, top items
        """
        stats = {
            "total_phrases": len(self.proverbs),
            "total_generated": len(self.history),
            "total_favorites": len(self.favorites),
            "total_tags": len(self.get_all_tags()),
            "phrase_usage": self._calculate_phrase_usage(),
            "top_rated_malaphors": self._get_top_rated_malaphors(10),
            "generation_trends": self._calculate_generation_trends(),
            "top_tags": self._get_top_tags(10),
            "source_distribution": self._get_source_distribution(),
            "average_rating": self._calculate_average_rating()
        }
        return stats

    def _calculate_phrase_usage(self) -> Dict[str, int]:
        """Calculate how many times each phrase was used in generation.

        Returns: Dict mapping phrase original to usage count
        """
        usage = {}
        for entry in self.history:
            source1 = entry.get("source1", "")
            source2 = entry.get("source2", "")
            usage[source1] = usage.get(source1, 0) + 1
            usage[source2] = usage.get(source2, 0) + 1

        # Sort by usage (descending)
        return dict(sorted(usage.items(), key=lambda x: x[1], reverse=True))

    def _get_top_rated_malaphors(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get top N rated malaphors from history.

        Args:
            limit: Max number of results to return

        Returns: List of top rated malaphors with ratings
        """
        # Malaphors are rated if they're in phrase_pair_ratings
        rated = []
        for entry in self.history:
            key = f"{entry.get('source1', '')}||{entry.get('source2', '')}"
            rating = self.phrase_pair_ratings.get(key, 0)
            if rating > 0:
                rated.append({
                    "malaphor": entry.get("malaphor", ""),
                    "rating": rating,
                    "timestamp": entry.get("timestamp", "")
                })

        # Sort by rating descending
        rated.sort(key=lambda x: x["rating"], reverse=True)
        return rated[:limit]

    def _calculate_generation_trends(self) -> Dict[str, any]:
        """Calculate generation trends over time.

        Returns: Dict with daily/weekly generation counts
        """
        from datetime import datetime, timedelta

        trends = {
            "daily_count": {},
            "total_by_day": 0
        }

        if not self.history:
            return trends

        # Group by date
        by_date = {}
        for entry in self.history:
            timestamp = entry.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    date_str = dt.date().isoformat()
                    by_date[date_str] = by_date.get(date_str, 0) + 1
                except:
                    pass

        trends["daily_count"] = dict(sorted(by_date.items()))
        trends["total_by_day"] = len(by_date)

        return trends

    def _get_top_tags(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently used tags.

        Args:
            limit: Max number of tags to return

        Returns: List of (tag, count) tuples sorted by count
        """
        tag_counts = {}
        for proverb in self.proverbs:
            tags = proverb.get("tags", [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by count descending
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]

    def _get_source_distribution(self) -> Dict[str, int]:
        """Get distribution of phrases by source.

        Returns: Dict mapping source to phrase count
        """
        source_counts = {}
        for proverb in self.proverbs:
            source = proverb.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

        return dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True))

    def _calculate_average_rating(self) -> float:
        """Calculate average rating of all rated phrase pairs.

        Returns: Average rating (0.0 if no ratings)
        """
        if not self.phrase_pair_ratings:
            return 0.0

        ratings = list(self.phrase_pair_ratings.values())
        if not ratings:
            return 0.0

        return sum(ratings) / len(ratings)

    def export_statistics_csv(self) -> str:
        """Generate CSV export of statistics.

        Returns: CSV formatted string
        """
        import csv
        from io import StringIO

        stats = self.get_statistics()
        output = StringIO()
        writer = csv.writer(output)

        # Summary section
        writer.writerow(["STATISTICS SUMMARY"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Phrases", stats["total_phrases"]])
        writer.writerow(["Total Generated", stats["total_generated"]])
        writer.writerow(["Total Favorites", stats["total_favorites"]])
        writer.writerow(["Total Tags", stats["total_tags"]])
        writer.writerow(["Average Rating", f"{stats['average_rating']:.2f}"])

        # Top phrases section
        writer.writerow([])
        writer.writerow(["TOP USED PHRASES"])
        writer.writerow(["Phrase", "Usage Count"])
        for phrase, count in list(stats["phrase_usage"].items())[:10]:
            writer.writerow([phrase, count])

        # Top tags section
        writer.writerow([])
        writer.writerow(["TOP TAGS"])
        writer.writerow(["Tag", "Count"])
        for tag, count in stats["top_tags"]:
            writer.writerow([tag, count])

        # Source distribution section
        writer.writerow([])
        writer.writerow(["SOURCE DISTRIBUTION"])
        writer.writerow(["Source", "Phrase Count"])
        for source, count in stats["source_distribution"].items():
            writer.writerow([source, count])

        return output.getvalue()

    def get_gallery_entries(
        self,
        source: str = "history",
        sort_by: str = "recent",
        favorites_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Return gallery-ready entries with rating and favorite metadata."""
        favorite_lookup = {item for item in self.favorites}
        source_mode = (source or "history").lower()

        if source_mode == "favorites":
            entries = [entry for entry in self.history if entry.get("malaphor", "") in favorite_lookup]
        else:
            entries = list(self.history)

        if favorites_only:
            entries = [entry for entry in entries if entry.get("malaphor", "") in favorite_lookup]

        def parse_timestamp(value: str) -> datetime:
            if not value:
                return datetime.min.replace(tzinfo=timezone.utc)
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return datetime.min.replace(tzinfo=timezone.utc)

        gallery_entries: List[Dict[str, Any]] = []
        for entry in entries:
            source1 = entry.get("source1", "")
            source2 = entry.get("source2", "")
            rating = self.get_pair_rating(source1, source2) or 0.0
            gallery_entries.append(
                {
                    **entry,
                    "rating": rating,
                    "is_favorite": entry.get("malaphor", "") in favorite_lookup,
                }
            )

        sort_mode = (sort_by or "recent").lower()
        if sort_mode == "rating":
            gallery_entries.sort(
                key=lambda entry: (entry.get("rating", 0.0), parse_timestamp(entry.get("timestamp", ""))),
                reverse=True,
            )
        elif sort_mode == "alpha":
            gallery_entries.sort(key=lambda entry: entry.get("malaphor", "").lower())
        else:
            gallery_entries.sort(key=lambda entry: parse_timestamp(entry.get("timestamp", "")), reverse=True)

        if limit is not None and limit >= 0:
            gallery_entries = gallery_entries[:limit]

        return gallery_entries

    @staticmethod
    def _safe_format(template: str, context: Dict[str, Any]) -> str:
        class _FormatDict(dict):
            def __missing__(self, key):
                return ""

        return template.format_map(_FormatDict(context))

    def _build_generation_result(
        self,
        proverb1: Dict[str, str],
        proverb2: Dict[str, str],
        category: Optional[str] = None,
        template: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        context = {
            "source1_beginning": proverb1.get("beginning", ""),
            "source1_ending": proverb1.get("ending", ""),
            "source1_original": proverb1.get("original", ""),
            "source2_beginning": proverb2.get("beginning", ""),
            "source2_ending": proverb2.get("ending", ""),
            "source2_original": proverb2.get("original", ""),
        }

        if template:
            pattern = template.get("pattern", "{source1_beginning} {source2_ending}")
            malaphor = self._safe_format(pattern, context).strip()
            template_name = template.get("name", "")
        else:
            malaphor = f"{context['source1_beginning']} {context['source2_ending']}".strip()
            template_name = ""

        result = {
            "malaphor": malaphor,
            "source1": proverb1.get("original", ""),
            "source2": proverb2.get("original", ""),
            "category": category or "Any",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if template_name:
            result["template"] = template_name
        return result

    def count_words(self, text: str) -> int:
        """Count words in a string."""
        return len(re.findall(r"\b[\w'-]+\b", text or ""))

    def estimate_syllables(self, word: str) -> int:
        """Estimate syllables for a word using a simple heuristic."""
        normalized = re.sub(r"[^a-zA-Z]", "", word or "").lower()
        if not normalized:
            return 0

        vowels = "aeiouy"
        syllables = 0
        previous_is_vowel = False
        for character in normalized:
            is_vowel = character in vowels
            if is_vowel and not previous_is_vowel:
                syllables += 1
            previous_is_vowel = is_vowel

        if normalized.endswith("e") and syllables > 1:
            syllables -= 1

        return max(1, syllables)

    def count_syllables(self, text: str) -> int:
        """Estimate syllables for a phrase."""
        return sum(self.estimate_syllables(word) for word in (text or "").split())

    def _last_word(self, text: str) -> str:
        words = re.findall(r"[\w'-]+", text or "")
        return words[-1].lower() if words else ""

    def _rhyme_key(self, text: str, length: int = 2) -> str:
        last_word = self._last_word(text)
        if len(last_word) <= length:
            return last_word
        return last_word[-length:]

    def find_rhyming_pairs(self, limit: int = 10, rhyme_length: int = 2) -> List[Tuple[int, int]]:
        """Find phrase pairs whose endings rhyme using a simple suffix match."""
        pairs = []
        for left_index, proverb1 in enumerate(self.proverbs):
            left_key = self._rhyme_key(proverb1.get("original", ""), rhyme_length)
            if not left_key:
                continue
            for right_index, proverb2 in enumerate(self.proverbs):
                if left_index == right_index:
                    continue
                right_key = self._rhyme_key(proverb2.get("original", ""), rhyme_length)
                if left_key == right_key:
                    pairs.append((left_index, right_index))
                    if len(pairs) >= limit:
                        return pairs
        return pairs

    def generate_rhyming_random(self, rhyme_length: int = 2) -> Dict[str, str]:
        """Generate a malaphor using a rhyming pair when possible."""
        pairs = self.find_rhyming_pairs(limit=50, rhyme_length=rhyme_length)
        if not pairs:
            return self.generate_malaphor()

        left_index, right_index = random.choice(pairs)
        result = self._build_generation_result(self.proverbs[left_index], self.proverbs[right_index])
        if not self._save_history_entry(result):
            raise OSError("Could not save history.json. Check the destination and permissions.")
        return result

    def generate_with_constraints(
        self,
        min_words: Optional[int] = None,
        max_words: Optional[int] = None,
        min_syllables: Optional[int] = None,
        max_syllables: Optional[int] = None,
        category: Optional[str] = None,
        template_name: Optional[str] = None,
        max_attempts: int = 200,
    ) -> Dict[str, str]:
        """Generate a malaphor that satisfies the requested constraints."""
        template = self.get_generation_template(template_name) if template_name else None
        if len(self.proverbs) < 2:
            raise ValueError("Not enough proverbs to generate a malaphor")

        if category:
            category_lower = category.lower()
            filtered_indices = [
                i for i, proverb in enumerate(self.proverbs)
                if category_lower in [tag.lower() for tag in proverb.get("tags", [])]
            ]
            if len(filtered_indices) < 2:
                raise ValueError(f"Not enough phrases with tag '{category}' to generate malaphor")
        else:
            filtered_indices = list(range(len(self.proverbs)))

        for _ in range(max_attempts):
            left_index = random.choice(filtered_indices)
            right_index = random.choice(filtered_indices)
            if left_index == right_index:
                continue

            result = self._build_generation_result(
                self.proverbs[left_index],
                self.proverbs[right_index],
                category=category,
                template=template,
            )

            word_count = self.count_words(result["malaphor"])
            syllable_count = self.count_syllables(result["malaphor"])

            if min_words is not None and word_count < min_words:
                continue
            if max_words is not None and word_count > max_words:
                continue
            if min_syllables is not None and syllable_count < min_syllables:
                continue
            if max_syllables is not None and syllable_count > max_syllables:
                continue

            if not self._save_history_entry(result):
                raise OSError("Could not save history.json. Check the destination and permissions.")
            return result

        raise ValueError("Unable to satisfy the requested constraints")

    def _generation_templates_path(self) -> Path:
        return Path("generation_templates.json")

    def _load_generation_templates(self) -> List[Dict[str, str]]:
        default_templates = [
            {
                "name": "Default Blend",
                "pattern": "{source1_beginning} {source2_ending}",
                "description": "Blend the beginning of one phrase with the ending of another.",
            },
            {
                "name": "Reverse Blend",
                "pattern": "{source2_beginning} {source1_ending}",
                "description": "Swap the usual blend direction for a new variation.",
            },
            {
                "name": "Original Pairing",
                "pattern": "{source1_original} + {source2_original}",
                "description": "Show the source phrases together without blending.",
            },
        ]

        path = self._generation_templates_path()
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return [template for template in data if isinstance(template, dict) and template.get("name")]
        except (OSError, json.JSONDecodeError):
            pass
        return default_templates

    def _save_generation_templates(self) -> bool:
        return self._write_json(self._generation_templates_path(), self.generation_templates)

    def get_generation_templates(self) -> List[Dict[str, str]]:
        return list(self.generation_templates)

    def get_generation_template(self, name: str) -> Optional[Dict[str, str]]:
        for template in self.generation_templates:
            if template.get("name", "").lower() == (name or "").lower():
                return template
        return None

    def save_generation_template(self, name: str, pattern: str, description: str = "") -> bool:
        """Save or update a generation template."""
        if not name or not pattern:
            return False

        template = {
            "name": name,
            "pattern": pattern,
            "description": description,
        }

        existing_index = next((index for index, item in enumerate(self.generation_templates) if item.get("name", "").lower() == name.lower()), None)
        if existing_index is None:
            self.generation_templates.append(template)
        else:
            self.generation_templates[existing_index] = template
        return self._save_generation_templates()

    def delete_generation_template(self, name: str) -> bool:
        before = len(self.generation_templates)
        self.generation_templates = [template for template in self.generation_templates if template.get("name", "").lower() != (name or "").lower()]
        return len(self.generation_templates) != before and self._save_generation_templates()

    def generate_from_template(
        self,
        template_name: str,
        category: Optional[str] = None,
        source1_index: Optional[int] = None,
        source2_index: Optional[int] = None,
        language: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate a malaphor using a named template."""
        template = self.get_generation_template(template_name)
        if template is None:
            raise ValueError(f"Unknown generation template: {template_name}")

        if len(self.proverbs) < 2:
            raise ValueError("Not enough proverbs to generate a malaphor")

        filtered_indices = list(range(len(self.proverbs)))
        if language:
            language_key = str(language).lower()
            filtered_indices = [
                i for i, proverb in enumerate(self.proverbs)
                if str(proverb.get("language", "en")).lower() == language_key
            ]
        if category:
            category_lower = category.lower()
            filtered_indices = [
                i for i in filtered_indices
                if category_lower in [tag.lower() for tag in self.proverbs[i].get("tags", [])]
            ]
        if len(filtered_indices) < 2:
            raise ValueError(f"Not enough matching phrases to generate malaphor")

        left_index = source1_index if source1_index in filtered_indices else random.choice(filtered_indices)
        right_index = source2_index if source2_index in filtered_indices else random.choice(filtered_indices)

        attempts = 0
        while left_index == right_index and attempts < 20:
            right_index = random.choice(filtered_indices)
            attempts += 1

        result = self._build_generation_result(
            self.proverbs[left_index],
            self.proverbs[right_index],
            category=category,
            template=template,
        )
        if not self._save_history_entry(result):
            raise OSError("Could not save history.json. Check the destination and permissions.")
        return result

    def compare_malaphors(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a comparison payload for multiple malaphors."""
        comparison_rows = []
        for entry in entries:
            comparison_rows.append({
                "malaphor": entry.get("malaphor", ""),
                "source1": entry.get("source1", ""),
                "source2": entry.get("source2", ""),
                "rating": entry.get("rating", 0),
                "timestamp": entry.get("timestamp", ""),
            })

        return {
            "count": len(comparison_rows),
            "rows": comparison_rows,
        }

    def format_malaphor_with_metadata(
        self,
        malaphor: str,
        source1: str,
        source2: str,
        rating: Optional[float] = None,
        timestamp: Optional[str] = None,
        format_type: str = "plain",
    ) -> str:
        """Format a malaphor and metadata for sharing or copying."""
        payload = {
            "malaphor": malaphor,
            "source1": source1,
            "source2": source2,
            "rating": rating,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        }

        if format_type == "json":
            return json.dumps(payload, indent=2, ensure_ascii=False)
        if format_type == "markdown":
            rating_text = f"Rating: {rating}" if rating is not None else "Rating: n/a"
            return (
                f"**Malaphor:** {malaphor}\n\n"
                f"**Sources:**\n- {source1}\n- {source2}\n"
                f"**{rating_text}**\n"
                f"**Timestamp:** {payload['timestamp']}"
            )
        if format_type == "csv":
            return ",".join([
                json.dumps(payload["malaphor"]),
                json.dumps(payload["source1"]),
                json.dumps(payload["source2"]),
                json.dumps(str(payload["rating"]) if payload["rating"] is not None else ""),
                json.dumps(payload["timestamp"]),
            ])

        rating_text = f"\nRating: {rating}" if rating is not None else ""
        return (
            f"Malaphor: {malaphor}\n"
            f"From: {source1} + {source2}"
            f"{rating_text}\n"
            f"Timestamp: {payload['timestamp']}"
        )

    def _settings_profiles_path(self) -> Path:
        return Path("settings_profiles.json")

    def _load_settings_profiles(self) -> Dict[str, Dict[str, Any]]:
        try:
            path = self._settings_profiles_path()
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return {str(name): profile for name, profile in data.items() if isinstance(profile, dict)}
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def _save_settings_profiles(self, profiles: Dict[str, Dict[str, Any]]) -> bool:
        return self._write_json(self._settings_profiles_path(), profiles)

    def list_settings_profiles(self) -> List[str]:
        return sorted(self._load_settings_profiles().keys())

    def save_settings_profile(self, name: str, profile: Dict[str, Any]) -> bool:
        if not name:
            return False
        profiles = self._load_settings_profiles()
        profiles[name] = profile
        return self._save_settings_profiles(profiles)

    def load_settings_profile(self, name: str) -> Optional[Dict[str, Any]]:
        return self._load_settings_profiles().get(name)

    def delete_settings_profile(self, name: str) -> bool:
        profiles = self._load_settings_profiles()
        if name not in profiles:
            return False
        del profiles[name]
        return self._save_settings_profiles(profiles)

    def get_history_page(self, page: int = 1, page_size: int = 100, newest_first: bool = True) -> Dict[str, Any]:
        """Return a paginated slice of history for lazy loading."""
        page = max(1, page)
        page_size = max(1, page_size)
        items = list(reversed(self.history)) if newest_first else list(self.history)
        total_items = len(items)
        total_pages = max(1, (total_items + page_size - 1) // page_size)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "items": items[start_index:end_index],
        }

    def move_proverb(self, source_index: int, target_index: int) -> bool:
        """Reorder the proverb list."""
        if source_index < 0 or source_index >= len(self.proverbs):
            return False
        if target_index < 0:
            target_index = 0
        if target_index >= len(self.proverbs):
            target_index = len(self.proverbs) - 1

        updated = list(self.proverbs)
        updated.insert(target_index, updated.pop(source_index))
        if not self._write_json("malaphors.json", {"proverbs": updated}):
            return False
        self.proverbs = updated
        self._build_search_index()
        self.search.cache_clear()
        return True
