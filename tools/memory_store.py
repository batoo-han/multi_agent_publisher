import logging
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Векторная память публикаций с использованием Chroma и OpenAIEmbeddings.
    Позволяет сохранять новые публикации и извлекать похожие примеры.
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        openai_api_key: str
    ):
        """
        :param persist_directory: путь к директории хранения Chroma данных
        :param collection_name: имя коллекции в Chroma
        :param openai_api_key: API-ключ OpenAI для эмбеддингов
        """
        try:
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=persist_directory,
                collection_name=collection_name,
            )
            logger.info(
                "Initialized MemoryStore: collection=%s, persist_dir=%s",
                collection_name,
                persist_directory,
            )
        except Exception as e:
            logger.error("Failed to initialize MemoryStore: %s", e)
            raise

    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Добавляет текстовый документ в векторное хранилище.

        :param text: содержание публикации (например, заголовок + тело)
        :param metadata: дополнительные данные (дата, id идеи и т.д.)
        """
        try:
            doc = Document(page_content=text, metadata=metadata or {})
            self.vectorstore.add_documents(documents=[doc])
            self.vectorstore.persist()
            logger.info("Added document to memory: metadata=%s", metadata)
        except Exception as e:
            logger.error("Error adding document to memory: %s", e)
            raise

    def get_similar(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Извлекает k наиболее похожих документов по текстовому запросу.

        :param query: текстовый запрос для поиска
        :param k: количество результатов
        :return: список словарей с ключами 'text', 'metadata', 'score'
        """
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            formatted: List[Dict[str, Any]] = []
            for doc, score in results:
                formatted.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score,
                })
            logger.info("Retrieved %d similar documents for query", len(formatted))
            return formatted
        except Exception as e:
            logger.error("Error retrieving similar documents: %s", e)
            raise