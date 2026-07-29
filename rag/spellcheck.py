from spellchecker import SpellChecker

spell = SpellChecker()

# Technical terms we don't want the spell checker to change
CUSTOM_TERMS = {
    "ligthrag": "LightRAG",
    "lightrag": "LightRAG",
    "graph rag": "GraphRAG",
    "graphrag": "GraphRAG",
    "rank rag": "RankRAG",
    "rankrag": "RankRAG",
}


def normalize_question(question):
    q = question.lower()

    for wrong, correct in CUSTOM_TERMS.items():
        q = q.replace(wrong, correct)

    words = []

    for word in q.split():
        corrected = spell.correction(word)
        words.append(corrected if corrected else word)

    return " ".join(words)