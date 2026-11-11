# Frequently asked questions

## What does maliphors-inator do?

It combines the beginning of one idiom or proverb with the ending of another. Source phrases, generated history and favorites are separate collections. See the [user guide](USER_GUIDE.md).

## How do I get started?

Follow [installation](README.md#installation), then run `python main.py` from the repository root. Help → Getting Started explains the first workflow; Help → Feature Tour highlights the actual controls. Generate a result, then use Add to Favorites to keep it.

## Why can I not generate a result?

Generation needs at least two different matching source phrases. Choose language `all`, remove a category restriction, or add/import phrases. Help → Troubleshooting shows the loaded collection counts and working directory.

## Why is my library empty or different from yesterday?

The app reads JSON from the current working directory. Start in the same directory each time. The installed Daily Test uses its own data directory. See [storage and backups](USER_GUIDE.md#files-and-backups).

## Can I import my exported files?

Phrase-library JSON with a `proverbs` list can be reimported. History, favorites and text exports have different purposes and are not phrase imports. Required fields and an example are in the [import format](USER_GUIDE.md#import-format).

## Are backups automatic?

Direct source launches do not make automatic backups. Close all writers and copy the JSON files before broad changes. The Daily Test launcher keeps 14 startup ZIP backups. Follow the [restore instructions](USER_GUIDE.md#files-and-backups); undo is not a backup.

## Can two windows or the CLI share a data directory?

Use one writer at a time. Processes do not synchronize changes; the Daily Test lock only covers its own launches. Close the desktop before changing its data through the CLI.

## Does the app need the internet?

The main app stores data locally and exposes no network service. Its help articles, demo and diagnostics work offline. Installing dependencies and opening GitHub links require internet access.

## Which platforms are validated?

The recorded alpha technical checks cover Ubuntu 26.04.1, Python 3.14.4 and Tk 8.6.17. Other environments are unvalidated. The project remains pre-alpha pending human review and independent handoff; see [current gates](ROADMAP.md#alpha-readiness).

## How do I search or find a command?

Use Manual Combine to search source phrases or Manage History/Manage Favorites to filter saved entries. F1 opens help for the active screen. Ctrl+Shift+P opens the action palette. Help → Search Help searches local articles.

## Where do I report a problem?

Use [GitHub Issues](https://github.com/richardnoragon/maliphors-inator/issues) for ordinary bugs, including revision, environment, steps and expected/actual results. Send vulnerabilities or confidential conduct reports to richardnoragon@mac.com; see [security](SECURITY.md) and [conduct](CODE_OF_CONDUCT.md).

## May I redistribute the application?

The project uses a proprietary license. Read [LICENSE](LICENSE) and obtain the copyright holder's permission for uses that require it.
