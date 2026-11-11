"""Cancellable, side-effect-free import and cleanup planning."""
from copy import deepcopy
import json
from pathlib import Path


class OperationCancelled(Exception):
    pass


def checkpoint(cancel=None, progress=None, done=0, total=0):
    if cancel is not None and cancel.is_set():
        raise OperationCancelled('Cancelled before saving; data is unchanged')
    if progress:
        progress(done, total)


def phrase_error(phrase):
    if not isinstance(phrase, dict):
        return 'Expected a phrase object'
    for key in ('original', 'beginning', 'ending'):
        if not isinstance(phrase.get(key), str) or not phrase[key].strip():
            return f'{key} must be non-empty text'
    for key in ('language', 'source'):
        if key in phrase and not isinstance(phrase[key], str):
            return f'{key} must be text'
    if 'tags' in phrase and (not isinstance(phrase['tags'], list) or any(not isinstance(t, str) for t in phrase['tags'])):
        return 'tags must be a list of text values'
    return None


def classify_rows(rows, existing):
    seen = {p['original'] for p in existing}
    result = []
    for row in rows:
        item = deepcopy(row)
        error = phrase_error(item['phrase'])
        item['error'] = error
        if error:
            item['status'] = 'invalid'
        elif item['phrase']['original'] in seen:
            item['status'] = 'duplicate'
        else:
            item['status'] = 'new'
            if item.get('include', True):
                seen.add(item['phrase']['original'])
        result.append(item)
    return result


def preview_import(path, existing, cancel=None, progress=None):
    path = Path(path)
    if path.stat().st_size > 25 * 1024 * 1024:
        raise ValueError('Import exceeds the 25 MB limit; split it into smaller files')
    checkpoint(cancel)
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or not isinstance(value.get('proverbs'), list):
        raise ValueError('Expected an object with a proverbs list')
    rows = []
    total = len(value['proverbs'])
    for index, phrase in enumerate(value['proverbs']):
        checkpoint(cancel, progress, index, total)
        rows.append({'id': index, 'phrase': phrase, 'include': True})
    checkpoint(cancel, progress, total, total)
    return classify_rows(rows, existing)


def import_additions(rows, existing, cancel=None, progress=None):
    classified = classify_rows(rows, existing)
    additions = []
    for index, row in enumerate(classified):
        checkpoint(cancel, progress, index, len(classified))
        if not row.get('include', True):
            continue
        if row['error']:
            raise ValueError(f"Row {row['id']+1}: {row['error']}. Correct it or exclude it.")
        if row['status'] == 'new':
            additions.append(deepcopy(row['phrase']))
    checkpoint(cancel, progress, len(classified), len(classified))
    return additions


def plan_cleanup(phrases, remove_invalid=True, remove_duplicates=True, cancel=None, progress=None):
    seen = set()
    kept, removed = [], []
    for index, phrase in enumerate(phrases):
        checkpoint(cancel, progress, index, len(phrases))
        invalid = phrase_error(phrase)
        key = str(phrase.get('original', '')).strip().casefold() if isinstance(phrase, dict) else ''
        if (remove_invalid and invalid) or (remove_duplicates and key in seen):
            removed.append(index)
        else:
            kept.append(deepcopy(phrase))
            seen.add(key)
    checkpoint(cancel, progress, len(phrases), len(phrases))
    return {'phrases': kept, 'removed': removed}
