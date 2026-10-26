# Windows PC Health Report Generator

A lightweight Python and PowerShell tool that collects basic Windows
system information and generates a timestamped text health report.

## Features

- Identifies the Windows operating system and system architecture
- Reports CPU load and RAM usage
- Checks fixed-drive capacity and available storage
- Flags drives with low free space
- Generates timestamped diagnostic reports
- Provides a simple summary of basic health checks

## Technologies

- Python
- PowerShell
- Windows CIM (Common Information Model)
- Linux/WSL development environment

## Requirements

- Windows 10 or later
- Python 3
- PowerShell and Windows CIM access
- WSL Windows interoperability if running from Ubuntu

No third-party Python packages are required by the current script.

## How to Run

From the project directory in WSL Ubuntu:

```bash
python health_report.py
cd ~/projects/pc-health-report
git --version
git status --short

The script queries Windows through `powershell.exe` and saves a
timestamped report in the project directory.

## Validation

The project was tested for Python syntax, successful report generation,
Windows operating system detection, drive-check output, and health-check
output.

## Limitations

This tool provides basic system-health indicators. It is not a full
hardware diagnostic, does not repair problems automatically, and cannot
guarantee that a computer is healthy.

## Example

See `sample_report.txt` for an example using fictional, sanitized data.
