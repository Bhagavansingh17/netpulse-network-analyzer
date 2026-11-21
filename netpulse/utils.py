import shutil
import subprocess
from typing import Optional, Sequence


class NetPulseError(RuntimeError):
    pass


def require_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise NetPulseError(
            f"Required command '{name}' was not found. "
            f"Install it with the package manager for your Linux distribution."
        )
    return path


def run_command(
    command: Sequence[str],
    timeout: float = 10.0,
) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired as exc:
        raise NetPulseError(
            f"Command timed out after {timeout:g}s: {' '.join(command)}"
        ) from exc
    except PermissionError as exc:
        raise NetPulseError(
            f"Permission denied while running: {' '.join(command)}"
        ) from exc
    except OSError as exc:
        raise NetPulseError(f"Could not run {' '.join(command)}: {exc}") from exc


def read_counter(path: str) -> int:
    try:
        with open(path, "r", encoding="ascii") as handle:
            return int(handle.read().strip())
    except (FileNotFoundError, PermissionError, ValueError, OSError):
        return 0


def format_bytes(value: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    number = float(value)
    for unit in units:
        if number < 1000 or unit == units[-1]:
            return f"{number:.1f} {unit}"
        number /= 1000
    return f"{number:.1f} TB"
