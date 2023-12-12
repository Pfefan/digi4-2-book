import os
from concurrent.futures import ProcessPoolExecutor
import cairosvg
from PyPDF2 import PdfMerger
from slugify import slugify

class SVGtoPDFConverter:
    """
    A class to convert SVG files to PDF using cairo.
    """
    def __init__(self):
        pass

    def convert_single_svg_to_pdf(self, svg_file, svg_path):
        """
        Convert a single SVG file to PDF.

        Parameters:
        svg_file (str): The path to the SVG file.
        svg_path (str): The directory where the SVG file is located.

        Returns:
        str: The path to the generated PDF file.
        """
        pdf_filename = os.path.splitext(os.path.basename(svg_file))[0] + '.pdf'
        pdf_file = os.path.join(svg_path, 'temp_pdf', pdf_filename)

        cairosvg.svg2pdf(url=svg_file, write_to=pdf_file, unsafe=True)

        return pdf_file

    def convert_all_svgs_to_pdf(self, svg_path, filename):
        """
        Convert all SVG files in a directory to PDF.

        Parameters:
        svg_path (str): The directory where the SVG files are located.
        filename (str): The name of the output PDF file.
        
        Returns:
        bool: The successful execution of the conversion
        str: The error code when the program fails
        """
        merger = None
        os.makedirs("output", exist_ok=True)
        os.makedirs(os.path.join(svg_path, "temp_pdf"), exist_ok=True)

        svg_files = [os.path.join(svg_path, svg_filename) for svg_filename in os.listdir(svg_path) if svg_filename.endswith('.svg')]
        svg_files.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

        filename = slugify(filename) + ".pdf"
        output_pdf = os.path.join("output", filename)

        try:
            merger = PdfMerger()

            with ProcessPoolExecutor() as executor:
                pdf_files = executor.map(self.convert_single_svg_to_pdf, svg_files, [svg_path]*len(svg_files))

                for pdf_file in pdf_files:
                    merger.append(pdf_file)

            merger.write(output_pdf)
        except Exception as e:
            return False, str(e)
        finally:
            if merger is not None:
                merger.close()
        return True, ""
