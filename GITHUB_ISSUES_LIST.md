# GitHub Issues List - maliphors-inator Improvements Roadmap

Current naming and module mappings: [REBRANDING.md](REBRANDING.md). Completed-task descriptions retain their original names.

**Total Issues:** 37
**Repository:** maliphors-inator
**Created:** 2026-09-07
**Updated:** 2026-10-01
**Version:** 1.1.0
**Application status:** Pre-alpha; alpha readiness in progress as of 2026-10-01. See the [readiness gates](ROADMAP.md#alpha-readiness) and [stage definitions](alpha.md). Feature completion below does not establish application maturity; the full enhancement backlog is not an alpha prerequisite.
**Phase 1 Status:** ✅ COMPLETE (2026-09-08)
**Phase 2 Status:** ✅ COMPLETE (2026-09-10)

---

## 📋 HOW TO USE THIS LIST

These 37 issues are ready to be added to GitHub. You can:

**Option 1: Manual Creation in GitHub UI**
- Go to your repository's Issues tab
- Click "New issue"
- Copy the issue template below and paste into the title/description
- Apply labels from the list provided

**Option 2: Bulk Import (if using GitHub CLI)**
```bash
# Install GitHub CLI: https://cli.github.com
# Login: gh auth login
# Then create issues programmatically (see script below)
```

**Option 3: API Import**
Use the GitHub API to create issues with labels and milestone assignments.

---

## 🏷️ LABEL SCHEME

**Categories (6):**
- `category:ui-ux` - UI/UX improvements
- `category:generation` - Phrase generation & logic
- `category:capabilities` - New application features
- `category:data-quality` - Data management & quality
- `category:testing` - Testing & reliability
- `category:performance` - Performance optimization

**Impact (3):**
- `impact:high` - Critical for project success
- `impact:medium` - Meaningful improvement
- `impact:low` - Nice-to-have, polish

**Effort (3):**
- `effort:quick-win` - 1-2 hours
- `effort:medium` - 3-5 hours
- `effort:complex` - 6+ hours

**Priority/Phase (4 Milestones):**
- `phase:foundation` - Phase 1 (Weeks 1-2)
- `phase:polish` - Phase 2 (Weeks 3-4)
- `phase:advanced` - Phase 3 (Weeks 5-6)
- `phase:poweruser` - Phase 4 (Week 7+)

---

# PHASE 1: FOUNDATION (Weeks 1-2)

## Issue #1: UX-1 - Persist History to JSON

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:high`, `effort:medium`, `phase:foundation`
**Milestone:** Phase 1: Foundation
**Estimate:** 2-3 hours

### Description

Currently, generated malaphors are displayed in the UI history but lost when the app closes. This task adds persistence by saving each generated malaphor to `history.json` immediately after generation, and auto-loading on app startup.

### Acceptance Criteria

- [x] Each generated malaphor saved to `history.json` with timestamp
- [x] History auto-loaded from file on app startup (if exists)
- [x] History dialog reflects newly persisted malaphors
- [x] File format: JSON array of `{malaphor, source1, source2, timestamp}`
- [x] Handles missing/corrupted history.json gracefully
- [x] All existing history tests pass

### Implementation Notes

- Add new method `_save_history_entry()` to MalaphorGenerator
- Add `_load_history_from_file()` to load on init
- Update UI history display to use persisted data
- Add error handling for file I/O
- Consider max history size (keep last N entries)

### Dependencies

None

### Related Issues

None

---

## Issue #2: TEST-1 - Unit Tests for MalaphorGenerator

**Type:** Testing & Reliability
**Labels:** `category:testing`, `impact:high`, `effort:complex`, `phase:foundation`
**Milestone:** Phase 1: Foundation
**Estimate:** 4-5 hours

### Description

The MalaphorGenerator class lacks unit test coverage for critical methods: `smart_split_phrase()`, `generate_random()`, `search()`, and `import_malaphors()`. This task adds comprehensive test suite reaching 85%+ coverage.

### Acceptance Criteria

- [x] 15+ unit tests for MalaphorGenerator methods
- [x] Tests for `smart_split_phrase()` including edge cases
- [x] Tests for `generate_random()` (validity, consistency)
- [x] Tests for `search()` (case insensitivity, partial matches)
- [x] Tests for `import_malaphors()` (deduplication, merge logic)
- [x] Coverage report shows ≥85% for malaphor_logic.py
- [x] All tests pass, no skipped tests
- [x] Tests use pytest fixtures for reusable data

### Implementation Notes

- Create `test_malaphor_logic.py` (or extend if exists)
- Use unittest.mock for file I/O
- Create test fixtures for sample phrase data
- Test edge cases: empty input, unicode, special characters, large datasets
- Don't mock the actual generation algorithm; test its correctness

### Dependencies

None

### Related Issues

None

---

## Issue #3: DATA-1 - Expand Phrase Database to 200+ Proverbs

**Type:** Data & Quality
**Labels:** `category:data-quality`, `impact:high`, `effort:complex`, `phase:foundation`
**Milestone:** Phase 1: Foundation
**Estimate:** 4-6 hours

### Description

Current database has only 3 phrases, severely limiting generation variety. This task curates 200+ well-known proverbs and idioms from public sources, validates structure, and merges into malaphors.json.

### Acceptance Criteria

- [x] Minimum 200+ phrases added to the default database
- [x] All phrases validated (JSON format, no syntax errors)
- [x] Each phrase has: original, beginning, ending fields
- [x] No duplicate phrases (by "original" field)
- [x] Phrases cover a broad mix of common proverb themes and idioms
- [x] Dataset is loaded and validated without app startup issues
- [x] malaphors.json structure remains backward compatible
- [x] Generation produces more varied results

### Implementation Notes

- Curated a larger built-in dataset in `malaphors.json`
- Validated JSON structure and deduplication before finalization
- Confirmed the generator still loads and runs against the expanded dataset
- Updated documentation to reflect the new dataset size and status

### Dependencies

None

### Related Issues

#4 (FEAT-1 was completed as part of the dataset consolidation)

---

## Issue #4: FEAT-1 - Migrate and Integrate newmalaphors.json Dataset

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:high`, `effort:medium`, `phase:foundation`
**Milestone:** Phase 1: Foundation
**Estimate:** 2-3 hours

### Description

Repository contains `newmalaphors.json` with 100+ phrase beginnings/endings but incomplete structure. This task validates, fixes structure, and merges into main malaphors.json.

### Acceptance Criteria

- [x] The expanded dataset was normalized to the standard `{original, beginning, ending}` schema
- [x] The main JSON dataset was deduplicated and expanded in place
- [x] The app loads the merged dataset without startup errors
- [x] Generation continues to work with the larger phrase collection
- [x] No data loss or corruption occurred during the migration update

### Implementation Notes

- Consolidated the phrase database around a single valid JSON schema
- Deduplicated the dataset before finalizing the build
- Verified the generator still works with the broader data set
- Kept the repository in a backward-compatible shape for the app

### Dependencies

None

### Related Issues

#3 (DATA-1)

---

# PHASE 2: POLISH & EXPLORATION (Weeks 3-4)

## Issue #5: UX-3 - Progress Dialogs for Bulk Operations

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:medium`, `effort:complex`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

When importing large phrase datasets or exporting full history, UI becomes unresponsive. Add progress dialogs with cancel buttons for async operations.

### Acceptance Criteria

- [x] Progress dialog appears during import (modal, non-blocking)
- [x] Progress dialog shows during export operations
- [x] Cancel button stops operation gracefully
- [x] Progress bar increments accurately
- [x] Handles 1000+ item imports smoothly
- [x] Dialog disappears on completion
- [x] Error messages appear if operation fails

### Implementation Notes

- Create reusable `ProgressDialog` class in malaphor_ui.py
- Use threading to keep UI responsive
- Update progress via thread-safe queue
- Test with large imports (1000+ phrases)
- Ensure proper cleanup on cancel

### Dependencies

None

### Related Issues

None

---

## Issue #6: FEAT-2 - Generate N Suggestions at Once

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:medium`, `effort:complex`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Currently, users can only generate one malaphor at a time. Add button to generate N suggestions (default 5) shown as a grid or list. User can select one to make it active.

### Acceptance Criteria

- [x] New button "Generate 5 Malaphors" in main UI
- [x] Generates 5 random malaphors using existing logic
- [x] Displays all 5 in a scrollable list or grid
- [x] Each suggestion shows: text, source phrases
- [x] User can click to select one (makes it active in main display)
- [x] User can regenerate to get new batch
- [x] Can configure N (5, 10, 20)
- [x] Performance acceptable (instant for 5)

### Implementation Notes

- Extend `generate_random()` to generate multiple without duplicates
- Create `GenerateSuggestionsDialog` for display
- Use ListBox or Frame grid for layout
- Add selection callback to copy selection to main display
- Test duplicate prevention in batch generation

### Dependencies

#4 (better with larger database)

### Related Issues

None

---

## Issue #7: FEAT-7 - Phrase Similarity Detection

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:medium`, `effort:complex`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 4-5 hours
**Status:** ✅ COMPLETE

### Description

When manually adding a new phrase, detect if similar phrase already exists (edit distance < threshold). Warn user before adding to prevent duplicates.

### Acceptance Criteria

- [x] Similarity check runs before adding new phrase
- [x] Uses edit distance or fuzzy matching (difflib)
- [x] Shows warning dialog if similarity > 80%
- [x] User can override warning and add anyway
- [x] Similarity threshold configurable
- [x] Performance acceptable (< 1 second for 200+ phrases)
- [x] Unit tests for similarity algorithm

### Implementation Notes

- Use difflib.SequenceMatcher or levenshtein distance
- Check "original" field primarily
- Threshold: 80% similarity triggers warning
- Add config parameter for threshold
- Test with intentional duplicates

### Dependencies

None

### Related Issues

None

---

## Issue #8: UX-7 - Rating/Star System for Favorites

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:medium`, `effort:complex`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Users can mark malaphors as favorites, but no granular rating. Add 1-5 star rating inline, store rating with malaphor, sort favorites by rating.

### Acceptance Criteria

- [x] Star rating widget (1-5 stars) displayed with each malaphor in history
- [x] Clicking star updates rating and saves to file
- [x] Favorites dialog shows star rating
- [x] Ability to sort favorites by rating (highest first)
- [x] Rating persisted to JSON (rating field added to schema)
- [x] UI clearly shows current rating
- [x] Can remove rating (unrate)

### Implementation Notes

- Create custom `StarRating` widget in Tkinter
- Extend favorite entry schema: `{malaphor, source1, source2, rating, timestamp}`
- Update search/filter to use rating
- Test rating persistence across app restarts
- Consider showing average rating for similar malaphors

### Dependencies

#1 (UX-1: history persistence)

### Related Issues

None

---

## Issue #9: FEAT-3 - Weighted Random Generation

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:medium`, `effort:medium`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Generate malaphors based on phrase pair ratings. Favor combinations that users liked before for better results over time.

### Acceptance Criteria

- [x] Track which phrase pairs produced rated malaphors
- [x] Generation algorithm weights pairs by average rating
- [x] Generate button accepts optional "smart" mode
- [x] Results skew toward higher-rated combinations
- [x] Performance acceptable
- [x] Graceful fallback if no ratings exist

### Implementation Notes

- Build phrase pair rating database (initially all equal weight)
- Modify `generate_random()` to accept weighted mode
- Use rating data from favorites
- Test with series of generations and ratings

### Dependencies

#8 (UX-7: ratings)

### Related Issues

None

---

## Issue #10: FEAT-8 - Batch Phrase Import with Auto-Splitting

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:medium`, `effort:complex`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Import list of proverbs and auto-detect split points. User reviews and corrects splits before committing. Faster bulk data entry.

### Acceptance Criteria

- [x] New "Batch Import" dialog
- [x] Accepts list of proverbs (one per line or paste)
- [x] Auto-detects split point for each using heuristics
- [x] Shows preview with proposed beginning/ending
- [x] User can edit splits before import
- [x] Deduplicates against existing database
- [x] Imports with confirmation

### Implementation Notes

- Create `BatchImportDialog` class
- Use existing `smart_split_phrase()` logic
- Build UI with editable table of splits
- Test with known proverbs

### Dependencies

None

### Related Issues

None

---

## Issue #11: UX-5 - Keyboard Shortcuts (QUICK WIN)

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:low`, `effort:quick-win`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 2-3 hours
**Status:** ✅ COMPLETE

### Description

Power users want keyboard shortcuts. Add hotkeys for frequent actions.

### Acceptance Criteria

- [x] Ctrl+G: Generate malaphor
- [x] Ctrl+C: Copy to clipboard
- [x] Ctrl+H: Show history dialog
- [x] Ctrl+F: Focus search box
- [x] Ctrl+S: Save to favorites
- [x] Shortcuts displayed in menu/tooltip
- [x] Conflicts with OS shortcuts avoided

### Implementation Notes

- Bind keys in root window
- Add menu items with shortcut display
- Test on Windows/macOS/Linux

### Dependencies

None

### Related Issues

None

---

## Issue #12: UX-9 - Copy Generation Stats to Clipboard (QUICK WIN)

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:low`, `effort:quick-win`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 1-2 hours
**Status:** ✅ COMPLETE

### Description

Add button to copy malaphor with source phrases in formatted way. Useful for content creators and writers.

### Acceptance Criteria

- [x] New button "Copy Stats" in malaphor display
- [x] Copies formatted text: "Malaphor: [text]\nFrom: [source1] + [source2]"
- [x] Optional formats: plain text, markdown, JSON
- [x] Confirms copy to user (popup or status)

### Implementation Notes

- Add method to format malaphor output
- Use pyperclip or tkinter clipboard
- Add format dropdown or menu

### Dependencies

None

### Related Issues

None

---

## Issue #13: UX-10 - Recent Searches Dropdown (QUICK WIN)

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:low`, `effort:quick-win`, `phase:polish`
**Milestone:** Phase 2: Polish
**Estimate:** 2-3 hours
**Status:** ✅ COMPLETE

### Description

Remember and show last 10 searches in history/favorites search box for quick access.

### Acceptance Criteria

- [x] Search history stored in-memory (last 10)
- [x] Dropdown shows recent searches
- [x] Click to rerun search
- [x] Clear history option

### Implementation Notes

- Maintain deque of last 10 searches
- Attach dropdown to search Entry widget
- Populate on focus or button click

### Dependencies

None

### Related Issues

None

---

# PHASE 3: ADVANCED FEATURES (Weeks 5-6)

## Issue #14: FEAT-11 - Statistics Dashboard

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Add new dashboard tab showing statistics: total phrases, most-used phrases, generation count, favorite count, top pairings, etc. Provides insight into user patterns.

### Acceptance Criteria

- [x] New "Statistics" tab in main UI
- [x] Shows: total phrases, total generated, total favorites
- [x] Shows: most frequently used phrases in generation
- [x] Shows: top 10 rated malaphors
- [x] Shows: generation trends over time (if history persisted)
- [x] Charts or tables display data clearly
- [x] Statistics update in real-time
- [x] Export statistics to CSV

### Implementation Notes

- Created `show_statistics_dashboard()` UI method with tabbed interface
- Implemented 7 statistics calculation methods in MalaphorGenerator
- Tabs: Summary Statistics, Top Phrases, Top Tags, Sources Distribution, Top Rated Malaphors
- CSV export with comprehensive statistics report
- Real-time updates using current history and phrase pair ratings
- Methods implemented: `get_statistics()`, `_calculate_phrase_usage()`, `_get_top_rated_malaphors()`, `_calculate_generation_trends()`, `_get_top_tags()`, `_get_source_distribution()`, `_calculate_average_rating()`, `export_statistics_csv()`

### Dependencies

#1 (UX-1: persisted history), #8 (UX-7: ratings)

### Related Issues

None

---

## Issue #15: FEAT-10 - Export as Image (PNG/SVG)

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 4-5 hours
**Status:** ✅ COMPLETE

### Description

Add button to export selected malaphor as PNG/SVG image with styling. Includes malaphor text, source phrases, rating. Shareable on social media.

### Acceptance Criteria

- [ ] "Export as Image" button in malaphor display
- [ ] Generates PNG with malaphor text, source phrases, styling
- [ ] Text is readable (font size, color, contrast)
- [ ] Includes optional caption/timestamp
- [ ] Saves to user-selected location
- [ ] SVG option for scalable graphics
- [ ] Template-based styling (editable templates)
- [ ] Performance: < 2 seconds per image

### Implementation Notes

- Use Pillow (PIL) for PNG generation
- Use svgwrite for SVG generation
- Create design templates (fonts, colors, backgrounds)
- Allow simple customization (color, layout)
- Test with various malaphor lengths

### Dependencies

None

### Related Issues

None

---

## Issue #16: FEAT-4 - Category/Tag System for Phrases

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 4-5 hours
**Status:** ✅ COMPLETE

### Description

Add tagging system to phrases. Users can tag phrases or set preset tags. Generate malaphors within category or across categories for more control.

### Acceptance Criteria

- [x] Phrase schema includes tags array: `{original, beginning, ending, tags: []}`
- [x] Tag editor UI in "Manage Phrases" dialog
- [x] Preset tags available (animal, food, emotion, wisdom, nature, etc.)
- [x] Custom tags allowed
- [x] Generate dropdown: "Any", "Within Category", "Specific Category"
- [x] Filters phrases by category during generation
- [x] Can filter/search by tag
- [x] UI shows tags in phrase display

### Implementation Notes

- Updated phrase schema: added tags field to all 253 phrases
- Created `show_tag_management_dialog()` UI for viewing and editing tags with filter dropdown
- Created `show_generate_by_category_dialog()` UI for category-constrained generation
- Preset tags: animal, food, emotion, wisdom, nature, weather, body, color, time, place, action, object, historical, modern, literary, proverbial, humorous, and more
- Methods: `add_tags_to_phrase()`, `remove_tags_from_phrase()`, `get_phrase_tags()`, `get_all_tags()`, `get_phrases_by_tag()`, `generate_with_category()`, `migrate_schema_add_tags()`
- Schema migration: all 253 phrases now have tags field (initially empty, ready for user tagging)
- Tag filtering validates minimum phrase count for generation (requires at least 2 phrases with tag)

### Dependencies

None

### Related Issues

#3 (DATA-1: expanded database used for tagging)

---

## Issue #17: UX-2 - Undo/Redo for Destructive Operations

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 4-5 hours
**Status:** ✅ COMPLETE

### Description

Users can accidentally delete phrases or favorites. Add undo/redo capability to recover from mistakes. Improves confidence in destructive operations.

### Acceptance Criteria

- [ ] Undo/Redo buttons in main UI (or menu)
- [ ] Works for: delete phrase, delete history item, delete favorite
- [ ] Undo button reverses last action
- [ ] Redo reverses undo
- [ ] Stack maintains state (history)
- [ ] Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Shift+Z (redo)
- [ ] Max undo depth configurable (default 20)
- [ ] Undo stack persists across operations

### Implementation Notes

- Implement Command pattern for operations
- Create `UndoRedoStack` class
- Each destructive operation creates Command object
- Test with sequence of operations
- Consider memory implications of stack size

### Dependencies

None

### Related Issues

None

---

## Issue #18: DATA-2 - Add Source/Attribution to Phrases

**Type:** Data & Quality
**Labels:** `category:data-quality`, `impact:medium`, `effort:medium`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 2-3 hours
**Status:** ✅ COMPLETE

### Description

Tag each phrase with origin (e.g., "Shakespeare", "Folk wisdom", "Modern"). Show in UI. Educational value.

### Acceptance Criteria

- [x] Phrase schema includes source field: `{original, beginning, ending, source}`
- [x] Preset sources available (Shakespeare, Folk Wisdom, Modern, Historical, etc.)
- [x] Custom sources allowed
- [x] Source displayed in history/dialogs
- [x] Can filter by source
- [x] Database updated with source info for existing phrases

### Implementation Notes

- Update schema and database
- Create source selector in phrase editor
- Display source in UI (tooltip or label)
- Update import logic to preserve source info

### Dependencies

None

### Related Issues

None

---

## Issue #19: DATA-4 - Validate & Deduplicate Database

**Type:** Data & Quality
**Labels:** `category:data-quality`, `impact:medium`, `effort:medium`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 2-3 hours
**Status:** ✅ COMPLETE

### Description

Audit database for duplicates/similar phrases and resolve conflicts. Improve data quality.

### Acceptance Criteria

- [x] Audit script identifies exact duplicates
- [x] Identifies similar phrases (> 80% match)
- [x] Shows conflicts to user with resolution options
- [x] User can merge, delete, or keep both
- [x] Generates report of changes
- [x] Database integrity validated after cleanup

### Implementation Notes

- Create audit tool (could be CLI or UI)
- Use similarity detection from #7
- Build conflict resolution UI
- Log all changes

### Dependencies

#7 (FEAT-7: similarity detection)

### Related Issues

None

---

## Issue #20: TEST-2 - Integration Tests (End-to-End)

**Type:** Testing & Reliability
**Labels:** `category:testing`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 4-5 hours

### Description

Test full workflows: import → generate → favorite → export. Catch UI/logic mismatches.

### Acceptance Criteria

- [ ] Test import workflow (add phrases → verify in UI)
- [ ] Test generate workflow (generate → copy → view)
- [ ] Test favorite workflow (favorite → search → sort by rating)
- [ ] Test export workflows (JSON, text formats)
- [ ] Test history persistence across restarts
- [ ] All scenarios pass
- [ ] Coverage for error conditions

### Implementation Notes

- Create integration test module
- Test fixtures with sample data
- Mock file I/O where needed
- Simulate user actions

### Dependencies

#1 (UX-1: history persistence)

### Related Issues

None

---

# PHASE 4: POWER USER FEATURES (Week 7+)

## Issue #21: FEAT-16 - Malaphor Gallery/Showcase View

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:medium`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 5-6 hours
**Status:** ✅ COMPLETE

### Description

Replace text-based history with visual gallery. Show malaphors as cards with title, rating stars, generated date. Browse, filter, sort favorites.

### Acceptance Criteria

- [ ] New "Gallery" view tab alongside text history
- [ ] Malaphors displayed as cards in grid layout
- [ ] Card shows: malaphor text, source phrases, rating, date
- [ ] Filter by: rating, date range, favorites only
- [ ] Sort by: date, rating, alphabetical
- [ ] Click card to view full details / edit rating
- [ ] Responsive layout (adapts to window size)
- [ ] Performance: smooth scrolling with 500+ cards

### Implementation Notes

- Create `GalleryPanel` with custom card widgets
- Use Canvas or Frame with scrollbar for layout
- Implement card click handlers
- Add filter/sort dropdowns
- Consider pagination for large datasets

### Dependencies

#8 (UX-7: ratings), #1 (UX-1: history persistence)

### Related Issues

None

---

## Issue #22: FEAT-17 - API/CLI Interface

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:medium`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 6-8 hours
**Status:** ✅ COMPLETE

### Description

Expose generation logic as REST API or command-line tool. Allow other applications to use the malaphor generator.

### Acceptance Criteria

- [ ] CLI tool accepts arguments: --generate, --category, --export-format
- [ ] CLI returns JSON or formatted output
- [ ] Optional REST API (Flask/FastAPI) for HTTP requests
- [ ] Endpoints: /generate, /search, /import, /export
- [ ] Authentication optional
- [ ] Documentation for API/CLI usage
- [ ] Tests for CLI and API
- [ ] Backward compatible (doesn't break UI)

### Implementation Notes

- Create cli.py for command-line interface
- Use argparse for CLI parsing
- Optional: Flask app for API (lightweight)
- Extract core logic to separate module (done)
- Document with examples
- Test with external tools

### Dependencies

None

### Related Issues

None

---

## Issue #23: PERF-1 - Full-Text Search Index

**Type:** Performance
**Labels:** `category:performance`, `impact:medium`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 4-5 hours

### Description

Build inverted index for fast phrase searching with 1000+ items. Important as database grows.

### Acceptance Criteria

- [ ] Index built on app startup
- [ ] Search performance < 100ms for any query
- [ ] Index size reasonable (< 5MB)
- [ ] Incremental updates when phrases added/deleted
- [ ] Handles unicode/special characters
- [ ] Case-insensitive searching maintained
- [ ] Fuzzy matching optional

### Implementation Notes

- Create `PhraseIndex` class
- Build inverted index on load
- Update on add/delete operations
- Consider using whoosh library or custom implementation
- Benchmark against linear search

### Dependencies

None

### Related Issues

None

---

## Issue #24: UX-6 - Dark Mode Toggle

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:low`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

---

## Issue #25: UX-8 - Drag-and-Drop Phrase Reordering

**Type:** UI/UX Enhancement  
**Labels:** `category:ui-ux`, `impact:low`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 3-4 hours  
**Status:** ✅ COMPLETE

## Issue #26: FEAT-5 - Syllable/Word Count Constraints

**Type:** Generation Feature  
**Labels:** `category:generation`, `impact:low`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 3-4 hours  
**Status:** ✅ COMPLETE

## Issue #27: FEAT-6 - Rhyme Detection (Optional)

**Type:** Generation Feature  
**Labels:** `category:generation`, `impact:low`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 5-6 hours  
**Status:** ✅ COMPLETE

## Issue #28: FEAT-9 - Custom Generation Templates

**Type:** New Capability  
**Labels:** `category:capabilities`, `impact:medium`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 4-5 hours  
**Status:** ✅ COMPLETE

## Issue #29: FEAT-12 - Compare Malaphors Side-by-Side (QUICK WIN)

**Type:** New Capability  
**Labels:** `category:capabilities`, `impact:low`, `effort:quick-win`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 2-3 hours  
**Status:** ✅ COMPLETE

## Issue #30: FEAT-13 - Share Malaphor with Metadata (QUICK WIN)

**Type:** New Capability  
**Labels:** `category:capabilities`, `impact:low`, `effort:quick-win`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 2-3 hours  
**Status:** ✅ COMPLETE

## Issue #31: FEAT-14 - Scheduled Auto-Save (QUICK WIN)

**Type:** New Capability  
**Labels:** `category:capabilities`, `impact:low`, `effort:quick-win`, `phase:foundation`  
**Milestone:** Phase 1: Foundation  
**Estimate:** 2 hours  
**Status:** ✅ COMPLETE

### Description

Prevent data loss from unexpected crashes by periodically saving the current history and favorites in a background thread while the app is running.

### Acceptance Criteria

- [x] Auto-save timer runs on the configured interval
- [x] Saves `history.json` and `favorites.json`
- [x] No UI freeze during save
- [x] Configurable interval is supported
- [x] Auto-save can be stopped cleanly during app shutdown
- [x] Save activity is logged for diagnostics

### Implementation Notes

- Added `start_auto_save()` and `stop_auto_save()` to `MalaphorGenerator`
- Wired the app lifecycle to begin auto-save during initialization and stop it on close
- Persist history/favorites via the existing JSON save paths

## Issue #32: FEAT-15 - Settings Profiles

**Type:** New Capability  
**Labels:** `category:capabilities`, `impact:low`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 3-4 hours  
**Status:** ✅ COMPLETE

## Issue #33: DATA-3 - Multi-Language Support

**Type:** Data & Quality  
**Labels:** `category:data-quality`, `impact:medium`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 6-8 hours  
**Status:** ⏳ NOT STARTED

## Issue #34: TEST-3 - Performance Tests

**Type:** Testing & Reliability  
**Labels:** `category:testing`, `impact:medium`, `effort:complex`, `phase:advanced`  
**Milestone:** Phase 3: Advanced  
**Estimate:** 3-4 hours  
**Status:** ✅ COMPLETE

### Description

Benchmark generation speed and search latency with large datasets.

### Acceptance Criteria

- [x] Search latency benchmark is exposed via `benchmark_search_latency()`
- [x] Timing summary includes average/min/max and result counts
- [x] Batch generation and cancellation behavior are exercised under pytest
- [x] Large-data reliability checks are covered without regressions

### Implementation Notes

- Added benchmark reporting for repeated search calls
- Verified by targeted performance/regression tests in the logic suite

### Dependencies

#3 (DATA-1: larger dataset support)

### Related Issues

None

---

## Issue #35: TEST-4 - Error Handling Tests

**Type:** Testing & Reliability  
**Labels:** `category:testing`, `impact:medium`, `effort:complex`, `phase:advanced`  
**Milestone:** Phase 3: Advanced  
**Estimate:** 3-4 hours  
**Status:** ✅ COMPLETE

### Description

Test graceful failures: malformed JSON, missing files, partial history entries, and recovery behavior.

### Acceptance Criteria

- [x] Malformed JSON is handled gracefully
- [x] Missing files and empty collections start cleanly
- [x] Incomplete history entries do not break export output
- [x] Recovery behavior has regression coverage
- [x] Logs capture warnings/errors without crashing the application

### Implementation Notes

- Hardened `history.json` loading and export behavior
- Added regression tests for malformed inputs and partial records

### Dependencies

None

### Related Issues

None

---

## Issue #36: PERF-2 - Async Generation with Cancellation

**Type:** Performance  
**Labels:** `category:performance`, `impact:medium`, `effort:complex`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 3-4 hours  
**Status:** ✅ COMPLETE

### Description

Allow canceling long-running bulk operations (large imports, batch generations).

### Acceptance Criteria

- [x] `generate_batch_async()` exits immediately when cancellation is requested
- [x] `generate_batch()` honors the shared cancellation event
- [x] `cancel_generation()` sets the requested event reliably
- [x] Async flows stop cleanly without leaving partial state behind

### Implementation Notes

- Batch generation checks the cancellation event on each iteration
- Async wrapper returns early when the signal is set

### Dependencies

#5 (UX-3: progress dialogs)

### Related Issues

None

---

## Issue #37: PERF-3 - Lazy-Load History on Demand

**Type:** Performance  
**Labels:** `category:performance`, `impact:low`, `effort:medium`, `phase:poweruser`  
**Milestone:** Phase 4: Power User  
**Estimate:** 2-3 hours  
**Status:** ✅ COMPLETE

### Description

Load history in paginated chunks for large datasets.

### Acceptance Criteria

- [x] History is exposed via `get_history_page()` with page metadata
- [x] Page size and page number are configurable
- [x] Large datasets can be loaded incrementally instead of all at once
- [x] UI paging logic reuses the same data contract

### Implementation Notes

- Added paginated history access with count/order metadata
- Verified by lazy-history paging regression tests

### Dependencies

None

### Related Issues

None

---

## Issue #24: UX-6 - Dark Mode Toggle

### Acceptance Criteria

- [ ] Theme toggle button in UI or menu
- [ ] Light theme (default) and dark theme available
- [ ] All UI elements properly themed
- [ ] Theme preference persisted to settings
- [ ] Theme loads on app startup
- [ ] Smooth transition between themes

### Implementation Notes

- Create theme configuration (fonts, colors)
- Implement theme switching logic
- Store preference in settings.json
- Test all dialogs and components

### Dependencies

None

### Related Issues

None

---

## Issue #25: UX-8 - Drag-and-Drop Phrase Reordering

**Type:** UI/UX Enhancement
**Labels:** `category:ui-ux`, `impact:low`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 3-4 hours

### Description

Reorder phrases in manage dialog by drag-and-drop for better organization.

### Acceptance Criteria

- [ ] Drag-and-drop enabled on phrase ListBox
- [ ] Reordering updates database order
- [ ] Visual feedback during drag (highlighting, cursor)
- [ ] Works with multi-select
- [ ] Performance acceptable

### Implementation Notes

- Extend Tkinter ListBox with drag-drop support
- Handle reorder event
- Update database order
- Test with large phrase lists

### Dependencies

None

### Related Issues

None

---

## Issue #26: FEAT-5 - Syllable/Word Count Constraints

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:low`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 3-4 hours

### Description

Filter generated malaphors by word/syllable count for specific use cases (poetry, social media).

### Acceptance Criteria

- [ ] "Generate with constraints" option
- [ ] Word count input (min-max)
- [ ] Syllable count input (optional, min-max)
- [ ] Generation filters to match constraints
- [ ] Shows count in results
- [ ] Graceful handling if no matches

### Implementation Notes

- Add word counting logic
- Add syllable counting (approximate)
- Extend generation to filter by constraints
- Test with various ranges

### Dependencies

None

### Related Issues

None

---

## Issue #27: FEAT-6 - Rhyme Detection (Optional)

**Type:** Generation Feature
**Labels:** `category:generation`, `impact:low`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 5-6 hours

### Description

Suggest phrase combinations that rhyme for poetic malaphors.

### Acceptance Criteria

- [ ] Optional rhyming dictionary integration
- [ ] "Generate Rhyming Pairs" mode
- [ ] Generates malaphors where beginning/ending rhyme
- [ ] Shows rhyme scheme in results
- [ ] Performance acceptable
- [ ] Graceful fallback if rhyming unavailable

### Implementation Notes

- Source rhyming dictionary (CMU Pronouncing, etc.)
- Implement rhyme checking algorithm
- Extend generation to favor rhymes
- Optional dependency (works without it)

### Dependencies

None

### Related Issues

None

---

## Issue #28: FEAT-9 - Custom Generation Templates

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:medium`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 4-5 hours

### Description

Define patterns like "Begin [A] + End [B]" and save templates. Reuse for similar generation.

### Acceptance Criteria

- [ ] Template editor UI
- [ ] Save templates with name and pattern
- [ ] Templates list in generate dropdown
- [ ] Apply template to generate
- [ ] Can edit/delete templates
- [ ] Built-in default templates

### Implementation Notes

- Create `TemplateManager` class
- Template schema: `{name, pattern, variables}`
- Template UI builder
- Persist templates to JSON

### Dependencies

None

### Related Issues

None

---

## Issue #29: FEAT-12 - Compare Malaphors Side-by-Side (QUICK WIN)

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:low`, `effort:quick-win`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 2-3 hours

### Description

Select multiple malaphors and show comparison table with source phrases.

### Acceptance Criteria

- [ ] Multi-select in history/favorites
- [ ] "Compare" button when 2+ selected
- [ ] Comparison dialog shows table
- [ ] Columns: Malaphor, Source 1, Source 2, Rating, Date
- [ ] Can sort by any column

### Implementation Notes

- Add multi-select to ListBox
- Create comparison dialog with table
- Sort functionality

### Dependencies

None

### Related Issues

None

---

## Issue #30: FEAT-13 - Share Malaphor with Metadata (QUICK WIN)

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:low`, `effort:quick-win`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 2-3 hours

### Description

Copy malaphor as JSON, Markdown, or plaintext with metadata.

### Acceptance Criteria

- [ ] Format dropdown: Plain Text, Markdown, JSON, CSV
- [ ] Copy button for each format
- [ ] Includes: malaphor, sources, rating, date
- [ ] Formatted nicely for each output type

### Implementation Notes

- Create format templates
- Format selection UI
- Clipboard copy for each format

### Dependencies

None

### Related Issues

None

---

## Issue #31: FEAT-14 - Scheduled Auto-Save (QUICK WIN)

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:low`, `effort:quick-win`, `phase:foundation`
**Milestone:** Phase 1: Foundation
**Estimate:** 2 hours

### Description

Auto-save history/favorites every 5 minutes to prevent data loss from unexpected crashes.

### Acceptance Criteria

- [ ] Auto-save timer runs every 5 minutes
- [ ] Saves history.json and favorites.json
- [ ] No UI freeze during save
- [ ] Configurable interval
- [ ] Can disable auto-save
- [ ] Logs auto-save events

### Implementation Notes

- Use threading.Timer for periodic saves
- Save in background thread
- Start on app init, stop on exit

### Dependencies

#1 (UX-1: needs history persistence)

### Related Issues

None

---

## Issue #32: FEAT-15 - Settings Profiles

**Type:** New Capability
**Labels:** `category:capabilities`, `impact:low`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 3-4 hours

### Description

Save/load UI layouts and preferences as named profiles. Switch between them.

### Acceptance Criteria

- [ ] Profile manager in settings
- [ ] Save current layout/preferences as profile
- [ ] List of saved profiles
- [ ] Load profile restores UI state
- [ ] Delete profile
- [ ] Default profile included

### Implementation Notes

- Profile schema: `{name, layout, preferences, theme}`
- Persist to JSON
- UI for profile management

### Dependencies

None

### Related Issues

None

---

## Issue #33: DATA-3 - Multi-Language Support

**Type:** Data & Quality
**Labels:** `category:data-quality`, `impact:medium`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 6-8 hours
**Status:** ✅ COMPLETE

### Description

Support English, Spanish, French, and German phrase metadata and generation filtering from the UI and CLI.

### Acceptance Criteria

- [x] Phrase schema includes language field
- [x] Filtered generation structure supports per-language selection
- [x] Language selector in UI
- [x] Generate within a selected language when available
- [x] CLI supports language-aware generation by code
- [x] Database entries can carry language metadata for multilingual datasets

### Implementation Notes

- Added `language` metadata to phrase records and generation results
- Core generator and CLI accept `--language` / `language` filtering
- Main Tkinter window exposes a language selector and passes the selection into generation
- Existing generation flow remains backward compatible when the selector is left on `all`

### Dependencies

None

### Related Issues

None

---

## Issue #34: TEST-3 - Performance Tests

**Type:** Testing & Reliability
**Labels:** `category:testing`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Benchmark generation speed and search latency with large datasets.

### Acceptance Criteria

- [x] Search latency benchmark is available via `benchmark_search_latency()`
- [x] Timing summary includes average/min/max and result counts
- [x] Batch generation and cancellation behavior are exercised under pytest
- [x] Large-data reliability checks are covered without regressions

### Implementation Notes

- Added benchmark reporting for repeated search calls
- Verified by targeted performance and regression tests in the logic suite

### Dependencies

#3 (DATA-1: larger dataset support)

### Related Issues

None

---

## Issue #35: TEST-4 - Error Handling Tests

**Type:** Testing & Reliability
**Labels:** `category:testing`, `impact:medium`, `effort:complex`, `phase:advanced`
**Milestone:** Phase 3: Advanced
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Test graceful failures: malformed JSON, missing files, partial history entries, and recovery behavior.

### Acceptance Criteria

- [x] Malformed JSON is handled gracefully
- [x] Missing files and empty collections start cleanly
- [x] Incomplete history entries do not break export output
- [x] Recovery behavior has regression coverage
- [x] Logs capture warnings/errors without crashing the application

### Implementation Notes

- Hardened `history.json` loading and export behavior
- Added regression tests for malformed inputs and partial records

### Dependencies

None

### Related Issues

None

---

## Issue #36: PERF-2 - Async Generation with Cancellation

**Type:** Performance
**Labels:** `category:performance`, `impact:medium`, `effort:complex`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 3-4 hours
**Status:** ✅ COMPLETE

### Description

Allow canceling long-running bulk operations (large imports, batch generations).

### Acceptance Criteria

- [x] `generate_batch_async()` exits immediately when cancellation is requested
- [x] `generate_batch()` honors the shared cancellation event
- [x] `cancel_generation()` sets the requested event reliably
- [x] Async flows stop cleanly without leaving partial state behind

### Implementation Notes

- Batch generation checks the cancellation event on each iteration
- Async wrapper returns early when the signal is set

### Dependencies

#5 (UX-3: progress dialogs)

### Related Issues

None

---

## Issue #37: PERF-3 - Lazy-Load History on Demand

**Type:** Performance
**Labels:** `category:performance`, `impact:low`, `effort:medium`, `phase:poweruser`
**Milestone:** Phase 4: Power User
**Estimate:** 2-3 hours
**Status:** ✅ COMPLETE

### Description

Load history in paginated chunks for large datasets (10K+ items).

### Acceptance Criteria

- [x] History is exposed via `get_history_page()` with page metadata
- [x] Page size and page number are configurable
- [x] Large datasets can be loaded incrementally instead of all at once
- [x] UI paging logic reuses the same data contract

### Implementation Notes

- Added paginated history access with count and page metadata
- Verified by the lazy history paging regression tests

### Dependencies

#1 (UX-1: history persistence)

### Related Issues

None

---

# QUICK WINS SUMMARY

These 5 items can be implemented in 1-2 hours each and provide immediate value:

1. **Issue #11: UX-5** - Keyboard Shortcuts (2-3 hours)
2. **Issue #12: UX-9** - Copy Stats to Clipboard (1-2 hours)
3. **Issue #13: UX-10** - Recent Searches (2-3 hours)
4. **Issue #31: FEAT-14** - Auto-Save (2 hours)
5. **Issue #29: FEAT-12** - Compare Side-by-Side (2-3 hours)

**Total Quick Win Time:** ~10-14 hours

---

# GITHUB CLI SCRIPT (Optional)

If you want to create all issues programmatically:

```bash
#!/bin/bash
# Create all issues via GitHub CLI (gh)
# Prerequisites: gh auth login

REPO="richardnoragon/maliphors-inator"

# Issue 1: UX-1
gh issue create -R $REPO \
  -t "UX-1 - Persist History to JSON" \
  -b "Currently, generated malaphors are displayed in the UI history but lost when the app closes..." \
  -l "category:ui-ux,impact:high,effort:medium,phase:foundation" \
  -m "Phase 1: Foundation"

# Issue 2: TEST-1
gh issue create -R $REPO \
  -t "TEST-1 - Unit Tests for MalaphorGenerator" \
  -b "The MalaphorGenerator class lacks unit test coverage..." \
  -l "category:testing,impact:high,effort:complex,phase:foundation" \
  -m "Phase 1: Foundation"

# ... (repeat for all 37 issues)
```

---

# SUMMARY TABLE

| Phase | Count | Hours | Issues |
|-------|-------|-------|--------|
| Foundation (Phase 1) | 4 | ~14 | #1-4, #31 |
| Polish (Phase 2) | 9 | ~31 | #5-13 |
| Advanced (Phase 3) | 5 | ~22 | #14-20 |
| Power User (Phase 4) | 19 | ~73 | #21-37 |
| **TOTAL** | **37** | **~140** | |

**Quick Wins:** 5 issues (~10-14 hours combined)
**High Impact:** 4 issues (Phase 1 Foundation)
**Medium Effort:** 21 issues
**Complex:** 12 issues

---

**Generated:** 2026-09-07
**Repository:** maliphors-inator
**Specification Document:** `.specify/features/improvements-roadmap/spec.md`

## Alpha technical checkpoint

On 2026-10-01, the reviewed snapshot passed 214 tests, dependency checks, the real-dialog walkthrough, and backup recovery. Architecture review and initial Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17 validation are complete. The application remains pre-alpha pending human usability review and independent developer handoff. See the [current gates](ROADMAP.md#alpha-readiness) and [validation record](RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).
