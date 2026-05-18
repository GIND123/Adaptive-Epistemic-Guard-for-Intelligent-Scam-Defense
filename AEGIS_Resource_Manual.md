# AEGIS Resource Manual

**Adaptive Epistemic Guard for Intelligent Scam Defense**

Fine-tuned Gemma 4 E4B model for real-time detection of epistemic manipulation in phone conversations. Built for the Gemma 4 Good Hackathon.

---

## File Structure

```
resources/
│
├── gguf/
│   ├── gemma-4-e4b-it.Q4_K_M.gguf    # Quantized model (~5.3 GB) — run with Ollama
│   └── Modelfile                       # Ollama config with AEGIS system prompt
│
├── lora_adapter/
│   ├── adapter_model.safetensors       # LoRA weights (42M trainable params)
│   ├── adapter_config.json             # LoRA config (r=16, alpha=16)
│   ├── tokenizer.json                  # Tokenizer
│   ├── tokenizer_config.json           # Tokenizer config
│   ├── chat_template.jinja             # Gemma 4 chat template
│   └── README.md                       # Auto-generated adapter readme
│
└── data/
    ├── scam_conversations.jsonl         # 3,562 synthetic scam call transcripts
    ├── legit_conversations.jsonl        # 2,839 legitimate call transcripts
    ├── annotated_data.json              # 440 annotated samples (240 scam, 200 legit)
    ├── train_data.json                  # 396 training examples (SFT format)
    ├── eval_data.json                   # 44 evaluation examples
    ├── training_stats.json              # Training metrics and hyperparameters
    └── sanity_test_results.json         # Post-training validation outputs
```

---

## Quick Start — Run AEGIS Locally with Ollama

### Prerequisites

- **Ollama** installed — https://ollama.com/download
- **~6 GB free disk space** for the model
- **8 GB+ RAM** recommended (runs on CPU; GPU optional)

### Step 1: Create the Ollama Model

```bash
cd resources/gguf/
ollama create aegis -f Modelfile
```

This registers the GGUF model with Ollama using the AEGIS system prompt and parameters.

### Step 2: Run AEGIS

```bash
ollama run aegis
```

### Step 3: Test It

Paste a transcript into the prompt. AEGIS will return a JSON analysis.

**Example — Scam call:**

```
Analyze this phone call for epistemic manipulation:

Caller: Hello, this is Agent Williams from the IRS Criminal Investigation Division.
We have found serious discrepancies in your tax filings from 2023.
A federal arrest warrant has been issued in your name.
You must pay $4,500 immediately via gift cards to resolve this before officers are dispatched.
Do NOT hang up this phone or contact anyone else, as this is a federal matter.
```

**Expected output:**

```json
{
  "vectors": {
    "belief_installation":      {"score": 95, "evidence": "False IRS identity and fabricated warrant"},
    "verification_suppression": {"score": 90, "evidence": "Forbids contacting anyone else"},
    "urgency_fabrication":      {"score": 100, "evidence": "Immediate payment demanded"},
    "authority_hijacking":      {"score": 100, "evidence": "Impersonates federal agent"},
    "emotional_flooding":       {"score": 85, "evidence": "Threat of arrest"},
    "exit_path_closure":        {"score": 95, "evidence": "Do NOT hang up instruction"}
  },
  "integrity_score": 5,
  "risk_level": "CRITICAL",
  "explanation": "Extreme epistemic manipulation across all vectors...",
  "recommended_action": "IMMEDIATELY terminate the call. Report to FBI IC3 and FTC."
}
```

**Example — Legitimate call:**

```
Analyze this phone call for epistemic manipulation:

Caller: Hi, this is Dr. Chen's office calling to confirm your appointment
scheduled for Thursday at 2:30 PM. If you need to reschedule, please call us
back at 555-0123 during office hours. Thank you and have a great day!
```

**Expected output:** `integrity_score: 95`, `risk_level: LOW`

### Step 4: Use via API

Ollama exposes a local API at `http://localhost:11434`:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "aegis",
  "prompt": "Analyze this phone call for epistemic manipulation:\n\n[PASTE TRANSCRIPT HERE]",
  "stream": false
}'
```

---

## Using the LoRA Adapter (Advanced)

If you want to load the adapter in Python for further fine-tuning or inference with the full-precision model:

```python
from unsloth import FastModel
from unsloth.chat_templates import get_chat_template

model, tokenizer = FastModel.from_pretrained(
    model_name="resources/lora_adapter",
    max_seq_length=4096,
    load_in_4bit=True,
    dtype=None,
)
tokenizer = get_chat_template(tokenizer, chat_template="gemma-4")
```

**Requirements:** `unsloth`, `transformers==5.5.0`, `torch`, CUDA-capable GPU.

---

## Data Files

| File | Records | Description |
|------|---------|-------------|
| `scam_conversations.jsonl` | 3,562 | Synthetic scam transcripts across 6 types |
| `legit_conversations.jsonl` | 2,839 | Synthetic legitimate call transcripts |
| `annotated_data.json` | 440 | Model-annotated samples with vector scores |
| `train_data.json` | 396 | SFT training split (90%) |
| `eval_data.json` | 44 | Evaluation split (10%) |

### Scam Types in Dataset

- Government impersonation (IRS, SSA, law enforcement)
- Tech support scams
- Romance/relationship scams
- Investment/cryptocurrency scams
- Grandparent/family emergency scams
- Prize/lottery scams

---

## The Six Epistemic Manipulation Vectors

AEGIS analyzes each call across six dimensions, scoring 0–100:

| Vector | What It Detects |
|--------|-----------------|
| **belief_installation** | Unverified claims presented as established facts |
| **verification_suppression** | Discouraging the target from checking claims independently |
| **urgency_fabrication** | Artificial time pressure to prevent rational evaluation |
| **authority_hijacking** | Exploiting institutional trust through false credentials |
| **emotional_flooding** | Overwhelming emotions to disable critical thinking |
| **exit_path_closure** | Eliminating the target's ability to disengage or seek help |

### Output Fields

- **integrity_score** (0–100): Overall epistemic safety. 100 = fully safe, 0 = fully compromised.
- **risk_level**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
- **explanation**: Plain-language summary of findings.
- **recommended_action**: Specific next step for the user.

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | `unsloth/gemma-4-E4B-it` |
| Method | LoRA (r=16, alpha=16) |
| Trainable params | 42.4M / 8.04B (0.53%) |
| Training samples | 396 |
| Epochs | 3 |
| Effective batch size | 8 |
| Learning rate | 2e-4 |
| Optimizer | AdamW 8-bit |
| Final training loss | 0.4065 |
| Best eval loss | 1.4254 (step 100) |
| GPU | NVIDIA A100-SXM4-80GB |
| Training time | ~10 minutes |
| Quantization | Q4_K_M (GGUF) |

---

## Troubleshooting

**Ollama says "model not found"**
Make sure you ran `ollama create aegis -f Modelfile` from inside the `gguf/` directory.

**Slow on CPU**
The Q4_K_M quantization is optimized for CPU inference but responses may take 15–30 seconds. For faster results, use a machine with a GPU and ensure Ollama detects it.

**JSON parsing errors in output**
Occasionally the model may produce malformed JSON. Retry the prompt or add "Respond with ONLY valid JSON, no markdown" to your query.

**Out of memory**
The Q4_K_M model needs ~6 GB RAM. Close other applications or use a machine with more memory.
