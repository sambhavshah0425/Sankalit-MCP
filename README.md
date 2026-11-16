# sankalit-mcp

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for **Claude Desktop** that gives Claude two abilities:

1. **Sandboxed file tools** over a workspace folder or network share: list, search, read, copy, move, rename, delete and create folders.
2. **Brand-compliant document creation**: Claude sends text or structured data, and the server builds a Word (`.docx`) or PDF file with a cover page, header, footer, fonts and colors that follow the Sankalit brand style guide.

The server runs as a local process and talks to Claude Desktop over standard input/output (stdio). It has no web server, no open ports and no database.

## Why this MCP exists

Consulting teams produce a steady stream of reports, proposals and meeting minutes, and keep their project files on a shared network drive. Using Claude for that work runs into four practical problems, which this server is built to solve:

| Problem | How `sankalit-mcp` addresses it |
|---|---|
| **Claude cannot reach the team's shared drive reliably.** Claude Desktop starts MCP servers as background processes, which often cannot see a mapped drive letter such as `Z:`. | `SANKALIT_DRIVE_MAP` translates the drive letter to its network share, and `SANKALIT_WORKSPACE` sets exactly which folders are available. |
| **Giving an AI broad file access is risky.** | Every file operation is resolved through one path check and limited to the configured workspace roots. Unsupported file types are rejected on create and read. |
| **Documents written by an AI do not follow the company style.** Fonts, margins, cover page, header, footer and colors have to be fixed by hand afterwards. | Documents are built from templates driven by the Sankalit brand style guide: cover page, revision table, branded header and footer, heading and body styles, and "Page X of Y" fields. |
| **Producing the final file takes several manual steps.** Without a tool, Claude drafts text, someone pastes it into Word, formats it and exports a PDF. | One `create_document` call writes the finished `.docx` or `.pdf` straight to its destination folder. |

The brand rules also stay in step with the style guide: they are compiled from the guidelines PDF and handed to Claude (`get_brand_guidelines` and the `brand://instructions` resource), so the assistant knows the house style before it writes anything.

**Typical uses**

- "Create a technical report for this project in the `Reports` folder, using the standard template."
- "Find last quarter's proposals on the shared drive and summarise them."
- "Write a proposal from this brief and save it as a PDF."
- "Move the signed-off drawings into the `Issued` folder."

## Features

