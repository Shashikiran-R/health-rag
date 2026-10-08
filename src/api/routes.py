from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.guardrails.scope_guard import ScopeGuard
from src.retrieval.retriever import Retriever
from src.guardrails.relevance_check import RelevanceChecker
from src.generation.prompt_builder import PromptBuilder
from src.generation.answer_generator import AnswerGenerator
from src.config import TOP_K
from src.document_metadata import DOCUMENT_METADATA

router = APIRouter()

REFUSAL_OUT_OF_SCOPE = "I'm not able to provide medical advice, calorie targets, or weight recommendations. Please consult a registered dietitian or your healthcare provider for personalised guidance."
REFUSAL_NOT_IN_CORPUS = "I don't appear to cover this topic. I only have information from the following documents: {documents}"

class ChatEngine:
    def __init__(self):
        self.scope_guard = ScopeGuard()
        self.retriever = Retriever()
        self.relevance_checker = RelevanceChecker()
        self.prompt_builder = PromptBuilder()
        self.answer_generator = AnswerGenerator()

    def ask(self, query: str) -> str:
        if self.scope_guard.is_out_of_scope(query):
            return REFUSAL_OUT_OF_SCOPE
        
        results = self.retriever.search(query, k=TOP_K)
        relevant = self.relevance_checker.check_relevance(results)
        if not relevant:
            doc_names = [meta.get("title", doc_id) for doc_id, meta in DOCUMENT_METADATA.items()]
            return REFUSAL_NOT_IN_CORPUS.format(documents=", ".join(doc_names))

        prompt = self.prompt_builder.build(query, relevant)
        return self.answer_generator.generate(prompt)

engine = ChatEngine()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        ans = engine.ask(req.query)
        return ChatResponse(response=ans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
