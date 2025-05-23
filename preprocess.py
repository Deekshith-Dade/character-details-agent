import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()  # take environment variables

from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage

from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from models_init import llm, embedder, pc
import json


splitter = RecursiveCharacterTextSplitter(
    chunk_size = 2000,
    chunk_overlap=200,
)

from prompts import summary_prompt, character_prompt


def extract_clean_chapters(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for idx, item in enumerate(book.get_items()):
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, 'html.parser')
            text = soup.get_text()
            
            text = text.replace("The Project Gutenberg eBook of The Brothers Karamazov by Fyodor Dostoyevsky\n\n\n\n\n\n\n", "")
            
            if len(text.strip()) > 200:
                chapters.append({
                    "id": f"chapter_{idx}",
                    "text": text.strip()
                })
    return chapters

def summarize_long_chapter(text):
    summary_system_prompt = summary_prompt.format(text=text)
    summary = llm.invoke([SystemMessage(content=summary_system_prompt)])
    
    return summary.content

def chunk_chapter(chapter_id, chapter_text):
    chunks = splitter.split_text(chapter_text)
    chunk_objects = []
    
    for i, chunk in enumerate(chunks):
        chunk_objects.append({
            "id": f"{chapter_id}_chunk_{i}",
            "text": chunk,
            "chapter_id": chapter_id,
            "chunk_index": i,
        })
    
    return chunk_objects

class Character(BaseModel):
    name: str = Field(
        description = "Name of the character in the book"
    )
    role: str = Field(
        description = "A single or two word description of the characters role in the book"
    )

class Characters(BaseModel):
    characters: list[Character]
    

def preprocess(epub_path):
    
    
    book_title = epub_path.split("/")[-1].split(".")[0].lower()
    book_title = book_title.replace(" ", "-")
    book_title = ''.join(c for c in book_title if c.isalnum() or c == '-')
    
    output_path = f"books/{book_title}"
    os.makedirs(output_path, exist_ok=True)
    if os.path.exists(f"{output_path}/chapter_details.json"):
        print(f"Chapter details already exist for {book_title}")
        return f"{book_title}", f"{output_path}"
    
    # Extract all the chapters
    chapters = extract_clean_chapters(epub_path)
    print(f"Total chapters extracted: {len(chapters)}")
    
    # Initialize Pinecone index
    index_name = f"{book_title}"
    print(f"Index name: {index_name}")
    
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings dimension
            metric="cosine",
            spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
            ),
            deletion_protection="disabled",
        )
        
    index = pc.Index(index_name)
    
    # Summarization for each chapter
    if not os.path.exists(f"{output_path}/chapter_summaries.json"):
        for chapter in tqdm(chapters, desc="Summarizing chapters"):
            try:
                joined_summary = summarize_long_chapter(chapter["text"])
                chapter["summary"] = joined_summary
            except Exception as e:
                chapter["summary"] = ""
                print(f"Error summarizing {chapter['id']}: {e}")
        with open(f"{output_path}/chapter_summaries.json", "w") as f:
            json.dump(chapters, f, indent=2)
    else:
        with open(f"{output_path}/chapter_summaries.json", "r") as f:
            chapters = json.load(f)
            
    
    
    
    # Embeddings to pincone
    all_chunks = []

    for chapter in tqdm(chapters, desc="Chunking chapters"):
        chapter_id = chapter["id"]
        chapter_text = chapter["text"]
        
        chapter_chunks = chunk_chapter(chapter_id, chapter_text)
        all_chunks.extend(chapter_chunks)

    print(f"Total chunks to embed and upload: {len(all_chunks)}")
    
    chunk_vectors = []

    for chunk in tqdm(all_chunks, desc="Embedding chunks"):
        embedding = embedder.embed_query(chunk['text'])
        
        metadata = {
            "text": chunk['text'],
            "chapter_id": chunk['chapter_id'],
            "chunk_index": chunk['chunk_index']
        }
        
        vector = (chunk['id'], embedding, metadata)
        chunk_vectors.append(vector)
        
    batch_size = 100
    for i in range(0, len(chunk_vectors), batch_size):
        batch = chunk_vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size + 1} of {(len(chunk_vectors) + batch_size - 1)//batch_size}")

    print("Successfully uploaded all chunks to Pinecone!")
    
    
    
    with open(f"{output_path}/chapter_details.json", "w") as f:
        json.dump(chapters, f, indent=2)
    
    return index_name, f"{output_path}"


if __name__ == "__main__":
    epub_path = "/Users/deekshith/Documents/Projects/agents/character-details/books/files/charles-darwin_the-origin-of-species.epub"
    index_name = preprocess(epub_path)
    print(f"Index name: {index_name}")
    
    
    
    
    
    
    