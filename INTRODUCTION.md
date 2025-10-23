# gptctl INTRODUCTION

## Export ChatGPT Data

When you use **Settings → Data Controls → Export Data**, you get a ZIP archive that contains everything linked to your account (conversations, settings, etc.). The most useful part for you is the **conversations.json** file, which holds all your chats/threads in structured form.

```text
chatgpt-data-d_m _Y
├── chat.html
├── conversations.json    <--------------------
├── dalle-generations
│   ├── file-xxx
│   ├── ...
│   └── ...
├── message_feedback.json
├── shared_conversations.json
├── user-xxx
│   ├── file_xxx
│   ├── file_xxx
│   ├── ...
└── user.json

```

## 🚀 Why gptctl?

When ChatGPT exports your data as a massive `conversations.json`, it’s nearly unreadable.  
**gptctl** makes it practical — view, filter, and export your conversations cleanly from the terminal.

Whether you want to archive old chats, analyze your prompts, or create markdown summaries — gptctl helps you do it with ease.

---

## ✨ Features

- 🧭 **List** all conversations with filters and sorting  
- 👁️ **Show** detailed messages (excluding system prompts if desired)  
- 📦 **Export** to JSON, Markdown, or other formats  
- ⚙️ **Configurable** input/output paths via config file or CLI  
- 🐚 **Shell completion** support for Bash/Zsh  
- 🧩 **Extensible** design — ready for plugins and new export formats  

---

## ⚡ Quick Start

```bash
# 1. Clone or install
pip install git+https://github.com/Zigr/gptctl.git

# 2. Run basic commands
gptctl list
gptctl show 12345
gptctl export markdown -t "*" --sort created --order asc

## 🧰 Commands Overview

Run gptctl --help to view all options.

---

## ⚙️ Configuration

Default config location:

```text
~/.config/gptctl/config.json

```

Example configuration:

```json
{
  "input": "~/Downloads/conversations.json",
  "output_dir": "~/chatgpt_exports",
  "format": "markdown",
  "skip_system": true
}
```

Override any setting using command-line flags.

---

## 🪄 Examples

List all conversations:

```bash
gptctl list --sort created --order desc

```

Export all chats to Markdown:

```bash
gptctl export markdown -t "*" --output ./exports

```

## Possible uses of exported personal conversation data

### 1. **Personal archive**

- Keep a full local backup of your chats in case you ever want to delete them from OpenAI but still keep a copy.
- Organize them chronologically or by project.

### 2. **Search & indexing**

- Load the JSON into tools like **[Obsidian](https://obsidian.md/), [Notion](https://www.notion.com/), or [Logseq](https://logseq.com/), etc...** to make your chats searchable alongside your notes.
- Use a local search/indexing tool (like `ripgrep`, `fzf`, or a small Python script) to quickly find past conversations.

### 3. **Custom parsing**

- Because it’s JSON, you can parse it with **Python, Node.js, or jq** and:

  - Extract only your prompts.
  - Extract only assistant replies.
  - Group threads by title (if they had one).
  - Convert to Markdown for easier reading.

### 4. **Knowledge base**

- Import useful conversations into your personal **knowledge system** (e.g., wiki, documentation, or project repo).
- Tag them by topic (like you already do with “Zigr profile”, “Cats care”, etc.) to make them reusable.

### 5. **Training/reference**

- Use your exported conversations as **context material** for other AI tools or even for fine-tuning / prompting local LLMs.

### 6. **Legal / privacy use**

It’s also a transparency tool: you can see exactly what data is stored about you and delete anything you don’t want kept.

---

## What this tool can do

1. **View** the content of ***conversation.json*** file: list all conversations threads with sorting, show individual thread.

2. **Export Threads**: Since ChatGPT does **not** allow to change user account email, you must create a **new** account if you want to use a different email. So you can import/upload your previous conversations/threads.

3. **Organization**: This tool splits your large `conversations.json` into manageable individual JSON chat files—perfect for archiving or referencing. As well as small batches.

4. **Manual import**: With these smaller JSON files, you can open a new chat in your new ChatGPT account and paste or upload the conversation piece by piece, possibly in a batch and promp ChatGPT to “learn” your old context, if your account plan allows this.

5. **Export** threads (individual/batch/all) in order to view personal archive in markdown format wit/without TOC.
  
   - **Moving Chats**: Since ChatGPT does **not** allow you to change your account email, you must create a **new** account if you want to use a different email. Unfortunately, there is no official “import” feature available, so your old chats cannot be directly transferred to the new account.

   - **Organization**: This tool splits your large `conversations.json` into manageable individual JSON chat files—perfect for archiving or referencing.

   - **Manual import**: With these smaller JSON files, you can open a new chat in your new ChatGPT account and paste or “upload” the conversation piece by piece, prompting ChatGPT to “learn” your old context.** **Manual Re-import**: With these smaller JSON files, you can open a new chat in your new ChatGPT account and paste or “upload” the conversation piece by piece, prompting ChatGPT to “learn” your old context.

---

## [Installation](./INSTALL.md)

---

## Usage

1. **Export** your data from your old ChatGPT account via the official “Export Data” functionality.

2. **Unzip** the file OpenAI sends, and locate the `conversations.json` inside.

3. **Copy** this `conversations.json` into the **some known place**

---

## 🤝 Contributing

Contributions are very welcome!
Please see [CONTRIBUTING](./CONTRIBUTING.md)

## 📜 License

This project is licensed under the MIT License
© 2025 Zigr

## 🌟 Support & Feedback

If you find gptctl useful, please give it a ⭐ on GitHub — it helps others discover the project.
For suggestions, feedback, or feature requests, visit the [Discussions](https://github.com/Zigr/gptctl/discussions)

## [DEMOS](./DEMOS.md)

---
