from __future__ import annotations
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
import expansion
import timeit

import os
import json
import numpy as np


# Function to preload datasud vectors by saving them separately
def preload_datasud_vectors(model, datasud_keywords):
    if not os.path.isfile(
        "datasud_keywords_vectors/" + model.model_type + "/" + model.model_name + ".npy"
    ):
        print("Saving datasud keywords vectors for", model.model_name)
        start = timeit.default_timer()
        vectors = model.model.query(datasud_keywords)
        np.save(
            "datasud_keywords_vectors/"
            + model.model_type
            + "/"
            + model.model_name
            + ".npy",
            vectors,
        )
        end = timeit.default_timer()
        print("Vectors saved")


# Function to preload models by calling most_similar
def preload_magnitude_model(model_type, model_name, datasud_keywords):
    model = expansion.MagnitudeModel(model_type, model_name)
    model.most_similar("Chargement")
    preload_datasud_vectors(model, datasud_keywords)
    model = None


with open("datasud_keywords.json", encoding="utf-16") as json_file:
    datasud_keywords = json.load(json_file,)["result"]

# Looping on embeddings to preload them
print("\nStarting Preloading")
start = timeit.default_timer()
for model_type in expansion.ModelType:
    path = "embeddings/" + model_type.value
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".magnitude"):
                preload_magnitude_model(model_type, filename, datasud_keywords)
end = timeit.default_timer()
print("Preloading Done:", end - start, "\n")


# Structure for search expand query
class Search_Expand_Query(BaseModel):
    keywords: str
    model_type: Optional[expansion.ModelType] = expansion.ModelType.word2vec
    model_name: Optional[
        str
    ] = "frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude"
    max_depth: Optional[int] = Field(1, ge=0, le=3)
    max_width: Optional[int] = Field(10, ge=0, le=50)
    max_datasud_keywords: Optional[int] = Field(5, ge=0, le=50)


# Structures for search expand query results
class Cluster(BaseModel):
    sense: str
    similar_senses: Optional[List[Tuple[Cluster, expansion.SimilarityType]]]
    sense_definition: Optional[str]


Cluster.update_forward_refs()


class ResponseFromSense(BaseModel):
    original_keyword: str
    tree: Optional[List[Cluster]]
    datasud_keywords: Optional[List[str]]


class Query_Response(BaseModel):
    data: List[ResponseFromSense]


app = FastAPI()


@app.get("/help_model/{model_type}")
async def get_model_names(model_type: expansion.ModelType):
    """
    # Function
    ## Use
    Return every variant models available for the model_type given in parameter

    ## Parameter
    ### Required
    - **model_type**: Type of the models

    ## Output
    List of variant models available
    """
    path = "api-expansion/embeddings/" + model_type.value
    results = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            results.append(filename)
        for filename in dirs:
            results.append(filename)
        return results


@app.post("/query_expand", response_model=Query_Response)
async def manage_query_expand(query: Search_Expand_Query):
    """
    
    # Function
    ## use
    Returns results of the search query expansion given in parameter:


    ## Parameters
    ### Required Parameters:
    - **keywords**: String

    ### Optional Parameters:
    - **model_type**: Type of the model | default value: word2vec
    - **model_name**: Variant of the model | default value: frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude
    - **max_depth**: Depth of the keyword search | default value: 1
    - **max_width**: Width of the keyword search | default value: 10 # Ignore when using wordnet
    - **max_datasud_keywords**: If >0, include the first <x> most similar words from the datasud database for each word, default to 5

    ## Output:
    - **data**: list of search result
    - **search result**:
        - **original_keyword**: keyword at the root of the resulting tree
        - **tree**: list of clusters
         - **cluster**: 
            - **word**: word at the center of the cluster
            - **similar_words**: list of tuples of type (cluster, similarityType)
            - **similarityType**: relation between two clusters (synonyms, hyponyms, hypernyms, similars)
            - **Only when using wordnet**:
                - **sense_definition**: definition of the synset
        - **datasud_keywords**: list of string
    """

    if query.model_type != expansion.ModelType.wordnet:
        model = expansion.MagnitudeModel(query.model_type, query.model_name)
    else:
        model = expansion.WordnetModel()

    data = expansion.expand_keywords(
        model,
        query.keywords,
        query.max_depth,
        query.max_width,
        query.max_datasud_keywords,
    )
    return data
