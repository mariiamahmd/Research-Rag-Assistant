import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MISTRAL_API_KEY = st.secrets.get(
    "MISTRAL_API_KEY",
    os.getenv("MISTRAL_API_KEY")
)

client = OpenAI(
    api_key=MISTRAL_API_KEY,
    base_url="https://api.mistral.ai/v1"
)


MODEL = "mistral-small-latest"


def answer(question, documents):
    context = "\n\n".join(
        doc["text"] for doc in documents
    )

    prompt = f"""
You are an AI research assistant.

Answer ONLY using the provided context.

If the answer cannot be found in the context, say:
"I couldn't find the answer in the uploaded papers."

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content