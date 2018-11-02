from fuzzywuzzy import fuzz
from pptx2md.global_var import g
import re

class outputter(object):
    def __init__(self, file_path):
        self.ofile = open(file_path, 'w', encoding='utf8')
    def put_title(self, text, level):
        pass
    def put_list(self, text, level):
        pass
    def put_para(self, text):
        pass
    def put_image(self, path, width):
        pass
    def get_accent(self, text):
        pass
    def get_strong(self, text):
        pass
    def get_colored(self, text, rgb):
        pass
    def get_escaped(self, text):
        pass
    def write(self, text):
        self.ofile.write(text)


class md_outputter(outputter):
    # write outputs to markdown
    def __init__(self, file_path):
        self.ofile = open(file_path, 'w', encoding='utf8')
        self.esc_re1 = re.compile(r'([\\\*`!_\{\}\[\]\(\)#\+-\.])')
        self.esc_re2 = re.compile(r'(<[^>]+>)')

    def put_title(self, text, level):
        text = text.strip()
        if fuzz.ratio(text, g.last_title.get(level, '')) < 92:
            self.ofile.write('#'*level + ' ' + text + '\n\n')
            g.last_title[level] = text

    def put_list(self, text, level):
        self.ofile.write('  '*level + '* ' + text.strip() + '\n')
        
    def put_para(self, text):
        self.ofile.write(text + '\n\n')

    def put_image(self, path, width):
        self.ofile.write('<img src="%s" width=%spx />\n\n' % (path, width))
    
    def get_accent(self, text):
        return ' _' + text + '_ '
    
    def get_strong(self, text):
        return ' __' + text + '__ '

    def get_colored(self, text, rgb):
        return ' <span style="color:#%s">%s</span> ' % (str(rgb), text)

    def esc_repl(delf, match):
        return '\\' + match.group(0)
        pass

    def get_escaped(self, text):
        text = re.sub(self.esc_re1, self.esc_repl, text)
        text = re.sub(self.esc_re2, self.esc_repl, text)
        return text


class wiki_outputter(outputter):
    # write outputs to markdown
    def put_title(self, text, level):
        text = text.strip()
        if fuzz.ratio(text, g.last_title.get(level, '')) < 92:
            self.ofile.write('!'*level + ' ' + text + '\n\n')
            g.last_title[level] = text

    def put_list(self, text, level):
        self.ofile.write('*'*level + ' ' + text.strip() + '\n')
        
    def put_para(self, text):
        self.ofile.write(text + '\n\n')

    def put_image(self, path, width):
        self.ofile.write('<img src="%s" width=%spx />\n\n' % (path, width))
    
    def get_accent(self, text):
        return ' __' + text + '__ '
    
    def get_strong(self, text):
        return ' \'\'' + text + '\'\' '

    def get_colored(self, text, rgb):
        return ' @@color:%s;%s@@ ' % (str(rgb), text)