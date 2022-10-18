# semantic-search

## About Project

This project implements a semantic search for text and images. Instead of searching for literal matches, it considers the contextual meaning of the words in query text and data. For Images, search works not only with cropped or distorted images but also with similar scenes in different lighting, the same person from different angles, etc.

## Usage

Search is implemented as REST API. It contains Georgian proverbs and a sample image dataset for searching. Users can add new sentences, and new images, search for similar images to the one already in storage by its id, or search for a keyword in all texts. You can run the server by installing all of the requirements described in [requirements.txt](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/requirements.txt) and run the FastAPI server with:
```sh
uvicorn app.main:app
```
Alternatively, you can run the application in docker by running the following commands in the project root:
```sh
docker build . -t semantic-search
docker run -p 8080:8080 semantic-search
```

## API
Please refer to [API Documentation](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/api_docs.md).

## Structure
The project is divided into conceptual code and an actual search engine.

### Text Similarity
[Text Similarity.ipynb](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/Text%20Similarity.ipynb) contains experimentation on computing the similarity of two texts and finding similar texts in a given corpus.

### Image Similarity
[Image Similarity.ipynb](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/Image%20Similarity.ipynb) explores different ways of comparing two images and searching for similar pictures in the sample dataset.

### App
Implements actual search engine. Currently, this part is implemented as REST API.

[main](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/app/main.py) implements the server and searching.

[comparator](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/app/comparator.py) contains comparator classes for both texts and images.

[storage](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/app/storage.py) contains a class for storing texts and images. Other storage or database integrations can be implemented here.

## Contribute
Thanks for taking the time to contribute to this project! There are many ways you can help out.

### Questions
If you have a question, create an issue, and label it as a question.

### Issues for bugs or feature requests
If you encounter any bugs in the code or want to request a new feature, please create an issue to report it and add a label to indicate what type of issue it is.

### Contribute Code
We welcome your pull requests for bug fixes. To implement something new, please create an issue first so we can discuss it together.

When your code is ready to be submitted, submit a pull request to begin the code review process.

## Areas of Improvement

* At the moment storage class reads texts and images from static files. New data is added but not saved after the application shutdown. This behavior can be improved by implementing persistent storage.
* Instead of using static files, database integrations can also be implemented in the storage module.
* Search Engine works by computing the similarity between a query and all entries in the corpus. For large corpus, this will take too long. You can use more advanced algorithms to increase speed. Please refer to this [article](https://www.sbert.net/examples/applications/semantic-search/README.html).

## License
This project is licensed under the terms of the MIT open source license. Please refer to [LICENSE](https://github.com/Supernova-PulsarAIGeorgia/semantic-search/blob/main/LICENSE) for the full terms.
