from typing import List, Optional, Union, Dict
from PIL import Image

from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.storage import TextStorage, ImageStorage
from app.storage import StorageImage
from app.comparator import Comparator, TextComparatorLD, TextComparatorLM, ImageComparator

import heapq
import requests
import asyncio
import tqdm

app = FastAPI()

app.mount("/images", StaticFiles(directory="storage/images"), name="images")

txt_storage = TextStorage('storage/texts.json')
img_storage = ImageStorage('storage/images')

txt_comparator = TextComparatorLD()
# txt_comparator = TextComparatorLM()

img_comparator = ImageComparator()

'''Request body for /search-text'''
class SearchTextBody(BaseModel):
    text: str
    topk: Optional[int] = -1
    threshold: Optional[float] = 0.5

'''Request body for /search-text'''
class SearchImageBody(BaseModel):
    id: int
    topk: Optional[int] = -1
    threshold: Optional[float] = 0.5


@app.post("/add-text", status_code=status.HTTP_201_CREATED)
async def add_text(texts: Union[str, List[str]]):
    if type(texts) == str:
        texts = [texts]
    asyncio.create_task(add_text_helper(texts=texts))
    return "Success"


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/search-text")
async def search_text(search_query: SearchTextBody):
    ranks = []
    query_message = search_query.text

    for text in txt_storage:
        occurrences = find_in_doc(doc=text, 
                                query=query_message, 
                                comparator=txt_comparator, 
                                threshold=search_query.threshold)

        if occurrences:
            max_similarity = max([occ['similarity'] for occ in occurrences])
            ranks.append({
                            'text': text,
                            'similarity': max_similarity,
                            'occurrences': occurrences
                        })

    topk = search_query.topk
    if topk == -1:
        topk = len(ranks)
    else:
        topk = min(topk, len(ranks))

    result = heapq.nlargest(topk, ranks, key=lambda x: x['similarity'])

    return result


@app.post("/add-image-file")
async def add_image_file(image_file: UploadFile):
    return "Not Implemented"


@app.post("/add-image-url")
async def add_image_url(image_url: Union[str, List[str]]):
    if type(image_url) == str:
        image_url = [image_url]
    ids = []
    for url in image_url:
        image = download_image(url)
        encoding = img_comparator.encode(image=image)
        id = img_storage.append(image=StorageImage(image=image, encoding=encoding))
        ids.append(id)
    return ids


@app.get("/search-image")
async def search_image(search_query: SearchImageBody):
    query_image = img_storage.get(search_query.id)

    if not query_image:
        raise HTTPException(status_code=404, detail=f"Could not find image: '{search_query.id}'") 

    query_image_encoding = query_image.encoding
    
    ranks = []

    for image in img_storage:
        similarity = img_comparator.similarity(query_image_encoding, image.encoding)
        ranks.append({
                        'id': image.id,
                        'similarity': similarity
                    })

    topk = search_query.topk
    if topk == -1:
        topk = len(ranks)
    else:
        topk = min(topk, len(ranks))

    result = heapq.nlargest(topk, ranks, key=lambda x: x['similarity'])

    return result


async def add_text_helper(texts: List[str]):
    print("Encoding texts")
    for text in tqdm.tqdm(texts):
        # any pre-processing needed for texts can be written here
        txt_storage.append(text)


def download_image(url: str) -> Image:
    resp = requests.get(url, stream=True)
    if not resp.ok:
        raise HTTPException(
            status_code=424, 
            detail=f"Could not download image from: {url}")

    return Image.open(resp.raw)


'''
    Given document and query phrase, searches for phrase in document.
    returns all parts of document with more similarity than threshold.
'''
def find_in_doc(doc: str, query: str, comparator: Comparator, threshold: float) -> List[Dict]:
    result = []
    cur_start = 0
    cur_end = 0
    query_word_count = query.count(' ') + 1

    for i in range(query_word_count):
        cur_end = doc.find(' ', cur_end + 1)
        if cur_end == -1: 
            cur_end = len(doc)
            break

    while cur_end <= len(doc):
        similarity = comparator.similarity(doc[cur_start:cur_end], query)
        if similarity > threshold:
            result.append({
                            'similarity': similarity,
                            'start': cur_start,
                            'end': cur_end,
                            'word': doc[cur_start:cur_end]
                        })

        if cur_end == len(doc):
            break

        cur_start = doc.find(' ', cur_start + 1)

        cur_end = doc.find(' ', cur_end + 1)
        if cur_end == -1:
            cur_end = len(doc)
    
    return result


