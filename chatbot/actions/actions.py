# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import sqlite3
import json
import requests
import codecs
import sql_query


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


# Reset the slot keywords
class ResetSlot(Action):
    def name(self):
        return "action_reset_keywords_slot"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("keywords", None)]


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

        request_url = get_request_keywords_url(tracker.get_slot("keywords"))
        data = requests.post(request_url).json()

        results = data["result"]["results"]
        catalog_url = "https://trouver.datasud.fr/dataset/"

        if len(results) > 0:
            dispatcher.utter_message(text="Voici les résultats que j'ai pu trouver:\n_")

            for result in results[0:5]:
                message = ""
                # message += result["thumbnail"] + "\n"
                message += result["title"] + "\n"
                message += catalog_url + result["name"] + "\n_"
                dispatcher.utter_message(text=message)
        else:
            dispatcher.utter_message(
                text="Désolé, je n'ai trouvé aucun résultat pour ta recherche."
            )
