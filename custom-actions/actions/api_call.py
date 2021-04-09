import requests

# Local: "localhost:8000"
# Docker: "query-exp:80"
API_expansion_host_name = "localhost:8000"

API_reranking_host_name = ""

# API Expansion Requests


def get_keywords_expansion_query(keywords):
    """
    Find new keywords that might interest the user by calling the expansion API

    Input: Keywords as string (separated by spaces)
    Output: See API documentation at http://localhost:8000/doc
    """

    search_expand_url = "http://" + API_expansion_host_name + "/query_expand"

    body = {"keywords": keywords, "max_width": 5, "max_datasud_keywords": 5}

    results = requests.post(search_expand_url, json=body).json()

    return results


def add_expansion_search_query(conversation_id, user_search, date):

    """
    Send a request to the expansion API to add a new search
    """

    add_new_search_query_url = "http://" + API_expansion_host_name + "/add_search"

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

    add_new_feedback_query_url = "http://" + API_expansion_host_name + "/add_feedback"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "data": feedbacks_list,
    }

    requests.post(add_new_feedback_query_url, json=body).json()


# API Reranking Requests


# API Datasud Requests
