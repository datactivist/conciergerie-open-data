# Documentation Rasa / Rasa X

## Installation

__Dépendence:__
pip : 20.2.4 ou moins

__Installation Windows:__

1. pip install --use-feature=2020-resolver rasa

2. pip uninstall ujson / pip install ujson-1.35-cp37-cp37m-linux_x86_64.whl

3. conda install ujson==1.35

4. pip install  --use-feature=2020-resolver rasa-x --extra-index-url

Rasa x (en local) très peu stable

__Installation Linux:__

TODO

## Répartition des fichiers

Squelette d'un chatbot (obtenu en faisant rasa init)

1. Dossier action: Dossier contenant le fichier actions.py qui permet l'appel a des fonctions personnalisés.

2. Dossier data:

    1. Fichier nlu.yml: Contient les données d'entraînements pour chaque intention et entité à détecter.

    2. Fichier rules.yml: Une rule représente un cout dialogue entre l'utilisateur et le chatbot qui devrait toujours suivre le même chemin (ex: Si l'utilisateur dit "bonjour", il faut répondre "bonjour")

    3. Fichier stories.yml: Une story représente un dialogue possible entre l'utilisateur et le chatbot. (ex: une demande de changement d'adresse mail)

3. Dossier models: Dossier contenant les différentes itérations du modèle.

4. tests: Dossier contenant les stories qui devraient être aquises par le modèle.

5. Fichier config.yml: Contient la pipeline et les policies:

    1. Pipeline: Liste des différents composants NLU, un message de l'utilisateur sera traité par chaque composant. Un composant NLU est un objet qui va traité le message d'une certaine façon: extraction d'entité, prédiction d'intentions...

    2. Policies: Liste des politiques de choix d'action a chaque étape de la conversation. Si plusieurs politiques, celle qui est la plus confiante est choisit.

6. domain.yml: Définit les différentes variables du chatbot: Les actions, les intentions de l'utilisateur, les réponses, les entités...

7. credentials.yml: Contient les différents login des api que le chatbot utilise

8. endpoints.yml: Entrée Sortie globale du modèle: serveur contenant le modèle, serveur de stockage des conversations...

## Rasa

Ligne de commande:

1. rasa init: Crée les dossiers et fichiers nécessaires pour un chatbot basique

2. rasa train: train le modèle sur les nouvelles additions

3. rasa shell: discussion avec le chatbot

4. rasa run: Permet de lancer le chatbot sur un serveur. Option --enable-api pour activer l'api.

5. rasa interactive: train le modèle puis permet la génération de données d'entraînement. Ajouter le modèle avec l'option --model pour passer l'entraînement. Discussion avec le bot avec une demande de confirmation à chaque décision. Appuyer sur ctrl+C permet différentes actions:

    1. Continue: Reprendre là ou l'on était

    2. Undo Last: Annuler la dernière action (impossibilité d'annuler plus d'une action)

    3. Fork: Todo

    4. Start Fresh: Réinitialiser la discussion actuelle (création d'une nouvelle story)

    5. Export & Quit: Ajoute les différentes story et données d'entraînements crées et qui l'interface.

    6. Ctrl+C: Quitte sans faire de modification

## Rasa X

Rasa X offre une interface graphique intuitif et une facilité de partage du chatbot.

![1-Interactive_Chat](https://i.ibb.co/xg9qsYM/1-Interactive.png)

L'onglet "Talk to your bot" permet d'avoir une conversation intéractive avec le chatbot (à la manière de rasa interactive)

1. Conversation actuelle

2. Conversation actuelle sous le format Story, avec possibilité de l'ajouter aux données d'entraînement ou de la supprimer.

3. Entités Prédites

4. Boite d'envoie de message

Chaque décision peut être corrigé en cliquant dessus.

![2-Conversatons_lists](https://i.ibb.co/4Sgt9xh/2-Conversation.png)

L'onglet conversations contient toutes les conversations que le chatbot a eu avec vous ou avec d'autres utilisateurs.

1. Liste des conversations

2. Affichage de la conversations

3. Action a faire pour la conversation actuelle

![3-NLU_Predictions](https://i.ibb.co/YXDR793/3-NLUPredictions.png)

L'onglet NLU Inbox contient toutes les prédictions d'intentions et d'entités que le NLU a fait.

1. Liste des prédictions

2. Actions a effectuer pour la prédiction actuelle.

![4-Models](https://i.ibb.co/vvd1Wp6/4-Modeles.png)

L'onglet models contient toutes les itérations du modèle et permet de passer de l'une à l'autre.

![5-Training_Data](https://i.ibb.co/VSVybcc/5-Training.png)

Enfin, il y a la possibilité de modifier les différents fichiers composants le chatbot directement depuis l'interface ainsi que d'entraîner le modèle avec les nouvelles données.
