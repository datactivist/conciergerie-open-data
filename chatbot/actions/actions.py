# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import sqlite3
import json
import requests
import codecs
from typing import Any, Text, Dict, List

from actions import sql_query

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

flag_activate_api_call = True
flag_activate_sql_query_commit = True


def get_request_keywords_url(keywords):
    """
    Return URL to request Datasud API

    Input: Keywords as string (separated by spaces)
    Output: URL as string
    """

    url = "https://trouver.datasud.fr/api/3/action/package_search?q="
    special_characters = [
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
        ":",
        ";",
        "<",
        "=",
        ">",
        "?",
        "@",
    ]

    for special_character in special_characters:
        encoding = str(codecs.encode(special_character.encode("utf-8"), "hex"))
        keywords = keywords.replace(
            special_character, "%" + encoding[2 : len(encoding) - 1]
        )

    for word in keywords.split(" "):
        url += word + "+"

    return url[0 : len(url) - 1]


def keywords_expansion(keywords):
    """
    Find new keywords that might interest the user by calling the expansion API

    Input: Keywords as string (separated by spaces)
    Output: Proposed Keywords as string (separated by |)
    """

    search_expand_url = "http://127.0.0.1:8000/query_expand"

    data = {"keywords": keywords, "max_width": 5, "max_datasud_keywords": 5}

    results = requests.post(search_expand_url, json=data).json()

    keywords_expansion = ""

    for og_key in results:
        for sense in og_key["tree"]:
            for similar_sense in sense["similar_senses"]:
                keyword = similar_sense[0]["sense"]
                if keyword not in keywords_expansion:
                    keywords_expansion += "|" + keyword

        for dtsud_keyword in og_key["datasud_keywords"]:
            if dtsud_keyword not in keywords_expansion:
                keywords_expansion += "|" + dtsud_keyword

    return keywords_expansion[1:]


class ResetKeywordsSlot(Action):
    """
    Reset all the slots of the rasa chatbot
    """

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("keywords", None),
            SlotSet("keywords_augmentation", None),
            SlotSet("keywords_feedback", None),
            SlotSet("results_title", None),
            SlotSet("results_url", None),
            SlotSet("results_feedback", None),
        ]


class AskForKeywordsFeedbackSlotAction(Action):
    """
    Ask the user to choose which keywords are useful to him during the search_form
    """

    def name(self) -> Text:
        return "action_ask_keywords_feedback"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        keywords_expanded = keywords_expansion(tracker.get_slot("keywords"))

        data = []

        for i, keyword in enumerate(keywords_expanded.split("|")):
            data.append({"title": keyword, "payload": "k" + str(i)})

        message = {"payload": "quickReplies", "data": data}

        dispatcher.utter_message(
            text="Essayons d'améliorer votre recherche, pouvez-vous sélectionner les mots-clés qui vous semblent pertinents ?",
            json_message=message,
        )

        return [SlotSet("keywords_augmentation", keywords_expanded)]


class UtterConfirmSearch(Action):
    """
    Ask the user to confirm the keywords he will use for the search
    """

    def name(self):
        return "action_utter_confirm_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        keywords = tracker.get_slot("keywords").split(" ")
        keywords_aug = tracker.get_slot("keywords_augmentation").split("|")
        keywords_feedback = tracker.get_slot("keywords_feedback").split(" ")

        message = "Souhaitez-vous bien faire une recherche avec ces mots-clés ?\n"

        for keyword in keywords:
            message += keyword + " "

        for keyword in keywords_feedback:
            if keyword in keywords_aug:
                message += keyword + " "

        dispatcher.utter_message(text=message)


class SearchKeywordsInDatabase(Action):
    """
    Search DataSud API with keywords provided by the users and display results
    """

    def name(self):
        return "action_search_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        keywords = tracker.get_slot("keywords")

        if flag_activate_api_call:
            request_url = get_request_keywords_url(keywords)
            data = requests.post(request_url).json()
        else:
            with open("fake_api_results.json", encoding="utf-8") as f:
                data = json.load(f)

        results = data["result"]["results"]
        catalog_url = "https://trouver.datasud.fr/dataset/"

        if len(results) > 0:

            data = []
            results_title_slot = ""
            results_url_slot = ""
            for i, result in enumerate(results[0:5]):
                data.append(
                    {
                        "title": str(i + 1) + " - " + result["title"],
                        "description": catalog_url + result["name"],
                    }
                )
                results_title_slot += result["title"] + "|"
                results_url_slot += result["name"] + "|"

            message = {"payload": "collapsible", "data": data}
            dispatcher.utter_message(
                text="Voici les résultats que j'ai pu trouver:", json_message=message,
            )

            return [
                SlotSet(
                    "results_title", results_title_slot[: len(results_title_slot) - 1],
                ),
                SlotSet("results_url", results_url_slot[: len(results_url_slot) - 1]),
            ]
        else:
            dispatcher.utter_message(
                text="Désolé, je n'ai trouvé aucun résultat pour ta recherche."
            )
            return [SlotSet("results_title", None), SlotSet("results_url", None)]


class SendSearchInfo(Action):
    """
    Send search information to the database
    """

    def name(self):
        return "action_send_search_information_to_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        sql_query.add_new_search_query(
            tracker.sender_id,
            tracker.get_slot("keywords").replace(" ", "|"),
            flag_activate_sql_query_commit,
        )


class SendKeywordsFeedback(Action):
    """
    Send keywords proposed to the user to the database
    """

    def name(self):
        return "action_send_keywords_feedback_to_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id
        keywords_user = tracker.get_slot("keywords").replace(" ", "|")

        keywords_proposed = tracker.get_slot("keywords_augmentation")
        keywords_feedback = tracker.get_slot("keywords_feedback")

        if keywords_proposed is not None:

            keywords_proposed = keywords_proposed.split("|")
            keywords_feedback = keywords_feedback.split(" ")

            for keyword in keywords_proposed:

                if keyword in keywords_feedback:
                    feedback = 1
                else:
                    feedback = -1

                sql_query.add_keyword_proposed(
                    conversation_id,
                    keywords_user,
                    keyword,
                    feedback,
                    flag_activate_sql_query_commit,
                )


class SendResultsFeedback(Action):
    """
    Send Search results feedback to the database
    """

    def name(self):
        return "action_send_results_feedback_to_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id
        keywords_user = tracker.get_slot("keywords").replace(" ", "|")

        results_title_data = tracker.get_slot("results_title")
        results_url_data = tracker.get_slot("results_url")

        results_feedback = tracker.get_slot("results_feedback")
        if results_feedback is not None:
            results_feedback = results_feedback.split(" ")
        else:
            results_feedback = []

        if results_title_data is not None:
            results_title_data = results_title_data.split("|")
            results_url_data = results_url_data.split("|")
            for i in range(len(results_title_data)):

                if len(results_feedback) > 0:

                    if "0" not in results_feedback:

                        if str(i + 1) in results_feedback:
                            feedback = 1
                        else:
                            feedback = -1

                        sql_query.add_result(
                            conversation_id,
                            keywords_user,
                            (results_title_data[i], results_url_data[i]),
                            feedback,
                            flag_activate_sql_query_commit,
                        )
                    else:
                        sql_query.add_result(
                            conversation_id,
                            keywords_user,
                            (results_title_data[i], results_url_data[i]),
                            -1,
                            flag_activate_sql_query_commit,
                        )
                else:
                    sql_query.add_result(
                        conversation_id,
                        keywords_user,
                        (results_title_data[i], results_url_data[i]),
                        0,
                        flag_activate_sql_query_commit,
                    )
