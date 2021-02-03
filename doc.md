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

TODO
