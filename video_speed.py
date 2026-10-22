#!/usr/bin/env python3
"""
Cambia la velocidad de un video y exporta MP4 sin alterar el tono del audio.

Requiere Python 3.9+ y FFmpeg instalado.

Ejemplos:
    python3 video_speed.py "mi video.mp4" x1.5
    python3 video_speed.py video.mkv 0,75 -o resultado.mp4
    python3 video_speed.py video.mp4 2x --overwrite

Conserva el primer video y todas las pistas de audio.
Omite subtítulos y capítulos porque sus tiempos también deberían ajustarse.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def parse_speed(value: str) -> float:
    """Acepta x1.5, 1.5x, 1.5 y 1,5."""
    text = value.strip().lower().replace(",", ".")

    if text.startswith("x"):
        text = text[1:]
    elif text.endswith("x"):
        text = text[:-1]

    try:
        speed = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Velocidad inválida: {value!r}."
        ) from exc

    if not math.isfinite(speed) or speed <= 0:
        raise argparse.ArgumentTypeError(
            "La velocidad debe ser un número finito mayor que cero."
        )

    return speed


def build_atempo_chain(speed: float) -> str:
    """Encadena factores entre 0.5 y 2 para conservar el tono del audio."""
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError("La velocidad debe ser finita y mayor que cero.")

    filters = []
    remaining = speed

    while remaining > 2:
        filters.append("atempo=2")
        remaining /= 2

    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining *= 2

    if remaining != 1 or not filters:
        filters.append(f"atempo={remaining!r}")

    return ",".join(filters)


def change_speed(
    source: Path,
    output: Path,
    speed: float,
    *,
    overwrite: bool = False,
    crf: int = 20,
    preset: str = "medium",
) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError(
            "FFmpeg no está instalado o no está en el PATH."
        )

    source = source.expanduser().resolve()
    output = output.expanduser().resolve()

    if not source.is_file():
        raise ValueError(
            f"La entrada no existe o no es un archivo: {source}"
        )

    if source == output or (
        output.exists() and source.samefile(output)
    ):
        raise ValueError(
            "La salida debe ser distinta del archivo original."
        )

    if output.suffix.lower() != ".mp4":
        raise ValueError(
            "El archivo de salida debe terminar en .mp4."
        )

    if not output.parent.is_dir():
        raise ValueError(
            f"La carpeta de salida no existe: {output.parent}"
        )

    if output.exists() and not overwrite:
        raise FileExistsError(
            f"Ya existe: {output}. "
            "Usá --overwrite para reemplazarlo."
        )

    if not 0 <= crf <= 51:
        raise ValueError("--crf debe estar entre 0 y 51.")

    tempo = build_atempo_chain(speed)

    # Escala los tiempos del video y adapta dimensiones impares a H.264.
    video_filter = (
        f"settb=AVTB,setpts=PTS/{speed!r},"
        "pad=ceil(iw/2)*2:ceil(ih/2)*2"
    )

    # Ajusta también el desfase inicial de cada pista de audio.
    audio_filter = (
        f"{tempo},asetpts=PTS-STARTPTS+STARTPTS/{speed!r}"
    )

    # Procesa primero en un temporal: un fallo no destruye una salida previa.
    with tempfile.TemporaryDirectory(
        prefix=".video-speed-",
        dir=output.parent,
    ) as folder:
        temporary = Path(folder) / "output.mp4"

        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel", "error",
            "-stats",
            "-nostdin",
            "-n",
            "-copyts",
            "-start_at_zero",
            "-i", str(source),
            "-map", "0:V:0",
            "-map", "0:a?",
            "-map_metadata", "0",
            "-map_chapters", "-1",
            "-vf", video_filter,
            "-af", audio_filter,
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-fps_mode", "vfr",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(temporary),
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"FFmpeg falló (código {exc.returncode}). "
                "Revisá el mensaje anterior."
            ) from exc

        if overwrite:
            os.replace(temporary, output)
        else:
            # No reemplaza archivos, incluso si otro proceso creó la salida
            # mientras FFmpeg estaba trabajando.
            os.link(temporary, output)

    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Cambia la velocidad de un video y genera un MP4 "
            "con video H.264 y audio AAC."
        )
    )

    parser.add_argument(
        "video",
        type=Path,
        help="Ruta al video original.",
    )
    parser.add_argument(
        "speed",
        type=parse_speed,
        help="Velocidad: x1.5, 1.5x, 0.75 o 0,75.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Ruta del archivo de salida .mp4.",
    )
    parser.add_argument(
        "-y", "--overwrite",
        action="store_true",
        help="Reemplazar la salida si existe.",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=20,
        help="Calidad de 0 a 51; menor es mejor (predeterminado: 20).",
    )
    parser.add_argument(
        "--preset",
        default="medium",
        choices=[
            "ultrafast", "superfast", "veryfast", "faster", "fast",
            "medium", "slow", "slower", "veryslow",
        ],
        help=(
            "Velocidad de codificación; más lento suele comprimir mejor "
            "(predeterminado: medium)."
        ),
    )

    args = parser.parse_args()

    try:
        label = str(args.speed).removesuffix(".0").replace(".", "_")
        output = args.output or args.video.with_name(
            f"{args.video.stem}_x{label}.mp4"
        )

        result = change_speed(
            args.video,
            output,
            args.speed,
            overwrite=args.overwrite,
            crf=args.crf,
            preset=args.preset,
        )

    except KeyboardInterrupt:
        print("\nConversión cancelada.", file=sys.stderr)
        return 130
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Video generado: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
