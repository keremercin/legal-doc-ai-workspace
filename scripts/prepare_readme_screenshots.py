from pathlib import Path

from PIL import Image, ImageEnhance


def process(src: str, out_name: str, box: tuple[int, int, int, int]) -> None:
    out_dir = Path("docs/screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).crop(box)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    img.save(out_dir / out_name, quality=95)
    print((out_dir / out_name).resolve())


def main() -> None:
    process(
        r"C:\Users\kerem\AppData\Local\Temp\codex-clipboard-ec5376d4-daf9-4e2c-b247-2fe66459f670.png",
        "workspace-dashboard-clean.png",
        (110, 160, 1295, 985),
    )
    process(
        r"C:\Users\kerem\AppData\Local\Temp\codex-clipboard-49912f04-c961-45b1-979d-2a4d1c43d984.png",
        "multi-doc-qa-clean.png",
        (95, 160, 1290, 950),
    )


if __name__ == "__main__":
    main()
