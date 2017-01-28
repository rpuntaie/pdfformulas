#!/usr/bin/env python2
# vim: fileencoding=utf-8 

"""
Dump the formulas of a PDF
as PNG files in the ``formulas`` subfolder.

The subfolder ``formulas`` is created, if not there yet.

The PDF content must be accessible as text.

Requires:Pillow, PyMuPDF, PdfMiner
"""

from __future__ import print_function
import os, os.path, sys

# https://github.com/rk700/PyMuPDF -> fitz
# https://github.com/euske/pdfminer


if sys.version_info.major == 3:
    print("This depends on pdfminer and is therefore restricted to Python2.")
    sys.exit()
else:
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfpage import PDFTextExtractionNotAllowed
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.converter import PDFPageAggregator
    from pdfminer.layout import LAParams, LTTextBox, LTChar
    import fitz
    import re
    import tempfile
    from PIL import Image, ImageChops
    from collections import defaultdict, Iterable

import argparse

FORMULA_ID = r'\(\d+\.\d+\)'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('pdffile', type=str, help='PDF file to parse and dump formulas of')
parser.add_argument('--dxmin', dest='dxmin', type=int, action='store', default=0, 
                   help="""Additional left margin, which defines what is normal text.

If the text before a formula is the beginning of a paragraph
it might start a little indented.
In this case it helps to move dxmin to the right.
Units are those used in the PDF. Try 10.""")
parser.add_argument('--frompage', type=int, dest='frompage', action='store', 
                    default=None, help='PDF page number to start with.')
parser.add_argument('--topage', type=int, dest='topage', action='store', 
                   default=None, help='PDF page number to stop at.')
parser.add_argument('--page', type=int, dest='page', action='store', 
                   default=None, help='PDF page number')
parser.add_argument('--formulaid', type=str, dest='formulaid', action='store',
                   default=FORMULA_ID,
                   help="""The regular expression by which a formula is found.

Formulas are recognized by their ID on the right.
The regular expression used is::

    r'^\s*\(\d*\.\d*\)\s*\n'

e.g.::

    (2.13)

To find the rectangle comprising the formula
the text before and after is located,
which begins on the left of the page (dxmin).
The formula is assumed to be indented
with regard to normal text.""")
parser.add_argument('--stats', dest='stats', action='store_true', 
                   default=False, help="""Only print (formula,page)-refs statistics.
This tells which formulas are most often referenced in normal text
and are thus likely the most important ones.""")


def main():
    args = parser.parse_args()
    #args = self
    #args.formulaid = FORMULA_ID
    #args.dxmin = 0
    #args.stats = True
    #args.frompage = 15
    #args.topage = 907
    ##args.page = 408#283+14
    ##args.pdffile = '/mnt/usb/donkoks/ExplorationInMathematicalPhysics_ElegantLanguage.pdf'
    #args.pdffile = '/mnt/u/temp/stone_goldbart.pdf'

    pdffile = args.pdffile 
    imagefolder = os.path.join(os.path.dirname(pdffile),'formulas')
    self = formulas_to_images(pdffile,imagefolder,args.formulaid, args.dxmin)
    if not os.path.exists(imagefolder):
        os.mkdir(imagefolder)
    if args.page:
        args.frompage = args.page
        args.topage = args.page
    if args.stats:
        f_p_rs = self.formula_page_refs(args.frompage, args.topage)
        for frm, pgs in sorted(f_p_rs.items(),key=lambda x:len(x[1]),reverse=True): 
            print(frm)
            for pnum in pgs:
                print("  ", pnum)
    else:
        self(args.frompage,args.topage)


def _trim(im):
    px = im.getpixel((0,0))
    bg = Image.new(im.mode, im.size, px)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def _first_char(o):
    while not isinstance(o._objs[0], LTChar):
        o = o._objs[0]
    return o._objs[0]

def _last_char(o):
    while not isinstance(o._objs[0], LTChar):
        o = o._objs[0]
    for i,o in enumerate(reversed(o._objs)):
        if isinstance(o, LTChar):
            break
    #o
    return o

