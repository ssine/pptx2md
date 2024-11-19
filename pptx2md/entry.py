import logging

import pptx2md.outputter as outputter
from pptx2md.parser import parse
from pptx2md.types import ConversionConfig
from pptx2md.utils import load_pptx, prepare_titles

logger = logging.getLogger(__name__)


def convert(config: ConversionConfig):
    if config.title_path:
        config.custom_titles = prepare_titles(config.title_path)

    prs = load_pptx(config.pptx_path)

    logger.info("conversion started")

    ast = parse(config, prs)

    if str(config.output_path).endswith('.json'):
        with open(config.output_path, 'w') as f:
            f.write(ast.model_dump_json(indent=2))
        logger.info(f'presentation data saved to {config.output_path}')
        return

    if config.is_wiki:
        out = outputter.WikiFormatter(config)
    elif config.is_mdk:
        out = outputter.MadokoFormatter(config)
    elif config.is_qmd:
        out = outputter.QuartoFormatter(config)
    else:
        out = outputter.MarkdownFormatter(config)

    out.output(ast)
    logger.info(f'converted document saved to {config.output_path}')
