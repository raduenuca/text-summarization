from setuptools import find_packages, setup

setup(
    name='summarize',
    py_modules=['text_rank', 'main'],
    version='0.1.0',
    description='TextRank implementation in Python using NLP Cube',
    author='Radu Enuca',
    author_email='',
    url='https://github.com/raduenuca/text-summarization',
    install_requires=['networkx>=1.11.0', 'nlpcube>=0.1', 'numpy>=1.11.2', 'click>=6.6', 'editdistance==0.4'],
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        summarize=main:cli
    ''',
)