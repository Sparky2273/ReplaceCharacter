<div align="center">

<h1>✏️ ReplaceCharacter</h1>

<p><strong>A free, open-source batch file-rename suite with a clean GUI — replace, remove, or transform characters and words in hundreds of filenames at once, with live preview, undo/redo, and regex support.</strong></p>

<p>
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/GUI-PyQt6-purple?style=flat-square" alt="PyQt6">
  <img src="https://img.shields.io/badge/regex-supported-orange?style=flat-square" alt="Regex">
  <img src="https://img.shields.io/badge/undo%2Fredo-yes-brightgreen?style=flat-square" alt="Undo/Redo">
  <img src="https://img.shields.io/badge/single--file-yes-teal?style=flat-square" alt="Single File">
</p>

<p>
  <a href="#-quick-start-windows-exe">⚡ Quick Start (EXE)</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-run-from-source">Run from Source</a> ·
  <a href="#-how-to-use">How to Use</a> ·
  <a href="#-regex-examples">Regex Examples</a> ·
  <a href="#-undo--redo">Undo / Redo</a> ·
  <a href="#-troubleshooting">Troubleshooting</a>
</p>

</div>

---

## 📖 Table of Contents

- [What Is This?](#-what-is-this)
- [Features](#-features)
- [Quick Start — Windows EXE](#-quick-start-windows-exe)
- [Run from Source](#-run-from-source)
- [How to Use](#-how-to-use)
  - [Replace Characters](#replace-characters)
  - [Remove Words](#remove-words)
  - [Live Preview](#live-preview)
  - [Processing a Folder](#processing-a-folder)
- [Regex Support](#-regex-support)
  - [Regex Examples](#regex-examples)
- [Undo / Redo](#-undo--redo)
- [Options Reference](#-options-reference)
- [File Logging](#-file-logging)
- [Saved Preferences](#-saved-preferences)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contact & Support](#-contact--support)
- [License](#-license)

---

## 🔍 What Is This?

**ReplaceCharacter** is a desktop application that renames files in bulk by finding and replacing — or completely removing — characters, words, and patterns from filenames. Instead of renaming files one by one, you load a folder, set your rules, preview the result, and apply everything in one click.

**Who is this for?**
- Anyone who has downloaded files with ugly naming patterns (e.g., spaces replaced by underscores, numbers prefixed, dates in the wrong format)
- Photographers, video editors, and musicians managing large media libraries
- Developers cleaning up generated or downloaded file sets
- Anyone who has ever needed to rename dozens or hundreds of files at once

Everything runs **100% locally and offline** — no internet, no server, no data sent anywhere.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 **Replace Mode** | Find any character, word, or pattern in filenames and replace it with something else |
| 🗑️ **Remove Mode** | Remove any word or substring from filenames entirely (replacement = nothing) |
| 🔍 **Regex Support** | Use full Python regular expressions instead of plain text for advanced pattern matching |
| 🔡 **Case-Insensitive Option** | Match patterns regardless of uppercase or lowercase |
| 👁️ **Live Preview** | See exactly what every filename will become *before* applying any changes — in a clear before/after table |
| ↩️ **Undo / Redo** | Instantly reverse or reapply any batch rename operation, with timestamps on each action |
| 📂 **Folder Processing** | Load an entire folder and rename all files inside it in one operation |
| 📄 **Individual File Mode** | Select and rename specific files only |
| 🖱️ **Drag & Drop** | Drag a file or folder directly onto the window to load it instantly |
| 📊 **Batch Progress Bar** | Live progress bar with filename display during large batch operations |
| ⏱️ **Activity Indicator** | Real-time status: "Processing…", "Undoing…", "Redoing…" |
| 🧵 **Non-Blocking UI** | All renaming runs in a background QThread — the window stays responsive on large folders |
| 📋 **Operation Log Panel** | Color-coded timestamped log of every rename: ✔ success, ✘ error, — no change |
| 📝 **Optional File Logging** | Write the full log to `replace_character.log` for an audit trail |
| 💾 **Saves Preferences** | Remembers your last settings (theme, regex toggle, case sensitivity, directory) between sessions |
| 🎨 **Light / Dark Theme** | One-click toggle between light and dark themes |
| 📦 **Single File** | Entire app in one Python file — easy to audit, share, and run |

---

## ⚡ Quick Start (Windows EXE)

No Python needed.

1. Go to the [**Releases**](../../releases) page of this repository.
2. Download `ReplaceCharacter.exe`.
3. Double-click it — the app opens immediately. No installation required.
4. Load a file or folder, set your replace rules, check the Preview tab, then click **⚡ Apply Changes**.

> Fully portable — run it from any folder or USB drive.

---

## 🐍 Run from Source

### Requirements

- Python 3.8 or newer — [https://www.python.org/downloads/](https://www.python.org/downloads/)
  - Windows: tick ✅ **"Add Python to PATH"** during installation
- PyQt6 (the only non-standard dependency — everything else is Python stdlib)

### Step 1 — Get the Script

Download `ReplaceCharacter_V1.py` from this repository, or clone:

```bash
git clone https://github.com/Sparky2273/ReplaceCharacter.git
cd ReplaceCharacter
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run

```bash
python ReplaceCharacter_V1.py
```

---

## 📖 How to Use

### Replace Characters

This mode finds every occurrence of a character or word in a filename (excluding the extension) and replaces it with something new.

1. Click **Select File** or **Select Folder** — or drag and drop a file/folder onto the window.
2. In the **Replace** section, tick the **Enable Replace** checkbox.
3. In the **Find** box, type the character or word you want to replace (e.g., a space ` `, an underscore `_`, or a word like `copy`).
4. In the **Replace with** box, type what you want instead (e.g., `-`). Leave it empty to delete the matched text.
5. Optionally enable **Regex** or **Case-Insensitive** (see below).
6. Click the **Preview** tab to see the before/after table — verify nothing unexpected will change.
7. Click **⚡ Apply Changes**.

**Example:** Replace all spaces with underscores in a folder of music files:
- Find: ` ` (space)
- Replace with: `_`
- Result: `My Song Name.mp3` → `My_Song_Name.mp3`

---

### Remove Words

This mode removes a specific word or substring from every filename — no replacement, just deletion.

1. Load your file or folder (same as above).
2. In the **Remove** section, tick the **Enable Remove** checkbox.
3. Type the word or text to remove (e.g., ` - Copy`, `(1)`, `final_`).
4. Preview → Apply.

**Example:** Remove ` - Copy` from filenames after duplicating:
- Remove: ` - Copy`
- Result: `Report - Copy.docx` → `Report.docx`

> **Tip:** You can use **both Replace and Remove at the same time** — the replace step runs first, then the remove step is applied to the result.

---

### Live Preview

Before applying any change, always check the **Preview** tab:

- Click the **Preview** tab (next to the Log tab).
- Click **🔍 Generate Preview** to build the before/after table.
- The table shows three columns: **Original Name**, **New Name**, and **Changed** (✔ if the name will change, — if it stays the same).
- Files with no change are shown with a dimmed "—" marker — only files that actually change are renamed.
- If everything looks correct, switch back to the main tab and click **⚡ Apply Changes**.

---

### Processing a Folder

- Click **Select Folder** and choose a directory.
- ReplaceCharacter processes every **file** directly inside that folder (not subfolders — one level deep).
- Subfolders themselves are not renamed — only the files within them.
- The progress bar shows `current / total` and the filename being processed.

---

## 🔍 Regex Support

Enable the **Use Regex** checkbox to treat the **Find** field as a Python regular expression instead of plain text. This gives you powerful pattern-based matching.

### Regex Examples

| Goal | Find (Regex) | Replace with | Example |
|---|---|---|---|
| Remove leading digits and a dot | `^\d+\.` | *(empty)* | `01. Song Name.mp3` → `Song Name.mp3` |
| Replace multiple spaces with one | `\s+` | ` ` | `My  File   Name.txt` → `My File Name.txt` |
| Remove anything in parentheses | `\s*\([^)]*\)` | *(empty)* | `Report (v2) Final.docx` → `Report Final.docx` |
| Remove trailing spaces or dashes | `[\s\-]+$` | *(empty)* | `My File  - .txt` → `My File.txt` |
| Replace underscores or hyphens | `[_\-]` | ` ` | `my_file-name.txt` → `my file name.txt` |
| Remove date pattern `YYYY-MM-DD` | `\d{4}-\d{2}-\d{2}` | *(empty)* | `photo_2024-03-15.jpg` → `photo_.jpg` |
| Remove bracketed numbers `[1]` | `\s*\[\d+\]` | *(empty)* | `Track [1].mp3` → `Track.mp3` |

> **Important:** The extension (`.mp3`, `.txt`, `.docx`, etc.) is **never changed** — the regex is applied only to the filename stem (the part before the last dot). You cannot accidentally remove a file extension.

### Regex Tips
- Enable **Case-Insensitive** together with regex to match regardless of letter case.
- If your regex is invalid, the Preview step will show an error in the log and no changes will be applied.
- Test complex patterns in the Preview tab before applying.

---

## ↩️ Undo / Redo

Every batch rename operation is recorded and can be fully reversed.

- **Undo (↩)** — reverses the most recent rename batch, restoring all filenames to what they were before.
- **Redo (↪)** — reapplies a rename batch that was undone.
- The Undo and Redo buttons show a label with the **number of files** and **timestamp** of the operation (e.g., `↩ Undo (12 rename(s) @ 14:35:02)`).
- Multiple operations are stacked — you can undo several operations in sequence.
- Undo also available from the **Edit menu** in the menu bar (`Ctrl+Z` / `Ctrl+Y`).

> **Note:** Undo only works while the app is open in the same session. Undo history is not saved to disk and is lost when the app is closed.

---

## ⚙️ Options Reference

| Option | Description |
|---|---|
| **Enable Replace** | Activates the Find → Replace with step |
| **Find** | The character, word, or regex pattern to search for in filenames |
| **Replace with** | What to substitute for each match (leave empty to delete matches) |
| **Enable Remove** | Activates the Remove word step |
| **Remove word** | The exact substring to delete from every filename |
| **Use Regex** | Treats the **Find** field as a Python regex pattern |
| **Case-Insensitive** | Matches regardless of uppercase/lowercase for both Replace and Remove |
| **Enable File Logging** | Writes all log entries to `replace_character.log` with timestamps |

---

## 📝 File Logging

- Enable with the **Enable Logging** checkbox.
- Logs are written to `replace_character.log` in the same folder as the app.
- Each entry: `YYYY-MM-DD HH:MM:SS  [LEVEL]  Message`
- Useful for auditing what was renamed on a specific date.
- File logging is off by default.

---

## 💾 Saved Preferences

The app saves your settings to `replace_character_config.json` in the same folder, and restores them next time you open the app. Settings saved:

| Setting | What is remembered |
|---|---|
| `theme` | Light or dark theme |
| `use_regex` | Whether regex mode was on |
| `case_sensitive` | Whether case-sensitive matching was on |
| `enable_logging` | Whether file logging was enabled |
| `last_directory` | The last folder you opened |
| `old_char` | The last value in the Find field |
| `new_char` | The last value in the Replace with field |
| `remove_word` | The last value in the Remove word field |

Delete `replace_character_config.json` to reset all preferences to defaults.

---

## 🔧 Troubleshooting

**"No module named PyQt6"**
→ Run `pip install -r requirements.txt` and try again.

**Files were renamed but I want the original names back**
→ Click the **↩ Undo** button immediately — it will restore all filenames from the last operation.

**Undo button is greyed out**
→ The undo history is only kept in the current session. If you closed and reopened the app, the history is gone. You can manually redo the rename in the opposite direction (swap Find/Replace).

**Regex error in the log**
→ Your regular expression has a syntax error. Check the Pattern in the Find field — the log panel will show the exact error message. Fix the pattern and try Preview again.

**Some files say "no change" in the log**
→ The pattern did not match those filenames. This is normal — they are skipped safely.

**"Permission denied" error for some files**
→ The file may be open in another application, or you may not have write access to that folder. Close apps that have the files open and try again.

**The app renamed more files than expected**
→ Check the Preview before applying next time. Use the case-sensitive option or a more specific pattern to narrow the match.

---

## ❓ FAQ

**Q: Does this change file extensions?**
A: No. The extension (e.g., `.mp3`, `.jpg`, `.docx`) is always preserved. Only the filename stem (the name before the last dot) is changed.

**Q: Can it process subfolders recursively?**
A: In v1.0.0, processing is one level deep (files directly inside the selected folder). Recursive subfolder support may be added in a future version.

**Q: What happens if two files would end up with the same name after renaming?**
A: The second file's rename will fail with a "file already exists" error, which is shown in the log. The first file is renamed successfully. Use the Preview tab to spot collisions before applying.

**Q: Can I use both Replace and Remove at the same time?**
A: Yes. Enable both checkboxes. The replace step runs first, then the remove step is applied to the result.

**Q: Is this safe for system files or important files?**
A: Only use it on files in folders you own and manage. The undo feature can reverse mistakes within the same session. For very important files, always work on a copy first.

**Q: Does the app send any data over the internet?**
A: No. ReplaceCharacter is 100% offline.

---

## 📬 Contact & Support

- **Telegram:** [@Sparky2273](https://t.me/Sparky2273)
- **Email:** mhashemi6699@gmail.com
- **Bug Reports & Feature Requests:** [Open a GitHub Issue](../../issues)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by SPARKS**

*Rename smarter, not harder.*

</div>
