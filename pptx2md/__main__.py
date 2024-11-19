import argparse
from pathlib import Path

import pptx2md.outputter as outputter
from pptx2md.log import setup_logging
from pptx2md.parser import parse
from pptx2md.types import ConversionConfig
from pptx2md.utils import load_pptx, prepare_titles

setup_logging(compat_tqdm=True)


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
                            help='keep wmf formatted image untouched(avoid exceptions under linux)')
    arg_parser.add_argument('--disable-color', action="store_true", help='do not add color HTML tags')
    arg_parser.add_argument('--disable-escaping',
                            action="store_true",
                            help='do not attempt to escape special characters')
    arg_parser.add_argument('--disable-notes', action="store_true", help='do not add presenter notes')
    arg_parser.add_argument('--enable-slides', action="store_true", help='deliniate slides `\n---\n`')
    arg_parser.add_argument('--try-multi-column', action="store_true", help='try to detect multi-column slides')
    arg_parser.add_argument('--wiki', action="store_true", help='generate output as wikitext(TiddlyWiki)')
    arg_parser.add_argument('--mdk', action="store_true", help='generate output as madoko markdown')
    arg_parser.add_argument('--qmd', action="store_true", help='generate output as quarto markdown presentation')
    arg_parser.add_argument('--min-block-size',
                            type=int,
                            default=15,
                            help='the minimum character number of a text block to be converted')
    arg_parser.add_argument("--page", type=int, default=None, help="only convert the specified page")

    args = arg_parser.parse_args()

    # Determine output path if not specified
    if args.output is None:
        extension = '.tid' if args.wiki else '.qmd' if args.qmd else '.md'
        args.output = Path(f'out{extension}')

    return ConversionConfig(pptx_path=args.pptx_path,
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
                            page=args.page)


def main():
    config = parse_args()

    if config.title_path:
        config.custom_titles = prepare_titles(config.title_path)

    prs = load_pptx(config.pptx_path)

    if str(config.output_path).endswith('.json'):
        with open(config.output_path, 'w') as f:
            f.write(parse(config, prs).model_dump_json(indent=2))
        return

    if config.is_wiki:
        out = outputter.wiki_outputter(config.output_path)
    elif config.is_mdk:
        out = outputter.madoko_outputter(config.output_path)
    elif config.is_qmd:
        out = outputter.quarto_outputter(config.output_path)
    else:
        out = outputter.md_outputter(config.output_path)

    parse(prs, out)


if __name__ == '__main__':
    main()
