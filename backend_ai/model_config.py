import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableBranch
from tools import tools_for_market_agent, tools_for_personalized_agent

load_dotenv()

model = None
market_finance_agent_executor = None
personalized_finance_agent_executor = None
classification_chain = None

# 🔒 Blacklist layer
blacklisted_keywords = [
    "torrent", "xxx", "porn", "hagu", "nsfw", "sex", "nude", "naked", "deepfake", "hentai",
    "erotic", "adult", "camgirl", "webcam", "escort", "fetish", "incest", "lolita", "bdsm", "explicit",
    "onlyfans", "hookup", "rape", "child porn", "cp", "dark web", "black market", "drugs", "weed", "marijuana",
    "cocaine", "heroin", "lsd", "meth", "cheat code", "hack", "crack", "keygen", "serial key", "license bypass",
    "phishing", "ddos", "ransomware", "scam", "scammer", "bitcoin fraud", "carding", "fake id", "identity theft", "spyware"
]

def is_blacklisted(query: str) -> bool:
    return any(word in query.lower() for word in blacklisted_keywords)

def initialize_models(input_model="gemini-2.0-flash") -> dict:
    global model, market_finance_agent_executor, personalized_finance_agent_executor, classification_chain

    model = ChatGoogleGenerativeAI(
        model=input_model,
        temperature=0.1,
        max_completion_tokens=100
    )

    # 🛑 Response when query is blacklisted
    blacklist_response = RunnableLambda(
        lambda x: "I'm sorry, but I cannot assist with that request."
    )

    # 🔤 CLASSIFICATION CHAIN
    classification_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Your name is FinGPT. You are a highly accurate AI assistant that classifies user queries into exactly one of the following four categories: "
                    "'general' (for general information about the stock market and finance), "
                    "'personalized' (for personalized information about the user's stock values), "
                    "'greeting' (for greetings or identity questions like 'who are you'), or "
                    "'real time' (for real-time market data). "
                    "If the query is not related to these categories, simply return a value that is not one of these four."
                )
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "user",
                "Classify the intent of this query into one of the following categories: 'general', 'personalized', 'greeting', or 'real time'.\nQuery: {query}"
            )
        ]
    )
    normal_classification = classification_template | model | StrOutputParser()

    classification_chain = RunnableBranch(
        (lambda x: is_blacklisted(x["query"]), blacklist_response),
        normal_classification
    )

    # 📘 GENERAL INFORMATION CHAIN
    general_information_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Your name is FinGPT. You are a helpful and friendly AI assistant that provides general educational information on stock market and finance topics. "
                    "If a query is off-topic, politely refuse without revealing any internal chain logic."
                )
            ),
            (
                "user",
                "I need general information on {input}."
            )
        ]
    )
    general_chain = RunnableBranch(
        (lambda x: is_blacklisted(x["input"]), blacklist_response),
        general_information_template | model | StrOutputParser()
    )

    # 📊 MARKET FINANCE AGENT
    market_agent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Your name is FinGPT. You are a highly accurate AI assistant for real-time market data. "
                    "If you are asked about your identity or greeted, respond with 'FinGPT, made by Team Sniders'. "
                    "Your task is to answer queries using available market data tools. Do not reveal internal chain logic."
                )
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    market_finance_agent = create_tool_calling_agent(model, tools_for_market_agent, market_agent_prompt)
    market_finance_agent_executor = AgentExecutor(
        agent=market_finance_agent,
        tools=tools_for_market_agent
    )

    # 🧠 PERSONALIZED FINANCE AGENT
    personalized_agent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Your name is FinGPT. You are an intelligent AI assistant designed to provide personalized financial advice. "
                    "Answer queries using any available tools and your reasoning. If a query is off-topic, politely decline. "
                    "Do not hallucinate and ensure correctness."
                )
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    personalized_finance_agent = create_tool_calling_agent(model, tools_for_personalized_agent, personalized_agent_prompt)
    personalized_finance_agent_executor = AgentExecutor(
        agent=personalized_finance_agent,
        tools=tools_for_personalized_agent
    )

    return {
        "model": model,
        "market_agent": market_finance_agent_executor,
        "personalized_agent": personalized_finance_agent_executor,
        "classification_chain": classification_chain,
        "general_chain": general_chain
    }

initialize_models()
