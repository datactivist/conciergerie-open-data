# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import json
import re
from typing import Any, Text, Dict, List
from datetime import datetime

from actions import api_call

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType, FollowupAction

keywords_delimitor = " |,|;|_|\|"


def get_keywords_expanded_list(keywords_expanded, user_search):
    """
    Input: keywords_expanded: Output of the expansion API
           user_search: search entered by the user
    Output: A list of keywords to display to the user

    Order example: [barrage éolien]
     - take the first keyword for barrage from the referentiel
     - take the first keyword for barrage from the embeddings
     - take the first keyword for éolien from the referentiel
     - take the first keyword for éolien from the embeddings
     - take the second keyword for barrage from the referentiel
     [...]
    """

    user_search_list = re.split(keywords_delimitor, user_search)
    for i in range(len(user_search_list)):
        user_search_list[i] = user_search_list[i].lower()
    exp_terms = []
    done = False
    index = 0

    while not done and index < 25:
        done = True
        for og_key in keywords_expanded:  # loop on original keywords
            # Take the n°index of the referentiel
            og_word = og_key["referentiel"]["tags"]
            if og_word is not None and len(og_word) > index:  # if it exist
                done = False
                for ref_tag_word in re.split(keywords_delimitor, og_word[index]):
                    if (
                        ref_tag_word.lower() not in user_search_list
                        and ref_tag_word.lower() not in exp_terms
                    ):
                        exp_terms.append(ref_tag_word.lower())

            # Take the n°index of the embeddings
            og_word = og_key["tree"][0]["similar_senses"]
            if og_word is not None and len(og_word) > index:  # if it exist
                done = False
                for ref_tag_word in re.split(
                    keywords_delimitor, og_word[index][0]["sense"]
                ):
                    if (
                        ref_tag_word.lower() not in user_search_list
                        and ref_tag_word.lower() not in exp_terms
                    ):
                        exp_terms.append(ref_tag_word.lower())
        index += 1
    return "|".join(exp_terms)


def keyword_originating_from_og_key(keyword, og_key_tree):

    """
    Input:  keyword: A keyword proposed by the expansion API
            og_key_tree: A tree resulting from a keyword entered by the user

    Output: True if keyword was proposed because of its similarity with og_key_tree["original_keyword], False if not
    """

    if og_key_tree["referentiel"]["tags"] is not None:
        for keyw in og_key_tree["referentiel"]["tags"]:
            if keyw == keyword:
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
            SlotSet("results", None),
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

        user_search = tracker.get_slot("keywords")

        keywords_expanded = api_call.get_keywords_expansion_query(
            user_search, {"name": "datasud"}
        )

        print(keywords_expanded)

        keywords_expanded_list = get_keywords_expanded_list(
            keywords_expanded, user_search
        )

        print("show user:", keywords_expanded_list)

        if len(keywords_expanded_list) > 0:
            keywords = [
                {"content_type": "text", "title": x, "payload": "k" + str(i)}
                for i, x in enumerate(
                    re.split(keywords_delimitor, keywords_expanded_list)
                )
            ]

            # Le custom payload est détecté comme un texte, donc j'ajoute un type qui permet facilement de détecter que c'est un un custom payload au niveau du widget
            payload = {
                "type": "custom_payload_keywords",
                "text": "Essayons d'améliorer votre recherche. Cliquez sur les mots-clés qui vous semblent intéressants pour les ajouter à votre message.",
                "nb_max_keywords": 8,
                "keywords": keywords,
            }

            dispatcher.utter_message(json.dumps(payload))

            return [
                SlotSet("keywords_expanded", keywords_expanded),
                SlotSet("keywords_proposed", keywords_expanded_list),
            ]

        else:
            return [
                SlotSet("keywords_expanded", ""),
                SlotSet("keywords_proposed", ""),
                SlotSet("keywords_feedback", ""),
                SlotSet("requested_slot", None),
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
        conversation_id = tracker.sender_id
        keywords_feedback = tracker.get_slot("keywords_feedback")

        results = api_call.get_results_from_keywords(keywords, keywords_feedback, 5)

        reranking_data = []
        reranking_data.append({"api_hostname": "datasud", "results_list": results})

        catalog_url = "https://trouver.datasud.fr/dataset/"
        if len(results) > 0:

            results = api_call.get_search_reranking_query(
                conversation_id, keywords, reranking_data
            )

            results_payload = []
            for i, result in enumerate(results[0:5]):
                results_payload.append(
                    {
                        "title": result["title"],
                        "author": result["owner_org"],
                        "url": catalog_url + result["url"],
                        "description": result["description"],
                    }
                )

            dispatcher.utter_message(text="Voici les résultats que j'ai pu trouver:")
            payload = {
                "type": "custom_payload_results_display",
                "nb_max_results": 5,
                "results": results_payload,
            }

            dispatcher.utter_message(json.dumps(payload))

            return [
                SlotSet("results", results),
            ]
        else:
            dispatcher.utter_message(
                text="Je suis désolé, je n'ai trouvé aucun résultat pour votre recherche."
            )

            return [
                SlotSet("results", None),
            ]


class SendSearchInfo(Action):
    """
    Send search information to the database
    """

    def name(self):
        return "action_send_search_information_to_API"

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

        api_call.add_reranking_search_query(
            tracker.sender_id, tracker.get_slot("keywords"), date
        )


class SendKeywordsFeedback(Action):

    """
    Send keywords proposed to the user to the database
    """

    def name(self):
        return "action_send_keywords_feedback_to_expansion_API"

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

            keywords_proposed = re.split(keywords_delimitor, keywords_proposed)
            keywords_feedback = re.split(keywords_delimitor, keywords_feedback)

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


class FeedbackProposition(Action):
    """
    If we found results, ask the user if he wants to give feedback
    """

    def name(self):
        return "action_feedback_proposition"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        results = tracker.get_slot("results")
        if results != None and len(results) > 0:
            dispatcher.utter_message(
                text="Seriez-vous d'accord de prendre quelques secondes de votre temps pour m'aider à m'améliorer ?"
            )
        else:
            # return {"event": "followup", "name": "action_recap_feedback_to_user"}
            return [FollowupAction("utter_submit_feedback_form")]


class AskForResultsFeedbackSlotAction(Action):
    """
    Ask the user to choose which results were useful to him
    """

    def name(self) -> Text:
        return "action_ask_results_feedback"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        results = tracker.get_slot("results")

        feedback_payload = []
        catalog_url = "https://trouver.datasud.fr/dataset/"
        for i, result in enumerate(results[0:5]):
            feedback_payload.append(
                {
                    "title": result["title"],
                    "author": result["owner_org"],
                    "url": catalog_url + result["url"],
                    "description": result["description"],
                }
            )

        dispatcher.utter_message(
            text="Veuillez cocher les résultats qui vous ont étés utiles:"
        )
        payload = {
            "type": "custom_payload_feedbacks_display",
            "nb_max_feedbacks": 5,
            "feedbacks": feedback_payload,
        }

        dispatcher.utter_message(json.dumps(payload))


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

        dispatcher.utter_message(text="Merci beaucoup pour votre retour!")


class InitialMessage(Action):
    """
    First message sent to user by chatbot
    """

    def name(self):
        return "action_initial_message"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        propositions = [
            {"payload": "/request_search", "title": "Je recherche des données"},
            {
                "payload": "/ask_datasud",
                "title": "J'aimerais en savoir plus sur Datasud",
            },
            {
                "payload": "/ask_cu",
                "title": "Je voudrais connaître les conditions d'utilisation",
            },
            {"payload": "/goodbye", "title": "Je n'ai besoin de rien"},
        ]

        dispatcher.utter_message(
            text="Bonjour, comment puis-je vous aider ?", buttons=propositions
        )


class SetDatasudFlag(Action):
    """
    Set has_asked_datasud_flag to True
    """

    def name(self):
        return "action_set_datasud_flag"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("has_asked_datasud_flag", True),
        ]


