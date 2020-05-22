"""Python implementation of the TextRank algorithm.
From this paper:
    https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf
Based on:
    https://gist.github.com/voidfiles/1646117
    https://github.com/davidadamojr/TextRank
"""
import editdistance
import itertools
import networkx as nx


def filter_for_tags(tagged, tags=None):
    """Apply syntactic filters based on POS tags."""
    if tags is None:
        tags = ['NOUN', 'ADJ', 'PROPN']

    return [item for item in tagged if item[1] in tags]


def normalize(tagged):
    """Return a list of tuples with the first item's periods removed."""
    return [(item[0].replace('.', ''), item[1]) for item in tagged]


def unique_everseen(iterable, key=None):
    """List unique elements in order of appearance.
    Examples:
        unique_everseen('AAAABBBCCDAABBB') --> A B C D
        unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in [x for x in iterable if x not in seen]:
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def build_graph(nodes):
    """Return a networkx graph instance.
    :param nodes: List of hashables that represent the nodes of a graph.
    """
    gr = nx.Graph()  # initialize an undirected graph
    gr.add_nodes_from(nodes)
    node_pairs = list(itertools.combinations(nodes, 2))

    # add edges to the graph (weighted by Levenshtein distance)
    for pair in node_pairs:
        first_string = pair[0]
        second_string = pair[1]
        lev_distance = editdistance.eval(first_string, second_string)
        gr.add_edge(first_string, second_string, weight=lev_distance)

    return gr


def extract_key_phrases(pos_tagged, keywords_length=10, keywords_length_pct=0.1):
    """Return a set of key phrases.
    """
    text_list = [(x[0], x[2]) for x in pos_tagged]

    tagged = filter_for_tags(pos_tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

    # this will be used to determine adjacent words in order to construct
    # key phrases with two words

    graph = build_graph(word_set_list)

    # pageRank - initial value of 1.0, error tolerance of 0,0001,
    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important words in ascending order of importance
    key_phrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    # the number of key phrases returned will be relative to the size of the
    # text (based on percentage)
    index = min(keywords_length, int(len(key_phrases) * keywords_length_pct))
    key_phrases = key_phrases[0:index + 1]

    # take key phrases with multiple words into consideration as done in the
    # paper - if two words are adjacent in the text and are selected as
    # keywords, join them together
    modified_key_phrases = set([])
    # keeps track of individual keywords that have been joined to form a
    # key phrase
    dealt_with = set([])
    i = 0
    j = 1
    while j < len(text_list):
        first_lemma = text_list[i][0]
        first_word = text_list[i][1]
        second_lemma = text_list[j][0]
        second_word = text_list[j][1]
        if first_lemma in key_phrases and second_lemma in key_phrases:
            key_phrase = first_word + ' ' + second_word
            modified_key_phrases.add(key_phrase)
            dealt_with.add(first_lemma)
            dealt_with.add(second_lemma)
        else:
            if first_lemma in key_phrases and first_lemma not in dealt_with:
                modified_key_phrases.add(first_word)

            # if this is the last word in the text, and it is a keyword, it
            # definitely has no chance of being a key phrase at this point
            if j == len(text_list) - 1 and second_lemma in key_phrases and second_lemma not in dealt_with:
                modified_key_phrases.add(second_word)

        i = i + 1
        j = j + 1

    return modified_key_phrases


def extract_sentences(sentence_tokens, summary_length=100, summary_length_pct=0.1, clean_sentences=True):
    """Return a paragraph formatted summary of the source text.
    :param summary_length_pct: Desired summary length as percentage from the total
    :param sentence_tokens: List of sentences
    :param clean_sentences: When True will only return complete sentences
    :param summary_length: Desired summary length as absolute value (if this is smaller than percentage it will win)
    """
    graph = build_graph(sentence_tokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    # return a summary_length word summary
    summary = ' '.join(sentences)
    summary_words = summary.split()

    # Pick the minimum from summary_length and the summary_length_pct but it must have at least one complete sentence
    # if possible
    summary_length_pct = int(len(summary_words) * summary_length_pct)
    summary_words_pct = summary_words[0:summary_length_pct]
    dot_indices_pct = [idx for idx, word in enumerate(summary_words_pct) if word.find('.') != -1]

    summary_words_abs = summary_words[0:summary_length]
    dot_indices_abs = [idx for idx, word in enumerate(summary_words_abs) if word.find('.') != -1]

    there_are_no_dots = len(dot_indices_pct) == 0 and len(dot_indices_abs) == 0
    there_are_dots_in_both = len(dot_indices_abs) > 0 and len(dot_indices_pct) > 0

    if there_are_no_dots or there_are_dots_in_both:
        # Doesn't matter, pick the smallest one
        summary_length = min(summary_length_pct, summary_length)

    if summary_length_pct > summary_length and (not dot_indices_abs):
        summary_length = summary_length_pct

    # Find closest dot position
    if clean_sentences:
        before = summary_words[0:summary_length]
        before_dot_indices = [idx for idx, word in enumerate(before) if word.find('.') != -1]

        after = summary_words[summary_length:]
        after_dot_indices = [idx for idx, word in enumerate(after) if word.find('.') != -1]

        diff_before = 0
        if before_dot_indices:
            dot_before = max(before_dot_indices)
            diff_before = summary_length - dot_before

        diff_after = summary_length
        if after_dot_indices:
            diff_after = min(after_dot_indices)

        if diff_after <= diff_before:
            summary_length = summary_length + diff_after
        else:
            summary_length = dot_before

    summary_words = summary_words[0:summary_length + 1]
    summary = ' '.join(summary_words)

    return summary
