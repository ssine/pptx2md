import logging
import os
import re
import shutil
import tempfile
import uuid

from pptx import Presentation

logger = logging.getLogger(__name__)


def fix_null_rels(file_path):
    temp_dir_name = tempfile.mkdtemp()
    shutil.unpack_archive(file_path, temp_dir_name, 'zip')
    rels = [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(temp_dir_name)
        for f in filenames
        if os.path.splitext(f)[1] == '.rels'
    ]
    pat = re.compile(r'<\S*Relationship[^>]+Target\S*=\S*"NULL"[^>]*/>', re.I)
    for fn in rels:
        f = open(fn, 'r+')
        content = f.read()
        res = pat.search(content)
        if res is not None:
            content = pat.sub('', content)
            f.seek(0)
            f.truncate()
            f.write(content)
        f.close()
    tfn = uuid.uuid4().hex
    shutil.make_archive(tfn, 'zip', temp_dir_name)
    shutil.rmtree(temp_dir_name)
    tgt = f'{file_path[:-5]}_purged.pptx'
    shutil.move(f'{tfn}.zip', tgt)
    return tgt


def load_pptx(file_path: str) -> Presentation:
    if not os.path.exists(file_path):
        logger.error(f'source file {file_path} not exist!')
        logger.error(f'absolute path: {os.path.abspath(file_path)}')
        raise FileNotFoundError(file_path)
    try:
        prs = Presentation(file_path)
    except KeyError as err:
        if len(err.args) > 0 and re.match(r'There is no item named .*NULL.* in the archive', str(err.args[0])):
            logger.info('corrupted links found, trying to purge...')
            try:
                res_path = fix_null_rels(file_path)
                logger.info(f'purged file saved to {res_path}.')
                prs = Presentation(res_path)
            except:
                logger.error(
                    'failed to purge corrupted links, you can report this at https://github.com/ssine/pptx2md/issues')
                raise err
        else:
            logger.error('unknown error, you can report this at https://github.com/ssine/pptx2md/issues')
            raise err
    return prs
