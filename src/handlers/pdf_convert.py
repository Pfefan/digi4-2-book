import os
import string
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from concurrent.futures import ProcessPoolExecutor

class Convert:
    def __init__(self):
        pass

    def svg_to_pdf_handler(self, svg_file, svg_path):
            return self.svg_to_pdf(svg_file, svg_path)

    def svg_to_pdf(self, svg_file, svg_path):
        drawing = svg2rlg(svg_file)
        pdf_filename = os.path.splitext(os.path.basename(svg_file))[0] + '.pdf'
        pdf_file = os.path.join(svg_path, 'temp_pdf', pdf_filename)
        canvas_obj = canvas.Canvas(pdf_file, pagesize=A4)
        page_width, page_height = A4
        drawing_width, drawing_height = drawing.minWidth(), drawing.height
        scale_factor = min(page_width / drawing_width, page_height / drawing_height)
        drawing.width, drawing.height = drawing_width * scale_factor, drawing_height * scale_factor
        drawing.scale(scale_factor, scale_factor)
        drawing.drawOn(canvas_obj, x=0, y=0)
        canvas_obj.save()
        return pdf_file

    def convert_svg_to_pdf(self, svg_path, filename):
        svg_files = [os.path.join(svg_path, svg_filename) for svg_filename in os.listdir(svg_path) if svg_filename.endswith('.svg')]
        svg_files.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

        os.makedirs("output", exist_ok=True)
        os.makedirs(os.path.join(svg_path, "temp_pdf"), exist_ok=True)

        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        output_pdf = ''.join(c if c in valid_chars else '_' for c in filename) + ".pdf"
        output_pdf = os.path.join("output", output_pdf)

        merger = PdfMerger()

        # Convert each SVG file to PDF in parallel using a process pool
        with ProcessPoolExecutor() as executor:
            pdf_files = executor.map(self.svg_to_pdf_handler, svg_files, [svg_path]*len(svg_files))

            for pdf_file in pdf_files:
                merger.append(pdf_file)

        merger.write(output_pdf)
        merger.close()