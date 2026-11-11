# Tasks: Comprehensive Improvements & Features Roadmap

Current project: `maliphors-inator`. See [rebranding and module mappings](../../../REBRANDING.md). Completed-task records below retain their historical paths.

**Feature:** improvements-roadmap\
**Version:** 1.1.0\
**Date:** 2026-10-01\
**Total Tasks:** 37\
**Estimated Total Time:** ~140 hours\
**Application status:** Pre-alpha; alpha readiness in progress as of 2026-10-01. See the [readiness gates](../../../ROADMAP.md#alpha-readiness) and [stage definitions](../../../alpha.md). Feature completion below does not establish application maturity; the full enhancement backlog is not an alpha prerequisite.

---

## PHASE 1: Foundation (Weeks 1-2)

### Task 1: UX-1 - Persist History to JSON

**Title:** Save generated malaphors to persistent history.json file

**Type:** UI/UX Enhancement (Priority: HIGH)  
**Estimate:** 2-3 hours  
**Category:** `category:ui-ux`, `impact:high`, `effort:medium`  
**Milestone:** `phase:foundation`

**Description:**
Currently, generated malaphors are displayed in the UI history but lost when the app closes. This task adds persistence by saving each generated malaphor to `history.json` immediately after generation, and auto-loading on app startup.

**Acceptance Criteria:**
- [x] Each generated malaphor saved to `history.json` with timestamp
- [x] History auto-loaded from file on app startup (if exists)
- [x] History dialog reflects newly persisted malaphors
- [x] File format: JSON array of {malaphor, source1, source2, timestamp}
- [x] Handles missing/corrupted history.json gracefully
- [x] All existing history tests pass

**Implementation Notes:**
- Add new method `_save_history_entry()` to MalaphorGenerator
- Add `_load_history_from_file()` to load on init
- Update UI history display to use persisted data
- Add error handling for file I/O
- Consider max history size (keep last N entries)

**Dependencies:** None

**Related Issues:** None

---

### Task 2: TEST-1 - Unit Tests for MalaphorGenerator

**Title:** Add comprehensive unit tests for core malaphor generation logic

**Type:** Testing & Reliability (Priority: HIGH)  
**Estimate:** 4-5 hours  
**Category:** `category:testing`, `impact:high`, `effort:complex`  
**Milestone:** `phase:foundation`

**Description:**
The MalaphorGenerator class lacks unit test coverage for critical methods: `smart_split_phrase()`, `generate_random()`, `search()`, and `import_malaphors()`. This task adds comprehensive test suite reaching 85%+ coverage.

**Acceptance Criteria:**
- [x] 15+ unit tests for MalaphorGenerator methods
- [x] Tests for `smart_split_phrase()` including edge cases (empty strings, no delimiters, multiple delimiters)
- [x] Tests for `generate_random()` (validity of output, consistency)
- [x] Tests for `search()` (case insensitivity, partial matches)
- [x] Tests for `import_malaphors()` (deduplication, merge logic)
- [x] Coverage report shows ≥85% for malaphor_logic.py
- [x] All tests pass, no skipped tests
- [x] Tests use pytest fixtures for reusable data

**Implementation Notes:**
- Create `test_malaphor_logic.py` (or extend if exists)
- Use unittest.mock for file I/O
- Create test fixtures for sample phrase data
- Test edge cases: empty input, unicode, special characters, large datasets
- Don't mock the actual generation algorithm; test its correctness

**Dependencies:** None

**Related Issues:** None

---

### Task 3: DATA-1 - Expand Phrase Database to 200+ Proverbs

**Title:** Curate and integrate 200+ proverbs, idioms, and phrases into malaphors.json

**Type:** Data & Quality (Priority: HIGH)  
**Estimate:** 4-6 hours  
**Category:** `category:data-quality`, `impact:high`, `effort:complex`  
**Milestone:** `phase:foundation`

**Description:**
Current database has only 3 phrases, severely limiting generation variety. This task curates 200+ well-known proverbs and idioms from public sources, validates structure, and merges into malaphors.json.

**Acceptance Criteria:**
- [x] Minimum 200+ phrases added to the default database
- [x] All phrases validated (JSON format, no syntax errors)
- [x] Each phrase has: original, beginning, ending fields
- [x] No duplicate phrases (by "original" field)
- [x] Phrases cover a diverse set of common proverb themes and idioms
- [x] malaphors.json structure remains backward compatible
- [x] App loads database without errors
- [x] Generation produces more varied results

**Implementation Notes:**
- Curated and inserted a larger built-in proverb dataset into `malaphors.json`
- Validated deduplication and JSON structure before finalizing the dataset
- Verified the generator still loads and produces valid malaphors with the expanded content

**Dependencies:** None

**Related Issues:** FEAT-1 (completed alongside the dataset normalization)

---

### Task 4: FEAT-1 - Migrate and Integrate newmalaphors.json Dataset

**Title:** Fix JSON structure in newmalaphors.json and merge into main database

**Type:** Generation Feature (Priority: HIGH)  
**Estimate:** 2-3 hours  
**Category:** `category:generation`, `impact:high`, `effort:medium`  
**Milestone:** `phase:foundation`

**Description:**
Repository contains `newmalaphors.json` with 100+ phrase beginnings/endings but incomplete structure. This task validates, fixes structure, and merges into main malaphors.json.

**Acceptance Criteria:**
- [x] The dataset was normalized to the standard `{original, beginning, ending}` schema
- [x] The main database was deduplicated and expanded in place
- [x] The app loads the merged dataset without startup errors
- [x] Generation continues to work with the expanded phrase collection
- [x] No data loss or corruption occurred during the file update

**Implementation Notes:**
- Consolidated the phrase database around a single valid JSON schema
- Deduplicated and validated the aggregated phrase set
- Confirmed the generator still executes successfully against the broadened dataset

**Dependencies:** None

**Related Issues:** DATA-1 (completed)

---

## PHASE 2: Polish & Exploration (Weeks 3-4)

### Task 5: UX-3 - Progress Dialogs for Bulk Operations

**Title:** Show progress bars/dialogs during long-running import/export operations

**Type:** UI/UX Enhancement (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:ui-ux`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
When importing large phrase datasets or exporting full history, UI becomes unresponsive. Add progress dialogs with cancel buttons for async operations.

**Acceptance Criteria:**
- [x] Progress dialog appears during import (modal, non-blocking)
- [x] Progress dialog shows during export operations
- [x] Cancel button stops operation gracefully
- [x] Progress bar increments accurately
- [x] Handles 1000+ item imports smoothly
- [x] Dialog disappears on completion
- [x] Error messages appear if operation fails

**Implementation Notes:**
- Create reusable `ProgressDialog` class in malaphor_ui.py
- Use threading to keep UI responsive
- Update progress via thread-safe queue
- Test with large imports (1000+ phrases)
- Ensure proper cleanup on cancel

**Dependencies:** None

**Related Issues:** None

---

### Task 6: FEAT-2 - Generate N Suggestions at Once

**Title:** Add "Generate 5 Malaphors" feature to show multiple suggestions

**Type:** Generation Feature (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:generation`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Currently, users can only generate one malaphor at a time. Add button to generate N suggestions (default 5) shown as a grid or list. User can select one to make it active.

**Acceptance Criteria:**
- [x] New button "Generate 5 Malaphors" in main UI
- [x] Generates 5 random malaphors using existing logic
- [x] Displays all 5 in a scrollable list or grid
- [x] Each suggestion shows: text, source phrases
- [x] User can click to select one (makes it active in main display)
- [x] User can regenerate to get new batch
- [x] Can configure N (5, 10, 20)
- [x] Performance acceptable (instant for 5)

**Implementation Notes:**
- Extend generate_random() to generate multiple without duplicates
- Create `GenerateSuggestionsDialog` for display
- Use ListBox or Frame grid for layout
- Add selection callback to copy selection to main display
- Test duplicate prevention in batch generation

**Dependencies:** FEAT-1 (better with larger database)

**Related Issues:** None

---

### Task 7: FEAT-7 - Phrase Similarity Detection

**Title:** Warn users when adding duplicate or highly similar phrases

**Type:** Generation Feature (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:generation`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
When manually adding a new phrase, detect if similar phrase already exists (edit distance < threshold). Warn user before adding to prevent duplicates.

**Acceptance Criteria:**
- [x] Similarity check runs before adding new phrase
- [x] Uses edit distance or fuzzy matching (difflib)
- [x] Shows warning dialog if similarity > 80%
- [x] User can override warning and add anyway
- [x] Similarity threshold configurable
- [x] Performance acceptable (< 1 second for 200+ phrases)
- [x] Unit tests for similarity algorithm

**Implementation Notes:**
- Use difflib.SequenceMatcher or levenshtein distance
- Check "original" field primarily
- Threshold: 80% similarity triggers warning
- Add config parameter for threshold
- Test with intentional duplicates

**Dependencies:** None

**Related Issues:** None

---

### Task 8: UX-7 - Rating/Star System for Favorites

**Title:** Add inline 1-5 star rating system for generated and favorite malaphors

**Type:** UI/UX Enhancement (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:ui-ux`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Users can mark malaphors as favorites, but no granular rating. Add 1-5 star rating inline, store rating with malaphor, sort favorites by rating.

**Acceptance Criteria:**
- [x] Star rating widget (1-5 stars) displayed with each malaphor in history
- [x] Clicking star updates rating and saves to file
- [x] Favorites dialog shows star rating
- [x] Ability to sort favorites by rating (highest first)
- [x] Rating persisted to JSON (rating field added to schema)
- [x] UI clearly shows current rating
- [x] Can remove rating (unrate)

**Implementation Notes:**
- Create custom `StarRating` widget in Tkinter
- Extend favorite entry schema: {malaphor, source1, source2, rating, timestamp}
- Update search/filter to use rating
- Test rating persistence across app restarts
- Consider showing average rating for similar malaphors

**Dependencies:** UX-1 (history persistence needed for ratings)

**Related Issues:** None

---

## PHASE 3: Advanced Features (Weeks 5-6)

### Task 9: FEAT-11 - Statistics Dashboard

**Title:** Create statistics view showing generation insights and trends

**Type:** New Capability (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:capabilities`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

**Description:**
Add new dashboard tab showing statistics: total phrases, most-used phrases, generation count, favorite count, top pairings, etc. Provides insight into user patterns.

**Acceptance Criteria:**
- [x] New "Statistics" tab in main UI
- [x] Shows: total phrases, total generated, total favorites
- [x] Shows: most frequently used phrases in generation
- [x] Shows: top 10 rated malaphors
- [x] Shows: generation trends over time (if history persisted)
- [x] Charts or tables display data clearly
- [x] Statistics update in real-time
- [x] Export statistics to CSV

**Implementation Notes:**
- Created `show_statistics_dashboard()` UI method in malaphor_ui.py
- Implemented statistics calculation methods in MalaphorGenerator
- Tabbed interface with Summary, Top Phrases, Top Tags, Sources, Top Rated tabs
- CSV export with statistics summary, top items, and distributions
- Methods: `get_statistics()`, `_calculate_phrase_usage()`, `_get_top_rated_malaphors()`, `_calculate_generation_trends()`, `_get_top_tags()`, `_get_source_distribution()`, `export_statistics_csv()`
- Provides real-time statistics updates using current history and ratings data

**Dependencies:** UX-1 (persisted history), UX-7 (ratings)

**Related Issues:** None

---

### Task 10: FEAT-10 - Export as Image (PNG/SVG)

**Title:** Generate stylized image of malaphor with source phrases (shareable)

**Type:** New Capability (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:capabilities`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`

**Description:**
Add button to export selected malaphor as PNG/SVG image with styling. Includes malaphor text, source phrases, rating. Shareable on social media.

**Acceptance Criteria:**
- [ ] "Export as Image" button in malaphor display
- [ ] Generates PNG with malaphor text, source phrases, styling
- [ ] Text is readable (font size, color, contrast)
- [ ] Includes optional caption/timestamp
- [ ] Saves to user-selected location
- [ ] SVG option for scalable graphics
- [ ] Template-based styling (editable templates)
- [ ] Performance: < 2 seconds per image

**Implementation Notes:**
- Use Pillow (PIL) for PNG generation
- Use svgwrite for SVG generation
- Create design templates (fonts, colors, backgrounds)
- Allow simple customization (color, layout)
- Test with various malaphor lengths

**Dependencies:** None

**Related Issues:** None

---

### Task 11: FEAT-4 - Category/Tag System for Phrases

**Title:** Tag phrases (animal, food, emotion, etc.) and generate by category

**Type:** Generation Feature (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:generation`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

**Description:**
Add tagging system to phrases. Users can tag phrases or set preset tags. Generate malaphors within category or across categories for more control.

**Acceptance Criteria:**
- [x] Phrase schema includes tags array: {original, beginning, ending, tags: []}
- [x] Tag editor UI in "Manage Phrases" dialog
- [x] Preset tags available (animal, food, emotion, wisdom, nature, etc.)
- [x] Custom tags allowed
- [x] Generate dropdown: "Any", "Within Category", "Specific Category"
- [x] Filters phrases by category during generation
- [x] Can filter/search by tag
- [x] UI shows tags in phrase display

**Implementation Notes:**
- Updated phrase schema: added tags field to all phrase objects
- Created `show_tag_management_dialog()` UI for tag editing and viewing
- Created `show_generate_by_category_dialog()` UI for category-filtered generation
- Preset tags: animal, food, emotion, wisdom, nature, weather, body, color, time, place, action, object, historical, modern, literary, proverbial, humorous
- Methods: `add_tags_to_phrase()`, `remove_tags_from_phrase()`, `get_phrase_tags()`, `get_all_tags()`, `get_phrases_by_tag()`, `generate_with_category()`, `migrate_schema_add_tags()`
- Schema migration: all 253 phrases migrated with tags field (initially empty)
- Tag-based filtering during generation with validation for minimum phrase count

**Dependencies:** None

**Related Issues:** DATA-1

---

### Task 12: UX-2 - Undo/Redo for Destructive Operations

**Title:** Add undo/redo stack for delete operations on phrases, history, favorites

**Type:** UI/UX Enhancement (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:ui-ux`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`

**Description:**
Users can accidentally delete phrases or favorites. Add undo/redo capability to recover from mistakes. Improves confidence in destructive operations.

**Acceptance Criteria:**
- [ ] Undo/Redo buttons in main UI (or menu)
- [ ] Works for: delete phrase, delete history item, delete favorite
- [ ] Undo button reverses last action
- [ ] Redo reverses undo
- [ ] Stack maintains state (history)
- [ ] Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Shift+Z (redo)
- [ ] Max undo depth configurable (default 20)
- [ ] Undo stack persists across operations

**Implementation Notes:**
- Implement Command pattern for operations
- Create `UndoRedoStack` class
- Each destructive operation creates Command object
- Test with sequence of operations
- Consider memory implications of stack size

**Dependencies:** None

**Related Issues:** None

---

## PHASE 4: Power User Features (Week 7+)

### Task 13: FEAT-16 - Malaphor Gallery/Showcase View

**Title:** Visual gallery of generated malaphors with cards (Pinterest-style)

**Type:** New Capability (Priority: MEDIUM)  
**Estimate:** 5-6 hours  
**Category:** `category:capabilities`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:poweruser`

**Description:**
Replace text-based history with visual gallery. Show malaphors as cards with title, rating stars, generated date. Browse, filter, sort favorites. Similar to Pinterest layout.

**Acceptance Criteria:**
- [ ] New "Gallery" view tab alongside text history
- [ ] Malaphors displayed as cards in grid layout
- [ ] Card shows: malaphor text, source phrases, rating, date
- [ ] Filter by: rating, date range, favorites only
- [ ] Sort by: date, rating, alphabetical
- [ ] Click card to view full details / edit rating
- [ ] Responsive layout (adapts to window size)
- [ ] Performance: smooth scrolling with 500+ cards

**Implementation Notes:**
- Create `GalleryPanel` with custom card widgets
- Use Canvas or Frame with scrollbar for layout
- Implement card click handlers
- Add filter/sort dropdowns
- Consider pagination for large datasets

**Dependencies:** UX-7 (ratings), UX-1 (history persistence)

**Related Issues:** None

---

### Task 14: FEAT-17 - API/CLI Interface

**Title:** Expose generation logic as REST API or command-line tool

**Type:** New Capability (Priority: MEDIUM)  
**Estimate:** 6-8 hours  
**Category:** `category:capabilities`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:poweruser`

**Description:**
Allow other applications to use the malaphor generator via API or CLI. Example: `malaphor --generate 5 --category animal` or `curl http://localhost:5000/generate`.

**Acceptance Criteria:**
- [ ] CLI tool accepts arguments: --generate, --category, --export-format
- [ ] CLI returns JSON or formatted output
- [ ] Optional REST API (Flask/FastAPI) for HTTP requests
- [ ] Endpoints: /generate, /search, /import, /export
- [ ] Authentication optional
- [ ] Documentation for API/CLI usage
- [ ] Tests for CLI and API
- [ ] Backward compatible (doesn't break UI)

**Implementation Notes:**
- Create cli.py for command-line interface
- Use argparse for CLI parsing
- Optional: Flask app for API (lightweight)
- Extract core logic to separate module (done)
- Document with examples
- Test with external tools

**Dependencies:** None

**Related Issues:** None

---

### Task 15: PERF-1 - Full-Text Search Index

**Title:** Build inverted index for fast phrase searching with 1000+ items

**Type:** Performance (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:performance`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:poweruser`

**Description:**
Current search is linear (loops through phrases). Build inverted index for O(1) lookups. Important as database grows to 1000+ phrases.

**Acceptance Criteria:**
- [ ] Index built on app startup
- [ ] Search performance < 100ms for any query
- [ ] Index size reasonable (< 5MB)
- [ ] Incremental updates when phrases added/deleted
- [ ] Handles unicode/special characters
- [ ] Case-insensitive searching maintained
- [ ] Fuzzy matching optional

**Implementation Notes:**
- Create `PhraseIndex` class
- Build inverted index on load
- Update on add/delete operations
- Consider using whoosh library or custom implementation
- Benchmark against linear search

**Dependencies:** None

**Related Issues:** None

---

### Task 16: UX-9 - Copy Generation Stats to Clipboard

**Title:** Copy formatted malaphor + source phrases to clipboard

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 1-2 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

### Task 17: UX-10 - Recent Searches Dropdown

**Title:** Remember and show last 10 searches in history/favorites search box

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

### Task 18: FEAT-14 - Scheduled Auto-Save

**Title:** Auto-save history/favorites every 5 minutes to prevent data loss

**Type:** New Capability (Priority: LOW)  
**Estimate:** 2 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:foundation`  
**Status:** ⏳ IN PROGRESS

### Task 19: UX-5 - Keyboard Shortcuts

**Title:** Add keyboard hotkeys for common operations

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

### Task 20: UX-6 - Dark Mode Toggle

**Title:** Add light/dark theme toggle with persistent preference

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 21: UX-8 - Drag-and-Drop Phrase Reordering

**Title:** Reorder phrases in manage dialog by drag-and-drop

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 22: FEAT-3 - Weighted Random Generation

**Title:** Generate based on phrase pair ratings (favor good combinations)

**Type:** Generation Feature (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:generation`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

### Task 23: FEAT-5 - Syllable/Word Count Constraints

**Title:** Filter generated malaphors by word/syllable count

**Type:** Generation Feature (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:generation`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 24: FEAT-6 - Rhyme Detection (Optional)

**Title:** Suggest phrase combinations that rhyme

**Type:** Generation Feature (Priority: LOW)  
**Estimate:** 5-6 hours  
**Category:** `category:generation`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 26: FEAT-9 - Custom Generation Templates

**Title:** Save and reuse generation templates/patterns

**Type:** New Capability (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:capabilities`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

### Task 27: FEAT-12 - Compare Malaphors Side-by-Side

**Title:** Select multiple malaphors and show comparison table

**Type:** New Capability (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 28: FEAT-13 - Share Malaphor with Metadata

**Title:** Copy malaphor as JSON, Markdown, or plaintext with metadata

**Type:** New Capability (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 29: FEAT-15 - Settings Profiles

**Title:** Save/load UI layouts and preferences as named profiles

**Type:** New Capability (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

### Task 33: TEST-2 - Integration Tests (End-to-End)

**Title:** Test full workflows: import → generate → favorite → export

**Type:** Testing & Reliability (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:testing`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

### Task 34: TEST-3 - Performance Tests

**Title:** Benchmark generation speed and search latency with large datasets

**Type:** Testing & Reliability (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:testing`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

**Description:**
Benchmark generation and search speed with representative large datasets and surface timing metrics for regression tracking.

**Acceptance Criteria:**
- [x] Search latency benchmark is exposed through `benchmark_search_latency()`
- [x] Timing summary includes average/min/max and result counts
- [x] Batch generation and cancellation code paths are exercised under test
- [x] Large-data reliability checks do not regress behavior

**Implementation Notes:**
- Added benchmark reporting for repeated search calls
- Verified cancellation-safe batch generation and history paging under pytest

### Task 35: TEST-4 - Error Handling Tests

**Title:** Test graceful failures (malformed JSON, permissions, etc.)

**Type:** Testing & Reliability (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:testing`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

**Description:**
Ensure malformed, missing, and partial data sources fail gracefully without crashing the app or export flow.

**Acceptance Criteria:**
- [x] Malformed `history.json` is handled gracefully
- [x] Incomplete history entries do not break export output
- [x] Missing files and empty collections start cleanly instead of crashing
- [x] Recovery paths are covered by regression tests

**Implementation Notes:**
- Hardened `history.json` loading and export behavior
- Added regression coverage for malformed inputs and partial records

### Task 36: PERF-2 - Async Generation with Cancellation

**Title:** Allow canceling long-running bulk operations

**Type:** Performance (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:performance`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

**Description:**
Allow batch generation to exit early when a cancellation event is set, without leaving partial state behind.

**Acceptance Criteria:**
- [x] `generate_batch_async()` exits immediately when cancellation is requested
- [x] `generate_batch()` honors the shared cancellation event
- [x] `cancel_generation()` sets the requested event reliably
- [x] Async flows do not continue once cancelled

**Implementation Notes:**
- Batch generation checks `cancel_event.is_set()` at each iteration
- Async wrapper returns early for cancelled work

### Task 37: PERF-3 - Lazy-Load History on Demand

**Title:** Load history in paginated chunks for large datasets

**Type:** Performance (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:performance`, `impact:low`, `effort:medium`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

**Description:**
Support paginated access to stored history so large datasets can be displayed without loading the full list at once.

**Acceptance Criteria:**
- [x] `get_history_page()` returns page metadata and items
- [x] Page size and page number are configurable
- [x] History can be loaded incrementally instead of all at once
- [x] UI paging logic uses the same data contract

**Implementation Notes:**
- Added paginated history access with counts and page metadata
- Verified by the lazy history paging regression tests

---

## QUICK WINS (1-2 Hours Each)

### Task 16: UX-9 - Copy Generation Stats to Clipboard

**Title:** Copy formatted malaphor + source phrases to clipboard

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 1-2 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Add button to copy current malaphor with sources in formatted way. Useful for content creators and writers.

**Acceptance Criteria:**
- [x] New button "Copy Stats" in malaphor display
- [x] Copies formatted text: "Malaphor: [text]\nFrom: [source1] + [source2]"
- [x] Optional formats: plain text, markdown, JSON
- [x] Confirms copy to user (popup or status)

**Implementation Notes:**
- Add method to format malaphor output
- Use pyperclip or tkinter clipboard
- Add format dropdown or menu

**Dependencies:** None

**Related Issues:** None

---

### Task 17: UX-10 - Recent Searches Dropdown

**Title:** Remember and show last 10 searches in history/favorites search box

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Store search queries in memory. Show dropdown in search box with recent searches for quick access.

**Acceptance Criteria:**
- [ ] Search history stored in-memory (last 10)
- [ ] Dropdown shows recent searches
- [ ] Click to rerun search
- [ ] Clear history option
- [ ] Persists across sessions (optional)

**Implementation Notes:**
- Maintain deque of last 10 searches
- Attach dropdown to search Entry widget
- Populate on focus or button click

**Dependencies:** None

**Related Issues:** None

---

### Task 18: FEAT-14 - Scheduled Auto-Save

**Title:** Auto-save history/favorites every 5 minutes to prevent data loss

**Type:** New Capability (Priority: LOW)  
**Estimate:** 2 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:foundation`  
**Status:** ✅ COMPLETE

**Description:**
Prevent data loss from unexpected crashes. Periodically save state even if user doesn't explicitly save.

**Acceptance Criteria:**
- [x] Auto-save timer runs every 5 minutes
- [x] Saves history.json and favorites.json
- [x] No UI freeze during save
- [x] Configurable interval
- [x] Can disable auto-save
- [x] Logs auto-save events

**Implementation Notes:**
- Use a background thread to run periodic saves without blocking the UI
- Start auto-save when the app initializes and stop it on shutdown
- Persist the current history and favorites to their JSON files

**Dependencies:** UX-1 (needs history persistence)

**Related Issues:** None

---

### Task 19: UX-5 - Keyboard Shortcuts

**Title:** Add keyboard hotkeys for common operations

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Power users want keyboard shortcuts. Add hotkeys for frequent actions.

**Acceptance Criteria:**
- [x] Ctrl+G: Generate malaphor
- [x] Ctrl+C: Copy to clipboard
- [x] Ctrl+H: Show history dialog
- [x] Ctrl+F: Focus search box
- [x] Ctrl+S: Save to favorites
- [x] Shortcuts displayed in menu/tooltip
- [x] Conflicts with OS shortcuts avoided

**Implementation Notes:**
- Bind keys in root window
- Add menu items with shortcut display
- Test on Windows/macOS/Linux

**Dependencies:** None

**Related Issues:** None

---

## REMAINING ITEMS (Lower Priority)

### Task 20: UX-6 - Dark Mode Toggle

**Title:** Add light/dark theme toggle with persistent preference

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`

**Estimate:** 3-4 hours

---

### Task 21: UX-8 - Drag-and-Drop Phrase Reordering

**Title:** Reorder phrases in manage dialog by drag-and-drop

**Type:** UI/UX Enhancement (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:ui-ux`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`

---

### Task 22: FEAT-3 - Weighted Random Generation

**Title:** Generate based on phrase pair ratings (favor good combinations)

**Type:** Generation Feature (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:generation`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Generate malaphors based on phrase pair ratings. Favor combinations that users liked before for better results over time.

**Acceptance Criteria:**
- [x] Track which phrase pairs produced rated malaphors
- [x] Generation algorithm weights pairs by average rating
- [x] Generate button accepts optional "smart" mode
- [x] Results skew toward higher-rated combinations
- [x] Performance acceptable
- [x] Graceful fallback if no ratings exist

---

### Task 23: FEAT-5 - Syllable/Word Count Constraints

**Title:** Filter generated malaphors by word/syllable count

**Type:** Generation Feature (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:generation`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`

---

### Task 24: FEAT-6 - Rhyme Detection (Optional)

**Title:** Suggest phrase combinations that rhyme

**Type:** Generation Feature (Priority: LOW)  
**Estimate:** 5-6 hours  
**Category:** `category:generation`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`

---

### Task 25: FEAT-8 - Batch Phrase Import with Auto-Splitting

**Title:** Import list of proverbs with auto-detection and splitting

**Type:** Generation Feature (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:generation`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:polish`  
**Status:** ✅ COMPLETE

**Description:**
Import list of proverbs and auto-detect split points. User reviews and corrects splits before committing. Faster bulk data entry.

**Acceptance Criteria:**
- [x] New "Batch Import" dialog
- [x] Accepts list of proverbs (one per line or paste)
- [x] Auto-detects split point for each using heuristics
- [x] Shows preview with proposed beginning/ending
- [x] User can edit splits before import
- [x] Deduplicates against existing database
- [x] Imports with confirmation

---

### Task 26: FEAT-9 - Custom Generation Templates

**Title:** Save and reuse generation templates/patterns

**Type:** New Capability (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:capabilities`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`

---

### Task 27: FEAT-12 - Compare Malaphors Side-by-Side

**Title:** Select multiple malaphors and show comparison table

**Type:** New Capability (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:poweruser`

---

### Task 28: FEAT-13 - Share Malaphor with Metadata

**Title:** Copy malaphor as JSON, Markdown, or plaintext with metadata

**Type:** New Capability (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:quick-win`  
**Milestone:** `phase:poweruser`

---

### Task 29: FEAT-15 - Settings Profiles

**Title:** Save/load UI layouts and preferences as named profiles

**Type:** New Capability (Priority: LOW)  
**Estimate:** 3-4 hours  
**Category:** `category:capabilities`, `impact:low`, `effort:complex`  
**Milestone:** `phase:poweruser`

---

### Task 30: DATA-2 - Add Source/Attribution to Phrases

**Title:** Tag each phrase with origin (Shakespeare, folk wisdom, etc.)

**Type:** Data & Quality (Priority: MEDIUM)  
**Estimate:** 2-3 hours  
**Category:** `category:data-quality`, `impact:medium`, `effort:medium`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

**Description:**
Add source/attribution field to phrase schema. Users can tag phrases with origin (Shakespeare, Folk Wisdom, Modern, Historical, etc.) for educational value.

**Acceptance Criteria:**
- [x] Phrase schema includes source field: `{original, beginning, ending, source}`
- [x] Preset sources available (Shakespeare, Folk Wisdom, Modern, Historical, etc.)
- [x] Custom sources allowed
- [x] Source displayed in history/dialogs
- [x] Can filter by source
- [x] Database updated with source info for existing phrases

**Implementation Notes:**
- Added methods: `set_phrase_source()`, `get_phrase_source()`, `get_all_sources()`, `get_phrases_by_source()`, `migrate_schema_add_source()`
- Created `show_source_management_dialog()` UI for source management
- Schema migration applied: all 253 phrases now have source attribution
- Preset sources: Shakespeare, Folk Wisdom, Modern, Historical, American Idiom, etc.

---

### Task 31: DATA-3 - Multi-Language Support

**Title:** Support English, Spanish, French, German phrases

**Type:** Data & Quality (Priority: MEDIUM)  
**Estimate:** 6-8 hours  
**Category:** `category:data-quality`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:poweruser`  
**Status:** ✅ COMPLETE

**Description:**
Support language-tagged phrase metadata and language-aware generation filtering in the core logic, CLI, and main Tkinter UI.

**Acceptance Criteria:**
- [x] Phrase schema includes language metadata
- [x] Generator accepts `language` filtering for phrase selection
- [x] CLI supports `--language` generation requests
- [x] UI has a language selector affecting generation
- [x] Existing generation remains compatible when language is unset or set to `all`

**Implementation Notes:**
- Added `language` field handling in `MalaphorGenerator.generate_malaphor()` and `generate_multiple()`
- CLI already accepts `--language` and passes it through to the generator
- Main Tkinter window includes a language combobox with `all`, `en`, `es`, `fr`, and `de` options
- Validation coverage added for language-aware generation and UI pass-through

---

### Task 32: DATA-4 - Validate & Deduplicate Database

**Title:** Audit database for duplicates/similar phrases and resolve

**Type:** Data & Quality (Priority: MEDIUM)  
**Estimate:** 2-3 hours  
**Category:** `category:data-quality`, `impact:medium`, `effort:medium`  
**Milestone:** `phase:advanced`  
**Status:** ✅ COMPLETE

**Description:**
Audit database for exact and similar duplicates. Provide tools to identify and resolve conflicts. Improve data quality.

**Acceptance Criteria:**
- [x] Audit script identifies exact duplicates
- [x] Identifies similar phrases (> 80% match using difflib)
- [x] Shows conflicts to user with resolution options
- [x] User can merge, delete, or keep both
- [x] Generates report of changes
- [x] Database integrity validated after cleanup
- [x] Full cleanup workflow available

**Implementation Notes:**
- Added methods: `find_exact_duplicates()`, `find_similar_phrases()`, `validate_schema()`, `deduplicate_database()`, `clean_database()`
- Created `show_database_validation_dialog()` UI for validation and cleanup
- Uses difflib.SequenceMatcher for similarity detection (configurable threshold)
- Full validation report includes: schema compliance, exact duplicates, similar phrases, missing fields
- Cleanup report tracks: items removed, indices, changes made
- All 253 phrases validated: 253 valid, 0 invalid
- Similar phrase groups identified: 2 groups at 85%+ similarity

---

### Task 33: TEST-2 - Integration Tests (End-to-End)

**Title:** Test full workflows: import → generate → favorite → export

**Type:** Testing & Reliability (Priority: MEDIUM)  
**Estimate:** 4-5 hours  
**Category:** `category:testing`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`

---

### Task 34: TEST-3 - Performance Tests

**Title:** Benchmark generation speed and search latency with large datasets

**Type:** Testing & Reliability (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:testing`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`

---

### Task 35: TEST-4 - Error Handling Tests

**Title:** Test graceful failures (malformed JSON, permissions, etc.)

**Type:** Testing & Reliability (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:testing`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:advanced`

---

### Task 36: PERF-2 - Async Generation with Cancellation

**Title:** Allow canceling long-running bulk operations

**Type:** Performance (Priority: MEDIUM)  
**Estimate:** 3-4 hours  
**Category:** `category:performance`, `impact:medium`, `effort:complex`  
**Milestone:** `phase:poweruser`

---

### Task 37: PERF-3 - Lazy-Load History on Demand

**Title:** Load history in paginated chunks for large datasets

**Type:** Performance (Priority: LOW)  
**Estimate:** 2-3 hours  
**Category:** `category:performance`, `impact:low`, `effort:medium`  
**Milestone:** `phase:poweruser`

---

## Summary

**Total Tasks:** 37  
**Total Estimated Time:** ~140 hours  
**Distribution:**
- Phase 1 (Foundation): 4 tasks, ~14 hours
- Phase 2 (Polish): 9 tasks, ~31 hours
- Phase 3 (Advanced): 5 tasks, ~22 hours
- Phase 4 (Power User): 19 tasks, ~73 hours

**Quick Wins (1-2 hours):** 5 tasks
**Medium (3-5 hours):** 21 tasks
**Complex (6+ hours):** 11 tasks

## Alpha technical checkpoint

On 2026-10-01, the reviewed snapshot passed 214 tests, dependency checks, the real-dialog walkthrough, and backup recovery. Architecture review and initial Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17 validation are complete. The application remains pre-alpha pending human usability review and independent developer handoff. See the [current gates](../../../ROADMAP.md#alpha-readiness) and [validation record](../../../RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).
