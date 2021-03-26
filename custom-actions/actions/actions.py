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
from datetime import datetime

from actions import sql_query
from actions import api_call

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

flag_activate_api_call = False
flag_activate_sql_query_commit = True


def get_request_keywords_url(keywords, keywords_feedback):
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

    url += "||".join(keywords.split(" "))

    if keywords != "" and keywords_feedback != "":
        url += "||"

    url += "||".join(keywords_feedback.split(" "))

    return url


def get_keywords_expanded_list(keywords_expanded):
    """
    Input: Output of the expansion API
    Output: A list of keywords to display to the user
    """

    exp_terms = set([])

    for og_key in keywords_expanded:

        for dtsud_keyword in og_key["datasud_keywords"]:
            exp_terms.add(dtsud_keyword)

        for sense in og_key["tree"]:
            for similar_sense in sense["similar_senses"]:
                exp_terms.add(similar_sense[0]["sense"])

    return "|".join(exp_terms)


def keyword_originating_from_og_key(keyword, og_key_tree):

    """
    Input:  keyword: A keyword proposed by the expansion API
            og_key_tree: A tree resulting from a keyword entered by the user

    Output: True if keyword was proposed because of its similarity with og_key_tree["original_keyword], False if not
    """

    for dtsud_keyword in og_key_tree["datasud_keywords"]:

        if dtsud_keyword == keyword:

            return True

    for sense in og_key_tree["tree"]:

        for similar_sense in sense["similar_senses"]:

            if similar_sense[0]["sense"] == keyword:

                return True

    return False


def process_keyword_feedback(keyword_proposed, keywords_expanded, keywords_feedback):

    """
    Input:  keyword_proposed: A keyword proposed to the user
            keywords_expanded: Output of the API expansion (see API doc)
            keywords_feedback: List of keywords chosen by the user

    Output: original_keywords: list of keywords that resulted in the proposition of keyword by the API
            feedback: wether or not keyword_proposed was chosen by the user
    """

    original_keywords = []

    for og_key_tree in keywords_expanded:

        if keyword_originating_from_og_key(keyword_proposed, og_key_tree):

            original_keywords.append(og_key_tree["original_keyword"])

    if keyword_proposed in keywords_feedback:
        feedback = 1
    else:
        feedback = -1

    return original_keywords, feedback


