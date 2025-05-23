from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone
import os

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
embedder = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)