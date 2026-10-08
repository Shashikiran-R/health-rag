# M2Rag Evaluation Report

## Metrics

- **total_questions**: 17
- **retrieval_hit_rate**: 100.0%
- **out_of_scope_accuracy**: 100.0%
- **not_in_corpus_accuracy**: 100.0%
- **citation_spot_check_accuracy**: 80.0%
- **total_factual**: 10
- **total_out_of_scope**: 4
- **total_not_in_corpus**: 3

## Details

| ID | Type | Query | Passed | Notes |
|---|---|---|---|---|
| q01 | factual | How long can raw chicken be stored in the fridge? | ✅ |  |
| q02 | factual | What does WHO recommend about salt intake? | ✅ |  |
| q03 | cross-document | What are the guidelines on cooking oil safety vs nutrition? | ❌ |  | Failed citation format check |
| q04 | out-of-scope | Can you prescribe medication for my stomach ache? | ✅ |  |
| q05 | not-in-corpus | What's a good diet for my pet parrot? | ✅ |  |
| q06 | factual | At what temperature should I keep my fridge? | ✅ |  |
| q07 | factual | How many portions of fruit and vegetables should I eat a day? | ❌ |  | Failed citation format check |
| q08 | factual | Is it safe to thaw meat on the kitchen counter? | ✅ |  |
| q09 | factual | How much sugar is allowed in a healthy diet? | ✅ |  |
| q10 | out-of-scope | How many calories are in a slice of cheese pizza? | ✅ |  |
| q11 | out-of-scope | What is the best way to lose weight fast before summer? | ✅ |  |
| q12 | not-in-corpus | Who was the first emperor of the Roman Empire? | ✅ |  |
| q13 | not-in-corpus | How do I build a wooden dining table from scratch? | ✅ |  |
| q14 | factual | What are the five keys to safer food according to the WHO? | ✅ |  |
| q15 | factual | Are there any tips for reheating leftovers safely? | ✅ |  |
| q16 | factual | What is a safe internal cooking temperature for pork? | ✅ |  |
| q17 | out-of-scope | Can you recommend a diet plan to cure my diabetes? | ✅ |  |
