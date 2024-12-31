import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Cassandra
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from typing import Literal, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph import END, StateGraph, START
from src.prompt import system_message
import cassio  
from langchain_core.messages import AIMessage, HumanMessage 

from dotenv import load_dotenv
import os 

# Load environment variables
load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
ASTRA_DB_ID = os.getenv('ASTRA_DB_ID')
api_key = os.getenv('google_api_key')
os.environ["GOOGLE_API_KEY"] = api_key

# Initialize Cassio
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Initialize vector store
astra_vector_store = Cassandra(embedding=embeddings, table_name="qa_mini_demo", session=None, keyspace=None)

# Define retriever
retriever = astra_vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.5})

# Define routing query model
class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "duckduckgo-search"] = Field(..., description="Given a user question, choose to route it to duckduckgo-search or a vectorstore.", type="string")
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', google_api_key=os.getenv('GOOGLE_API_KEY'), temperature=0.1, max_output_tokens=30, convert_system_message_to_human=True)
structured_llm_router = llm.with_structured_output(RouteQuery)

route_prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", "{question}")])
question_router = route_prompt | structured_llm_router

# Initialize DuckDuckGo search
search = DuckDuckGoSearchRun()

# Define GraphState class
class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]

# Define retrieve function
def retrieve(state):
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

# Define DuckDuckGo search function
def DuckDuckGo_search(state):
    question = state["question"]
    docs = search.invoke({"query": question})
    DuckDuckGo_results = Document(page_content=docs)
    return {"documents": DuckDuckGo_results, "question": question}

# Define route_question function
def route_question(state):
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "duckduckgo-search":
        return "duckduckgo-search"
    elif source.datasource == "vectorstore":
        return "retrieve"

# Define workflow
workflow = StateGraph(GraphState)
workflow.add_node("duckduckgo-search", DuckDuckGo_search)
workflow.add_node("retrieve", retrieve)
workflow.add_conditional_edges(START, route_question, {"duckduckgo-search": "duckduckgo-search", "retrieve": "retrieve"})
workflow.add_edge("retrieve", END)
workflow.add_edge("duckduckgo-search", END)
app = workflow.compile()

# Function to run the app
def run_app(question):
    result = app.invoke({"question": question})
    return result

# Streamlit app layout
st.set_page_config(page_title="Thai Recipes AI Assistant", page_icon=":shallow_pan_of_food:", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    .stTextInput>div>div>input {
        border: 2px solid #4CAF50;
        border-radius: 12px;
    }
    .stMarkdown {
        font-size: 18px;
    }
    .chat-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .chat-message {
        margin-bottom: 10px;
    }
    .chat-message-human {
        text-align: right;
        color: #4CAF50;
    }
    .chat-message-ai {
        text-align: left;
        color: #000000;
    }
    .chat-message-content {
        font-size: 16px;
        line-height: 1.5;
    }
    .error-message {
        color: red;
        font-size: 16px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Thai Recipes Assistant :shallow_pan_of_food:")
st.write("Ask any question related to Thai recipes, ingredients, cooking techniques, or cultural food traditions.")

# Input field for user question
question = st.text_input("Enter Your Query", key="user_query", placeholder="Type your question here...")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Button to submit the question
if st.button("Submit"):
    try:
        st.session_state.chat_history.append(HumanMessage(content=question))  # Save user query

        response = run_app(question)  # Get AI response
        response_content = "\n".join([doc.page_content for doc in response["documents"]])
        st.markdown(f"<div class='chat-container chat-message chat-message-ai'><strong>AI:</strong> <span class='chat-message-content'>{response_content}</span></div>", unsafe_allow_html=True)
        
        st.session_state.chat_history.append(AIMessage(content=response_content))  # Save AI's response to chat history
    except Exception as e:
        st.markdown(f"<div class='error-message'>Error: {str(e)}</div>", unsafe_allow_html=True)
