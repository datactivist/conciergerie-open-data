import requests
import json

# API Expansion
API_expansion_host_name = "127.0.0.1"
API_expansion_port = "8001"
API_expansion_url = "http://" + API_expansion_host_name + ":" + API_expansion_port + "/"


# API Reranking
API_reranking_host_name = "127.0.0.1"
API_reranking_port = "8002"
API_reranking_url = "http://" + API_reranking_host_name + ":" + API_reranking_port + "/"


def get_keywords_expansion_query(keywords, referentiel):

    """
    Find new keywords that might interest the user by calling the expansion API

    Input: Keywords as string (separated by spaces)
    Output: See API documentation at http://localhost:8000/doc
    """

    search_expand_url = API_expansion_url + "query_expand"

    body = {"keywords": keywords, "max_width": 5, "referentiel": referentiel}

    return requests.post(search_expand_url, json=body).json()


def add_expansion_search_query(conversation_id, user_search, date):

    """
    Send a request to the expansion API to add a new search
    """

    add_new_search_query_url = API_expansion_url + "add_search"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "date": date,
    }

    requests.post(add_new_search_query_url, json=body).json()


def add_expansion_feedback_query(conversation_id, user_search, feedbacks_list):

    """
    Send a request to the expansion API to add new feedbacks

    Input:  conversation_id: id of the rasa conversation
            user_search: keywords entered by user
            feedbacks_list: list of feedbacks
            feedback: dictionnary containing the original keyword, the proposed keyword, and the feedback

            ex of feedback:
            {
                "original_keyword": "barrage",
                "proposed_keyword": "digue",
                "feedback": -1
            }
    """

    add_new_feedback_query_url = API_expansion_url + "add_feedback"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "data": feedbacks_list,
    }

    requests.post(add_new_feedback_query_url, json=body).json()


# API Reranking Requests


def get_search_reranking_query(conversation_id, user_search, data):
    """
    Rerank the results by calling the reranking API

    Input:  - **conversation_id**: id of the rasa conversation
            - **user_search**: keywords entered by user
            - **data**: List of list of results
                - **api_hostname**: Host name of the API the results are from
                - **results_list**: see API documentation for every metadatas

    Output: See API documentation at <reranking API host name>/docs
    """

    search_reranking_url = API_reranking_url + "search_reranking"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "data": data,
    }

    return requests.post(search_reranking_url, json=body).json()


def add_reranking_search_query(conversation_id, user_search, date):

    """
    Send a request to the reranking API to add a new search
    """

    add_new_search_query_url = API_reranking_url + "add_search"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "date": date,
    }

    requests.post(add_new_search_query_url, json=body).json()


def add_reranking_feedback_query(
    conversation_id, user_search, keywords_feedback, feedbacks_list
):

    """
    Send a request to the reranking API to add new feedbacks

    Input:  conversation_id: id of the rasa conversation
            user_search: keywords entered by user
            feedbacks_list: list of feedbacks
            feedback: dictionnary containing the result and its metadata, and the feedback

            ex of feedback:
            {
                "result": {
                    "title": "Usines hydroélectriques concédées en Provence Alpes Côte d'Azur",
                    "url": "syncb021eba-fr-120066022-jdd-627db3a0-9448-4631-81b9-2f13f67b8557",
                    "description": "Description 1"
                    [...]
                },
                "feedback": 1
            }
    """

    add_new_feedback_query_url = API_reranking_url + "add_feedback"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "feedbacks_list": feedbacks_list,
    }

    requests.post(add_new_feedback_query_url, json=body).json()


# API Portail de données
