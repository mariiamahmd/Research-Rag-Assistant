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

# join all returned chunks 
def answer(question, documents):
    context = "\n\n".join(
        doc["text"] for doc in documents
    )

    prompt = f"""
You are an AI research assistant.

Use ONLY the provided context.

If multiple papers contain relevant information,
combine them into a single coherent answer.

If the answer is absent from the context,
reply exactly:

"I couldn't find the answer in the uploaded papers."

Do not use outside knowledge.
Be concise and cite information only from the provided context.

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
        temperature=0.2
    )

    return response.choices[0].message.content



def compare_answers(question, docs1, docs2):

    context1 = "\n\n".join(
        doc["text"] for doc in docs1
    )

    context2 = "\n\n".join(
        doc["text"] for doc in docs2
    )

    score1 = max(doc["rerank_score"] for doc in docs1)
    score2 = max(doc["rerank_score"] for doc in docs2)

    prompt = f"""
You are an AI research assistant.

Compare the two papers using ONLY the supplied contexts.

Structure your answer like this:

Paper 1
- Summary
- Answer to the question

Paper 2
- Summary
- Answer to the question

Comparison
- Main similarities
- Main differences
- Final conclusion

Paper 1 Relevance Score:
{score1:.3f}

Paper 2 Relevance Score:
{score2:.3f}

Question:
{question}

Paper 1 Context:
{context1}

Paper 2 Context:
{context2}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content