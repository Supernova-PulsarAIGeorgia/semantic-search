from typing import Dict, List, Tuple
from typing import Protocol, runtime_checkable

import Levenshtein as lev

from PIL import Image
from torchvision import transforms, models
import torch

from sentence_transformers import SentenceTransformer, util
import pickle


@runtime_checkable
class Comparator(Protocol):
    def __init__(self) :
        pass

    def encode(self):
        pass

    def similarity(self):
        pass

'''Compares texts using pre-trained language model.'''
class TextComparatorLM:

    def __init__(self):
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def encode(self, text: str) -> bytes:
        encoding = self.encoder.encode(text, convert_to_tensor=True)
        encoding = pickle.dumps(encoding)
        return encoding

    def similarity(self, encoding1: bytes, encoding2: bytes) -> float:
        encoding1 = pickle.loads(encoding1)
        encoding2 = pickle.loads(encoding2)

        similarity = util.pytorch_cos_sim(encoding1, encoding2)
        similarity = similarity.item()

        return similarity


class ImageComparator:

    def __init__(self):
        # self.device = torch.device("cpu")
        self.numberFeatures = 512
        self.max_channel = 3
        # self.modelName = "resnet-18"
        self.model = models.resnet18(weights='ResNet18_Weights.DEFAULT')
        self.featureLayer = self.model._modules.get('avgpool')
        # self.model = self.model.to(self.device
        self.model.eval()
        self.toTensor = transforms.ToTensor()
        self.normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        self.transformationForInput = transforms.Compose([transforms.Resize((224,224))])
        self.similarity_function = torch.nn.CosineSimilarity(dim = 0)

    def encode(self, image: Image) -> bytes:
        image = self.transformationForInput(image)
        image_ts = self.toTensor(image)
        if image_ts.size()[0] > self.max_channel:
            image_ts = image_ts[:self.max_channel, :, :]
        image_ts_norm = self.normalize(image_ts)
        image = image_ts_norm.unsqueeze(0)#.to(self.device)

        embedding = torch.zeros(1, self.numberFeatures, 1, 1)
        def copyData(m, i, o): embedding.copy_(o.data)
        handle = self.featureLayer.register_forward_hook(copyData)
        self.model(image)
        handle.remove()

        encoding = embedding[0, :, 0, 0]
        encoding = pickle.dumps(encoding)
        return encoding

    def similarity(self, encoding1: bytes, encoding2: bytes) -> float:
        encoding1 = pickle.loads(encoding1)
        encoding2 = pickle.loads(encoding2)

        similarity = util.pytorch_cos_sim(encoding1, encoding2)
        similarity = similarity.item()
        return similarity

'''Compares texts using Levenstein Distance.'''
class TextComparatorLD:

    def __init__(self):
        pass

    def encode(self):
        pass

    def distance(self, str1: str, str2: str) -> int:
        if not str1: return float('inf')
        if not str2: return float('inf')

        return lev.distance(str1, str2)
  
    '''
        Find similarity of two short phrases
        Return float from 0 to 1
    '''
    def similarity(self, str1: str, str2: str) -> float:
        if not str1: return 0
        if not str2: return 0
        
        max_len = max(len(str1), len(str2))
        distance_norm = lev.distance(str1, str2) / max_len
        similarity = 1 - distance_norm

        return similarity


# if __name__ == "__main__":
#     doc = ''
#     query = ''
#     finder = KeywordFinder()
#     print(finder.find_in_doc(doc=doc, query=query, threshold=0.7))
