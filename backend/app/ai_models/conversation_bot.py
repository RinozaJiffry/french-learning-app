"""
FrenchConversationBot:
- Simple retrieval-augmented generation (RAG)
- Uses SentenceTransformers + FAISS for knowledge retrieval
- Generates responses via DialoGPT
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class FrenchConversationBot:
    def __init__(self):
        # Conversational model
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

        # Knowledge retrieval
        self.sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.knowledge_base = self.load_knowledge()
        embeddings = self.sentence_model.encode(self.knowledge_base)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.astype("float32"))

    def load_knowledge(self):
        return [
            "In French cafés, you say 'Bonjour' when entering and 'Au revoir' when leaving.",
            "To order coffee, say 'Un café, s'il vous plaît'.",
            "French pronunciation emphasizes the last syllable of words.",
            "The French 'r' is rolled from the back of the throat."
        ]

    def retrieve_relevant_knowledge(self, query: str, k: int = 3):
        query_emb = self.sentence_model.encode([query])
        D, I = self.index.search(query_emb.astype("float32"), k)
        return [self.knowledge_base[i] for i in I[0]]

    def generate_response(self, user_input: str, scenario: str = "general") -> str:
        knowledge = self.retrieve_relevant_knowledge(user_input)
        context = f"Scenario: {scenario}\nRelevant info: {' '.join(knowledge)}\nUser: {user_input}\nBot:"
        inputs = self.tokenizer.encode(context, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=inputs.shape[1] + 50)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Bot:")[-1].strip()
