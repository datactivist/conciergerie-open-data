import requests
import re

# API Expansion
API_expansion_host_name = "127.0.0.1"
API_expansion_port = "8001"
API_expansion_url = "http://" + API_expansion_host_name + ":" + API_expansion_port + "/"


# API Reranking
API_reranking_host_name = "127.0.0.1"
API_reranking_port = "8002"
API_reranking_url = "http://" + API_reranking_host_name + ":" + API_reranking_port + "/"

# API Portail de données
API_datasud_host_name = "https://trouver.datasud.fr/api/3/action/package_search?"
portail = "datasud"

keywords_delimitor = " |,|;|_|\|"


def get_keywords_expansion_query(keywords, referentiel):

    """
    Find new keywords that might interest the user by calling the expansion API

    Input: Keywords as string (separated by spaces)
    Output: See API documentation at http://localhost:8000/doc
    """

    search_expand_url = API_expansion_url + "query_expand"

    body = {"keywords": keywords, "max_width": 8, "referentiel": referentiel, "only_vocabulary": True}

    print(body)

    try:
        return requests.post(search_expand_url, json=body).json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def add_expansion_search_query(conversation_id, user_search, date):

    """
    Send a request to the expansion API to add a new search
    """

    add_new_search_query_url = API_expansion_url + "add_search"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "portal": portail,
        "date": date,
    }

    try:
        requests.post(add_new_search_query_url, json=body).json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


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
        "portal": portail,
        "data": feedbacks_list,
    }

    try:
        requests.post(add_new_feedback_query_url, json=body).json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


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

    try:
        return requests.post(search_reranking_url, json=body).json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def add_reranking_search_query(conversation_id, user_search, date):

    """
    Send a request to the reranking API to add a new search
    """

    add_new_search_query_url = API_reranking_url + "add_search"

    body = {
        "conversation_id": conversation_id,
        "user_search": user_search,
        "portal": portail,
        "date": date,
    }

    try:
        requests.post(add_new_search_query_url, json=body).json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def add_reranking_feedback_query(
    conversation_id, user_search, search_target_feedback, feedbacks_list
):

    """
    Send a request to the reranking API to add new feedbacks

    Input:  conversation_id: id of the rasa conversation
            user_search: keywords entered by user
            search_target: The description of the target entered by the user
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
        "search_target": search_target_feedback,
        "feedbacks_list": feedbacks_list,
    }

    try:
        requests.post(add_new_feedback_query_url, json=body).json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# API Portail de données


def get_results_from_keywords(keywords, keywords_feedback, nb_results):

    """
    Try different type of requests operator until we have enough results. Order: + -> ||
    Input:  keywords: keywords entered by the user
            keywords_feedback: keywords selected from the expansion
    Output: List of formatted results
    """

    query_params_plus = "q=" + "+".join(
        re.split(keywords_delimitor, keywords)
        + re.split(keywords_delimitor, keywords_feedback)
    )

    query_params_base = "q=" + "+".join(re.split(keywords_delimitor, keywords))

    query_params_or = "q=" + "||".join(
        re.split(keywords_delimitor, keywords)
        + re.split(keywords_delimitor, keywords_feedback)
    )

    sorting = "&sort=score+desc,metadata_modified+desc"

    try:

        data = requests.post(API_datasud_host_name + query_params_plus + sorting).json()

        if len(data["result"]["results"]) < nb_results:
            data_temp = requests.post(
                API_datasud_host_name + query_params_base + sorting
            ).json()
            for result in data_temp["result"]["results"]:
                if result["name"] not in [
                    result_cmp["name"] for result_cmp in data["result"]["results"]
                ]:
                    data["result"]["results"].append(result)

            if len(data["result"]["results"]) < nb_results:
                data_temp = requests.post(
                    API_datasud_host_name + query_params_or + sorting
                ).json()
                for result in data_temp["result"]["results"]:
                    if result["name"] not in [
                        result_cmp["name"] for result_cmp in data["result"]["results"]
                    ]:
                        data["result"]["results"].append(result)

        return process_results_datasud(data, nb_results)

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def process_results_datasud(results, nb_results):

    """
    Input:  results: results from datasud
            nb_results: number of results to use
    Output: List of results formatted to reranking API
    """

    formatted_results = []

    results = results["result"]["results"][0:nb_results]

    for result in results:

        tags_list = [x["display_name"] for x in result["tags"]]
        groups_list = [
            {"name": x["display_name"], "description": x["description"]}
            for x in result["groups"]
        ]

        formatted_results.append(
            {
                "title": result["title"].replace('"', "'"),
                "url": result["name"],
                "description": result["notes"].replace('"', "'"),
                "portal": "datasud",
                "owner_org": result["organization"]["title"],
                "owner_org_description": result["organization"]["description"].replace(
                    '"', "'"
                ),
                "maintainer": result["maintainer"],
                "dataset_publication_date": result["dataset_publication_date"],
                "dataset_modification_date": result["dataset_modification_date"],
                "metadata_creation_date": result["metadata_created"],
                "metadata_modification_date": result["metadata_modified"],
                "tags": tags_list,
                "groups": groups_list,
            }
        )

    return formatted_results
