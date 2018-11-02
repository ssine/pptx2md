from setuptools import setup

setup(
    name = 'pptx2md',
    version = '1.0.0',
    packages = ['pptx2md'],
    entry_points = {
        'console_scripts': [
            'pptx2md = pptx2md.__main__:main'
        ]
    },
    install_requires = [
        'python-pptx',
        'fuzzywuzzy',
        'python-Levenshtein',
        'pillow'
    ]
)
