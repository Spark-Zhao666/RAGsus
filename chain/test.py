from chat_QA_chain_self import Chat_QA_chain_self
from QA_chain_self import QA_chain_self

import os
from dotenv import load_dotenv
load_dotenv()

model: str = "deepseek-chat"
temperature: float = 0.0
top_k: int = 4
chat_history: list = []
file_path: str = "/Users/zhaozhangmen/Desktop/ATX/chat_with_RAG_langchain-main/knowledge_db"
persist_path: str = "/Users/zhaozhangmen/Desktop/ATX/chat_with_RAG_langchain-main/vector_db"
appid: str = None
api_key: str = os.getenv("DeepSeek_API_for_RAG")
api_secret:str=None
embedding = "openai-embedding"
embedding_key = os.getenv("EMBEDDING_KEY")

qa_chain = QA_chain_self(model=model,
                              temperature=temperature,
                              top_k=top_k,
                              file_path=file_path,
                              persist_path=persist_path,
                              api_key=api_key,
                              embedding=embedding,
                              embedding_key=embedding_key)

question = "Hello, how are you?"
answer = qa_chain.answer(question)