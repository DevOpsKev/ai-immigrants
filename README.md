# AI Immigrants: "The Bloody Algos Are Here!"

A provocative exploration of AI ethics through the lens of immigration — free to download.

**Download:** [EPUB](https://aiibook.blob.core.windows.net/downloads/ai-immigrants.epub) | **Listen:** [Spotify](https://open.spotify.com/show/4kmEP6R0vaa5mXVnltwJ0j)

## Getting Started

### Prerequisites

- [Python 3.10+](https://www.python.org/)
- [Pandoc](https://pandoc.org/)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/) (for deployment only)

### Setup

```bash
git clone https://github.com/DevOpsKev/ai-immigrants.git
cd ai-immigrants
scripts/setup-deps.sh
```

### Pre-commit

Install pre-commit hooks to run linting and formatting checks before each commit:

```bash
pip install pre-commit
pre-commit install
```

### Build

```bash
python3 scripts/build-epub.py
```

Output: `output/ai-immigrants.epub`

### Deploy

Infrastructure (one-time):

```bash
scripts/deploy-infra.sh <resource-group-name>
```

Content:

```bash
python3 scripts/deploy-content.py aiibook
```

Or just push to `main` — GitHub Actions builds and deploys automatically.

## Project Structure

```
ai-immigrants/
├── assets/
│   └── front-cover.png
├── content/
│   ├── front-matter/
│   ├── chapters/          # 12 chapters in markdown
│   └── back-matter/
├── infra/
│   ├── main.bicep         # Azure Blob Storage
│   └── main.bicepparam.json
├── scripts/
│   ├── setup-deps.sh      # Install build dependencies
│   ├── build-epub.py      # Build EPUB from markdown
│   ├── deploy-infra.sh    # Deploy Azure infrastructure
│   ├── deploy-content.py  # Upload EPUB to blob storage
│   └── install-az-cli.sh  # Install Azure CLI locally
├── site/
│   ├── index.html         # Landing page
│   ├── book-mockup.png
│   └── CNAME
├── epub.css
├── metadata.yaml
└── .github/workflows/
    └── build-book.yml     # CI/CD pipeline
```

## CI/CD

Push to `main` triggers the GitHub Actions pipeline which builds the EPUB and deploys it to Azure Blob Storage. PRs build and upload the artifact for review but do not deploy.

### Required Secrets

- `AZURE_CREDENTIALS` — Service principal JSON
- `STORAGE_ACCOUNT_NAME` — `aiibook`

## License

Content © Kevin Ryan 2026. All rights reserved.