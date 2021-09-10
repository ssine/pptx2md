from setuptools import setup

setup(
    name = 'pptx2md',
    version = '1.0.0',
    keywords = ["pip", "pptx2md"],
    description = "convert pptx to markdown",
    long_description = "keeps the titles, formats including color, bold and italic, extracts the images",
    license = "MIT Licence",
    url = "https://github.com/ssine/pptx2md",
    author = "Liu Siyao",
    author_email = "liu.siyao@qq.com",
    packages = ['pptx2md'],
    entry_points = {
        'console_scripts': [
            'pptx2md = pptx2md.__main__:main'
        ]
    },
    install_requires = [
        'python-pptx',
        'rapidfuzz',
        'pillow'
    ]
)
