# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
import sqlite3
import json
import requests
import codecs
from actions import sql_query

flag_activate_api_call = False
flag_activate_sql_query_commit = False

## Entrée: Mots clés de la recherche
## Sortie: URL pour appeler l'api
def get_request_keywords_url(keywords):

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


# Find new keywords that might interest the user
def keywords_augmentation(keywords):

    keywords_augmentation = "TO|DO|FUNCTION"

    return keywords_augmentation


# Reset all the slots
class ResetKeywordsSlot(Action):
    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("keywords", None),
            SlotSet("keywords_augmentation", None),
            SlotSet("keywords_feedback", None),
            SlotSet("results", None),
            SlotSet("results_feedback", None),
        ]


# Entrée: Keywords proposed to the user, and number written by the user
# Sorite: Save the keywords chosen by the user in the slot "keywords_feedback"
class SetKeywordsFeedback(Action):
    def name(self):
        return "action_set_keywords_feedback_slot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        keywords_augmented = tracker.get_slot("keywords_augmentation")
        keywords_feedback = tracker.get_slot("keywords_feedback")

        final = ""
        list_augmentation = keywords_augmented.split("|")
        initialiaze = False
        for feedback in keywords_feedback.split(" "):
            if feedback.isdigit():
                feedback = int(feedback)
                if feedback == 0:
                    return [SlotSet("keywords_feedback", "")]
                elif feedback - 1 >= 0 and feedback - 1 < len(list_augmentation):
                    final += list_augmentation[feedback - 1] + "|"
                    initialiaze = True

        if initialiaze:
            return [SlotSet("keywords_feedback", final[0 : len(final) - 1])]
        else:
            return [SlotSet("keywords_feedback", "")]


# Entrée: Results found by the model, and number written by the user
# Sorite: Save the results chosen by the user in the slot "results_feedback"
class SetResultsFeedback(Action):
    def name(self):
        return "action_set_results_feedback_slot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        results = tracker.get_slot("results")
        results_feedback = tracker.get_slot("results_feedback")

        final = ""
        initialiaze = False
        if len(results) > 0:
            list_results = results.split("|")
            for feedback in results_feedback.split(" "):
                if feedback.isdigit():
                    feedback = int(feedback)
                    if feedback == 0:
                        return [SlotSet("results_feedback", "")]
                    elif feedback - 1 >= 0 and feedback - 1 < len(list_results):
                        final += list_results[feedback - 1] + "|"
                        initialiaze = True

        if initialiaze:
            return [SlotSet("results_feedback", final[0 : len(final) - 1])]
        else:
            return [SlotSet("results_feedback", "")]


# Ask the user to confirm the keywords used for the search
class UtterConfirmSearch(Action):
    def name(self):
        return "action_utter_confirm_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        keywords = tracker.get_slot("keywords")
        keywords_feedback = tracker.get_slot("keywords_feedback")

        message = "Tu souhaites bien faire une recherche avec ces mots-clés ?\n"
        for keyword in keywords.split(" "):
            message += keyword + " "

        for keyword in keywords_feedback.split("|"):
            message += keyword + " "

        dispatcher.utter_message(text=message)


# Ask the user to choose which keywords are useful to him during the search_form
class AskForKeywordsFeedbackSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_keywords_feedback"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        keywords_augmented = keywords_augmentation(tracker.get_slot("keywords"))

        message = "Essayons d'améliorer ta recherche, peux-tu écrire les numéros des mots-clés qui te semblent pertinent ?\n"

        message += "0 - Aucun\n"

        for i, keyword in enumerate(keywords_augmented.split("|")):
            message += str(i + 1) + " - " + keyword + "\n"

        dispatcher.utter_message(text=message)

        return [SlotSet("keywords_augmentation", keywords_augmented)]


# Search DataSud API with keywords provided by the users and display results
class SearchKeywordsInDatabase(Action):
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
            results = data["result"]["results"]
            catalog_url = "https://trouver.datasud.fr/dataset/"

            if len(results) > 0:
                dispatcher.utter_message(
                    text="Voici les résultats que j'ai pu trouver:\n_"
                )

                results_slot = ""
                for i, result in enumerate(results[0:5]):
                    message = ""
                    # message += result["thumbnail"] + "\n"
                    message += str(i + 1) + " - "
                    message += result["title"] + "\n"
                    message += catalog_url + result["name"] + "\n_"
                    results_slot += result["title"] + "|"
                    dispatcher.utter_message(text=message)

                return [SlotSet("results", results_slot[0 : len(results_slot) - 1])]
            else:
                dispatcher.utter_message(
                    text="Désolé, je n'ai trouvé aucun résultat pour ta recherche."
                )
                return [SlotSet("results", "")]
        else:
            dispatcher.utter_message(text="API CALL DEACTIVATED")
            return [SlotSet("results", "API CALL DEACTIVATED")]


# Send search information to database
class SendSearchInfo(Action):
    def name(self):
        return "action_send_search_information_to_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        sql_query.add_new_search_query(
            (tracker.sender_id, tracker.get_slot("keywords").replace(" ", "|")),
            flag_activate_sql_query_commit,
        )


# Send keywords feedback to database
class SendKeywordsFeedback(Action):
    def name(self):
        return "action_send_keywords_feedback_to_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        sql_query.add_feedback_augmentation(
            (tracker.sender_id, tracker.get_slot("keywords").replace(" ", "|")),
            (
                tracker.get_slot("keywords_augmentation"),
                tracker.get_slot("keywords_feedback"),
            ),
            flag_activate_sql_query_commit,
        )


# Search results feedback to database
class SendResultsFeedback(Action):
    def name(self):
        return "action_send_results_feedback_to_database"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        sql_query.add_feedback_results(
            (tracker.sender_id, tracker.get_slot("keywords").replace(" ", "|")),
            (
                tracker.get_slot("results"),
                tracker.get_slot("results_feedback"),
            ),
            flag_activate_sql_query_commit,
        )