# Copyright 2024 Liu Siyao
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import argparse
import logging
import subprocess
import sys
import re
from pathlib import Path
from pptx2md.entry import convert
from pptx2md.log import setup_logging
from pptx2md.types import ConversionConfig

setup_logging(compat_tqdm=True)
logger = logging.getLogger(__name__)


def parse_args() -> ConversionConfig:
    arg_parser = argparse.ArgumentParser(description='Convert pptx to markdown')
    arg_parser.add_argument('pptx_path', type=Path, help='path to the pptx file to be converted')
    arg_parser.add_argument('-t', '--title', type=Path, help='path to the custom title list file')
    arg_parser.add_argument('-o', '--output', type=Path, help='path of the output file')
    arg_parser.add_argument('-i', '--image-dir', type=Path, help='where to put images extracted')
    arg_parser.add_argument('--image-width', type=int, help='maximum image with in px')
    arg_parser.add_argument('--disable-image', action="store_true", help='disable image extraction')
    arg_parser.add_argument('--disable-wmf',
                            action="store_true",
                            help='keep wmf formatted image untouched (avoid exceptions under linux)')
    arg_parser.add_argument('--disable-color', action="store_true", help='do not add color HTML tags')
    arg_parser.add_argument('--disable-escaping', action="store_true", help='do not escape special characters')
    arg_parser.add_argument('--disable-notes', action="store_true", help='do not add presenter notes')
    arg_parser.add_argument('--enable-slides', action="store_true", help='deliniate slides `\n---\n`')
    arg_parser.add_argument('--try-multi-column', action="store_true", help='try to detect multi-column slides')
    arg_parser.add_argument('--wiki', action="store_true", help='generate output as wikitext(TiddlyWiki)')
    arg_parser.add_argument('--mdk', action="store_true", help='generate output as madoko markdown')
    arg_parser.add_argument('--qmd', action="store_true", help='generate output as quarto markdown presentation')
    arg_parser.add_argument('--min-block-size',
                            type=int,
                            default=15,
                            help='minimum characters per text block')
    arg_parser.add_argument("--page", type=int, default=None, help="only convert the specified page")
    arg_parser.add_argument("--keep-similar-titles", action="store_true",
                            help="allow repeated slide titles (append '(cont.)')")

    args = arg_parser.parse_args()

    extension = '.tid' if args.wiki else '.qmd' if args.qmd else '.md'
    if args.output is None:
        args.output = Path(f'out{extension}')

    return ConversionConfig(
        pptx_path=args.pptx_path,
        output_path=args.output,
        image_dir=args.image_dir or args.output.parent / 'img',
        title_path=args.title,
        image_width=args.image_width,
        disable_image=args.disable_image,
        disable_wmf=args.disable_wmf,
        disable_color=args.disable_color,
        disable_escaping=args.disable_escaping,
        disable_notes=args.disable_notes,
        enable_slides=args.enable_slides,
        try_multi_column=args.try_multi_column,
        is_wiki=args.wiki,
        is_mdk=args.mdk,
        is_qmd=args.qmd,
        min_block_size=args.min_block_size,
        page=args.page,
        keep_similar_titles=args.keep_similar_titles,
    )


def convert_wmf_to_svg(imgpath: Path):
    for wmf in sorted(imgpath.glob("*.wmf")):
        svg = wmf.with_suffix(".svg")
        try:
            subprocess.run([
                "inkscape", str(wmf),
                "--export-type=svg",
                "--export-filename", str(svg),
                "--export-plain-svg"
            ], check=True)
            print(f"[INFO] Converted {wmf.name} → {svg.name}")
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Failed to convert {wmf.name} to SVG: {e}")


def inject_svg_includes(md_file: Path, imgpath: Path, base_name: str):
    lines = md_file.read_text(encoding="utf-8").splitlines()
    new_lines = []
    slide_counter = 0

    for line in lines:
        if line.startswith("# "):
            slide_counter += 1
        new_lines.append(line)

        svg_file = imgpath / f"{base_name}_{slide_counter}.svg"
        if svg_file.exists():
            include_line = fr"\includesvg[width=0.9\linewidth]{{./{imgpath.name}/{svg_file.stem}}}"
            if include_line not in new_lines:
                new_lines.append("")
                new_lines.append(f"<!-- Converted WMF image from Slide {slide_counter} -->")
                new_lines.append(include_line)
                new_lines.append("")

    md_file.write_text("\n".join(new_lines), encoding="utf-8")


def main():
    config = parse_args()
    convert(config)

    if not config.disable_wmf:
        convert_wmf_to_svg(config.image_dir)
        inject_svg_includes(config.output_path, config.image_dir, config.pptx_path.stem)


if __name__ == '__main__':
    main()

