from tracemalloc import start
from typing import List, Optional, Tuple, Union, Dict
from enum import Enum
from PIL import Image as Image

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import MongoDB
from app.database import Post as DBPost
from app.similarity import TextSimilarityLev, TextSimilarityTr, ImageSimilarity

import heapq
import json
import requests
import asyncio
import tqdm

with open('app/config.json') as f:
    config = json.load(f)

CONNECTION_STRING = config['database']['connection_string']
LM_NAME = config['language_model']['name']
MESSAGE_WEIGHT = config['score_weights']['message_weight']
IMAGE_WEIGHT = config['score_weights']['image_weight']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database = MongoDB(CONNECTION_STRING)
txt_similarity_lev = TextSimilarityLev()
txt_similarity_tr = TextSimilarityTr(LM_NAME)
img_similarity = ImageSimilarity()


class MediaType(Enum):
    link = 'link'
    photo = 'photo'
    video = 'video'
    album = 'album'


class Attachment(BaseModel):
    media_type: MediaType
    thumbnail: Optional[str] = ""


class Post(BaseModel):
    post_id: str
    page_id: str
    message: Optional[str] = ""
    attachment: Optional[Attachment] = None


class TextSearchQuery(BaseModel):
    text: str
    topk: Optional[int] = -1
    threshold: Optional[float] = 0.0
    page_ids: Optional[List[str]] = []


class PostSearchQuery(BaseModel):
    post: Post
    topk: Optional[int] = -1
    threshold: Optional[float] = 0.0
    page_ids: Optional[List[str]] = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/search-text")
async def search_text(search_query: TextSearchQuery):
    posts = database.get_post_messages(search_query.page_ids)
    ranks = []
    query_message = search_query.text

    for post in posts:
        message = post.message
        occurrences = find_in_doc(doc=message, query=query_message, threshold=search_query.threshold)

        if occurrences:
            max_similarity = max([occ['similarity'] for occ in occurrences])
            ranks.append({
                            'similarity': max_similarity,
                            'occurrences': occurrences,
                            'post_id': post.post_id, 
                            'page_id': post.page_id
                        })

    topk = search_query.topk
    if topk == -1:
        topk = len(ranks)
    else:
        topk = min(topk, len(ranks))

    result = heapq.nlargest(topk, ranks, key=lambda x: x['similarity'])
    print(result)

    return result


@app.post("/encode-posts", status_code=status.HTTP_201_CREATED)
async def encode_posts(posts: Union[List[Post], Post]):
    asyncio.create_task(encode_posts_helper(posts=posts))
    return "Success"

async def encode_posts_helper(posts: Union[List[Post], Post]):
    if type(posts) == Post:
        posts = [posts]

    dbposts = []

    print("Encoding posts")
    for post in tqdm.tqdm(posts):
        try:
            dbpost = DBPost(page_id=post.page_id, post_id=post.post_id)

            if post.message:
                dbpost.message = post.message
                encoding = txt_similarity_tr.encode(post.message)
                dbpost.message_encoding = encoding

            if post.attachment:
                img = download_image(post.attachment.thumbnail)
                encoding = img_similarity.encode(img)
                dbpost.image_encoding = encoding

            dbposts.append(dbpost)
        except Exception as err:
            print(err)
    
    print("Inserting posts in database")
    database.put_posts(posts=dbposts)


@app.post("/search-post")
async def search_post(search_query: PostSearchQuery):
    query_msg_enc, query_img_enc = get_encodings(search_query.post)
    posts= database.get_posts(search_query.page_ids)
    ranks = []

    # rank posts
    for post in posts:
        msg_sim = 0
        img_sim = 0

        if post.message_encoding and query_msg_enc:
            msg_sim = txt_similarity_tr.similarity(post.message_encoding, query_msg_enc)
        if post.image_encoding and query_img_enc:
            img_sim = img_similarity.similarity(post.image_encoding, query_img_enc)

        # score = max(msg_sim, img_sim)
        # score = img_sim
        score = MESSAGE_WEIGHT * msg_sim + IMAGE_WEIGHT * img_sim

        ranks.append({
                        'similarity': score,
                        'message_similarity': msg_sim,
                        'image_similarity': img_sim,
                        'message': post.message,
                        'post_id': post.post_id,
                        'page_id': post.page_id,
                    })

    # filter posts with similarity threshold
    ranks = [x for x in ranks if x['similarity'] > 0.65] # search_query.threshold]

    # pick topk posts
    topk = search_query.topk
    if topk == -1:
        topk = len(ranks)
    else:
        topk = min(topk, len(ranks))

    result = heapq.nlargest(topk, ranks, key=lambda x: x['similarity'])

    return result


def get_encodings(post: Post)-> Tuple[bytes,bytes]:

    dbpost_it = database.get_post_encodings(post_id=post.post_id)
    try: 
        dbpost = next(dbpost_it)
        return dbpost.message_encoding, dbpost.image_encoding
    except StopIteration: 
        raise HTTPException(status_code=404, detail=f"Could not find post: '{post.post_id}'")


def download_image(url: str) -> Image:
    resp = requests.get(url, stream=True)
    if not resp.ok:
        raise HTTPException(
            status_code=424, 
            detail=f"Could not download image from: {url}")

    return Image.open(resp.raw)

'''
    Given document and query phrase, return all 
    parts of document with more similarity than threshold
'''
def find_in_doc(doc: str, query: str, threshold: float = 0.7) -> List[Dict]:
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
        similarity = txt_similarity_lev.similarity(doc[cur_start:cur_end], query)
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


