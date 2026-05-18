---
language:
- en
license: gemma
library_name: gguf
pipeline_tag: text-generation
tags:
- gemma
- gemma-4
- scam-detection
- ai-safety
- trust-and-safety
- social-engineering
- ollama
- gguf
- quantized
base_model: google/gemma-4-E4B-it
---

# AEGIS Gemma 4 E4B IT Scam Defense Ollama GGUF v1

AEGIS is a locally deployable Gemma 4 E4B instruction-tuned model package for scam-defense analysis. It is tuned for one job: analyze a phone-call transcript for epistemic manipulation and return structured JSON describing how a scammer is trying to distort the target's decision-making process.

This repository is the Ollama / GGUF release package for:

- Local inference with Ollama
- Offline demos and hackathon judging
- Safety and trust evaluation on scam-call transcripts

The package is designed for the `GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1` Hugging Face repo.

## What This Model Does

Given a conversation transcript, AEGIS scores six manipulation vectors:

1. `belief_installation`
2. `verification_suppression`
3. `urgency_fabrication`
4. `authority_hijacking`
5. `emotional_flooding`
6. `exit_path_closure`

It returns:

- Per-vector scores from `0-100`
- `integrity_score`
- `risk_level`
- A plain-language explanation
- A recommended next action
- Evidence snippets per vector

## Files

- `gemma-4-e4b-it.Q4_K_M.gguf`: quantized GGUF model for local inference
- `Modelfile`: Ollama model definition with the AEGIS system behavior and prompt template
- `README.md`: usage and model card

## Base Model

- Base model: `google/gemma-4-E4B-it`
- Deployment format: `GGUF`
- Quantization: `Q4_K_M`

## Training Summary

This release is derived from a fine-tuned Gemma 4 E4B instruction model adapted for scam-defense transcript analysis.

- Training method: LoRA
- LoRA rank: `16`
- Learning rate: `2e-4`
- Epochs: `3`
- Train size: `396`
- Eval size: `44`
- Max sequence length: `2048`
- Final reported training loss: `0.4065`
- Training hardware: `NVIDIA A100-SXM4-80GB`

## Recommended Use

Use this model to:

- Analyze scam and non-scam phone-call transcripts
- Demonstrate local-first AI safety tooling
- Power an Ollama-based Streamlit, Gradio, or desktop app
- Support structured risk scoring for research demos

Do not use this model as:

- A legal authority
- A replacement for emergency services
- A sole decision-maker in high-stakes financial or criminal matters

## Download And Run With Ollama

### Option 1: Download from Hugging Face, then create the Ollama model

1. Download the repository:

```bash
git lfs install
git clone https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1
cd aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1
```

2. Create the local Ollama model:

```bash
ollama create aegis -f Modelfile
```

3. Run it:

```bash
ollama run aegis
```

### Option 2: Download with the Hugging Face CLI

```bash
huggingface-cli download GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1 --local-dir .
ollama create aegis -f Modelfile
ollama run aegis
```

## Example Prompt

Paste a transcript like this into Ollama:

```text
Analyze this phone call for epistemic manipulation:

Caller: Hello, this is Agent Williams from the IRS Criminal Investigation Division.
We found major discrepancies in your tax filings.
A federal arrest warrant has been issued in your name.
You must pay immediately via gift cards to stop enforcement.
Do not hang up or contact anyone else.
```

Expected behavior:

- High `authority_hijacking`
- High `urgency_fabrication`
- High `verification_suppression`
- `risk_level` near `CRITICAL`
- Very low `integrity_score`

## Example Output Shape

The model is configured to emit JSON in this structure:

```json
{
  "manipulation_vectors": {
    "belief_installation": 95,
    "verification_suppression": 90,
    "urgency_fabrication": 100,
    "authority_hijacking": 100,
    "emotional_flooding": 85,
    "exit_path_closure": 95
  },
  "integrity_score": 5,
  "risk_level": "CRITICAL",
  "explanation": "The caller is using false authority, panic, and isolation tactics to block independent verification.",
  "recommended_action": "Terminate the call and verify the claim through an official number you find independently.",
  "evidence": {
    "belief_installation": "False claim of tax discrepancies and an arrest warrant.",
    "verification_suppression": "Instructs the target not to contact anyone else.",
    "urgency_fabrication": "Immediate payment demanded.",
    "authority_hijacking": "Claims to be from the IRS Criminal Investigation Division.",
    "emotional_flooding": "Threat of arrest creates fear.",
    "exit_path_closure": "Explicit instruction not to hang up."
  }
}
```

## Hardware Notes

- Runs locally with Ollama
- Suitable for laptops / desktops
- Quantized package size is about `5.3 GB`
- GPU helps, but CPU inference is possible with higher latency

## Limitations

- This model analyzes transcript text, not verified ground truth
- Scam tactics evolve and can differ by region and language
- Structured JSON output may occasionally need retry logic in downstream apps
- Scores should support human judgment, not replace it

## Safety Notes

This model is intended to help users recognize manipulative scam behavior. It should be deployed with:

- Clear user-facing disclaimers
- Human override
- Independent verification guidance
- Privacy-preserving local inference where possible

## Citation

If you use this model, cite the project repository and hackathon submission:

```bibtex
@misc{aegis_gemma4_2026,
  title={AEGIS: Adaptive Epistemic Guard for Intelligent Scam Defense},
  author={GOVINDFROM},
  year={2026},
  howpublished={Hugging Face model repository}
}
```
