import tempfile, os, fnmatch, re, shutil, uuid


def fix_null_rels(file_path):
  temp_dir_name = tempfile.mkdtemp()
  shutil.unpack_archive(file_path, temp_dir_name, 'zip')
  rels = [
      os.path.join(dp, f) for dp, dn, filenames in os.walk(temp_dir_name) for f in filenames
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
