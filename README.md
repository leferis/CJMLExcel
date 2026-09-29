# CJMLExcel

CJMLExcel is a desktop application that converts customer or user journey data in Excel workbooks into CJML 3.0 XML. It reads journey worksheets, maps actors and touchpoints, and creates an XML file that can be used by CJML-compatible tools.

## Features

- Select an `.xlsx` or `.xlsm` workbook; the application processes journey sheets and skips known template/support sheets.
- Read journey details, actors, touchpoints, phases, channels, dates, and experience ratings from the workbook.
- Optionally group actors under a shared name, assign actor icons, or arrange actors in journey order.
- Export the selected journeys as CJML 3.0 XML.

## Get a Release

Find available application releases and downloadable builds on the [GitHub Releases page](https://github.com/leferis/CJMLExcel/releases). The release version is listed with each release.

## Run from Source

The application requires Python 3.10 or newer and Tkinter. From the project directory, install the listed dependencies and start the app:

```powershell
py -m pip install -r requirements.txt
py parser.py
```

When the file picker opens, select an Excel workbook. The application processes its journey worksheets, excluding known template and supporting sheets, then offers a choice to generate XML directly or optionally group actors, assign icons, or sort actors. Follow the dialogs to finish processing.

The generated file is named `YYYY_MM_DD_<workbook-name>.xml` and is written to the application's current working directory. Close the workbook in Excel before selecting it if the application cannot read it.

## Build a Windows Executable

The repository includes a PyInstaller spec that bundles the icon assets. With the dependencies installed, run:

```powershell
py ExeCreator.py
```

The executable is created by PyInstaller in its `dist` output directory.