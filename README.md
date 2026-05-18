# AEGIS


<img width="2346" height="591" alt="image" src="https://github.com/user-attachments/assets/7c7d18f3-944b-485b-8ac1-21ba72949a85" />


**Adaptive Epistemic Guard for Intelligent Scam Defense**

Real-time epistemic manipulation detection for phone conversations, powered by a fine-tuned Gemma 4 E4B model running 100% locally via Ollama.

[![Gemma 4](https://img.shields.io/badge/Gemma_4-E4B-blue?logo=google)](https://huggingface.co/google/gemma-4-E4B-it)
[![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-black?logo=ollama)](https://ollama.com)
[![Model Weights](https://img.shields.io/badge/HuggingFace-GGUF_Weights-yellow?logo=huggingface)](https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> *The Gemma 4 Good Hackathon — Google DeepMind / Kaggle 2026*
> Tracks: Main Track · Safety and Trust Impact · Ollama Special Technology

---

## The Problem

$12.5 billion was lost to phone scams in the United States in 2024. Every existing detection system searches for keywords. Scammers adapted years ago — they no longer need to say specific phrases because the attack is not in the words. The attack is in the **structure of the conversation**.

A skilled scammer systematically dismantles the victim's capacity to think critically:

- They manufacture urgency so you stop deliberating and start reacting
- They invoke false authority so you defer instead of verify
- They isolate you from anyone who could offer a second opinion
- They plant false premises as established facts before you can question them
- They flood your emotions until rational analysis becomes impossible
- They close every exit until compliance feels like the only option

**AEGIS does not detect scam keywords. It detects epistemic manipulation — the real-time attack on a person's ability to think.**

---

## The Six Manipulation Vectors

AEGIS scores six dimensions of epistemic attack in every conversation, each on a scale of 0 to 100:

| Vector | What It Measures |
|---|---|
| Belief Installation | Unverified claims stated as established facts before the listener can question them |
| Verification Suppression | Active discouragement of independent checking ("don't call your bank", "don't tell anyone") |
| Urgency Fabrication | Artificial time pressure designed to bypass deliberative reasoning |
| Authority Hijacking | False claims of institutional, governmental, or professional power |
| Emotional Flooding | Deliberate emotional overload to disable critical thinking (fear, guilt, panic) |
| Exit Path Closure | Systematic elimination of the target's ability to disengage or seek help |

The **Epistemic Integrity Score** (EIS, 0 to 100) is the inverse of the average vector score. 100 means the conversation is clean. Below 70 is MEDIUM concern. Below 45 is HIGH risk. Below 20 is CRITICAL.

---

## Model

**Fine-tuned weights (GGUF for Ollama):**
https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1

**Base model:** `unsloth/gemma-4-e4b-it`

The model does not classify calls as scam or not scam. It outputs a structured JSON analysis of all six vectors simultaneously, with per-vector evidence quotes, an overall score, a plain-language explanation, and a recommended action. The framing is epistemic rather than binary, which makes it robust to novel scam scripts that keyword detectors miss.

---

## Training

### Dataset

6,401 synthetic scam conversations were generated across six scam categories:

- Government impersonation (IRS, Social Security Administration, law enforcement)
- Tech support scams
- Romance and relationship scams
- Investment and cryptocurrency scams
- Grandparent and family emergency scams
- Prize and lottery scams

2,839 legitimate call transcripts were generated as negative examples (doctor office calls, bank service calls, utility reminders, etc.).

440 conversations were selected and annotated with per-vector scores and evidence quotes. These formed the supervised fine-tuning dataset:

| Split | Count |
|---|---|
| Training | 396 (90%) |
| Evaluation | 44 (10%) |

Data files are in `resources/resources/data/`.

### Fine-Tuning Procedure

Fine-tuning was done with **Unsloth** on a **Google Colab A100 (80 GB)** using QLoRA (4-bit quantization during training).

The task is structured as instruction following: given a conversation transcript, produce the JSON analysis with all six vector scores and supporting evidence.

**Training configuration:**

| Parameter | Value |
|---|---|
| Base model | unsloth/gemma-4-e4b-it-unsloth-bnb-4bit |
| Method | QLoRA |
| LoRA rank | 16 |
| LoRA alpha | 16 |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Trainable parameters | 42.4M out of 8.04B (0.53%) |
| Max sequence length | 2048 tokens |
| Learning rate | 2e-4 |
| Optimizer | AdamW 8-bit |
| Per device batch size | 2 |
| Gradient accumulation | 4 (effective batch size: 8) |
| Epochs | 3 |
| Total steps | 150 |
| Final training loss | 0.4065 |
| Training time | approximately 10 minutes |
| GPU | NVIDIA A100-SXM4-80GB |

Training notebook and scripts are in the `Training/` folder.

### Export to GGUF

After training, the LoRA adapter was merged into the base weights and exported to GGUF Q4_K_M quantization using Unsloth:

```python
model.save_pretrained_gguf("aegis", tokenizer, quantization_method="q4_k_m")
```

The resulting GGUF file is 5.3 GB. It is uploaded to HuggingFace and registered with Ollama using a custom Modelfile that includes the full AEGIS system prompt, Gemma 4's native chat template, temperature 0.15, and a 800-token prediction limit.

---

## Architecture

```
Audio (microphone or browser tab)
          |
          v
  faster-whisper base.en
  (local CPU, int8, 6s chunks)
          |
          v
  Rolling transcript window
          |
          v
  AEGIS Model via Ollama
  (Gemma 4 E4B fine-tuned, localhost:11434)
          |
          v
  JSON analysis
  {6 vector scores, EIS, explanation, action}
          |
    ------+------
    |           |
    v           v
Verification   Flask
  Tools      backend
(local rules)  |
               v
          Browser dashboard
          Live EIS gauge
          Vector bars
          Timeline chart
          Alert + action
```

**Stack:**

| Component | Technology |
|---|---|
| Model inference | Ollama (local, no network) |
| Audio transcription | faster-whisper base.en (CPU, int8) |
| Backend | Flask 3 |
| Frontend | Vanilla JS, Chart.js 4, Web Speech API |
| Tab audio capture | getDisplayMedia + MediaRecorder |
| Cloud deployment | Railway (mock mode) |

---

## Running Locally

### Requirements

- Python 3.10 or higher
- Ollama — https://ollama.com/download
- 6 GB free disk for the model
- 8 GB RAM minimum (16 GB recommended)
- GPU is optional (CPU inference works, ~15 seconds per analysis)

### Step 1: Clone and install dependencies

```bash
git clone https://github.com/GIND123/Adaptive-Epistemic-Guard-for-Intelligent-Scam-Defense.git
cd Adaptive-Epistemic-Guard-for-Intelligent-Scam-Defense
pip install -r requirements.txt
```

### Step 2: Download the model GGUF

Download `gemma-4-e4b-it.Q4_K_M.gguf` from HuggingFace:

https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1

Place it in `resources/resources/gguf/`.

### Step 3: Register with Ollama

```bash
python setup_model.py
```

This runs `ollama create aegis -f Modelfile` from inside the `gguf/` directory. Only needs to be done once.

### Step 4: Launch the app

```bash
python app.py
```

Open `http://localhost:5001`.

On Windows, `run.bat` handles Ollama startup and browser launch automatically.

---

## Using the App

### Demo Tab

Choose from four built-in scenarios (IRS scam, tech support, romance investment, grandparent scam). Use Next Turn to advance one line at a time or Auto Play to run through the full scenario. Watch the Epistemic Integrity Score fall and individual vectors spike as the manipulation escalates.

### Live Tab (Type)

Type any conversation line, assign it to Caller or Receiver, and click Add Turn. Analyze fires automatically.

### Live Tab (Microphone)

Click Speak to use the browser's Web Speech API (Chrome or Edge only). Speak a line, and it is automatically added to the transcript and triggers analysis. Speaker toggles automatically between Caller and Receiver after each committed utterance.

### Live Tab (Tab Audio Capture)

For analyzing real scam call audio from a YouTube video or any browser tab:

1. Click the green Capture button in the Live tab
2. Chrome opens a screen/tab picker — select the YouTube tab
3. At the bottom of the picker, check **Share audio**
4. Click Share

Audio is transcribed in 6-second chunks by faster-whisper running locally. Each chunk is added to the transcript and triggers AEGIS analysis. The first chunk download of the `base` Whisper model (~150 MB) happens on first use.

---

## File Structure

```
.
├── app.py                        Flask backend and API endpoints
├── setup_model.py                One-time Ollama model registration
├── run.bat                       Windows launcher
├── requirements.txt
├── Procfile                      Railway deployment
├── railway.json
│
├── src/aegis/
│   ├── engine.py                 Ollama API calls, mock fallback
│   ├── tools.py                  Local verification tools
│   └── scenarios.py              Built-in demo scenarios
│
├── templates/
│   └── index.html                Single-page application
│
├── static/
│   ├── css/aegis.css
│   └── js/aegis.js
│
├── Training/
│   └── training notebook and scripts
│
└── resources/resources/
    ├── gguf/
    │   ├── Modelfile             Ollama config with AEGIS system prompt
    │   └── *.gguf                Model weights (download from HuggingFace)
    ├── lora_adapter/             LoRA weights and tokenizer files
    └── data/
        ├── scam_conversations.jsonl
        ├── legit_conversations.jsonl
        ├── annotated_data.json
        ├── train_data.json
        ├── eval_data.json
        ├── training_stats.json
        └── sanity_test_results.json
```

---

## Privacy Design

Every component runs locally. Nothing leaves the device.

- Audio is transcribed by faster-whisper on the local CPU. No cloud API.
- Model inference runs inside Ollama at `localhost:11434`. No external requests.
- Transcripts exist only in browser memory for the duration of the session.
- Verification tools use hardcoded local knowledge bases. No network calls.
- The model was trained before deployment and does not learn from user sessions.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | Ollama and model availability |
| `/api/scenarios` | GET | List of built-in demo scenarios |
| `/api/scenario/<id>` | GET | Full scenario with transcript turns |
| `/api/analyze` | POST | Run AEGIS analysis on a transcript |
| `/api/transcribe` | POST | Transcribe an audio chunk (WebM) |

---

## Acknowledgements

- Google DeepMind for the Gemma 4 model family
- Unsloth for the efficient QLoRA fine-tuning framework
- Ollama for local inference infrastructure
- SYSTRAN for faster-whisper

---

*AEGIS: Because the most dangerous attack is the one that changes how you see, not just what you see.*
