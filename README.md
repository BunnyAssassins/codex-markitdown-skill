# Codex MarkItDown Skill

A Codex skill that safely converts local documents into LLM-ready Markdown with [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

## What it adds

- Precise Codex routing for document-to-Markdown and structured text extraction tasks.
- A local-only wrapper that rejects URLs and avoids accidental overwrites.
- Batch conversion with per-file success and failure reporting.
- Tested extraction for plain text, DOCX, XLSX, and PPTX.

This project is an independent integration and is not affiliated with or endorsed by Microsoft.

## Install with the open skill installer

```powershell
python scripts/install_open_skill.py https://github.com/BunnyAssassins/codex-markitdown-skill --skill markitdown --with-deps
```

Or copy the `markitdown` directory into your Codex skills directory, create `markitdown/.codex-env`, and install `markitdown/requirements.txt` in that environment.

## Test

```powershell
markitdown\.codex-env\Scripts\python.exe -m pip install -r markitdown\requirements-dev.txt
markitdown\.codex-env\Scripts\python.exe -m unittest discover -s markitdown\tests -v
```

MarkItDown requires Python 3.10 or newer. The pinned dependency set enables PDF, Word, PowerPoint, and Excel conversion. Some capabilities, including cloud OCR, image descriptions, and transcription, need additional dependencies, credentials, or services.

## License

The skill integration is released under the MIT License. Microsoft MarkItDown is a separate dependency distributed under its own license.

