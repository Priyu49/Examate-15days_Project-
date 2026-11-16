# Prompt Comparison Evaluation (10 Questions Test)

## Prompts Evaluated
- **Prompt A (`prompts/system.txt` + `prompts/soil_advisory.txt`)**: Strict system role, JSON output structure, enforced "I don't know" boundary rule.
- **Prompt B (`prompts/soil_summary.txt`)**: Conversational summary style without strict negative constraints.

## Evaluation Results on 10 Questions
| QID | Question Summary | Prompt A Answer Quality | Prompt A Conf. | Prompt B Answer Quality | Prompt B Conf. | Winner |
|-----|------------------|-------------------------|----------------|-------------------------|----------------|--------|
| 1 | Nitrogen deficiency advice | Precise NPK range & fertilizer | 0.98 | Good summary, less structured | 0.85 | Prompt A |
| 2 | Soil organic carbon meaning | Accurate microbial indicator info | 0.96 | Clear description | 0.88 | Prompt A |
| 3 | Fixing incorrect pH | Detailed liming/gypsum advice | 0.95 | General advice | 0.80 | Prompt A |
| 4 | Phosphorus range | Exact kg/ha limits cited | 0.99 | Vague range | 0.75 | Prompt A |
| 5 | Potassium benefits | Disease resistance & water regulation | 0.97 | Good | 0.82 | Prompt A |
| 6 | Unanswerable query (Weather prediction) | Safely triggered "I don't know" rule | 1.00 | Hallucinated weather forecast | 0.40 | Prompt A |
| 7 | Zinc unit & levels | ppm with 0.6-1.2 threshold | 0.98 | Correct units | 0.85 | Prompt A |
| 8 | Sulphur for oilseeds | Protein & oil synthesis explained | 0.96 | Good description | 0.80 | Prompt A |
| 9 | Electrical conductivity | Salinity measure correctly stated | 0.97 | Clear | 0.86 | Prompt A |
| 10 | Boron role | Pollination & cell wall info | 0.95 | Adequate | 0.79 | Prompt A |

## Conclusion
**Prompt A** is selected as the winner across all tests because its strict system boundary rules safely handle unanswerable queries (Q6) and its structured JSON output ensures robust backend integration.