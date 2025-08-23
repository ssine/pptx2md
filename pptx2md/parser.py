# Copyright 2024 Liu Siyao
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import subprocess
from functools import partial
from operator import attrgetter
from typing import List, Union

from PIL import Image
from pptx import Presentation
from pptx.enum.dml import MSO_COLOR_TYPE, MSO_THEME_COLOR
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from rapidfuzz import process as fuze_process
from tqdm import tqdm

from pptx2md.multi_column import get_multi_column_slide_if_present
from pptx2md.types import (
    ConversionConfig,
    GeneralSlide,
    ImageElement,
    ListItemElement,
    ParagraphElement,
    ParsedPresentation,
    SlideElement,
    TableElement,
    TextRun,
    TextStyle,
    TitleElement,
)

logger = logging.getLogger(__name__)
picture_count = 0


def is_title(shape):
    if shape.is_placeholder and shape.placeholder_format.type in {
        PP_PLACEHOLDER.TITLE,
        PP_PLACEHOLDER.SUBTITLE,
        PP_PLACEHOLDER.VERTICAL_TITLE,
        PP_PLACEHOLDER.CENTER_TITLE,
    }:
        return True
    return False


def is_text_block(config: ConversionConfig, shape):
    if shape.has_text_frame:
        if shape.is_placeholder and shape.placeholder_format.type == PP_PLACEHOLDER.BODY:
            return True
        if len(shape.text) > config.min_block_size:
            return True
    return False


def is_list_block(shape) -> bool:
    levels = []
    for para in shape.text_frame.paragraphs:
        if para.level not in levels:
            levels.append(para.level)
        if para.level != 0 or len(levels) > 1:
            return True
    return False


def is_accent(font):
    if font.underline or font.italic or (
        font.color.type == MSO_COLOR_TYPE.SCHEME
        and font.color.theme_color in {
            MSO_THEME_COLOR.ACCENT_1,
            MSO_THEME_COLOR.ACCENT_2,
            MSO_THEME_COLOR.ACCENT_3,
            MSO_THEME_COLOR.ACCENT_4,
            MSO_THEME_COLOR.ACCENT_5,
            MSO_THEME_COLOR.ACCENT_6,
        }
    ):
        return True
    return False


def is_strong(font):
    if font.bold or (
        font.color.type == MSO_COLOR_TYPE.SCHEME
        and font.color.theme_color in {MSO_THEME_COLOR.DARK_1, MSO_THEME_COLOR.DARK_2}
    ):
        return True
    return False


def get_text_runs(para) -> List[TextRun]:
    runs = []
    for run in para.runs:
        result = TextRun(text=run.text, style=TextStyle())
        if result.text == '':
            continue
        try:
            if run.hyperlink.address:
                result.style.hyperlink = run.hyperlink.address
        except:
            result.style.hyperlink = 'error:ppt-link-parsing-issue'
        if is_accent(run.font):
            result.style.is_accent = True
        if is_strong(run.font):
            result.style.is_strong = True
        if run.font.color.type == MSO_COLOR_TYPE.RGB:
            result.style.color_rgb = run.font.color.rgb
        runs.append(result)
    return runs


def process_title(config: ConversionConfig, shape, slide_idx) -> TitleElement:
    text = shape.text_frame.text.strip()
    if config.custom_titles:
        res = fuze_process.extractOne(text, config.custom_titles.keys(), score_cutoff=92)
        if not res:
            return TitleElement(content=text.strip(), level=max(config.custom_titles.values()) + 1)
        else:
            logger.info(f'Title in slide {slide_idx} "{text}" is converted to "{res[0]}" as specified in title file.')
            return TitleElement(content=res[0].strip(), level=config.custom_titles[res[0]])
    else:
        return TitleElement(content=text.strip(), level=1)


def process_text_blocks(config: ConversionConfig, shape, slide_idx) -> List[Union[ListItemElement, ParagraphElement]]:
    results = []
    if is_list_block(shape):
        for para in shape.text_frame.paragraphs:
            if para.text.strip() == '':
                continue
            text = get_text_runs(para)
            results.append(ListItemElement(content=text, level=para.level))
    else:
        for para in shape.text_frame.paragraphs:
            if para.text.strip() == '':
                continue
            text = get_text_runs(para)
            results.append(ParagraphElement(content=text))
    return results


