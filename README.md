# `gptctl`

![Manage your ChatGPT exports](./docs/header.png &#x27;Manage your ChatGPT exports&#x27;)

CLI manager to organize(show,list,export,explore) ChatGPT user ***conversations.json***.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#)
[![Build](https://img.shields.io/github/actions/workflow/status/Zigr/chatgptctl/ci.yml)](#)
[![Stars](https://img.shields.io/github/stars/Zigr/chatgptctl.svg?style=social&amp;label=Star)](https://github.com/Zigr/chatgptctl/stargazers)

## [INTRODUCTION(more details)](./INTRODUCTION.md)

## [INSTALLATION(examples)](./INSTALL.md)

**Usage**:

```console
$ gptctl [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-i, --input TEXT`: Path to input conversations.json file
* `--output-dir TEXT`: Path to output directory  [default: ./data/conversations]
* `-o, --output TEXT`: Path to output file. Depends on the command used.  [default: ./data/messages_summary.json]
* `-c, --config PATH`: Path to config.json file with overrides internal defaults  [default: /home/zigr/.config/chatgptctl/config.json]
* `--dry-run`: Perform a trial run with no changes made. Output is printed to console.
* `-tl, --truncate-len INTEGER`: Shorten long strings (for ***dry-run*** preview)  [default: 120]
* `-v, --verbose`: Enable verbose output. Increase verbosity (-v, -vv(very verbose) -vvv(very very verbose, i.e. debug)) for more details.  [default: 0]
* `-V, --version`: Show version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `list`: List conversations from the ***input...
* `show`: Show conversation details from the...
* `export`: Export conversations from the ***input***...
* `config`: Configuration file(s) operations: show,...

## `gptctl list`

List conversations from the ***input OPTION*** conversations.json file. ✨

**Usage**:

```console
$ gptctl list [OPTIONS]
```

**Options**:

* `-s, --sort [no_sort|title|created|count]`: Sort by field  [default: no_sort]
* `-o, --order [asc|desc]`: Sort order  [default: desc]
* `--skip-system / --no-skip-system`: Skip system messages  [default: skip-system]
* `-t, --table / -T, --no-table`: Show as a table. Otherwise as a comma-separated titles  [default: table]
* `--help`: Show this message and exit.

## `gptctl show`

Show conversation details from the ***input OPTION*** conversations.json file. ✨

**Usage**:

```console
$ gptctl show [OPTIONS] TITLE
```

**Arguments**:

* `TITLE`: Title of the conversation to show  [required]

**Options**:

* `-toc, --toc-only`: Show user questions of the given converstation only
* `-sug, --suggestions`: Show **user** questions of the given converstation and **assistant** suggestions too
* `--skip-system / --no-skip-system`: Skip system messages  [default: skip-system]
* `--help`: Show this message and exit.

## `gptctl export`

Export conversations from the ***input*** conversations.json file to JSON or MARKDOWN format. See chatgptctl **export command --help** for details.

**Usage**:

```console
$ gptctl export [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `json`: Export one or ___more___ (in a batch)...
* `markdown`: Export one or ___more___ (in a batch)...
* `partial`: Export a range or subtree of messages,...

### `gptctl export json`

Export one or ___more___ (in a batch) conversations to a ___\*.json___ file(s). 🚀

Example Usage:

```bash
# Export one title
$ chatgptctl export json --title My\ conversation\ title\ 10
# Export several titles
$ chatgptctl --output-dir export json -t &#x27;My conversation title 5&#x27; -t &#x27;My conversation title 2&#x27; -t &#x27;My conversation title 15&#x27;
# Export all titles
$ chatgptctl export json --title &quot;*&quot;
```

**Usage**:

```console
$ gptctl export json [OPTIONS]
```

**Options**:

* `-t, --title TEXT`: **Title** of the conversation to export. May be used multiple times. Use asterisk(&#x27;*&#x27;) to export all titles
* `-b, --batch INTEGER`: Export number of ***batch*** conversations in one ***output-file***  [default: 0]
* `-p, --prefix-with-date`: Prefix output message(s) *.json files with their creation date.
* `-s, --sort [no_sort|title|created|count]`: Sort by field  [default: no_sort]
* `-o, --order [asc|desc]`: Sort order  [default: desc]
* `--skip-system / --no-skip-system`: Skip system messages  [default: skip-system]
* `--help`: Show this message and exit.

### `gptctl export markdown`

Export one or ___more___ (in a batch) conversations to a ___markdown (\*.md)___ file(s). 🚀

Example Usage:

```bash
# Sort all conversations by created date with **asc**(ending) order
# and export all conversations from input file **./data/conversations.json** into **./data/conversations-md** directory
# with file names prefixed by **creation date**
# and also export these conversations into single combined file **./data/conversations-all.md**

$ chatgptctl --input ./data/conversations.json --output-dir ./data/conversations-md --output ./data/conversations-all.md .data/conversations-md/ -t * --sort created --order asc --combined --prefix-with-date

```

**Usage**:

```console
$ gptctl export markdown [OPTIONS]
```

**Options**:

* `-t, --title TEXT`: **Title** of the conversation to export. May be used multiple times. Use asterisk(&#x27;*&#x27;) to export all titles
* `--combined`: Also write ***selected*** or ***all*** conversations in one ***output*** file. Check that you ***output*** OPTION is set correctly.
* `--combined-index`: Also write ***selected*** or ***all*** conversations in one ***output*** index file with TOC but without content, Check that you ***output*** OPTION is set correctly.
* `-p, --prefix-with-date`: Prefix output message(s) *.json files with their creation date.
* `-s, --sort [no_sort|title|created|count]`: Sort by field  [default: no_sort]
* `-o, --order [asc|desc]`: Sort order  [default: desc]
* `--skip-system / --no-skip-system`: Skip system messages  [default: skip-system]
* `--help`: Show this message and exit.

### `gptctl export partial`

Export a range or subtree of messages, preserving parent-child structure and chronology.
Example Usage:
chatgptctl export --start &quot;AI Agentic Workflows&quot; --end &quot;Dust / Pydust&quot; --include-children --depth 2 --context-limit 3 --format markdown

**Usage**:

```console
$ gptctl export partial [OPTIONS]
```

**Options**:

* `--thread TEXT`: Thread ID (optional, auto-detected)
* `--start TEXT`: Start message title or ID  [required]
* `--end TEXT`: End message title or ID (optional)
* `--include-children`: Include children recursively
* `--depth INTEGER`: Limit child recursion depth
* `--context-limit INTEGER`: Limit number of ancestors to include
* `--format TEXT`: Output format: markdown or text  [default: markdown]
* `--data-file PATH`: Path to ChatGPT export JSON file  [default: conversations.json]
* `--help`: Show this message and exit.

## `gptctl config`

Configuration file(s) operations: show, create

**Usage**:

```console
$ gptctl config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `show`: Show configuration
* `init`: **Initialize/create** configuration file...

### `gptctl config show`

Show configuration

**Usage**:

```console
$ gptctl config show [OPTIONS] [CONFIG_PATH]
```

**Arguments**:

* `[CONFIG_PATH]`: Path to config file to show  [default: /home/zigr/.config/chatgptctl/config.json]

**Options**:

* `--help`: Show this message and exit.

### `gptctl config init`

**Initialize/create** configuration file with defaults in a default location.
But you can init as many config files as you want. 
Just pass the configuration file in ***config_file*** argument.
NOTE: config files do not support inherited configuration values overrides.You simply create a new configuration.

**Usage**:

```console
$ gptctl config init [OPTIONS] [CONFIG_FILE]
```

**Arguments**:

* `[CONFIG_FILE]`: Path to config file to init  [default: /home/zigr/.config/chatgptctl/config.json]

**Options**:

* `--force`: Overwrite existing config.
* `--help`: Show this message and exit.
