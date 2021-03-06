#! /usr/bin/env python2
# vim: fileencoding=utf-8 

#sudo python2 setup.py bdist_wheel --universal
#twine upload ./dist/pdfformulas*.whl

from setuptools import setup
import os

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for classifiers

__version__ = '0.0.6'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

conf = dict(name='pdfformulas',
    version = __version__,
    description="pdfformulas dumps the formulas of a PDF as PNG files in the ``formulas`` subfolder.",
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    ],
    keywords=['PDF, Formula'],
    author = 'Roland Puntaier',
    author_email = 'roland.puntaier@gmail.com',
    license='MIT',
    url = 'https://github.com/rpuntaie/pdfformulas',
    packages=['pdfformulas'],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'PdfMiner>=20140328',
        'Pillow>=3.1.0'
    ],
    tests_require=[],
    entry_points={
         'console_scripts': [
         'pdfformulas = pdfformulas.pdfformulas:main',
              ]
      },

    )

if __name__ == '__main__':
    setup(**conf)
