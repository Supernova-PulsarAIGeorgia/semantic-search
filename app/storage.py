from typing import Protocol, runtime_checkable
from dataclasses import dataclass
import json


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


class ImageStorage():
    def __init__(self, src: str):
        pass

    def append(self):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


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
       if self._index < len(self._text_storage.texts) :
            result = self._text_storage.texts[self._index]
            self._index +=1
            return result
       raise StopIteration