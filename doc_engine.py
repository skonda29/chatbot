# import os
# os.environ["TRANSFORMERS_NO_TF"] = "1"
# from llama_index.core.settings import Settings
# Settings.llm = None

# import os
# from dotenv import load_dotenv
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
# from llama_index.core import StorageContext, load_index_from_storage
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# import google.generativeai as genai  

import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import google.generativeai as genai
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

PERSIST_DIR = "./index_store"

if os.path.exists(PERSIST_DIR):
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)  # <- Fix here!
else:
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    index.storage_context.persist(persist_dir=PERSIST_DIR)

query_engine = index.as_query_engine(llm=None)


def query_documents(user_query: str) -> str:
    context = query_engine.query(user_query)
    prompt = (
        "You are a supportive and understanding mental health assistant. "
        "Provide a warm, empathetic, and practical response to help the user with their concern. "
        "Here is some background information that might help you answer:\n\n"
        f"{context}\n\n"
        f"User's concern: {user_query}\n\n"
        "Respond as if you're offering thoughtful advice to a friend."
    )

    response = gemini_model.generate_content(prompt)
    return response.text