class ResetKeywordsSlot(Action):
    """
    Reset all the slots of the rasa chatbot
    """

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("keywords", None),
            SlotSet("keywords_expanded", None),
            SlotSet("keywords_feedback", None),
            SlotSet("results_title", None),
            SlotSet("results_url", None),
            SlotSet("results_description", None),
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

        keywords_expanded = api_call.get_keywords_expansion_query(
            tracker.get_slot("keywords")
        )

        keywords_expanded_list = get_keywords_expanded_list(keywords_expanded)

        data = []

        for i, keyword in enumerate(keywords_expanded_list.split("|")):
            data.append({"title": keyword, "payload": "k" + str(i)})

        message = {"payload": "quickReplies", "data": data}

        dispatcher.utter_message(
            text="Essayons d'améliorer votre recherche, pouvez-vous sélectionner les mots-clés qui vous semblent pertinents ?",
            json_message=message,
        )

        return [
            SlotSet("keywords_expanded", keywords_expanded),
            SlotSet("keywords_proposed", keywords_expanded_list),
        ]


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
        keywords_feedback = tracker.get_slot("keywords_feedback")

        request_url = get_request_keywords_url(keywords, keywords_feedback)
        if flag_activate_api_call:
            data = requests.post(request_url).json()
        else:
            with open("../fake_api_results.json", encoding="utf-8") as f:
                data = json.load(f)

        results = data["result"]["results"]
        catalog_url = "https://trouver.datasud.fr/dataset/"

        if len(results) > 0:

            data = []
            results_title_slot = ""
            results_url_slot = ""
            results_description_slot = ""
            for i, result in enumerate(results[0:5]):
                data.append(
                    {
                        "title": str(i + 1) + " - " + result["title"],
                        "url": catalog_url + result["name"],
                        "description": result["notes"],
                    }
                )
                results_title_slot += result["title"] + "|"
                results_url_slot += result["name"] + "|"
                results_description_slot += result["notes"] + "|"

            message = {"payload": "collapsible", "data": data}
            dispatcher.utter_message(
                text="Voici les résultats que j'ai pu trouver:", json_message=message,
            )

            return [
                SlotSet(
                    "results_title", results_title_slot[: len(results_title_slot) - 1],
                ),
                SlotSet("results_url", results_url_slot[: len(results_url_slot) - 1]),
                SlotSet(
                    "results_description",
                    results_description_slot[: len(results_description_slot) - 1],
                ),
            ]
        else:
            dispatcher.utter_message(
                text="Je suis désolé, je n'ai trouvé aucun résultat pour votre recherche."
            )
            return [
                SlotSet("results_title", None),
                SlotSet("results_url", None),
                SlotSet("results_description", None),
            ]


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

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        api_call.add_expansion_search_query(
            tracker.sender_id, tracker.get_slot("keywords"), date
        )

        # add reranking api call


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

        keywords_expanded = tracker.get_slot("keywords_expanded")
        keywords_proposed = tracker.get_slot("keywords_proposed")
        keywords_feedback = tracker.get_slot("keywords_feedback")

        feedbacks_list = []

        if keywords_proposed is not None and keywords_feedback is not None:

            keywords_proposed = keywords_proposed.split("|")
            keywords_feedback = keywords_feedback.split(" ")

            for keyword in keywords_proposed:

                original_keywords, feedback = process_keyword_feedback(
                    keyword, keywords_expanded, keywords_feedback
                )

                for og_keyword in original_keywords:

                    feedbacks_list.append(
                        {
                            "original_keyword": og_keyword,
                            "proposed_keyword": keyword,
                            "feedback": feedback,
                        }
                    )

            api_call.add_expansion_feedback_query(
                tracker.sender_id, tracker.get_slot("keywords"), feedbacks_list
            )


class AskForResultsFeedbackSlotAction(Action):
    """
    Ask the user to choose which results were useful to him
    """

    def name(self) -> Text:
        return "action_ask_results_feedback"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        results_title = tracker.get_slot("results_title")

        data = []

        for i, title in enumerate(results_title.split("|")):
            data.append({"title": title, "payload": "k" + str(i)})

        message = {"payload": "resultfeedback", "data": data}

        dispatcher.utter_message(
            text="Pouvez-vous cocher les jeu de données qui vous ont été pertinents ?",
            json_message=message,
        )


class RecapResultsFeedback(Action):
    """
    Feedback format example: 0 2 1
    Summarize the feedback to the user
    """

    def name(self):
        return "action_recap_feedback_to_user"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id

        results_title_data = tracker.get_slot("results_title")
        results_feedback = tracker.get_slot("results_feedback")

        if results_feedback is not None:
            results_feedback = results_feedback.split(" ")
        else:
            results_feedback = []

        recap_msg = ""
        if results_title_data is not None and len(results_feedback) > 0:

            results_title_data = results_title_data.split("|")

            for i in range(len(results_title_data)):

                if str(i) in results_feedback:
                    recap_msg += " - " + results_title_data[i] + "<br>"

        if len(recap_msg) == 0:
            final_msg = "Vous n'avez choisi aucun jeu de données."
        else:
            final_msg = (
                "Merci beaucoup!<br>Voilà ce que vous avez choisi:<br>" + recap_msg
            )

        dispatcher.utter_message(text=final_msg)


class SendResultsFeedback(Action):
    """
    Feedback format example: 0 3 4
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


# Actions triggered from rasa chatbot widget


class ActionGreetUser(Action):
    """
    Greet the user at the start of a conversation
    """

    def name(self):
        return "action_greet_user"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Bonjour, je suis là pour vous aider, cherchez vous un jeu de données ?"
        )
