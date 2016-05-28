usage: pdfformulas.py [-h] [--dxmin DXMIN] [--frompage FROMPAGE]
                      [--topage TOPAGE] [--page PAGE] [--formulaid FORMULAID]
                      [--stats]
                      pdffile

Dump the formulas of a PDF as PNG files in the ``formulas`` subfolder. The
subfolder ``formulas`` is created, if not there yet. The PDF content must be
accessible as text. 

positional arguments:
  pdffile               PDF file to parse and dump formulas of

optional arguments:
  -h, --help            show this help message and exit
  --dxmin DXMIN         Additional left margin, which defines what is normal
                        text. If the text before a formula is the beginning of
                        a paragraph it might start a little indented. In this
                        case it helps to move dxmin to the right. Units are
                        those used in the PDF. Try 10.
  --frompage FROMPAGE   PDF page number to start with.
  --topage TOPAGE       PDF page number to stop at.
  --page PAGE           PDF page number
  --formulaid FORMULAID
                        The regular expression by which a formula is found.
                        Formulas are recognized by their ID on the right. The
                        regular expression used is:: r'^\s*\(\d*\.\d*\)\s* '
                        e.g.:: (2.13) To find the rectangle comprising the
                        formula the text before and after is located, which
                        begins on the left of the page (dxmin). The formula is
                        assumed to be indented with regard to normal text.
  --stats               Only print (formula,page)-refs statistics. This tells
                        which formulas are most often referenced in normal
                        text and are thus likely the most important ones.


Requires: Pillow, PyMuPDF (needs compatible MuPDF installed), PdfMiner
Installation: LibMuPDF and PyMuPDF will need to be installed beforehand.
