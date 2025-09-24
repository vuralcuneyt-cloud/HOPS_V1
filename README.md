# HOPS_V1

HOPS_V1 is a PySide6 desktop application that industrialises the preparation of Etsy poster and print listings. It automates every stage of the artwork pipeline – from analysing source imagery and assigning SKUs to producing zipped delivery packages – while storing operational state in SQLite so high-volume shops can resume work at any step without losing context.【F:main.py†L1-L847】【F:core/database.py†L1-L205】

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Repository Layout](#repository-layout)
- [Runtime Workspace Structure](#runtime-workspace-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Using the Application](#using-the-application)
  - [Graphical Workflow](#graphical-workflow)
  - [Operational Checklist](#operational-checklist)
- [Database Model](#database-model)
- [Packaging and Distribution](#packaging-and-distribution)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Project Overview
The application boots by provisioning the Etsy production workspace inside the current user's home directory, creates desktop shortcuts, initialises the SQLite database, and then opens a single-window control panel tailored to batch production work.【F:main.py†L8-L844】【F:core/installer.py†L1-L43】【F:core/shortcuts.py†L1-L53】 Each action button in the sidebar triggers a specialised automation module, allowing operators to advance the workflow step-by-step or re-run individual phases as needed.【F:main.py†L99-L160】【F:core/analyzer.py†L1-L58】【F:core/design_pack.py†L1-L66】

## Key Features
- **Deterministic workspace provisioning:** `ensure_structure()` creates the complete folder hierarchy (data intake, design staging, master outputs, export targets, zip destination, and logs) under `~/HOPS_V1`, marking the log folder hidden on Windows for cleanliness.【F:core/paths.py†L1-L9】【F:core/installer.py†L1-L43】
- **Image ingestion with SKU assignment:** The Analyzer reads every file under `0_Data`, skips duplicates, calculates resolution/orientation, issues sequential `HOPS_########` SKUs, and persists records in `raw_data` with timestamps.【F:core/analyzer.py†L1-L58】【F:core/database.py†L19-L120】
- **Ratio-aware design packing:** Vertical assets are matched against configurable ratio tolerances, mapped to portrait sub-folders, and enriched with master frame codes; near-misses are labelled `Nearest_*` for manual intervention.【F:core/design_pack.py†L1-L66】
- **Orientation-driven file splitting:** Assets are renamed with their SKU, then routed to landscape, nearest, or main portrait queues based on database orientation and ratio classification.【F:core/split_up.py†L1-L104】
- **Design distribution & QC:** Approved files are copied into every expected ratio directory, while nearest results land in `Unmatched`. After the move, `design_check` verifies that required design files exist on disk.【F:core/run_design.py†L1-L64】
- **Mastering automation:** Bulk masters are fingerprinted to infer their intended ratio code, recorded in `master_check`, and moved/renamed into the structured master library accordingly.【F:core/run_master.py†L1-L112】
- **Export orchestration:** Finished deliverables are sorted into `5_Etsy/<SKU>/` folders by parsing master filenames, ensuring idempotent moves for both imagery and PDFs.【F:core/exporter.py†L1-L56】
- **Zip packaging for Etsy:** Each SKU directory is zipped into `6_Etsy_Zip/<SKU>.zip`, replacing older archives to keep listings ready for upload.【F:core/etsy_zip.py†L1-L36】
- **Fulfilment checklist:** The checklist cross-references expected master frame codes with exported assets, skipping already zipped SKUs, and writes gaps to `99_Logs_Reports/missing_files.txt` for action.【F:core/design_process.py†L1-L78】
- **Desktop shortcuts:** Optional helpers drop shortcuts to the workspace and packaged executable on the desktop (Windows `.lnk` or POSIX `.desktop` files).【F:core/shortcuts.py†L1-L53】

## System Requirements
- Python 3.11 – 3.13.【F:pyproject.toml†L1-L19】
- PySide6 for the GUI, Pillow for image metadata, and pywin32 for Windows shortcut integration (installed automatically via Poetry).【F:pyproject.toml†L10-L28】
- Optional: PyInstaller for generating distributable executables (bundled as a development dependency).【F:pyproject.toml†L22-L28】

## Repository Layout
```
HOPS_V1/
├── assets/            # Application icons and static assets
├── build/             # Intermediate PyInstaller build artefacts
├── core/              # Domain logic modules (analysis, packing, export, etc.)
├── dist/              # PyInstaller output when built
├── main.py            # PySide6 entry point and UI wiring
├── pyproject.toml     # Poetry project configuration and dependencies
└── HOPS_V1.spec       # PyInstaller build recipe
```

## Runtime Workspace Structure
The first launch scaffolds the production workspace in the user's home directory:
```
~/HOPS_V1/
├── 0_Data/                        # Drop incoming artwork here
├── 1_Main/                        # Queue for portrait-ready assets
├── 2_Design/
│   ├── 0_Portrait/
│   │   ├── Ratio/Ratio_24x36/{W_24,H_36}/
│   │   ├── Ratio/Ratio_18x24/{W_18,H_24}/
│   │   ├── Ratio/Ratio_24x30/{W_24,H_30}/
│   │   ├── Ratio/Ratio_11x14/{W_11,H_14}/
│   │   ├── Ratio/Ratio_A_Series/{W_23.386,H_33.110}/
│   │   └── Unmatched/
│   ├── 1_Landscape/
│   └── 2_Nearest/
├── 3_Master/{0_Sizes/Ratio/*,1_Bulk}/
├── 4_Export/{Bulk,Unmatched}/
├── 5_Etsy/
├── 6_Etsy_Zip/
└── 99_Logs_Reports/
    ├── config.json
    └── hops_v1.db
```
This tree mirrors the structure produced by `ensure_structure()` and is used by every workflow module when reading or writing files.【F:core/installer.py†L16-L43】

## Installation
1. **Clone the repository**
   ```bash
   git clone <repo_url>
   cd HOPS_V1
   ```
2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```
   Alternatively, create a virtual environment and install the runtime stack manually:
   ```bash
   pip install pyside6 pillow pywin32
   ```
3. **Launch the application in development mode**
   ```bash
   poetry run python main.py
   ```
   The first start provisions the workspace, creates shortcuts, initialises the database, and opens the control panel.【F:main.py†L8-L844】【F:core/installer.py†L16-L43】【F:core/database.py†L19-L205】

## Configuration
- Trimming tolerance (ratio matching window) is stored in `99_Logs_Reports/config.json`. Use the Settings panel to update the integer percentage or edit the file directly for scripted adjustments.【F:core/config.py†L1-L16】【F:main.py†L188-L305】
- The Settings view also exposes a guarded database reset that wipes operational tables after the operator types `confirm`. Use this when you need to restart the workflow from a clean slate.【F:core/database.py†L121-L205】【F:main.py†L236-L303】

## Using the Application
### Graphical Workflow
Each sidebar action runs a discrete module. The UI manages progress indicators and automatically chains dependent steps where appropriate.【F:main.py†L304-L379】 The recommended order is:
1. **Analyzer** – ingest source imagery, assign SKUs, and queue Design Pack automatically.【F:main.py†L304-L379】【F:core/analyzer.py†L1-L58】
2. **Split-Up** – rename assets with their SKU and route them to orientation-specific staging folders.【F:main.py†L380-L420】【F:core/split_up.py†L1-L104】
3. **Design** – duplicate approved portraits into every required ratio folder and verify the design inventory.【F:main.py†L421-L478】【F:core/run_design.py†L1-L64】
4. **Master** – fingerprint bulk master files, update the `master_check` table, and relocate them into the ratio-specific master library.【F:main.py†L479-L563】【F:core/run_master.py†L1-L112】
5. **Export** – stage final deliverables under `5_Etsy/<SKU>/` with deterministic overwrites.【F:main.py†L564-L615】【F:core/exporter.py†L1-L56】
6. **Check List** – audit exported SKUs against expected master codes and produce a `missing_files.txt` exception report.【F:main.py†L616-L704】【F:core/design_process.py†L1-L78】
7. **EtsyZ** – compress each SKU directory into upload-ready zip archives.【F:main.py†L705-L771】【F:core/etsy_zip.py†L1-L36】

Every backend function accepts an optional `progress_cb(index, total, message)` so that the UI (or alternative front-ends) can surface granular progress updates without duplicating business logic.【F:core/analyzer.py†L19-L58】【F:core/design_pack.py†L27-L64】【F:core/split_up.py†L32-L104】【F:core/run_master.py†L37-L112】【F:core/exporter.py†L18-L56】【F:core/etsy_zip.py†L12-L32】【F:core/design_process.py†L41-L70】

### Operational Checklist
- Drop fresh imagery into `~/HOPS_V1/0_Data/`.
- Run **Analyzer** to register assets and compute ratios (this also triggers **Design Pack** automatically from the Analyzer screen).
- Proceed through **Split-Up**, **Design**, **Master**, and **Export** when your creative team finishes each stage.
- Use **Check List** to identify missing masters before zipping.
- Execute **EtsyZ** to generate uploadable archives. SKUs that already have a zip file are skipped during the checklist, keeping the report focused on unshipped work.【F:core/design_process.py†L41-L70】

## Database Model
All operational state lives in `99_Logs_Reports/hops_v1.db`. Tables are created automatically with indexes that prevent duplicate ingestion and maintain unique design-pack combinations.【F:core/database.py†L19-L120】
- `raw_data`: image metadata captured during analysis (original name, SKU, dimensions, orientation, created timestamp).【F:core/database.py†L26-L52】
- `design_pack`: ratio matches and generated master frame codes with a uniqueness constraint on `(sku, result)`.【F:core/database.py†L54-L98】
- `design_check`: verification ledger that records whether required design files are present on disk.【F:core/database.py†L60-L89】【F:core/design_check.py†L1-L44】
- `master_check`: catalogue of inspected master assets and their inferred master design codes.【F:core/database.py†L90-L120】【F:core/run_master.py†L37-L84】
Resetting the database clears these tables and resets autoincrement counters so SKUs and reports remain tidy.【F:core/database.py†L121-L205】

## Packaging and Distribution
- Run the GUI locally with Poetry: `poetry run python main.py`.【F:main.py†L821-L844】
- Produce a Windows executable with PyInstaller using the supplied spec file:
  ```bash
  poetry run pyinstaller --noconfirm HOPS_V1.spec
  ```
  The packaged app emits into `dist/HOPS_V1/`, which the shortcut helper references when creating desktop links.【F:pyproject.toml†L22-L28】【F:core/shortcuts.py†L24-L52】

## Troubleshooting
- **Database is locked:** Another process may be reading `hops_v1.db`. Try closing external viewers; SQLite timeouts are kept short to avoid freezing the UI.【F:core/database.py†L10-L18】
- **Analyzer finds no files:** Confirm your assets are in `~/HOPS_V1/0_Data/` with unique base filenames so duplicate guards do not skip them.【F:core/analyzer.py†L24-L44】
- **Excess `Nearest_*` results:** Increase the trimming percentage in Settings to widen the allowable ratio tolerance.【F:core/design_pack.py†L27-L64】【F:main.py†L225-L305】
- **Shortcuts missing:** Ensure `pywin32` is installed on Windows or manually create symlinks on macOS/Linux; the helper handles both scenarios but will log warnings if permissions prevent shortcut creation.【F:core/shortcuts.py†L1-L53】

## Contributing
1. Fork and clone the repository.
2. Create a feature branch and implement your change.
3. Run the workflow end-to-end or add automated coverage for new modules.
4. Submit a pull request describing the motivation and validation steps.

## License
This project is released under the [MIT License](LICENSE).