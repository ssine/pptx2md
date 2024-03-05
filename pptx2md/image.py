# --coding:utf-8-- 
# author = ''


def convert_wmf_to_png(input_file, output_png_path):
    """
    Convert WMF data to a PNG file.

    """
    # from PIL import ImageGrab
    # shape.Copy()
    # image = ImageGrab.grabclipboard()
    # #image.save('{}.jpg'.format(filename), 'jpeg')
    # image.save(output_png_path)

    # from PIL import Image
    # Image.open(input_file).save(output_png_path)

    from wand.image import Image

    with Image(filename=input_file) as img:
        img.format = 'png'
        img.save(filename=output_png_path)
