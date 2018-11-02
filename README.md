# PPTX2MD

A tool to convert pptx into markdown.

## Installation & Usage

How to install:

1. make an empty directory
2. `git clone `
3. `pip install .`
4. this directory is useless then, remove it as you like

How to use:

Once you have installed it, use the command `pptx2md [filename]` to convert pptx file into markdown.

__Note.__ older .ppt files are not supported.

The default output filename is `out.md`, and any pictures extracted (and inserted into .md) will be placed in `/img/` folder.

### Custom Titles

This tool can only parse all the pptx titles into level 1 md titles, in order to get a hierarchical table of contents, specify your predefined title list in a file and provide it in `-t` argument:

This is a example title file

```
Data Link Layer Design Issues
  Services Provided to the Network Layer
  Framing
  Error Control & Flow Control
Error Detection and Correction
  Error Correcting Code (ECC)
  Error Detecting Code
Elementary Data Link Protocols
Sliding Window Protocols
  One-Bit Sliding Window Protocol
  Protocol Using Go Back N
  Using Selective Repeat
Performance of Sliding Window Protocols
Example Data Link Protocols
  PPP
```

Use it as `pptx2md [filename] -t titles.txt`.

### Other Arguments

* `-t` specify the title file
* `-o` path of the output file
* `-i` directory of the extracted pictures
* `--image_width` the maximum width of the pictures, in px.
* `--min_block_size` the minimum number of characters for a block to be outputted

## Screenshots

<img src="https://sine-img-bed.oss-cn-beijing.aliyuncs.com/pptx2md/pic1.png" height=400 >

The table of contents generated, after specifying a title list as above.

![2](https://sine-img-bed.oss-cn-beijing.aliyuncs.com/pptx2md/pic2.png)

* Left: source pptx file.
* Right: generated markdown file (rendered by madoko).

## Detailed Parse Rules

This part will be updated later.

1. 生成带有层级的列表
   * 每个para的level不同或不等于1时生成列表，否则生成段落块
2. Placeholder - TITLE 转换为md标题
   * 可以手动指定title层级
   * 与上一个title相同时不再重复
3. 保留部分字体样式（红色、加粗、斜体）
   * 主题预设样式/自带粗体斜体转换为粗体/斜体
   * RGB颜色原样保留
4. 图片转换成文件，在md中插入链接
   * 按比例缩放图片大小
5. (可选的)将中文标点转换为英文？
6. 解析顺序：从上至下、从左至右
7. 源文本转义
