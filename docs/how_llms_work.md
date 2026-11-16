# How LLMs Work: Core Architecture & Principles

Large Language Models (LLMs) are advanced neural networks designed to understand, summarize, generate, and predict new content based on vast training datasets.

## 1. Tokens & Tokenization
LLMs do not read words directly; they break text down into smaller pieces called **tokens** (where 1 token $\approx$ 4 characters or 0.75 words in English). 

## 2. Training Pipeline
- **Pre-training**: The model consumes terabytes of web text, books, and code to learn grammar, facts, and reasoning by predicting masked or subsequent words.
- **Fine-tuning & Alignment (RLHF)**: Models are trained using human feedback to follow instructions safely and act as helpful assistants (like agricultural advisory bots).

## 3. Next-Word Prediction Architecture
At their core, LLMs use the Transformer architecture (Attention mechanisms) to calculate probability distributions over vocabulary tokens and output the most likely next word.

## 4. Model Limitations
- **Hallucination**: Generating plausible-sounding incorrect facts.
- **Context Window Limits**: Fixed token memory per prompt interaction.
- **Outdated Knowledge**: Cutoff dates based on training data.


## Architecture Diagram
[Raw Text] ---> [Tokenization] ---> [Embedding Layer] ---> [Transformer Blocks (Attention)] ---> [Probability Distribution] ---> [Next Token Output] 