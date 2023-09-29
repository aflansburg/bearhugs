from pathlib import Path
from typing import Dict, List, Union

from langchain.document_loaders import JSONLoader
from langchain.llms.openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings


def load_json(file_path: str) -> Dict:
    """Load a JSON file using the specified schema."""
    if not Path(file_path).exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    loader = JSONLoader(
        file_path=file_path,
        jq_schema='.[].text',
        text_content=False
    )
    return loader.load()


def split_notes(loaded_json: Dict) -> List[str]:
    """Split notes from loaded JSON based on the defined criteria."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
        is_separator_regex=False
    )
    return splitter.split_documents(loaded_json)


def generate_embeddings(notes: List[str], open_ai_api_key: str, persist_dir: str) -> Chroma:
    """Generate embeddings using Chroma and OpenAI."""
    chroma_vectordb = Chroma.from_documents(
        documents=notes,
        embedding=OpenAIEmbeddings(openai_api_key=open_ai_api_key),
        persist_directory=persist_dir
    )
    chroma_vectordb.persist()
    return chroma_vectordb


def create_chain_executor(vector_db: Chroma, open_ai_api_key: str, query: str) -> Dict:
    """Create and execute a chain using the provided vector DB."""
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(
            temperature=0,
            openai_api_key=open_ai_api_key
        ),
        retriever=vector_db.as_retriever(search_kwargs={'k': 5}),
        return_source_documents=True
    )
    return qa_chain({'query': query})


def load_and_execute_json_chain(file_path: str, open_ai_api_key: str, query: str, persist_dir='data/chroma') -> Union[str, None]:
    """Main function to load and execute a JSON chain."""
    loaded_json = load_json(file_path)
    notes = split_notes(loaded_json)
    vector_db = generate_embeddings(notes, open_ai_api_key, persist_dir)
    chain_response = create_chain_executor(vector_db, open_ai_api_key, query)

    return chain_response.get('result')
