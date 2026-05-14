from dataclasses import dataclass


ES_MAPPING = {
    'id': {'type': 'text'},
    'text': {'type': 'text'},
    'metadata': {
        'type': 'nested',
        'properties': {
            'file_name': {'type': 'text'},
            'chunk_number': {'type': 'integer'},
            'char_start': {'type': 'integer'},
            'char_end': {'type': 'integer'},
        }
    }
}


@dataclass
class MetaData:
    """Метаданные документа."""

    file_name: str
    chunk_number: str
    char_start: int
    char_end: int

    def to_dict(self) -> dict:
        """Возвращает документ в виде словаря."""
        return {
            'file_name': self.file_name,
            'chunk_number': self.chunk_number,
            'char_start': self.char_start,
            'char_end': self.char_end
        }


class Chunk:
    """Чанк."""

    doc_id: str
    text: str
    metadata: MetaData

    def __init__(self, doc_id: str, text: str, metadata: MetaData):
        """Инициализирует экземпляр документа."""
        self.doc_id = doc_id
        self.text = text
        self.metadata = metadata

    def to_dict(self) -> dict:
        """Возвращает документ в виде словаря."""
        return {
            'id': self.doc_id,
            'text': self.text,
            'metadata': {
                'file_name': self.metadata.file_name,
                'chunk_number': self.metadata.chunk_number,
                'char_start': self.metadata.char_start,
                'char_end': self.metadata.char_end
            }
        }


class VectorizedChunk(Chunk):
    """Результат поисковой выдачи."""

    distance: float
    embedding: list[float]

    def __init__(
            self,
            chunk: Chunk,
            distance: float = None,
            embedding: list = None
    ):
        """Инициализирует объект чанк с эбмеддингом."""
        for key, value in chunk.__dict__.items():
            self.__setattr__(key, value)
        self.distance = distance
        self.embedding = embedding
