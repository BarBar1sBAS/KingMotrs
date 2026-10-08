"""Package only the static demo, with reproducible ZIP metadata."""

from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = [
    "index.html",
    "legal.html",
    "style.css",
    "motion.css",
    "tokens.css",
    "app.js",
    "robots.txt",
    *[
        "assets/" + name
        for name in (
            "logo.svg",
            "hero.webp",
            "process.webp",
            "team-smirnov.webp",
            "team-volkov.webp",
            "team-morozov.webp",
            "team-sokolov.webp",
            "team-orlov.webp",
            "maintenance.webp",
            "repair.webp",
            "diagnostics.webp",
            "parts.webp",
            "tires.webp",
            "wash.webp",
            "Manrope-Variable.ttf",
            "GolosText-Variable.ttf",
            "Manrope-OFL.txt",
            "Golos-OFL.txt",
        )
    ],
]


def package():
    dist = ROOT / "dist"
    # Only the disposable build directory is replaced.
    for name in PUBLIC_FILES:
        assert (ROOT / "prototype" / name).is_file(), name
    if dist.exists():
        shutil.rmtree(dist)
    for name in PUBLIC_FILES:
        target = dist / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "prototype" / name, target)
    output = ROOT / "output-v2/KingMotors-static.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(PUBLIC_FILES):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (dist / name).read_bytes())
    print(
        f"Static demo: {len(PUBLIC_FILES)} files, ZIP {output.stat().st_size:,} bytes"
    )


if __name__ == "__main__":
    package()
