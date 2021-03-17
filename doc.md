# Documentation Rasa / Rasa X

# Déploiement sans docker

## Téléchargement des dépendances

```py
sudo apt-get install gcc
pip install --use-feature=2020-resolver rasa
pip install --use-feature=2020-resolver rasa-x --extra-index-url https://pypi.rasa.com/simple
pip install nltk pymagnitude
pip install lz4 xxhash annoy fasteners torch
```

## Training du chatbot

Depuis le répertoire `conciergerie-open-data/chatbot/`

```
rasa train
```

## 1 - Lancement Rasa x
Depuis le répertoire `conciergerie-open-data/chatbot/`

```
rasa x
```

## 2 - Lancement Custom actions server
Depuis le répertoire `conciergerie-open-data/chatbot/custom-actions/`

```
rasa run actions --cors="*"
```

## 3 - Lancement expansion API
<https://github.com/moreymat/fastapi-query-expansion>

## 4 - Utilisation
Rasa-x accessible à l'adresse <http://localhost:5002>

La documentation de l'api est disponible à l'adresse <http://localhost:8000/docs>

Pour utiliser le widget, lancer le fichier html `conciergerie-open-data/widget/index.html`

# Déploiement avec Docker

## Training du chatbot

Depuis le répertoire `conciergerie-open-data/chatbot/`

```
rasa train
```

## 1 - Création docker image expansion API
<https://github.com/moreymat/fastapi-query-expansion>

## 2 - Création docker image custom actions

Dans le fichier `conciergerie-open-data/chatbot/custom-actions/actions.py`, changer la valeur de `search_expand_url` en <http://query-exp:80/query_expand>

Depuis le répertoire `conciergerie-open-data/chatbot/custom-actions/`: 

```
sudo docker build . -t rasa/rasa-actions-sdk:1.0.0
```

## 3 - Création docker image rasa x

Depuis le répertoire `conciergerie-open-data/chatbot/`


```sh
curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/0.37.1/install.sh
sudo bash ./install.sh
cd <root>/etc/rasa/
```

Dans le fichier `.env`, modifier ces deux attributs:
- RASA_X_VERSION=0.37.0
- RASA_VERSION=2.3.4

dans le fichier `credentials.yml`, ajouter la ligne:

```
rest:
```

Ajouter le fichier `docker-compose.override.yml` dans le répertoire `<root>/etc/rasa`

## Lancement du docker
Dans le répertoire `<root>/etc/rasa`:

```
sudo docker-compose up
```

## Utilisation

Rasa-x est disponible à l'adresse <http://localhost:80>

Pour utiliser le widget, modifier la valeur de `rasa_server_url` dans `conciergerie-open-data/widget/static/script.js` en <http://localhost:80/webhooks/rest/webhook>

Si et seulement si vous travaillez sous localhost, lancer google chrome avec
```
google-chrome --disable-web-security --user-data-dir
```

puis ouvrir dans le navigateur web le fichier `conciergerie-open-data/widget/index.html`

# Répartition des fichiers

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

6. rasa data validate: Vérifie qu'il n'y pas d'incohérences dans les données d'entraînements.

7. rasa test core --stories test_stories.yml --out results: Teste le modèle sur les stories données en entrées

8. rasa test nlu --nlu data/nlu.yml --cross-validation: Test le NLU avec une cross validation

## Rasa X

Rasa X permet de développer le chatbot avec des conversations réelles simplement.
Il offre une interface graphique intuitif.

### Interactive Chat

![1-Interactive_Chat](https://i.ibb.co/xg9qsYM/1-Interactive.png)

L'onglet "Talk to your bot" permet d'avoir une conversation intéractive avec le chatbot (à la manière de rasa interactive)

1. Conversation actuelle

2. Conversation actuelle sous le format Story, avec possibilité de l'ajouter aux données d'entraînement ou de la supprimer.

3. Entités Prédites

4. Boite d'envoie de message

Chaque décision peut être corrigé en cliquant dessus.

### Conversations

![2-Conversations_lists](https://i.ibb.co/4Sgt9xh/2-Conversation.png)

L'onglet conversations contient toutes les conversations que le chatbot a eu avec vous ou avec d'autres utilisateurs.

1. Liste des conversations

2. Affichage de la conversations

3. Action a faire pour la conversation actuelle

### NLU Predictions

![3-NLU_Predictions](https://i.ibb.co/YXDR793/3-NLUPredictions.png)

L'onglet NLU Inbox contient toutes les prédictions d'intentions et d'entités que le NLU a fait.

1. Liste des prédictions

2. Actions a effectuer pour la prédiction actuelle.

### Models

![4-Models](https://i.ibb.co/vvd1Wp6/4-Modeles.png)

L'onglet models contient toutes les itérations du modèle et permet de passer de l'une à l'autre.

### Training Data

![5-Training_Data](https://i.ibb.co/VSVybcc/5-Training.png)

Enfin, il y a la possibilité de modifier les différents fichiers composants le chatbot directement depuis l'interface ainsi que d'entraîner le modèle avec les nouvelles données.

## Testé le modèle

### Vérification de l'intégrité

Il est conseillé de tester le modèle à chaque ajout de nouvelles fonctionnalités pour s'assurer qu'il est toujours capable de réaliser ses anciennes fonctions:
- rasa data validate
- rasa test core --stories test_stories.yml --out results

Pensez à ajouter de nouvelles stories de test pour les nouvelles fonctions.

### Comparaisons de modèles

Lorsque vous ajoutez beaucoup de données, il est conseillé de comparer les performanes NLU du nouveau modèle avec l'ancien modèle pour s'assurer qu'il ne perd pas en performance (overfit/ajout d'ambiguité...):
rasa test -m model nlu --nlu data/nlu.yml --cross-validation

Vous pouvez comparer différentes configurations de pipeline:
rasa test nlu --nlu data/nlu.yml --config config_1.yml config_2.yml

De même pour différentes configurations de policies:

1. Entrainer différents modèles: rasa train core -c config_1.yml config_2.yml --out comparison_models

2. Tester les modèles: rasa test core -m comparison_models --stories stories_folder --out comparison_results --evaluate-model-directory