- Create `.txt`, `.md`, `.docx` and `.pdf` documents
- Four document templates: `technical_report`, `proposal`, `meeting_minutes`, `presentation`
- Read `.txt`, `.md`, `.docx` and `.pdf` documents as text
- Work with a mapped drive letter (for example `Z:\`) by translating it to its network share
- Restrict every file operation to one or more allowed workspace roots
- Compile brand rules (fonts, heading sizes, margins, colors) from a brand guidelines PDF and expose them to Claude
- A standalone brand compliance linter (`sankalit_mcp.brand`) for checking finished Word files

## Requirements

- Python 3.11 or newer
- Windows
- Microsoft Word, **only** if you want PDF output (PDFs are produced by converting a Word file with `docx2pdf`)

## Installation

```bash
git clone https://github.com/sambhavshah0425/Sankalit-MCP.git
cd Sankalit-MCP
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

This installs the `sankalit-mcp` command into `.venv\Scripts`.

## Configuration

Settings are read from environment variables when the server starts. Restart the server after changing them.

| Variable | Purpose | Example |
|---|---|---|
| `SANKALIT_WORKSPACE` | Folders the server may access. Separate several with `;`. If unset, the server uses the current folder (or the project folder when started from `System32`). | `Z:\;\\server\Marketing` |
| `SANKALIT_DRIVE_MAP` | Maps drive letters to their network shares, so the background process does not depend on your login session's drive mappings. Separate entries with `;`. | `Z=\\server\Sales` |

A path is allowed only if it is inside one of the workspace roots.

### Connect to Claude Desktop

Add the server to `claude_desktop_config.json` (on Windows: `%APPDATA%\Claude\claude_desktop_config.json`), then restart Claude Desktop:

```json
{
  "mcpServers": {
    "sankalit": {
      "command": "C:\\path\\to\\Sankalit-MCP\\.venv\\Scripts\\sankalit-mcp.exe",
      "env": {
        "SANKALIT_WORKSPACE": "Z:\\",
        "SANKALIT_DRIVE_MAP": "Z=\\\\server\\Sales"
      }
    }
  }
}
```

Adjust the paths to your machine. You can also start the server by hand with `sankalit-mcp` or `python -m sankalit_mcp.server`.

## Tools

Each tool is registered under two names, for example `create_document` and `create_document_tool`.

| Tool | What it does |
|---|---|
| `create_document` | Create a `.txt`, `.md`, `.docx` or `.pdf` file from text or structured content |
| `read_document` | Read a `.txt`, `.md`, `.docx` or `.pdf` file as text |
| `write_binary_file` | Copy a file into the workspace, or write base64 data |
| `list_directory` | List folders and files in a directory |
| `list_tree` | List a directory as a nested tree (depth 1-15) |
| `list_allowed_directories` | Show the workspace roots the server may access |
| `find_documents` | Search recursively by file name and extension |
| `document_info` | Size, timestamps and type of a file |
| `copy_document` / `move_document` | Copy or move a file |
| `rename_document` | Rename a file |
| `delete_document` | Delete a file |
| `create_directory` | Create a folder |
| `get_brand_guidelines` | Return the compiled brand rules as Markdown |
| `hello` | Connection test |

The server also publishes the resource `brand://instructions` with the same brand rules.

### Creating a branded document

For `.docx` and `.pdf` files, pass a `document_type` and `structured_content`:

```json
{
  "path": "Z:\\Reports\\Terminal Study.docx",
  "document_type": "technical_report",
  "structured_content": {
    "title": "Terminal Study",
    "client": "Example Client",
    "project_name": "Terminal 2",
    "location": "City",
    "discipline": "Airport Systems",
    "prepared_by": "A. Author",
    "revision": "Rev 00",
    "doc_no": "SKL-XXX-TR-001",
    "show_toc": false,
    "assumptions": ["Design life of 25 years"],
    "sections": [
      { "heading": "1. Scope", "text": "Scope text.", "level": 1 }
    ],
    "revisions": [
      { "rev": "Rev 00", "date": "01 January 2026", "prepared_by": "A. Author", "description": "Initial issue" }
    ]
  }
}
```

The metadata fields are optional, but a `technical_report` or `proposal` needs at least one section with body text. Plain text with Markdown-style headings (`# Title`, `## Section`) and `Project:` / `Client:` lines can be passed as `text_content` instead.

## Brand rules

At startup the server hashes `resources/brand/Sankalit Brand Guidelines.pdf` and, when the PDF has changed, extracts fonts, heading sizes, margins and colors into `resources/brand/brand_manifest.json` and `brand_instructions.md`.

The guidelines PDF is internal and is **not included in this repository** (it is listed in `.gitignore`). Without it the server uses built-in defaults: Calibri and Consolas fonts, 14/12/11 pt headings, 25/20/25/25 mm margins and the Sankalit orange `#F5A623`.

## Project structure

```text
src/sankalit_mcp/
├── server.py        MCP server: registers tools and the brand resource
├── config.py        workspace roots, drive map, supported extensions
├── registry.py      file extension -> handler lookup
├── tools/           one thin function per tool
├── services/        document, directory, search, metadata and template logic
│   └── brand/       brand PDF compiler and cache
├── handlers/        txt, md, docx and pdf readers/writers
├── storage/         file writing and metadata (size, SHA-256, MIME type)
├── utils/           path sandbox and validation
├── templates/       document templates, data models, cover and table components
├── styles/          brand-driven Word styling (margins, header, footer, headings)
└── brand/           standalone brand compliance linter and its rules
resources/brand/     compiled brand data
tests/               pytest suite
```

A tool call flows through `server.py` -> `tools/` -> `services/`, and every service resolves its paths through `utils/paths.py` first.

## Development

Run the tests:

```bash
python -m pytest tests
```

The tests write only to a temporary folder. `test_pdf_generation_e2e` creates a real PDF and therefore opens Microsoft Word; skip it with `-k "not test_pdf_generation_e2e"` if Word is not available.

To add a tool: write a function in `tools/`, add the service logic in `services/` (resolve paths with `resolve_path`), then register it in `server.py`.

## License

No license has been specified yet.
