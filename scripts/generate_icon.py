"""Generate the application icon assets used by the GUI and PyInstaller."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QPainter,
    QPen,
    QPolygonF,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets"
PNG_PATH = ASSETS_DIR / "app_icon.png"
ICO_PATH = ASSETS_DIR / "app_icon.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def main() -> int:
    app = QGuiApplication(sys.argv)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    images = [render_icon(size) for size in ICON_SIZES]
    images[-1].save(str(PNG_PATH), "PNG")
    write_ico(images, ICO_PATH)
    app.quit()
    return 0


def render_icon(size: int) -> QImage:
    """Render a clean square icon with a document/checkup motif."""

    scale = size / 256
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor("#12324A"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, size, size, int(38 * scale), int(38 * scale))

    painter.setBrush(QColor("#F6FAFC"))
    painter.drawRoundedRect(
        int(58 * scale),
        int(34 * scale),
        int(118 * scale),
        int(168 * scale),
        int(12 * scale),
        int(12 * scale),
    )

    painter.setBrush(QColor("#D9E7EF"))
    points = [
        (int(145 * scale), int(34 * scale)),
        (int(176 * scale), int(65 * scale)),
        (int(145 * scale), int(65 * scale)),
    ]
    painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))

    pen = QPen(QColor("#2FA36B"), max(9, int(16 * scale)))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(int(88 * scale), int(133 * scale), int(115 * scale), int(160 * scale))
    painter.drawLine(int(115 * scale), int(160 * scale), int(174 * scale), int(98 * scale))

    painter.setPen(QColor("#12324A"))
    font = QFont("Segoe UI", max(8, int(35 * scale)), QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(
        0,
        int(190 * scale),
        size,
        int(50 * scale),
        Qt.AlignmentFlag.AlignCenter,
        "IED",
    )

    painter.end()
    return image


def write_ico(images: list[QImage], path: Path) -> None:
    """Write a Windows ICO file containing PNG-encoded image entries."""

    png_blobs = []
    for image in images:
        buffer = image_to_png_bytes(image)
        png_blobs.append((image.width(), image.height(), buffer))

    header_size = 6 + 16 * len(png_blobs)
    offset = header_size
    directory_entries = []
    image_data = []
    for width, height, blob in png_blobs:
        directory_entries.append(
            struct.pack(
                "<BBBBHHII",
                0 if width >= 256 else width,
                0 if height >= 256 else height,
                0,
                0,
                1,
                32,
                len(blob),
                offset,
            )
        )
        image_data.append(blob)
        offset += len(blob)

    with path.open("wb") as handle:
        handle.write(struct.pack("<HHH", 0, 1, len(png_blobs)))
        handle.write(b"".join(directory_entries))
        handle.write(b"".join(image_data))


def image_to_png_bytes(image: QImage) -> bytes:
    """Serialize a QImage to PNG bytes without temporary files."""

    from PySide6.QtCore import QBuffer, QByteArray, QIODevice

    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(data)


if __name__ == "__main__":
    raise SystemExit(main())
