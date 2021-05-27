# Documentation Rasa / Rasa X

# Déploiement sans docker

## Téléchargement des dépendances (ancien chatbot / ancien widget)

```py
sudo apt-get install gcc
pip install --use-feature=2020-resolver rasa==2.3.4
pip install --use-feature=2020-resolver rasa-x==0.38.0 --extra-index-url https://pypi.rasa.com/simple
```

### Nouveau chatbot (botfront)

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
git clone https://github.com/RasaHQ/rasa.git
cd rasa
poetry install

pip install --use-feature=2020-resolver rasa-x==0.38.0 --extra-index-url https://pypi.rasa.com/simple
```

## Training du chatbot

Depuis le répertoire `conciergerie-open-data/`

```
rasa train
```

## 1 - Lancement APIs
<https://github.com/moreymat/fastapi-lexical-resources>
<https://github.com/moreymat/fastapi-query-expansion>
<https://github.com/moreymat/fastapi-search-reranking>

## 2 - Lancement Rasa x
Depuis le répertoire `conciergerie-open-data/`

```
rasa x
```

## 3 - Lancement Custom actions server
Depuis le répertoire `conciergerie-open-data/custom-actions/`

```
rasa run actions --cors="*"
```

## 4 - Utilisation
Rasa-x accessible à l'adresse <http://localhost:5002>

La documentation des apis est disponible aux adresses <http://localhost:8001/docs>, <http://localhost:8002/docs> et <http://localhost:8003/docs>

widget: <https://github.com/moreymat/Chatbot-Widget> (ancient widget)

# Déploiement avec Docker

Requirements:
    - python >= 3.X
    - docker >= 20.X
    - pytest

## 1 - Création docker image expansion API

<https://github.com/moreymat/fastapi-lexical-resources>
<https://github.com/moreymat/fastapi-query-expansion>
<https://github.com/moreymat/fastapi-search-reranking>


## 2 - Création fichier dockers

Depuis le répertoire `conciergerie-open-data/`
Changer configuration dans `docker-config.config` 

```
sudo bash ./start_docker.sh [-a|-i|-d|-s|-h]
```

Une fois le docker lancé, créez un compte admin depuis le répertoire `~/etc/rasa`:

```
sudo python3 rasa_x_commands.py create --update admin me <PASSWORD>
```

## 3 - Integrated version

Rasa X is available at <http://localhost:80>

Liez vos données d'entraînement avec cette méthode:

<https://rasa.com/docs/rasa-x/installation-and-setup/deploy#integrated-version-control>

Vous pouvez maintenant entraîner un nouveau modèle.


## Widget

<https://github.com/moreymat/Chatbot-Widget>


# Répartition des fichiers

Squelette d'un chatbot (obtenu en faisant rasa init)

1. action: Dossier contenant le fichier actions.py qui permet l'appel a des fonctions personnalisés.

2. data:

    1. nlu.yml: Contient les données d'entraînements pour chaque intention et entité à détecter.

    2. rules.yml: Une rule représente un court dialogue entre l'utilisateur et le chatbot qui devrait toujours suivre le même chemin (ex: Si l'utilisateur dit "bonjour", il faut répondre "bonjour")

    3. stories.yml: Une story représente un dialogue possible entre l'utilisateur et le chatbot. (ex: une demande de changement d'adresse mail)

3. models: Dossier contenant les différentes itérations du modèle.

4. tests: Dossier contenant les stories qui devraient être aquises par le modèle.

5. config.yml: Contient la pipeline et les policies:

    1. Pipeline: Liste des différents composants NLU, un message de l'utilisateur sera traité par chaque composant. Un composant NLU est un objet qui va traité le message d'une certaine façon: extraction d'entité, prédiction d'intentions...

    2. Policies: Liste des politiques de choix d'action a chaque étape de la conversation. Si plusieurs politiques, celle qui est la plus confiante est choisit.

6. domain.yml: Définit les différentes variables du chatbot: Les actions, les intentions de l'utilisateur, les réponses, les entités...

7. credentials.yml: Contient les différents login des api que le chatbot utilise

8. endpoints.yml: Entrée Sortie globale du modèle: serveur contenant le modèle, serveur de stockage des conversations...

## Rasa

Ligne de commande local:

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
