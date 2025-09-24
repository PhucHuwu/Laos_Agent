import os
from dotenv import load_dotenv
from groq import Groq
import faiss
import pickle
from chunking import chungking
from embedding import embedding

load_dotenv()
api = os.getenv("GROQ_API_KEY")

