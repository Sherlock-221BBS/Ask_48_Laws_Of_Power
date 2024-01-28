import streamlit as st 
import openai 

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.chains import ConversationalRetrievalChain 
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

openai.api_key = st.secrets["OPENAI_API_KEY"]


st.set_page_config(page_title = "RAG System")
st.title("Ask 48 Laws of Power")

def load_db(file, chain_type, k):
  loader = PyPDFLoader(file)
  pages = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 150)
  docs = text_splitter.split_documents(pages)

  embedding = OpenAIEmbeddings()
  vectordb = DocArrayInMemorySearch.from_documents(docs, embedding)
  llm = ChatOpenAI(model_name = 'gpt-3.5-turbo', temperature = 0)
  qa = ConversationalRetrievalChain.from_llm(
      llm, 
      vectordb.as_retriever(search_type = 'similarity',  
                            search_kwargs = {"k": k}), 
      return_source_documents = True, 
      return_generated_question= True
  )

  return qa


def query_llm(qa, query):
  
  result = qa({"question": query, "chat_history" : st.session_state.messages})
  result = result["answer"]
  st.session_state.messages.extend([(query, result)])
  return result

def initialize():
  if "messages" not in st.session_state:
    st.session_state.messages = []

  file_path = "./48lawsofpower.pdf"
  qa = load_db(file_path, "stuff", k = 5)
  return qa 

def conv_chain():
  qa = initialize()

  for message in st.session_state.messages:
    st.chat_message("human").write(message[0])
    st.chat_message("ai").write(message[1])

  if query:= st.chat_input():
    st.chat_message("human").write(query)
    response = query_llm(qa, query)
    st.chat_message("ai").write(response)

if __name__ == '__main__':
  conv_chain()

  