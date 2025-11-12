#!/usr/bin/env python3
"""
Herramienta simple para cambiar la velocidad de reproducción de un video usando ffmpeg.
Uso:
    python video_speed.py /ruta/al/video.mp4 x1.5
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
from typing import Tuple


def parse_speed(value: str) -> Tuple[float, str]:
    """Normaliza y valida la velocidad solicitada."""
    normalized = value.strip().lower()
    if normalized.startswith("x"):
        normalized = normalized[1:]
    normalized = normalized.replace(",", ".")

    try:
        speed = float(normalized)
    except ValueError as exc:  # pragma: no cover - defensive parsing
        raise ValueError(f"Velocidad inválida: {value}") from exc

    if speed <= 0:
        raise ValueError("La velocidad debe ser mayor que cero.")

    return speed, normalized


def build_atempo_chain(speed: float) -> str:
    """Devuelve una cadena de filtros atempo compatibles con ffmpeg."""
    filters = []
    remaining = speed

    while remaining > 2.0:
        filters.append(2.0)
        remaining /= 2.0

    while remaining < 0.5:
        filters.append(0.5)
        remaining /= 0.5

    if filters or abs(remaining - 1.0) > 1e-6:
        filters.append(remaining)

    parts = []
    for factor in filters:
        parts.append(f"atempo={factor:.6f}".rstrip("0").rstrip("."))

    return ",".join(parts)


def change_speed(input_path: pathlib.Path, speed: float, prefix: str) -> pathlib.Path:
    """Ejecuta ffmpeg para generar el video con otra velocidad."""
    output_name = f"{prefix}{input_path.name}"
    output_path = input_path.with_name(output_name)

    video_filter = f"setpts=PTS/{speed:.6f}".rstrip("0").rstrip(".")
    audio_filter = build_atempo_chain(speed)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-filter:v",
        video_filter,
    ]

    if audio_filter:
        cmd.extend(["-filter:a", audio_filter])

    cmd.append(str(output_path))

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:  # pragma: no cover - depende del entorno
        raise RuntimeError("ffmpeg no está instalado o no está en el PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"ffmpeg falló con código {exc.returncode}.") from exc

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aplica una velocidad (ej. x1.5) a un video usando ffmpeg."
    )
    parser.add_argument("video", type=pathlib.Path, help="Ruta al archivo de video.")
    parser.add_argument(
        "speed",
        type=str,
        help='Velocidad (ej. "x1.5", "0.75"). Se admite coma o punto decimal.',
    )

    args = parser.parse_args()

    video_path = args.video.expanduser().resolve()
    if not video_path.exists():
        parser.error(f"El archivo no existe: {video_path}")

    speed_value, speed_label = parse_speed(args.speed)
    prefix = f"_x_{speed_label.replace('.', '_')}"

    try:
        output_path = change_speed(video_path, speed_value, prefix)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Video generado: {output_path}")


if __name__ == "__main__":
    main()
