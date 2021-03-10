

![ScreenShot](static/img/banner.png)


  ***An Open Source ChatBot widget easy to connect to RASA bot through [Rest](https://rasa.com/docs/rasa/user-guide/connectors/your-own-website/#rest-channels) Channel.***


![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)
[![forthebadge](https://forthebadge.com/images/badges/for-you.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/made-with-javascript.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/uses-html.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/uses-css.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/built-with-swag.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/check-it-out.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/makes-people-smile.svg)](https://forthebadge.com)

## Features

- Text 
- Buttons
- Images
- Video 
- PDF Attachment
- Dropdown
- Quick replies
- Cards carousel
- Charts
- Collapsible
- Bot typing indicator
- Location access



## Instructions
- You can read the instructions here in [instructions.md](docs/instructions.md)

## Documentation
- Check out the documentation on how to send bot response from Rasa in [response.md](docs/responses.md)
- If you want to modify the UI elements, you can read on how to do here: [modifications.md](docs/modifications.md)

## Gallery:
- Check out the sample pics here [gallyery.md](docs/gallery.md)

## Sample Bots:
Below are the sample bot projects that were developed using Rasa and made to work with this widget
- [Restaurant Search Bot](https://github.com/JiteshGaikwad/Restaurant-Search-Bot.git)
- [HR Bot](https://github.com/JiteshGaikwad/HR_Bot)

## Library used:
- [Materialize CSS](https://materializecss.com) for CSS
- [Chart.js](https://www.chartjs.org/) for Charts

## Demo:

Check out the widget in action here [demo](https://www.youtube.com/watch?v=mnolLtOWykk)

# Forked for conciergerie

## CSS

Widget CSS modified to make it larger

## materialize library

materialize library is modified using https://github.com/Dogfalo/materialize/issues/2582#issuecomment-649188333 to have styling on lists 

## .collapsibles

collapsible take one more parameter along with `title` and `description`: `url` (of the datasud)

## .quickReplies

.quickReplies are modified to have these comportement instead:
- Can choose multiple chips
- Choosing a chip will delete it from the list and add it to the user text area

## showdown

Adding the showdown library to convert marddown to HTML

## resultFeedbackForm

Added the classes and function to have a form as a list of checkbox so the user can check which results were useful to him