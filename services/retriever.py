from langchain.retrievers import ParentDocumentRetriever
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import LocalFileStore, RedisStore, InMemoryStore
from langchain.storage._lc_store import create_kv_docstore

from langchain.document_transformers import (
    LongContextReorder,
)
from langchain.embeddings import OpenAIEmbeddings
import services.const as const

import dotenv
dotenv.load_dotenv()


class ParentDocRetriever(object):
    def __init__(self, embedding, collection_name, parent_chunk_size=2000, child_chunk_size=400):
        self.embedding = embedding

        self.parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size)
        # This text splitter is used to create the child documents
        # It should create documents smaller than the parent
        self.child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size)
        # The vectorstore to use to index the child chunks
        self.vectorstore = Chroma(collection_name=collection_name, embedding_function=self.embedding,
                                  persist_directory='vector_db')
        # The storage layer for the parent documents
        # self.store = InMemoryStore()
        # self.store = LocalFileStore(root_path='local_fs')
        fs = LocalFileStore(root_path='local_fs')
        self.store = create_kv_docstore(fs)

        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            child_splitter=self.child_splitter,
            parent_splitter=self.parent_splitter,
        )

    def add_documents(self, docs):
        self.retriever.add_documents(docs, ids=None)

    def search_vectors(self, query, top_k=2):
        return self.retriever.vectorstore.similarity_search(query, top_k)

    def get_relevant_documents(self, query, top_k=10):
        return self.retriever.get_relevant_documents(query, search_kwargs={"k": top_k})

    def get_relevant_documents_ordered(self, query, top_k=10):
        docs = self.get_relevant_documents(query, top_k)
        reordered_docs = LongContextReorder().transform_documents(docs)
        return reordered_docs


def get_retriever(collection_name=const.DEFAULT_VECTOR_COLLECTION):
    return ParentDocRetriever(
        OpenAIEmbeddings(model=const.OPENAI_EMBEDDING_MODEL),
        collection_name
    )
