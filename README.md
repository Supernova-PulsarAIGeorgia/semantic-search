# semantic-search

## About Project
---

This project implements a semantic search for text and images. Instead of searching for literal matches, it considers the contextual meaning of the words in query text and data. For Images, search works not only with cropped or distorted images but also with similar scenes in different lighting, the same person from different angles, etc.

## Usage
---

Search is implemented as REST API. It contains Gerogian proverbs and sample image dataset for searching. User can add new sentences, new image, seach similar images of the one already in storage by its id or search for a keyword in all texts.
You can run server by installing all of the requirements described in [requirements.txt](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/requirements.txt) and run FastAPI server with ```uvicorn app.main:app```. Alternatively you can run application in docker with running following comands in project root:
```docker build . -t semantic-search```
```docker run -p 8080:8080 semantic-search```

## API
---
reference

## Structure
---
The project is divided into conceptual code and an actual search engine.

### Text Similarity
[Text Similarity.ipynb]() contains experimentation on computing the similarity of two texts and finding similar texts in a given corpus.

### Image Similarity
[Image Similarity.ipynb]() explores different ways of comparing two images and searching for similar pictures in the sample dataset.

### App
Implements actual search engine. Currently this part is imjplemented as REST API. 

## Contribute
---
Thanks for taking the time to contribute to this project! There are many ways you can help out.

### Questions
If you have a question that needs an answer, create an issue, and label it as a question.

### Issues for bugs or feature requests
If you encounter any bugs in the code, or want to request a new feature or enhancement, please create an issue to report it. Kindly add a label to indicate what type of issue it is.

### Contribute Code
We welcome your pull requests for bug fixes. To implement something new, please create an issue first so we can discuss it together.

When your code is ready to be submitted, submit a pull request to begin the code review process. We have added a pull request template on our project.


## License
---
This project is licensed under the terms of the MIT open source license. Please refer to [LICENSE](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/LICENSE) for the full terms.
