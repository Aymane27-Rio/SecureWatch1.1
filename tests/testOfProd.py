import subprocess
import pathlib

# ensuring data/reports exists and script exits cleanly (fails if exit code not 0)

def test_securewatch_run():
    reports_dir = pathlib.Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["bash", "scripts/securewatch.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0, f"SecureWatch failed: {result.stderr}"