class formulas_to_images:
    """ convert mathematical formulas of a pdf to images 
    and dump them in the ``formulas`` subfolder.

    feh is good to check the images
    """

    def __init__(self, pdffile, imagefolder, formulaid = FORMULA_ID, dxmin=0): 
        #imagefolder, formulaid, dxmin = imagefolder,args.formulaid, args.dxmin

        self.pdffile     = pdffile     
        self.imagefolder = imagefolder 

        parser = PDFParser(open(pdffile, 'rb'))
        self.doc = PDFDocument(parser, "")
        if not self.doc.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        self.device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        self.interpreter = PDFPageInterpreter(rsrcmgr, self.device)

        self.fitzdoc = fitz.Document(self.pdffile)

        self.dxmin = dxmin
        self.formulaid = formulaid
        self.formulaiddef = r'^\s*' + self.formulaid + r'\s*\n'

    def __call__(self, frompage, topage):
        #pages = list(PDFPage.create_pages(self.doc))
        for pnum, page in enumerate(PDFPage.create_pages(self.doc)):
            pnum = pnum + 1
            #pnum, page = args.frompage, pages[args.frompage-1]
            if frompage and (pnum < frompage):
                continue
            if topage and (pnum > topage):
                break
            print(pnum)
            self.interpreter.process_page(page)
            ltpage = self.device.get_result()
            self.page_f2i(pnum, ltpage)

    def page_f2i(self,pnum,ltpage):

        objs = list(ltpage)
        xmin = int(min([o.x0 for o in objs])) + self.dxmin
        xmax = int(max([o.x1 for o in objs])+1)
        ymin = int(min([o.y0 for o in objs]))
        ymax = int(max([o.y1 for o in objs])+1)

        #above, below
        def a_b_clause(o,center,i):
            #a
            a = None
            for ib in range(0,len(objs)):
                if ib == i:
                    continue
                #ib = 7
                anb = objs[ib]
                if not issubclass(type(anb), LTTextBox):
                    continue
                if int(anb.x0) <= xmin and anb.y0 > center:
                    if not a or anb.y0 < a.y0:
                        a = anb
                elif anb.y0 > center:
                    nb = None
                    for bb in anb._objs:
                        if int(bb.x0) <= xmin and bb.y0 > center:
                            if not nb or bb.y0 < nb.y0:
                                nb = bb
                    if nb and (not a or nb.y0 < a.y0):
                        a = nb
            #b
            b = None
            if i >= 0:
                for ib in range(0,len(objs)):
                    if ib == i:
                        continue
                    anb = objs[ib]
                    if not issubclass(type(anb), LTTextBox):
                        continue
                    if int(anb.x0) <= xmin and anb.y1 < center:
                        if not b or anb.y1 > b.y1:
                            b = anb
                    elif anb.y0 < center:
                        nb = None
                        for bb in anb._objs:
                            if int(bb.x0) <= xmin and bb.y1 < center:
                                if not nb or bb.y1 > nb.y1:
                                    nb = bb
                        if nb and (not b or nb.y1 > b.y1):
                            b = nb
            else:
                for anb in objs[-i-1]._objs:
                    if anb.y1 < center:
                        if not b or anb.y1 > b.y1:
                            b = anb
            return a, b

        pg = self.fitzdoc.loadPage(pnum-1)
        pm=pg.getPixmap()
        tf  = tempfile.NamedTemporaryFile(suffix=".png")
        pm.writePNG(tf.name)
        im=Image.open(tf.name)
        imx,imy = im.size
        tf.close()
        #im.show()

        i_o = [int(o.x0)!=xmin and (i,o) or (-i-1,o._objs[0]) for i,o in enumerate(objs) 
                if issubclass(type(o),LTTextBox)
                    and re.search(self.formulaiddef,o.get_text())]
        i_o = list(sorted(i_o,key=lambda x:_first_char(x[1]).y0,reverse=True))

        i_o_s = [imy]
        i_o_e = [imy]
        for ii, (i, o) in enumerate(i_o):
            ochf = _first_char(o)
            i_o_s.append(ochf.y1)
            i_o_e.append(ochf.y0)
        i_o_s.append(0)
        i_o_e.append(0)
        #i_o_s 
        #i_o_e 

        iilen = len(i_o)
        for ii, (i, o) in enumerate(i_o):
            #ii, (i,o) = 3, i_o[3]
            ochf = _first_char(o)
            ochl = _last_char(o)
            dy = ochf.y1 - ochf.y0
            _frm,_to = i_o_s[ii+2],i_o_e[ii]
            cutrect = [xmin, _frm, ochl.x1, _to] #include the number...
            center = (ochf.y0 + ochf.y1)/2
            a,b = a_b_clause(o, center, i)
            found_a_b = 0
            if b and b.y1>_frm and b.y1<_to:
                found_a_b += 1
                cutrect[1] = b.y1
            if a and a.y0>_frm and a.y0<_to:
                found_a_b += 1
                cutrect[3] = a.y0
            if found_a_b == 2 or (ii==0 and b) or (ii==iilen-1 and a):
                cutrect[2] = ochf.x0 #unless we found y range

            #cutrect
            for repi in [1,2]:
                x0,y0,x1,y1 = cutrect
                cr = [x0,imy - y1,x1, imy - y0]
                im2 = im.crop([int(round(x))for x in cr])
                #im2.show()
                try:
                    im1 = _trim(im2)
                    if not im1:#= empty
                        cutrect = [xmin, i_o_s[ii+2], ochl.x1, i_o_e[ii]]
                        continue
                except:
                    im1 = im2
                    break

            #im1.show() 
            name = o.get_text().split('\n')[0]
            for f,t in zip('.()','_f__'): 
                name = name.replace(f,t).strip()
            #name
            name = name + 'p%d.png'%pnum
            newfn = os.path.join(self.imagefolder,name)
            print(newfn)
            im1.save(newfn)


    def formula_page_refs(self, frompage, topage):
        """finds all formulas and returns
        {formula : [page number per reference]}
        """
        #frompage,topage=(args.frompage, args.topage)
        f_p_rs = defaultdict(list)
        for pnum in range(self.fitzdoc.pageCount):
            if frompage and pnum < frompage:
                continue
            if topage and pnum > topage:
                break
            #pnum = frompage
            pg = self.fitzdoc.loadPage(pnum)
            text = pg.getText()
            spnum = str(pnum)
            for m in re.finditer(self.formulaid, text):
                frm = m.group(0)
                f_p_rs[frm].append(spnum)
            #note that this searches for other text than formulaiddef
            for m in re.finditer(r"\W+\s*("+self.formulaid+")\s*\n",text):
                frm = m.group(1)
                frmlist = f_p_rs[frm]
                ifrm = frmlist.index(spnum)
                frmlist[ifrm] = '*'+frmlist[ifrm]
        return f_p_rs

if __name__ == "__main__":
    main()

