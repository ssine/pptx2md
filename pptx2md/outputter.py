import os
import re
import urllib.parse

from rapidfuzz import fuzz

from pptx2md.global_var import g
from pptx2md.slide_data import ElementType, Presentation


class outputter(object):

    def __init__(self, file_path):
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        self.ofile = open(file_path, 'w', encoding='utf8')

    def output(self, presentation_data: Presentation):
        self.put_header()

        for slide_idx, slide in enumerate(presentation_data.slides):
            for element in slide.elements:
                if element.type == ElementType.TITLE:
                    self.put_title(element.content, element.level)
                elif element.type == ElementType.LIST_ITEM:
                    self.put_list(element.content, element.level)
                elif element.type == ElementType.PARAGRAPH:
                    self.put_para(element.content)
                elif element.type == ElementType.IMAGE:
                    path, max_width = element.content
                    self.put_image(path, max_width)
                elif element.type == ElementType.TABLE:
                    self.put_table(element.content)
                elif element.type == ElementType.NOTE:
                    self.put_note(element.content)
                elif element.type == ElementType.COLUMN_START:
                    self.put_column_start(element.content)
                elif element.type == ElementType.COLUMN_END:
                    self.put_column_end()

            if slide_idx < len(presentation_data.slides) - 1 and g.enable_slides:
                self.put_para("\n---\n")

        self.close()

    def put_header(self):
        pass

    def put_title(self, text, level):
        pass

    def put_list(self, text, level):
        pass

    def put_para(self, text):
        pass

    def put_image(self, path, max_width):
        pass

    def put_table(self, table):
        pass

    def get_accent(self, text):
        pass

    def get_strong(self, text):
        pass

    def get_colored(self, text, rgb):
        pass

    def get_hyperlink(self, text, url):
        pass

    def get_escaped(self, text):
        pass

    def write(self, text):
        self.ofile.write(text)

    def flush(self):
        self.ofile.flush()

    def close(self):
        self.ofile.close()


class md_outputter(outputter):
    # write outputs to markdown
    def __init__(self, file_path):
        super().__init__(file_path)
        self.esc_re1 = re.compile(r'([\\\*`!_\{\}\[\]\(\)#\+-\.])')
        self.esc_re2 = re.compile(r'(<[^>]+>)')

    def put_title(self, text, level):
        text = text.strip()
        if not fuzz.ratio(text, g.last_title.get(level, ''), score_cutoff=92):
            self.ofile.write('#' * level + ' ' + text + '\n\n')
            g.last_title[level] = text

    def put_list(self, text, level):
        self.ofile.write('  ' * level + '* ' + text.strip() + '\n')

    def put_para(self, text):
        self.ofile.write(text + '\n\n')

    def put_image(self, path, max_width=None):
        if max_width is None:
            self.ofile.write(f'![]({urllib.parse.quote(path)})\n\n')
        else:
            self.ofile.write(f'<img src="{path}" style="max-width:{max_width}px;" />\n\n')

    def put_table(self, table):
        gen_table_row = lambda row: '| ' + ' | '.join([c.replace('\n', '<br />') for c in row]) + ' |'
        self.ofile.write(gen_table_row(table[0]) + '\n')
        self.ofile.write(gen_table_row([':-:' for _ in table[0]]) + '\n')
        self.ofile.write('\n'.join([gen_table_row(row) for row in table[1:]]) + '\n\n')

    def get_accent(self, text):
        return ' _' + text + '_ '

    def get_strong(self, text):
        return ' __' + text + '__ '

    def get_colored(self, text, rgb):
        return ' <span style="color:#%s">%s</span> ' % (str(rgb), text)

    def get_hyperlink(self, text, url):
        return '[' + text + '](' + url + ')'

    def esc_repl(self, match):
        return '\\' + match.group(0)

    def get_escaped(self, text):
        text = re.sub(self.esc_re1, self.esc_repl, text)
        text = re.sub(self.esc_re2, self.esc_repl, text)
        return text


class wiki_outputter(outputter):
    # write outputs to wikitext
    def __init__(self, file_path):
        super().__init__(file_path)
        self.esc_re = re.compile(r'<([^>]+)>')

    def put_title(self, text, level):
        text = text.strip()
        if not fuzz.ratio(text, g.last_title.get(level, ''), score_cutoff=92):
            self.ofile.write('!' * level + ' ' + text + '\n\n')
            g.last_title[level] = text

    def put_list(self, text, level):
        self.ofile.write('*' * (level + 1) + ' ' + text.strip() + '\n')

    def put_para(self, text):
        self.ofile.write(text + '\n\n')

    def put_image(self, path, max_width):
        if max_width is None:
            self.ofile.write(f'<img src="{path}" />\n\n')
        else:
            self.ofile.write(f'<img src="{path}" width={max_width}px />\n\n')

    def get_accent(self, text):
        return ' __' + text + '__ '

    def get_strong(self, text):
        return ' \'\'' + text + '\'\' '

    def get_colored(self, text, rgb):
        return ' @@color:#%s; %s @@ ' % (str(rgb), text)

    def get_hyperlink(self, text, url):
        return '[[' + text + '|' + url + ']]'

    def esc_repl(self, match):
        return "''''" + match.group(0)

    def get_escaped(self, text):
        text = re.sub(self.esc_re, self.esc_repl, text)
        return text


