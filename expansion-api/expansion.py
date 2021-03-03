import json
import timeit
import numpy as np
from enum import Enum

from nltk.corpus import wordnet as wn
import nltk

from pymagnitude import *


class EmbeddingsType(str, Enum):
    word2vec = "word2vec"
    wordnet = "wordnet"
    fasttext = "fasttext"
    bert = "bert"
    elmo = "elmo"


class SimilarityType(str, Enum):
    synonym = "synonym"
    hyponym = "hyponym"
    hypernym = "hypernym"
    holonym = "holonym"
    similar = "similar"


class MagnitudeModel:
    """
    Class representing a Magnitude Model
    Input: Type of the embeddings and name of the embeddings
    """

    def __init__(self, embeddings_type, embeddings_name):
        self.embeddings_type = embeddings_type
        self.embeddings_name = embeddings_name
        self.model = self.load_model()

    def load_model(self):
        """
        load model using Magnitude
        """

        return Magnitude(
            "embeddings/" + self.embeddings_type + "/" + self.embeddings_name
        )

    def similarity(self, keyword1, keyword2):
        """
        Compute and return similarity between two words

        Input: Two words of type string
        Output: Similarity between the two keywords
        """

        return self.model.similarity(keyword1, keyword2)

    def most_similar(self, keyword, topn=10, slider=0):
        """
        Return the nearest neighbors of keyword

        Input:  keyword: a word of type string
                topn: number of neighbors to get (default: 10)
                slider: slide the results (default: 0)  - (i.e topn=10 and slider = 2 -> [2-12]) to avoid looping when depth>1
        Output: Return the topn closest words from keyword
        """

        similar_words = {}
        for sim_type in SimilarityType:
            similar_words[sim_type] = []

        most_similar = self.model.most_similar(keyword, topn=topn + slider)[slider:]

        similar_words[SimilarityType.similar] = [
            most_similar[i][0] for i in range(len(most_similar))
        ]

        return similar_words

    def load_datasud_keywords(self):
        """
        Load and return the presaved vectors of Datasud Keywords
        """

        with open("datasud_keywords.json", encoding="utf-16") as json_file:
            db_keywords_strings = json.load(json_file,)["result"]

        db_keywords_vectors = np.load(
            "datasud_keywords_vectors/"
            + self.embeddings_type
            + "/"
            + self.embeddings_name
            + ".npy"
        )
        return db_keywords_strings, db_keywords_vectors


class WordnetModel:
    """
    Class representing a WordNet model
    """

    def __init__(self):
        self.embeddings_type = EmbeddingsType.wordnet
        self.embeddings_name = "wolf-b-04.xml"

    def similarity(self, keyword1, keyword2):
        """
        Compute and return similarity between two object

        Input: Two keywords of type string, synset, or list of synset
        Output: Similiarity between the two objets using path_similarity
        """

        if type(keyword1) == nltk.corpus.reader.wordnet.Synset:
            keyword1 = [keyword1]
        elif type(str):
            keyword1 = wn.synsets(keyword1, lang="fra")

        if type(keyword2) == nltk.corpus.reader.wordnet.Synset:
            keyword2 = [keyword2]
        elif type(str):
            keyword2 = wn.synsets(keyword2, lang="fra")

        sim = 0
        for k1 in keyword1:
            for k2 in keyword2:
                new_sim = k1.path_similarity(k2)
                if new_sim != None and sim < new_sim:
                    sim = new_sim
        return sim

    def most_similar(self, synset, topn, slider):
        """
        Return a dictionnary with the list of similar words and their similarityType

        Input: Synset
        Output: List of synonyms, hyponyms, hypernyms and holonyms in a dictionnary
        """

        similar_words = {}
        for sim_type in SimilarityType:
            similar_words[sim_type] = []

        if type(synset) == nltk.corpus.reader.wordnet.Synset:
            for synonym in synset.lemma_names("fra"):
                similar_words[SimilarityType.synonym].append(synonym)

            for hyponym in synset.hyponyms():
                similar_words[SimilarityType.hyponym].append(hyponym)

            for hypernym in synset.hypernyms():
                similar_words[SimilarityType.hypernym].append(hypernym)

            for holonym in synset.member_holonyms():
                similar_words[SimilarityType.holonym].append(holonym)

        return similar_words

    def load_datasud_keywords(self):
        """
        Load and return the datasud keywords as a list of string | Twice to keep same behavour as MagnitudeModel
        """

        with open("datasud_keywords.json", encoding="utf-16") as json_file:
            db_keywords = json.load(json_file,)["result"]
        return db_keywords, db_keywords


