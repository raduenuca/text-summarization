import click
import os
from cube.api import Cube
import text_rank


def extract_sentences(sentences, length, length_pct, clean):
    sentence_tokens = []
    for sentence in sentences:
        words = []
        for entry in sentence:
            words.append(entry.word)

        sentence_tokens.append(' '.join(words))

    return text_rank.extract_sentences(sentence_tokens,
                                       summary_length=length,
                                       summary_length_pct=length_pct,
                                       clean_sentences=clean)


def extract_key_phrases(sentences, length, length_pct):
    # Perform POS Tagging
    tagged = []
    for sentence in sentences:
        for entry in sentence:
            tagged.append((entry.lemma, entry.upos, entry.word))

    return text_rank.extract_key_phrases(tagged, keywords_length=length, keywords_length_pct=length_pct)


@click.group()
@click.option('--language', default='ro')
@click.pass_context
def cli(ctx, language):
    cube = Cube(verbose=True)
    cube.load(language)

    ctx.ensure_object(dict)
    ctx.obj['CUBE'] = cube


@cli.command()
@click.argument('filename')
@click.option('--summary_length', default=100, help='Summary word length')
@click.option('--summary_length_pct', default=0.2, help='Summary word length in percentage of total')
@click.option('--clean_sentences', default=True, help='Clean sentences')
@click.pass_context
def summary(ctx, filename, summary_length, summary_length_pct, clean_sentences):
    """Print summary text to stdout."""

    cube = ctx.obj['CUBE']
    with open(filename) as f:
        text = f.read()

        sentences = cube(text)
        summary_text = extract_sentences(sentences, summary_length, summary_length_pct, clean_sentences)

        print(summary_text)


@cli.command()
@click.argument('filename')
@click.option('--keyword_length', default=10, help='Keyword word length')
@click.option('--keyword_length_pct', default=0.1, help='Keyword word length percentage of total')
@click.pass_context
def keywords(ctx, filename, keyword_length, keyword_length_pct):
    """Print key-phrases to stdout."""

    cube = ctx.obj['CUBE']
    with open(filename) as f:
        text = f.read()

        sentences = cube(text)
        phrases = extract_key_phrases(sentences, keyword_length, keyword_length_pct)
        print(phrases)


@cli.command()
@click.argument('source')
@click.argument('destination')
@click.option('--summary_length', default=100, help='Summary word length')
@click.option('--summary_length_pct', default=0.2, help='Summary word length in percentage of total')
@click.option('--clean_sentences', default=True, help='Clean sentences')
@click.option('--keyword_length', default=10, help='Keyword word length')
@click.option('--keyword_length_pct', default=0.1, help='Keyword word length percentage of total')
@click.pass_context
def extract_all(ctx, source, destination, summary_length, summary_length_pct, clean_sentences, keyword_length,
                keyword_length_pct):
    """Summarizes and extracts keywords for all files in folder"""

    cube = ctx.obj['CUBE']
    articles = os.listdir(source)

    for article in articles:
        print(f'Reading article: {article}')

        with open(f'{source}/{article}', encoding='utf-8') as f:
            text = f.read()

            sentences = cube(text)

            # Extract summary
            summary = extract_sentences(sentences, summary_length, summary_length_pct, clean_sentences)
            summary_directory = f'{destination}/summaries'
            if not os.path.exists(summary_directory):
                os.makedirs(summary_directory)

            print(f'Generating output to summaries/{article}')
            with open(f'{summary_directory}/{article}', 'w', encoding='utf-8') as summary_file:
                summary_file.write(summary)

            # Extract keywords
            phrases = extract_key_phrases(sentences, keyword_length, keyword_length_pct)

            keywords_directory = f'{destination}/keywords'
            if not os.path.exists(keywords_directory):
                os.makedirs(keywords_directory)

            print(f'Generating output to keywords/{article}')
            with open(f'{keywords_directory}/{article}', 'w', encoding='utf-8') as keywords_file:
                for key_phrase in phrases:
                    keywords_file.write(f'{key_phrase}\n')

    print('Summarization complete')


if __name__ == '__main__':
    cli()
