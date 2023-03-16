import collections 
import collections.abc
from pptx import Presentation
from pptx2md.global_var import g
import pptx2md.outputter as outputter
from pptx2md.parser import parse
from pptx2md.tools import fix_null_rels
import argparse
import os, re


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


def parse_args():
  arg_parser = argparse.ArgumentParser(description='Convert pptx to markdown')
  arg_parser.add_argument('pptx_path', help='path to the pptx file to be converted')
  arg_parser.add_argument('-t', '--title', help='path to the custom title list file')
  arg_parser.add_argument('-o', '--output', help='path of the output file')
  arg_parser.add_argument('-i', '--image-dir', help='where to put images extracted')
  arg_parser.add_argument('--image-width', help='maximum image with in px', type=int)
  arg_parser.add_argument('--disable-image', help='disable image extraction', action="store_true")
  arg_parser.add_argument('--disable-wmf',
                          help='keep wmf formatted image untouched(avoid exceptions under linux)',
                          action="store_true")
  arg_parser.add_argument('--disable-color', help='do not add color HTML tags', action="store_true")
  arg_parser.add_argument('--disable-escaping', help='do not attempt to escape special characters', action="store_true")
  arg_parser.add_argument('--wiki', help='generate output as wikitext(TiddlyWiki)', action="store_true")
  arg_parser.add_argument('--mdk', help='generate output as madoko markdown', action="store_true")
  arg_parser.add_argument('--min-block-size',
                          help='the minimum character number of a text block to be converted',
                          type=int,
                          default=15)
  return arg_parser.parse_args()


def main():
  args = parse_args()

  file_path = args.pptx_path
  g.file_prefix = ''.join(os.path.basename(file_path).split('.')[:-1])

  if args.title:
    g.use_custom_title
    prepare_titles(args.title)
    g.use_custom_title = True

  if args.wiki:
    out_path = 'out.tid'
  else:
    out_path = 'out.md'

  if args.output:
    out_path = args.output

  g.out_path = os.path.abspath(out_path)
  g.img_path = os.path.join(out_path, '../img')

  if args.image_dir:
    g.img_path = args.image_dir

  g.img_path = os.path.abspath(g.img_path)

  if args.image_width:
    g.max_img_width = args.image_width

  if args.min_block_size:
    g.text_block_threshold = args.min_block_size

  if args.disable_image:
    g.disable_image = True
  else:
    g.disable_image = False

  if args.disable_wmf:
    g.disable_wmf = True
  else:
    g.disable_wmf = False

  if args.disable_color:
    g.disable_color = True
  else:
    g.disable_color = False

  if args.disable_escaping:
    g.disable_escaping = True
  else:
    g.disable_escaping = False

  if not os.path.exists(file_path):
    print(f'source file {file_path} not exist!')
    print(f'absolute path: {os.path.abspath(file_path)}')
    exit(0)
  try:
    prs = Presentation(file_path)
  except KeyError as err:
    if len(err.args) > 0 and re.match(r'There is no item named .*NULL.* in the archive', str(err.args[0])):
      print('corrupted links found, trying to purge...')
      try:
        res_path = fix_null_rels(file_path)
        print(f'purged file saved to {res_path}.')
        prs = Presentation(res_path)
      except:
        print('failed, please report this bug at https://github.com/ssine/pptx2md/issues')
        exit(0)
    else:
      print('unknown error, please report this bug at https://github.com/ssine/pptx2md/issues')
      exit(0)
  if args.wiki:
    out = outputter.wiki_outputter(out_path)
  elif args.mdk:
    out = outputter.madoko_outputter(out_path)
  else:
    out = outputter.md_outputter(out_path)
  parse(prs, out)


if __name__ == '__main__':
  main()