def split_user_entry(user_entry):
    """
    Split the user entry into keywords

    Input: keywords as string
    Output: keywords as list

    Currently splitting them with space char
    """

    return user_entry.split(" ")


def second_key_from_tuple(tuple):
    """
    Return second value of a tuple, used for sorting array of dimension [n, 2] on the second value
    """

    return tuple[1]


def get_datasud_keywords(
    model, keyword, dtsud_keywords_strings, dtsud_keywords_vectors, max_k
):

    """
    Return the closest datasud keywords from keyword

    Input: keyword: keyword of type string or synset
           dtsud_keywords: list of keywords of type string from the datasud database
           max_k: number of neighbors to find
    Output: the max_k most similar datasud keywords
    """

    start = timeit.default_timer()

    data_sud = []

    for i, dtsud_keyword_vector in enumerate(dtsud_keywords_vectors):

        sim = model.similarity(keyword, dtsud_keyword_vector)

        if sim != 1 and sim > 0.2:
            data_sud.append((dtsud_keywords_strings[i], sim))

    data_sud.sort(key=second_key_from_tuple, reverse=True)

    return [data_sud[i][0] for i in range(min(max_k, len(data_sud)))]


def get_cluster(model, keyword, width, depth, current_depth):

    """
    Recursive function to build the data structure tree

    Input:  keyword: string or synset
            width: width of each cluster #Ignore when using WordnetModel
            depth: depth to achieve
            current_depth: current depth
    Output: A cluster
    """

    cluster = {}
    cluster["sense"] = str(keyword)
    cluster["similar_senses"] = []

    if current_depth < depth:

        # to avoid looping on most similar words
        slider = 1 if current_depth > 0 else 0
        similar_words = model.most_similar(keyword, width, slider)

        for word in similar_words[SimilarityType.synonym]:
            sub_cluster = {}
            sub_cluster["sense"] = word
            cluster["similar_senses"].append([sub_cluster, SimilarityType.synonym])

        for word in similar_words[SimilarityType.similar]:
            sub_cluster = get_cluster(model, word, width, depth, current_depth + 1)
            cluster["similar_senses"].append([sub_cluster, SimilarityType.similar])

    if current_depth + 1 < depth:

        for sim_type in SimilarityType:
            if (
                sim_type != SimilarityType.synonym
                and sim_type != SimilarityType.similar
            ):
                for sense in similar_words[sim_type]:
                    sub_cluster = get_cluster(
                        model, sense, width, depth, current_depth + 1
                    )
                    cluster["similar_senses"].append([sub_cluster, sim_type])

    if len(cluster["similar_senses"]) == 0:
        cluster["similar_senses"] = None

    return cluster


def expand_keywords(model, keywords, max_depth, max_width, max_dtsud_keywords):
    """
    Return the most similar keywords from the initial keywords

    Input:  keywords: a string
            max_depth: maximum depth of keywords search
            max_width: maximum width of keywords search
            max_dtsud_keywords: number of datasud keywords to return
    Output: Data structure with most similar keywords found
    """

    keywords = split_user_entry(keywords)

    data = []

    if max_dtsud_keywords > 0:
        db_keywords_strings, db_keywords_vectors = model.load_datasud_keywords()

    for keyword in keywords:
        if len(keyword) > 3:

            keyword = keyword.lower()

            # Generate list of sense for wordnet (just a list of size 1 if other embeddings type)
            senses = (
                wn.synsets(keyword, lang="fra")
                if model.embeddings_type == EmbeddingsType.wordnet
                else [keyword]
            )

            current_tree = []

            current_search_result = {}
            current_search_result["original_keyword"] = keyword

            for sense in senses:

                if max_dtsud_keywords > 0:
                    current_search_result["datasud_keywords"] = get_datasud_keywords(
                        model,
                        sense,
                        db_keywords_strings,
                        db_keywords_vectors,
                        max_dtsud_keywords,
                    )

                current_tree.append(get_cluster(model, sense, max_width, max_depth, 0))

            current_search_result["tree"] = current_tree
            data.append(current_search_result)

    return data
