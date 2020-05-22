# TextRank Text Summarization

*This is an adaptation of [David Adamo's](https://github.com/davidadamojr) 
[TextRank](https://github.com/davidadamojr/TextRank) implementation using [Adobe NLP Cube](https://github.com/adobe/NLP-Cube)* 

## Introduction 

This is a python implementation of TextRank for automatic keyword and sentence extraction (summarization) as done in 
[TextRank: Bringing Order into Texts](https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf). 
However, this implementation uses Levenshtein Distance as the relation between text units.

This implementation carries out automatic keyword and sentence extraction for different languages (*see `Adobe NLP Cube` supported languages*)

* Absolute or percenage based word summary
* Number of keywords extracted is relative to the size of the text (absolute or percentage based)
* Adjacent keywords in the text are concatenated into key phrases

## Usage

To install the library run the setup.py module located in the repository's root directory. Alternatively, if you have 
access to pip you may install the library directly from github:

```pip install git+git://github.com/raduenuca/text-summarization.git```

Use of the library requires downloading `NLP Cube` resources which are downloaded once per language. You may execute the 
following commands against the library:

```
summarize --help
summarize <summary|keywords|extract-all> --help
summarize summary <filename> 
summarize keywords <filename>
summarize --language=ro extract-all "examples/data/ro/articles" "examples/data/ro"
summarize --language=en extract-all "examples/data/en/articles" "examples/data/en"
```

Check the language codes supported by [Adobe NLP Cube](https://github.com/adobe/NLP-Cube)

# Dependencies

Dependencies are installed automatically with pip but can be installed separately.

* Networkx - https://pypi.python.org/pypi/networkx
* NLP Cube - https://pypi.python.org/pypi/nlpcube
* Click - https://pypi.python.org/pypi/click
* Numpy - https://pypi.python.org/pypi/numpy
