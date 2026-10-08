import json
import os
import re
from src.chat.engine import ChatEngine, REFUSAL_OUT_OF_SCOPE
from src.config import TOP_K
from src.document_metadata import DOCUMENT_METADATA

def run_evaluation():
    with open("eval/question_bank.json", "r") as f:
        questions = json.load(f)
        
    engine = ChatEngine()
    
    results = []
    
    metrics = {
        "total_questions": len(questions),
        "retrieval_hit_rate": 0.0,
        "out_of_scope_accuracy": 0.0,
        "not_in_corpus_accuracy": 0.0,
        "citation_spot_check_accuracy": 0.0,
        "total_factual": 0,
        "total_out_of_scope": 0,
        "total_not_in_corpus": 0
    }
    
    hits = 0
    citation_hits = 0
    oos_hits = 0
    nic_hits = 0
    
    print("Starting evaluation...")
    
    for idx, q in enumerate(questions, 1):
        q_type = q["type"]
        query = q["query"]
        print(f"[{idx}/{len(questions)}] Eval {q_type}: {query}")
        
        result_entry = {
            "id": q["id"],
            "query": query,
            "type": q_type,
            "passed": False,
            "notes": ""
        }
        
        if q_type in ["factual", "cross-document"]:
            metrics["total_factual"] += 1
            
            # Check scope guard
            if engine.scope_guard.is_out_of_scope(query):
                result_entry["notes"] = "Failed: incorrectly flagged as out-of-scope"
                results.append(result_entry)
                continue
                
            retrieved = engine.retriever.search(query, k=TOP_K)
            relevant = engine.relevance_checker.check_relevance(retrieved)
            
            # Check if expected document is in relevant chunks
            retrieved_doc_ids = set([chunk["metadata"]["document_id"] for chunk in relevant if "metadata" in chunk and "document_id" in chunk["metadata"]])
            expected_docs = set(q.get("expected_document_ids", []))
            
            if expected_docs.intersection(retrieved_doc_ids):
                hits += 1
                result_entry["retrieval_hit"] = True
            else:
                result_entry["retrieval_hit"] = False
                result_entry["notes"] = f"Failed retrieval: expected any of {expected_docs}, got {retrieved_doc_ids}"
                
            # Generate answer and check citations
            try:
                answer = engine.ask(query)
                # Matches [Title, Publisher, Year](URL)
                citation_pattern = r'\[.*?\]\(http.*?\)'
                if re.search(citation_pattern, answer):
                    citation_hits += 1
                    result_entry["citation_hit"] = True
                else:
                    result_entry["citation_hit"] = False
                    result_entry["notes"] += " | Failed citation format check"
            except Exception as e:
                result_entry["citation_hit"] = False
                result_entry["notes"] += f" | LLM error: {str(e)}"
                
            if result_entry.get("retrieval_hit") and result_entry.get("citation_hit"):
                result_entry["passed"] = True
                
        elif q_type == "out-of-scope":
            metrics["total_out_of_scope"] += 1
            answer = engine.ask(query)
            if answer == REFUSAL_OUT_OF_SCOPE:
                oos_hits += 1
                result_entry["passed"] = True
            else:
                result_entry["notes"] = f"Failed OOS: got {answer[:50]}..."
                
        elif q_type == "not-in-corpus":
            metrics["total_not_in_corpus"] += 1
            answer = engine.ask(query)
            if "I don't appear to cover this topic" in answer:
                nic_hits += 1
                result_entry["passed"] = True
            else:
                result_entry["notes"] = f"Failed NIC: got {answer[:50]}..."
                
        results.append(result_entry)
        
    if metrics["total_factual"] > 0:
        metrics["retrieval_hit_rate"] = hits / metrics["total_factual"]
        metrics["citation_spot_check_accuracy"] = citation_hits / metrics["total_factual"]
        
    if metrics["total_out_of_scope"] > 0:
        metrics["out_of_scope_accuracy"] = oos_hits / metrics["total_out_of_scope"]
        
    if metrics["total_not_in_corpus"] > 0:
        metrics["not_in_corpus_accuracy"] = nic_hits / metrics["total_not_in_corpus"]
        
    os.makedirs("eval/results", exist_ok=True)
    with open("eval/results/eval_report.json", "w") as f:
        json.dump({"metrics": metrics, "details": results}, f, indent=2)
        
    # Generate markdown report
    with open("eval/results/eval_report.md", "w") as f:
        f.write("# M2Rag Evaluation Report\n\n")
        f.write("## Metrics\n\n")
        for key, val in metrics.items():
            if isinstance(val, float):
                f.write(f"- **{key}**: {val:.1%}\n")
            else:
                f.write(f"- **{key}**: {val}\n")
                
        f.write("\n## Details\n\n")
        f.write("| ID | Type | Query | Passed | Notes |\n")
        f.write("|---|---|---|---|---|\n")
        for r in results:
            passed = "✅" if r["passed"] else "❌"
            notes = r["notes"] if not r["passed"] else ""
            f.write(f"| {r['id']} | {r['type']} | {r['query']} | {passed} | {notes} |\n")
            
    print("\n=== Evaluation Complete ===")
    print(f"Results saved to eval/results/")
    for key, val in metrics.items():
        if isinstance(val, float):
            print(f"{key}: {val:.1%}")
        else:
            print(f"{key}: {val}")

if __name__ == '__main__':
    run_evaluation()
