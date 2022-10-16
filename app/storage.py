from base64 import encode
from typing import Protocol, runtime_checkable, Optional
from dataclasses import dataclass
from PIL import Image
import json
import copy
import os
import torch


@runtime_checkable
class Storage(Protocol):

    def __init__(self):
        pass

    def append(self):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


@dataclass
class StorageImage:
    image: Image
    encoding: torch.Tensor
    id: Optional[int] = None


class ImageStorage():

    def __init__(self, src: str):
        self.src = src
        self.n = 0
        self.images = {}
        self._load_images()

    def _load_images(self):
        self.n = len(os.listdir(self.src))//2
        for id in range(self.n):
            image = Image.open(os.path.join(self.src, str(id) + '.jpg'))
            encoding = torch.load(os.path.join(self.src, str(id) + '.pt'))
            self.images[id] = StorageImage(id=id, image=image, encoding=encoding)

    def append(self, image: StorageImage) -> int:
        image.id = self.n
        self.n += 1
        self.images[image.id] = copy.deepcopy(image)
        # image.image.save(os.path.join(self.src, str(image.id) + 'jpg'))
        # torch.save(image.encoding, os.path.join(self.src, str(image.id) + '.pt'))
        return image.id

    def get(self, id: int) -> StorageImage:
        if id in self.images:
            return self.images[id]

    def __iter__(self):
        return ImageStorageIterator(self)

    def __len__(self):
        len(self.images)


class ImageStorageIterator:

   def __init__(self, image_storage: ImageStorage):
        self._image_storage = image_storage
        self._index = 0

   def __next__(self):
       if self._index < len(self._image_storage.images):
            result = self._image_storage.images[self._index]
            self._index +=1
            return result
       raise StopIteration


class TextStorage():

    def __init__(self, src: str):
        self.texts = json.load(open(src))

    def append(self, text: str):
        self.texts.append(text)
        # persist texts here

    def __iter__(self):
        return TextStorageIterator(self)

    def __len__(self):
        return len(self.texts)


class TextStorageIterator:

   def __init__(self, text_storage: TextStorage):
        self._text_storage = text_storage
        self._index = 0

   def __next__(self):
       if self._index < len(self._text_storage.texts):
            result = self._text_storage.texts[self._index]
            self._index +=1
            return result
       raise StopIteration