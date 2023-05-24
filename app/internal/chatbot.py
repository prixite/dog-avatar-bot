import os
import pickle

from langchain.document_loaders import PDFMinerLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


def load_docs():
    # Define the pickle file path
    pickle_file = "./app/internal/hexpulsedata_pickle.pkl"

    # Check if the pickle file exists
    if os.path.isfile(pickle_file):
        # Load data from the pickle file
        with open(pickle_file, "rb") as f:
            faiss_index = pickle.load(f)
    else:
        # If pickle file doesn't exist, process the documents and save to a new pickle file # noqa
        loader = PDFMinerLoader("./app/internal/hexpulsedata.pdf")
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1400, chunk_overlap=400
        )
        texts = text_splitter.split_documents(data)
        faiss_index = FAISS.from_documents(texts, OpenAIEmbeddings())
        # Save the faiss index to a pickle file
        with open(pickle_file, "wb") as f:
            pickle.dump(faiss_index, f)

    return faiss_index


class Chatbot:
    def __init__(self):
        self.faiss_index = load_docs()