class madoko_outputter(outputter):
    # write outputs to madoko markdown
    def __init__(self, file_path):
        super().__init__(file_path)
        self.ofile.write('[TOC]\n\n')
        self.esc_re1 = re.compile(r'([\\\*`!_\{\}\[\]\(\)#\+-\.])')
        self.esc_re2 = re.compile(r'(<[^>]+>)')

    def put_title(self, text, level):
        text = text.strip()
        if not fuzz.ratio(text, g.last_title.get(level, ''), score_cutoff=92):
            self.ofile.write('#' * level + ' ' + text + '\n\n')
            g.last_title[level] = text

    def put_list(self, text, level):
        self.ofile.write('  ' * level + '* ' + text.strip() + '\n')

    def put_para(self, text):
        self.ofile.write(text + '\n\n')

    def put_image(self, path, max_width):
        if max_width is None:
            self.ofile.write(f'<img src="{path}" />\n\n')
        elif max_width < 500:
            self.ofile.write(f'<img src="{path}" width={max_width}px />\n\n')
        else:
            self.ofile.write('~ Figure {caption: image caption}\n')
            self.ofile.write('![](%s){width:%spx;}\n' % (path, max_width))
            self.ofile.write('~\n\n')

    def get_accent(self, text):
        return ' _' + text + '_ '

    def get_strong(self, text):
        return ' __' + text + '__ '

    def get_colored(self, text, rgb):
        return ' <span style="color:#%s">%s</span> ' % (str(rgb), text)

    def get_hyperlink(self, text, url):
        return '[' + text + '](' + url + ')'

    def esc_repl(self, match):
        return '\\' + match.group(0)

    def get_escaped(self, text):
        text = re.sub(self.esc_re1, self.esc_repl, text)
        text = re.sub(self.esc_re2, self.esc_repl, text)
        return text


class quarto_outputter(outputter):
    # write outputs to quarto markdown - reveal js
    def __init__(self, file_path):
        super().__init__(file_path)
        self.esc_re1 = re.compile(r'([\\\*`!_\{\}\[\]\(\)#\+-\.])')
        self.esc_re2 = re.compile(r'(<[^>]+>)')

    def put_header(self):
        self.ofile.write('''---
title: "Presentation Title"
author: "Author"
format: 
  revealjs:
    slide-number: c/t
    width: 1600
    height: 900
    logo: img/logo.png
    footer: "Organization"
    incremental: true
    theme: [simple, custom.scss]
---
''')

    def put_title(self, text, level):
        text = text.strip()
        if not fuzz.ratio(text, g.last_title.get(level, ''), score_cutoff=92):
            self.ofile.write('#' * level + ' ' + text + '\n\n')
            g.last_title[level] = text
        else:
            # Allow for repeated slide titles - One or more - Add (cont.) to the title
            self.ofile.write('#' * level + ' ' + text + ' (cont.)' + '\n\n')
            g.last_title[level] = text

    def put_list(self, text, level):
        self.ofile.write('  ' * level + '* ' + text.strip() + '\n')

    def put_para(self, text):
        self.ofile.write(text + '\n\n')

    def put_image(self, path, max_width=None):
        if max_width is None:
            self.ofile.write(f'![]({urllib.parse.quote(path)})\n\n')
        else:
            self.ofile.write(f'<img src="{path}" style="max-width:{max_width}px;" />\n\n')

    def put_table(self, table):
        gen_table_row = lambda row: '| ' + ' | '.join([c.replace('\n', '<br />') for c in row]) + ' |'
        self.ofile.write(gen_table_row(table[0]) + '\n')
        self.ofile.write(gen_table_row([':-:' for _ in table[0]]) + '\n')
        self.ofile.write('\n'.join([gen_table_row(row) for row in table[1:]]) + '\n\n')

    def get_accent(self, text):
        return ' _' + text + '_ '

    def get_strong(self, text):
        return ' __' + text + '__ '

    def get_colored(self, text, rgb):
        return ' <span style="color:#%s">%s</span> ' % (str(rgb), text)

    def get_hyperlink(self, text, url):
        return '[' + text + '](' + url + ')'

    def esc_repl(self, match):
        return '\\' + match.group(0)

    def get_escaped(self, text):
        text = re.sub(self.esc_re1, self.esc_repl, text)
        text = re.sub(self.esc_re2, self.esc_repl, text)
        return text
