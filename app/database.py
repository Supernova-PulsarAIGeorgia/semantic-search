from dataclasses import dataclass
from typing import Dict, List, Iterable, Optional, Union

from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.errors import BulkWriteError

from bson.binary import Binary


@dataclass
class Post:
    post_id: str
    page_id: str
    message: Optional[str] = ""
    message_encoding: Optional[bytes] = bytes()
    image_encoding: Optional[bytes] = bytes()

class PostIterator:

    def __init__(self, cursor: Cursor):
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        cur_post = next(self.cursor)

        post = Post(post_id=cur_post['postId'], page_id=cur_post['pageId'])
        if 'message' in cur_post : post.message = cur_post['message'] 
        if 'messageEncoding' in cur_post : post.message_encoding = cur_post['messageEncoding'] 
        if 'imageEncoding' in cur_post : post.image_encoding = cur_post['imageEncoding'] 

        return post

class MongoDB:

    def __init__(self, connection_string) -> None:
        client = MongoClient(connection_string)
        self.encodings = client['cib-parse']['encodings']

    def get_posts(self, 
                    page_id: Union[str, List[str]] = None,  
                    post_id: Union[str, List[str]] = None) -> Iterable[Post]:

        filter = self._get_filter(page_id=page_id, post_id=post_id)
        projection = ['pageId', 'postId', 'message', 'messageEncoding', 'imageEncoding']

        cursor = self.encodings.find(filter=filter, projection=projection)
        return PostIterator(cursor=cursor)
    
    def get_post_encodings(self, 
                            page_id: Union[str, List[str]] = None,  
                            post_id: Union[str, List[str]] = None) -> Iterable[Post]:

        filter = self._get_filter(page_id=page_id, post_id=post_id)
        projection = ['pageId', 'postId', 'messageEncoding', 'imageEncoding']

        cursor = self.encodings.find(filter=filter, projection=projection)
        return PostIterator(cursor=cursor)

    def get_post_messages(self, 
                            page_id: Union[str, List[str]] = None,  
                            post_id: Union[str, List[str]] = None) -> Iterable[Post]:
                            
        filter = self._get_filter(page_id=page_id, post_id=post_id)
        projection = ['pageId', 'postId', 'message']

        cursor = self.encodings.find(filter=filter, projection=projection)
        return PostIterator(cursor=cursor)

    def put_posts(self, posts: List[Post]) -> None:
        post_dicts = []
        for post in posts:
            post = {
                    "postId": post.post_id,
                    "pageId": post.page_id,
                    "message" : post.message, 
                    "messageEncoding" : Binary(post.message_encoding),
                    "imageEncoding" : Binary(post.image_encoding),
                    }
            post_dicts.append(post)
        
        try:
            self.encodings.insert_many(post_dicts, ordered=False)
        except BulkWriteError:
            pass

    def _get_filter(self, 
                    page_id: Union[str, List[str]] = None,  
                    post_id: Union[str, List[str]] = None) -> Dict:

        if type(post_id) == str:
            post_id = [post_id]
        if type(page_id) == str:
            page_id = [page_id]

        filter = {}
        if post_id: filter['postId'] = { '$in' : post_id}
        if page_id: filter['pageId'] =  { '$in' : page_id}

        return filter