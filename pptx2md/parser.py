from __future__ import print_function
import pptx
from pptx.enum.shapes import PP_PLACEHOLDER, MSO_SHAPE_TYPE
from pptx.enum.dml import MSO_COLOR_TYPE, MSO_THEME_COLOR
from PIL import Image
import os
from rapidfuzz import process as fuze_process
from operator import attrgetter
from pptx2md.global_var import g
from pptx2md import global_var

picture_count = 0
slide_count = 0
global out

# pptx type defination rules
def is_title(shape):
    if shape.is_placeholder and (
        shape.placeholder_format.type == PP_PLACEHOLDER.TITLE
        or shape.placeholder_format.type == PP_PLACEHOLDER.SUBTITLE
        or shape.placeholder_format.type == PP_PLACEHOLDER.VERTICAL_TITLE
        or shape.placeholder_format.type == PP_PLACEHOLDER.CENTER_TITLE):
        return True
    return False

def is_text_block(shape):
    if shape.has_text_frame:
        if shape.is_placeholder and shape.placeholder_format.type == PP_PLACEHOLDER.BODY:
            return True
        if len(shape.text) > g.text_block_threshold:
            return True
    return False

def is_list_block(shape):
    levels = []
    for para in shape.text_frame.paragraphs:
        if para.level not in levels:
            levels.append(para.level)
        if para.level != 0 or len(levels) > 1:
            return True
    return False

def is_accent(font):
    if font.underline or font.italic or (font.color.type == MSO_COLOR_TYPE.SCHEME
                and (font.color.theme_color == MSO_THEME_COLOR.ACCENT_1
                    or font.color.theme_color == MSO_THEME_COLOR.ACCENT_2
                    or font.color.theme_color == MSO_THEME_COLOR.ACCENT_3
                    or font.color.theme_color == MSO_THEME_COLOR.ACCENT_4
                    or font.color.theme_color == MSO_THEME_COLOR.ACCENT_5
                    or font.color.theme_color == MSO_THEME_COLOR.ACCENT_6)):
        return True
    return False

def is_strong(font):
    if font.bold or (font.color.type == MSO_COLOR_TYPE.SCHEME
                and (font.color.theme_color == MSO_THEME_COLOR.DARK_1
                    or font.color.theme_color == MSO_THEME_COLOR.DARK_2)):
        return True
    return False

def get_formatted_text(para):
    res = ''
    for run in para.runs:
        text = run.text.strip()
        if text == '':
            continue
        text = out.get_escaped(text)
        if run.hyperlink.address:
            text = out.get_hyperlink(text, run.hyperlink.address)
        if is_accent(run.font):
            text = out.get_accent(text)
        elif is_strong(run.font):
            text = out.get_strong(text)
        if run.font.color.type == MSO_COLOR_TYPE.RGB:
            text = out.get_colored(text, run.font.color.rgb)
        res += text
    return res.strip()


def process_title(shape):
    global out
    text = shape.text_frame.text.strip()
    if g.use_custom_title:
        res = fuze_process.extractOne(text, g.titles.keys(), score_cutoff=92)
        if not res:
            g.max_custom_title
            out.put_title(text, g.max_custom_title + 1)
        else:
            print(text, ' transferred to ', res[0], '. the ratio is ', round(res[1]))
            out.put_title(res[0], g.titles[res[0]])
    else:
        out.put_title(text, 1)


def process_text_block(shape):
    global out
    if is_list_block(shape):
        # generate list block
        for para in shape.text_frame.paragraphs:
            if para.text.strip() == '':
                continue
            text = get_formatted_text(para)
            out.put_list(text, para.level)
        out.write('\n')
    else:
        # generate paragraph block
        for para in shape.text_frame.paragraphs:
            if para.text.strip() == '':
                continue
            text = get_formatted_text(para)
            out.put_para(text)

def process_picture(shape):
    if g.disable_image:
        return
    global picture_count
    global out
    pic_name = g.file_prefix + str(picture_count)
    pic_ext = shape.image.ext
    width = min(shape.image.size[0], g.max_img_width)
    if not os.path.exists(g.img_path):
        os.makedirs(g.img_path)

    output_path = g.path_name_ext(g.img_path, pic_name, pic_ext)
    common_path = os.path.commonpath([g.out_path, g.img_path])
    img_outputter_path = os.path.relpath(output_path, common_path)
    with open(output_path, 'wb') as f:
        f.write(shape.image.blob)
        picture_count += 1
    if pic_ext == 'wmf':
        if not g.disable_wmf:
            Image.open(output_path).save(os.path.splitext(output_path)[0]+'.png')
            out.put_image(os.path.splitext(img_outputter_path)[0]+'.png', width)
    else:
        out.put_image(img_outputter_path, width)

def ungroup_shapes(shapes):
    res = []
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            res.extend(ungroup_shapes(shape.shapes))
        else:
            res.append(shape)
    return res

# main
def parse(prs, outputer):
    global out
    out = outputer
    for slide in prs.slides:
        global slide_count
        slide_count += 1
        print('processing slide %d...' % slide_count)

        shapes = []
        try:
            shapes = sorted(ungroup_shapes(slide.shapes), key=attrgetter('top', 'left'))
        except:
            print('Bad shapes encountered in this slide. Please check or move them and try again.')
            print('shapes:')
            for sp in slide.shapes:
                print(sp.shape_type)
                print(sp.top, sp.left, sp.width, sp.height)
                
        for shape in shapes:
            if is_title(shape):
                process_title(shape)
            elif is_text_block(shape):
                process_text_block(shape)
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                process_picture(shape)
    out.close()
    print('all done!')