def convert_wmf_to_svg(wmf_path: str, svg_path: str) -> bool:
    try:
        result = subprocess.run(
            ['inkscape', wmf_path, '--export-type=svg', '--export-filename=' + svg_path],
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to convert {wmf_path} to SVG: {e}")
        return False


def process_picture(config: ConversionConfig, shape, slide_idx) -> Union[ImageElement, None]:
    if config.disable_image:
        return None

    global picture_count
    file_prefix = ''.join(os.path.basename(config.pptx_path).split('.')[:-1])
    pic_name = file_prefix + f'_{picture_count}'
    pic_ext = shape.image.ext
    if not os.path.exists(config.image_dir):
        os.makedirs(config.image_dir)

    output_path = config.image_dir / f'{pic_name}.{pic_ext}'
    common_path = os.path.commonpath([config.output_path, config.image_dir])
    img_outputter_path = os.path.relpath(output_path, common_path)

    with open(output_path, 'wb') as f:
        f.write(shape.image.blob)
        picture_count += 1

    if pic_ext == 'wmf':
        svg_path = config.image_dir / f'{pic_name}.svg'
        if convert_wmf_to_svg(str(output_path), str(svg_path)):
            logger.info(f"Converted WMF {output_path} to SVG {svg_path}")
            img_outputter_path = os.path.relpath(svg_path, common_path)
            return ImageElement(path=img_outputter_path, width=config.image_width)
        else:
            logger.warning(f"Failed to convert WMF {output_path}, skipped.")
            return None
    else:
        return ImageElement(path=img_outputter_path, width=config.image_width)


def process_table(config: ConversionConfig, shape, slide_idx) -> Union[TableElement, None]:
    table = [
        [sum([get_text_runs(p) for p in cell.text_frame.paragraphs], []) for cell in row.cells]
        for row in shape.table.rows
    ]
    if table:
        return TableElement(content=table)
    return None


def ungroup_shapes(shapes) -> List[SlideElement]:
    res = []
    for shape in shapes:
        try:
            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                res.extend(ungroup_shapes(shape.shapes))
            else:
                res.append(shape)
        except Exception as e:
            logger.warning(f'Failed to load shape {shape}, skipped: {e}')
    return res


def process_shapes(config: ConversionConfig, shapes, slide_idx: int) -> List[SlideElement]:
    results = []
    for shape in shapes:
        if is_title(shape):
            results.append(process_title(config, shape, slide_idx))
        elif is_text_block(config, shape):
            results.extend(process_text_blocks(config, shape, slide_idx))
        elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            try:
                pic = process_picture(config, shape, slide_idx)
                if pic:
                    results.append(pic)
            except AttributeError as e:
                logger.warning(f"Failed to process picture: {e}")
        elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            table = process_table(config, shape, slide_idx)
            if table:
                results.append(table)
        else:
            try:
                ph = shape.placeholder_format
                if ph.type == PP_PLACEHOLDER.OBJECT and hasattr(shape, "image"):
                    pic = process_picture(config, shape, slide_idx)
                    if pic:
                        results.append(pic)
            except:
                pass
    return results


def parse(config: ConversionConfig, prs: Presentation) -> ParsedPresentation:
    result = ParsedPresentation(slides=[])

    for idx, slide in enumerate(tqdm(prs.slides, desc='Converting slides')):
        if config.page is not None and idx + 1 != config.page:
            continue

        try:
            shapes = [
                sp for sp in ungroup_shapes(slide.shapes)
                if getattr(sp, "top", None) is not None and getattr(sp, "left", None) is not None
            ]
            shapes.sort(key=attrgetter('top', 'left'))
        except Exception as e:
            logger.warning(f"Failed to sort shapes on slide {idx + 1}: {e}")
            shapes = []

        if config.try_multi_column:
            multi_column_slide = get_multi_column_slide_if_present(
                prs, slide, partial(process_shapes, config=config, slide_idx=idx + 1))
            result_slide = multi_column_slide if multi_column_slide else GeneralSlide(elements=process_shapes(config, shapes, idx + 1))
        else:
            result_slide = GeneralSlide(elements=process_shapes(config, shapes, idx + 1))

        if not config.disable_notes and slide.has_notes_slide:
            text = slide.notes_slide.notes_text_frame.text
            if text:
                result_slide.notes.append(text)

        result.slides.append(result_slide)

    return result

