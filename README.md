# conciergerie-open-data

## ToDo

### Objectif #1 : Rasa docker

#### Pitch
> *"être capable de faire un petit déploiement local"*

#### Echéance : vendredi 5 janvier 2021.

#### Tâches
- [ ] trouver une image Docker à adapter (doc Rasa ?) => @Sylvain
- [ ] adapter image Docker pour un déploiement léger => @Mathieu
- [ ] construire bot acceptant user input en ligne de commande => @Sylvain
- [ ] coder un composant dédié d'extension de requête (base WordNet ou Word2Vec) => @Mathieu
- [ ] coder un composant dédié d'appel à l'API DataSud => @Mathieu
- [ ] permettre au bot de présenter les réponses de l'API DataSud à l'usager => @Sylvain
- [ ] permettre à l'usager de valider un ou plusieurs choix en ligne de commande (liste numérotée) => @Sylvain

## Méta-moteur de recherche
https://searx.github.io/searx/


### Cas particuliers

* La requête renvoie un jeu de données choisi dans l'échantillon mais non visé par la requête. Exemples :
    * "termes":"qualité de l'eau" teste "true" pour "cible_url": "https://trouver.datasud.fr/dataset/syncf2de19f-fr-120066022-jdd-58fa0f8a-fa62-4e33-a840-c4b701a19929" ;
    * "termes":"production d'énergies renouvelables" ou "production d'électricité solaire" testent "true" pour "cible_url": "https://trouver.datasud.fr/dataset/syncf2de19f-fr-120066022-jdd-58fa0f8a-fa62-4e33-a840-c4b701a19929" ;

* certaines requêtes s'avèrent attrapent tout : le succès sur un jeu de données n'augure pas de sa trouvabilité . Exemple : ":"test de la qualité de l'eau", "succes":true sur "cible_url":,"https://trouver.datasud.fr/dataset/syncc2605d7-fr-120066022-jdd-b25fcad6-acdd-4dd2-9551-95565e0c9097" renvoie 985 jeux de données ;




## Chatbot
* https://rasa.com/docs/rasa-x/

