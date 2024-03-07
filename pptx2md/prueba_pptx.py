import pptx

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER, MSO_SHAPE_TYPE
from pptx.enum.dml import MSO_COLOR_TYPE, MSO_THEME_COLOR


# file_path = "C:/Users/daedr/Documents/Docencia_UIS/david_2022/recursos_docencia2022ii/sitio/original/3_SimDigital_28.03.2023.pptx"
file_path = "/home/daedro/Documentos/Dev2024/github_repos/derb_site/original/Simulacion/3_SimDigital_28.03.2023.pptx"

prs = Presentation(file_path)
total_slides = len(prs.slides)
print(total_slides)

def is_two_column_text(slide):
    if  slide.slide_layout.name != "TITLE":
        text_shapes = [shape for shape in slide.shapes if hasattr(shape, 'text_frame') and shape.text_frame]
        print("Cantidad text shapes: %d"%len(text_shapes))
        return len(text_shapes) >= 2
    else:
        return False


for slide_number, slide in enumerate(prs.slides, start=1):
    layout = slide.slide_layout
    print("\n---")
    print("Slide %d uses layout: %s"%(slide_number, layout.name))

    if is_two_column_text(slide):
        print("Slide %d migh have two-column text layout"%slide_number)
    else:
        print("No two column text layout for Slide %d"%slide_number)