from pptx import Presentation
from pptx2md.global_var import g
from pptx2md.outputter import md_outputter
from pptx2md.parser import parse
import argparse

# initialization functions
def prepare_titles(title_path):
    with open(title_path, 'r', encoding='utf8') as f:
        indent = -1
        for line in f.readlines():
            cnt = 0
            while line[cnt] == ' ':
                cnt += 1
            if cnt == 0:
                g.titles[line.strip()] = 1
            else:
                if indent == -1:
                    indent = cnt
                    g.titles[line.strip()] = 2
                else:
                    g.titles[line.strip()] = cnt // indent + 1
                    g.max_custom_title = max([g.max_custom_title, cnt // indent + 1])

arg_parser = argparse.ArgumentParser(description='Convert pptx to markdown')
arg_parser.add_argument('pptx_path', help='path to the pptx file to be converted')
arg_parser.add_argument('-t', '--title', help='path to the custom title list file')
arg_parser.add_argument('-o', '--output', help='path of the output file')
arg_parser.add_argument('-i', '--image_dir', help='where to put images extracted')
arg_parser.add_argument('--image_width', help='maximum image with in px', type=int, default=500)
arg_parser.add_argument('--disable_image', help='disable image extraction', action="store_true")
arg_parser.add_argument('--min_block_size', help='the minimum character number of a text block to be converted', type=int, default=15)

def main():
    args = arg_parser.parse_args()

    file_path = args.pptx_path
    g.file_prefix = ''.join(file_path.split('.')[:-1])

    if args.title:
        g.use_custom_title
        prepare_titles(args.title)
        g.use_custom_title = True
    
    out_path = 'out.md'
    if args.output:
        out_path
        out_path = args.output
    
    if args.image_dir:
        g.img_path
        g.img_path = args.image_dir

    if args.image_width:
        g.max_img_width
        g.max_img_width = args.image_width
    
    if args.min_block_size:
        g.text_block_threshold
        g.text_block_threshold = args.min_block_size
    
    if args.disable_image:
        g.disable_image = True
    

    prs = Presentation(file_path)
    out = md_outputter(out_path)
    parse(prs, out)


if __name__ == '__main__':
    main()