class SetCUFlag(Action):
    """
    Set has_asked_cu_flag to True
    """

    def name(self):
        return "action_set_cu_flag"

    def run(self, dispatcher, tracker, domain):
        return [
            SlotSet("has_asked_cu_flag", True),
        ]


class AnythingElse(Action):
    """
    Message sent to user to ask if he needs anything else
    """

    def name(self):
        return "action_anything_else"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        has_asked_datasud_flag = tracker.get_slot("has_asked_datasud_flag")
        has_asked_cu_flag = tracker.get_slot("has_asked_cu_flag")

        propositions = []
        propositions.append(
            {"payload": "/request_search", "title": "Je recherche des données"}
        )
        if not has_asked_datasud_flag:
            propositions.append(
                {
                    "payload": "/ask_datasud",
                    "title": "J'aimerais en savoir plus sur Datasud",
                }
            )
        if not has_asked_cu_flag:
            propositions.append(
                {
                    "payload": "/ask_cu",
                    "title": "Je voudrais connaître les conditions d'utilisation",
                }
            )
        propositions.append({"payload": "/goodbye", "title": "Je n'ai besoin de rien"})

        dispatcher.utter_message(
            text="Avez-vous besoin d'autre chose ?", buttons=propositions
        )


class SendResultsFeedback(Action):
    """
    Feedback format example: 0 3 4
    Send Search results feedback to the database
    """

    def name(self):
        return "action_send_results_feedback_to_reranking_API"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id
        user_search = tracker.get_slot("keywords")
        keywords_feedback = tracker.get_slot("keywords_feedback")
        results = tracker.get_slot("results")

        results_feedback = tracker.get_slot("results_feedback")
        if results_feedback is not None:
            results_feedback = results_feedback.split(" ")
        else:
            results_feedback = []

        feedbacks_list = []
        if results is not None and len(results) > 0:
            if len(results_feedback) > 0:
                for i, result in enumerate(results):
                    if str(i) in results_feedback:
                        feedbacks_list.append({"result": result, "feedback": 1})
                    else:
                        feedbacks_list.append({"result": result, "feedback": -1})
            else:
                for i, result in enumerate(results):
                    feedbacks_list.append({"result": result, "feedback": 0})

        api_call.add_reranking_feedback_query(
            conversation_id, user_search, keywords_feedback, feedbacks_list
        )
