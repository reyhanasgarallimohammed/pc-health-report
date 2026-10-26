import json
import subprocess
from datetime import datetime
from pathlib import Path


POWERSHELL_COMMAND = r"""
$os = Get-CimInstance Win32_OperatingSystem
$cpu = (Get-CimInstance Win32_Processor |
    Measure-Object -Property LoadPercentage -Average).Average

if ($null -eq $cpu) { $cpu = 0 }

$disks = @(
    Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
    ForEach-Object {
        [PSCustomObject]@{
            Drive = $_.DeviceID
            TotalGB = [math]::Round($_.Size / 1GB, 2)
            FreeGB = [math]::Round($_.FreeSpace / 1GB, 2)
            UsedPercent = if ($_.Size -gt 0) {
                [math]::Round(100 * (1 - $_.FreeSpace / $_.Size), 1)
            } else { 0 }
        }
    }
)

[PSCustomObject]@{
    ComputerName = $env:COMPUTERNAME
    OperatingSystem = $os.Caption
    Architecture = $os.OSArchitecture
    TotalRAMGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    FreeRAMGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    LastBoot = [string]$os.LastBootUpTime
    CPUUsagePercent = [math]::Round($cpu, 1)
    Disks = $disks
} | ConvertTo-Json -Depth 4 -Compress
"""


def collect_windows_data():
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", POWERSHELL_COMMAND],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "PowerShell failed.")

    data = json.loads(result.stdout)
    data["RAMUsagePercent"] = round(
        100 * (1 - data["FreeRAMGB"] / data["TotalRAMGB"]), 1
    )
    return data


def generate_report(data):
    lines = [
        "=" * 45,
        "       WINDOWS PC HEALTH REPORT",
        "=" * 45,
        "",
        f"Computer name: {data['ComputerName']}",
        f"Operating system: {data['OperatingSystem']}",
        f"Architecture: {data['Architecture']}",
        f"CPU load: {data['CPUUsagePercent']}%",
        f"RAM total: {data['TotalRAMGB']} GB",
        f"RAM free: {data['FreeRAMGB']} GB",
        f"RAM usage: {data['RAMUsagePercent']}%",
        f"Last boot: {data['LastBoot']}",
        f"Report generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "FIXED DRIVE HEALTH",
        "-" * 45,
    ]

    for disk in data["Disks"]:
        lines.append(
            f"{disk['Drive']} Total: {disk['TotalGB']} GB | "
            f"Free: {disk['FreeGB']} GB | "
            f"Used: {disk['UsedPercent']}%"
        )

    lines.extend(["", "HEALTH CHECKS", "-" * 45])

    ram = data["RAMUsagePercent"]
    cpu = data["CPUUsagePercent"]

    lines.append(
        f"RAM: {'WARNING - high usage' if ram >= 90 else 'OK'}"
    )
    lines.append(
        f"CPU: {'WARNING - high load' if cpu >= 90 else 'OK'}"
    )

    for disk in data["Disks"]:
        status = "WARNING - low free space" if disk["UsedPercent"] >= 90 else "OK"
        lines.append(f"Drive {disk['Drive']}: {status}")

    lines.extend([
        "",
        "Note: These checks are basic indicators, not a complete",
        "hardware diagnostic or a guarantee of system health.",
    ])

    filename = f"windows_health_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    report_path = Path(filename)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


if __name__ == "__main__":
    try:
        print("Collecting Windows PC health information...")
        data = collect_windows_data()
        report = generate_report(data)
        print(f"Windows report generated: {report.resolve()}")
    except (OSError, subprocess.SubprocessError, RuntimeError,
            json.JSONDecodeError, KeyError, TypeError, ZeroDivisionError) as error:
        print(f"Could not generate report: {error}")
        raise SystemExit(1)
