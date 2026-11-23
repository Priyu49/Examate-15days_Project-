# MitraMaati Interview Brief

## 60-second pitch

MitraMaati is a soil-health advisory system that turns Soil Health Card readings
into clear, cited next steps for farmers. A farmer can ask a question or enter
all 12 readings and receive a traffic-light soil snapshot with a plain-language
explanation, a dose-direction cue, and the source behind it. The backend is
FastAPI; grounded answers use retrieval over Soil Health Card material, while
numeric classifications are deterministic and do not ask an LLM to choose a
threshold. The hardest problem was that nutrient sources can use different
cut-offs and measurement bases—for example, potassium low limits of 120, 108,
or 140 kg/ha, and phosphorus reported as either P or P2O5. MitraMaati resolves
that ambiguity by selecting one versioned threshold table per result, declaring
the standard and measurement basis, and computing the status directly from the
table. That makes the advice reproducible, reviewable, and safer to use.

## Threshold contract

All numeric classifications in this project use exactly one cited table:
[`data/records.json`](../data/records.json), the **MitraMaati Soil Health Card
reference table v1**. Its rows cite the Soil Health Card FAQ source. For
phosphorus, this application standard is **P (not P2O5)** and uses the table's
`kg/ha` values as supplied. The application does not silently convert P2O5 to
P or choose a threshold from retrieved text.

The classifier returns the table name, measurement basis, table path, source
URL, and deterministic comparison method alongside each result. A value marked
P2O5 must be converted and validated before it is sent to this P-basis
classifier.

## Ten likely interview questions

### 1. What problem does MitraMaati solve?

Soil Health Cards are useful but difficult to interpret quickly. MitraMaati
turns their readings into a cited explanation and a clear Low, Medium, or High
status so a farmer can understand the reading before acting on it.

### 2. What is the technical architecture?

The Streamlit interface calls a FastAPI backend. General questions go through a
grounded retrieval pipeline with citations; soil-card numbers go through a pure
Python classifier. Chroma-based retrieval, a LangGraph approval flow, request
metrics, and a small in-memory cache support the API.

### 3. What was the hardest problem?

Keeping classifications consistent when sources disagree. A low potassium
limit can appear as 120, 108, or 140 kg/ha, and phosphorus can be labelled P
or P2O5. Mixing those without declaring a basis gives a confident-looking but
unreliable answer.

### 4. How did you resolve conflicting thresholds?

I made the checked-in **MitraMaati Soil Health Card reference table v1** the
only classification authority. The result names that standard and cites
[`data/records.json`](../data/records.json), rather than letting retrieval or
an LLM select a convenient threshold.

### 5. Can you show a computed example?

Yes. The cited table defines Phosphorus (P) as **P (not P2O5)**, Low below 10
kg/ha, Medium from 10 through 25 kg/ha, and High above 25 kg/ha. Therefore a
P reading of 9 kg/ha is **Low** because `9 < 10`; it is not a language-model
judgement. This result uses MitraMaati Soil Health Card reference table v1.

### 6. How do you prevent an LLM from inventing numeric advice?

The numeric path does not use the LLM: `classify_soil_card` loads a record,
compares the supplied value to its low and high limits, and returns the
calculated status. The response includes `classification_method` as
`deterministic threshold comparison`, plus the selected standard and source.

### 7. What evidence does a user receive?

Every classification includes the parameter, supplied value, unit, status,
threshold bounds, meaning, source URL, threshold table, standard, and
measurement basis. Retrieval answers separately show their retrieved
citations.

### 8. What does the traffic-light card mean?

Low maps to red, Medium to yellow, and High to green. The status is computed
from the selected table; the accompanying recommendation is a general
direction, not a crop- and state-specific fertilizer prescription.

### 9. How did you evaluate the RAG portion?

The checked-in benchmark compares three retrieval configurations on five
questions. The selected 250-character, top-3 configuration reports 80% fact
accuracy, 100% citation recall, and 100% boundary safety. Those are project
evaluation results, not field-outcome claims.

### 10. What would you improve next?

I would add versioned regional and crop-specific standards with a required
sample method and nutrient-form field, then reject incompatible inputs before
classification. Each new standard would remain separately cited and selectable;
the classifier would still use exactly one declared table for every result.

## Demo route

1. Open the Soil card and enter `Phosphorus (P) = 9` kg/ha.
2. Show the Low result and the source citation.
3. Call out the returned standard, `P (not P2O5)` basis, and deterministic
   comparison method.
4. Contrast it with a general `/ask` response, which is grounded and cited but
   is not used to choose classification thresholds.
