# AEGIS


<img width="2346" height="591" alt="image" src="https://github.com/user-attachments/assets/7c7d18f3-944b-485b-8ac1-21ba72949a85" />


**Adaptive Epistemic Guard for Intelligent Scam Defense**

Real-time detection of epistemic manipulation in phone conversations, powered by a fine-tuned Gemma 4 E4B model.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Railway-brightgreen)](https://web-production-70160.up.railway.app/)
[![Model Weights](https://img.shields.io/badge/HuggingFace-GGUF_Weights-yellow?logo=huggingface)](https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1)
[![Gemma 4](https://img.shields.io/badge/Gemma_4-E4B_Fine--tuned-blue?logo=google)](https://huggingface.co/google/gemma-4-E4B-it)
[![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-black)](https://ollama.com)

> *Not just detecting scams. Detecting how scammers corrupt your ability to think.*

---

## Live Demo

**https://web-production-70160.up.railway.app/**

The hosted version runs in **mock mode** — instant pre-computed responses, no model weights on the server. For full AI inference with the fine-tuned Gemma 4 model, run locally (instructions below).

---

## What AEGIS Does

$12.5 billion was lost to phone scams in the United States in 2024. Every existing detector looks for keywords. Scammers adapted long ago.

The real attack is in the *structure* of the conversation. A skilled scammer does not need flagged phrases. They dismantle your capacity to evaluate their claims:

- They manufacture urgency so you stop deliberating and start reacting
- They invoke false authority so you defer instead of verify
- They cut you off from anyone who could help
- They plant false premises before you can question them
- They flood your emotions until rational analysis fails
- They close every exit until compliance feels like the only option

AEGIS tracks all six of these attack vectors simultaneously and produces an **Epistemic Integrity Score** showing how much of the listener's decision-making capacity has been compromised.

---

## The Six Manipulation Vectors

| Vector | What It Measures |
|---|---|
| Belief Installation | Unverified claims stated as established fact |
| Verification Suppression | Discouraging independent checking ("don't call your bank") |
| Urgency Fabrication | Artificial time pressure to bypass deliberation |
| Authority Hijacking | False claims of governmental or institutional power |
| Emotional Flooding | Deliberate overload of fear, guilt, or panic |
| Exit Path Closure | Eliminating the target's ability to disengage or seek help |

**Epistemic Integrity Score (EIS):** 100 = fully safe. Below 70 = MEDIUM concern. Below 45 = HIGH risk. Below 20 = CRITICAL, terminate the call.

---

## Using the Live Demo

Open **https://web-production-70160.up.railway.app/**

The interface has two panels: transcript on the left, analysis dashboard on the right.

### Demo Tab (quickest start)

1. Select a scenario from the dropdown (IRS Scam, Tech Support, Romance Investment, Grandparent Scam)
2. Click **Next Turn** to advance one line at a time, or **Auto Play** to run through automatically
3. Watch the EIS gauge drop and individual vectors spike as the manipulation escalates
4. The bottom timeline shows EIS history across the full conversation

### Live Tab — Type

1. Switch to the **Live** tab
2. Select the speaker (Caller or Receiver)
3. Type any line of dialogue and click **Add Turn**
4. Click **Analyze** or let it trigger automatically

Try pasting lines from a real scam call transcript, or from the FTC's robocall examples at [consumer.ftc.gov/features/robocall-scam-examples](https://consumer.ftc.gov/features/robocall-scam-examples).

### Live Tab — Voice (Chrome / Edge only)

1. Switch to the **Live** tab
2. Click the **Speak** button (microphone icon)
3. Allow microphone access when prompted
4. Speak a line — it transcribes automatically and adds to the transcript
5. The speaker toggles between Caller and Receiver after each committed utterance
6. Click **Speak** again to stop

Works best in Chrome or Edge. Uses the browser's built-in Web Speech API — no external service.

### Live Tab — Tab Audio Capture (Chrome / Edge only)

Use this to analyze audio playing in another browser tab in real time — for example, a YouTube scam call video or the FTC robocall audio clips.

1. Switch to the **Live** tab
2. Click the green **Capture** button
3. Chrome opens a screen/tab picker — select the tab playing the audio
4. At the bottom of the picker, check **Share audio** (this is unchecked by default)
5. Click **Share**
6. Audio from that tab is now captured, transcribed in 6-second chunks by Whisper running locally, and fed into AEGIS

Click **Capture** again to stop.

> Note: "Share audio" only appears when selecting a **Tab** (not a window or full screen). Make sure the audio tab is playing before you start the capture.

---

## Running Locally (Full AI Mode)

The local version uses the actual fine-tuned Gemma 4 model via Ollama. Analysis uses real inference instead of mock responses.

### Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) installed
- 6 GB free disk space for the model
- 8 GB RAM minimum (16 GB recommended)
- GPU optional — CPU inference works at ~15 seconds per analysis

### 1. Clone and install

```bash
git clone https://github.com/GIND123/Adaptive-Epistemic-Guard-for-Intelligent-Scam-Defense.git
cd Adaptive-Epistemic-Guard-for-Intelligent-Scam-Defense
pip install -r requirements.txt
```

### 2. Download the model

Download `gemma-4-e4b-it.Q4_K_M.gguf` (5.3 GB) from HuggingFace:

**https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1**

Place the file in:
```
resources/resources/gguf/gemma-4-e4b-it.Q4_K_M.gguf
```

### 3. Register with Ollama

```bash
python setup_model.py
```

This registers the model with Ollama using the AEGIS system prompt. Only needs to run once.

Alternatively, do it manually:
```bash
cd resources/resources/gguf
ollama create aegis -f Modelfile
```

### 4. Launch

```bash
python app.py
```

Open **http://localhost:5001**

On Windows, `run.bat` handles Ollama startup and opens the browser automatically.

### Switching between Mock and Live AI

The **Mock / Live AI** button in the Demo tab toggles between pre-computed mock responses (instant) and real model inference. If Ollama is not running, the app falls back to mock mode automatically and shows "Ollama Offline — Mock Mode" in the status indicator.

### Tab Audio Capture (local)

Tab audio capture works the same way locally as on the hosted version. The transcription runs via `faster-whisper` on your local CPU. On first use it downloads the Whisper `base` model (~150 MB). Subsequent uses are instant.

---

## Architecture

```
Audio (mic / tab capture)          Demo / typed input
         |                                 |
         v                                 |
  faster-whisper                           |
  base.en, local CPU                       |
         |                                 |
         v                                 v
         +-----------> Flask Backend <-----+
                        app.py :5001
                             |
                             v
                       AEGIS Engine
                        engine.py
                             |
                    ---------+---------
                    |                 |
                    v                 v
             Ollama :11434     Verification Tools
             (local only)       Authority Rules
                    |            Payment Risk DB
                    v                 |
           Gemma 4 E4B                |
           Fine-tuned                 |
           Q4_K_M GGUF                |
                    |                 |
                    +---------+-------+
                              |
                              v
                     6 Vector Scores
                     EIS (0-100)
                     Explanation
                     Recommended Action
                              |
                              v
                     Browser Dashboard
                     Gauge + Bars + Timeline
```

---

## Model Training

**Base model:** `unsloth/gemma-4-e4b-it`
**Fine-tuned weights:** [HuggingFace](https://huggingface.co/GOVINDFROM/aegis-gemma-4-e4b-it-scam-defense-ollama-gguf-v1)

| Parameter | Value |
|---|---|
| Method | QLoRA (LoRA r=16, alpha=16) |
| Trainable parameters | 42.4M / 8.04B (0.53%) |
| Training samples | 396 |
| Eval samples | 44 |
| Epochs | 3 |
| Learning rate | 2e-4 |
| Final training loss | 0.4065 |
| GPU | NVIDIA A100-SXM4-80GB |
| Training time | ~10 minutes |
| Export | GGUF Q4_K_M (5.3 GB) |

Training notebooks are in [`Training_notebooks/`](Training_notebooks/).
Dataset files are in [`resources/resources/data/`](resources/resources/data/).

---

## Repository Structure

```
.
├── app.py                        Flask backend and all API endpoints
├── setup_model.py                One-time Ollama model registration
├── run.bat                       Windows launcher (starts Ollama + opens browser)
├── requirements.txt
├── Procfile                      Railway deployment
├── railway.json
│
├── src/aegis/
│   ├── engine.py                 Ollama inference, mock fallback, prompt builder
│   ├── tools.py                  Local verification tools (authority, payment risk)
│   └── scenarios.py              Built-in demo scenarios (IRS, tech support, romance, grandparent)
│
├── templates/
│   └── index.html                Single-page application
│
├── static/
│   ├── css/aegis.css
│   └── js/aegis.js
│
├── Training_notebooks/
│   ├── aegis_training.ipynb      QLoRA fine-tuning notebook (Colab A100)
│   └── aegis_data_preparation.ipynb
│
├── examples/
│   └── real_test_case.txt        Annotated real-world test transcript with expected outputs
│
└── resources/resources/
    ├── gguf/
    │   ├── Modelfile             Ollama config with AEGIS system prompt
    │   └── *.gguf                Model weights — download from HuggingFace
    ├── lora_adapter/             LoRA adapter weights and tokenizer
    └── data/
        ├── scam_conversations.jsonl      3,562 synthetic scam transcripts
        ├── legit_conversations.jsonl     2,839 legitimate call transcripts
        ├── annotated_data.json           440 annotated training samples
        ├── train_data.json               396 training examples
        ├── eval_data.json                44 evaluation examples
        └── training_stats.json           Training metrics and hyperparameters
```

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | Returns `{ollama: bool, model: bool}` |
| `/api/scenarios` | GET | List of built-in scenarios |
| `/api/scenario/<id>` | GET | Full scenario with all transcript turns |
| `/api/analyze` | POST | Analyze a transcript. Body: `{transcript: [...], use_mock: bool}` |
| `/api/transcribe` | POST | Transcribe an audio chunk. Body: `multipart/form-data` with `audio` file |

**Analyze request body:**
```json
{
  "transcript": [
    {"speaker": "caller", "text": "This is Officer Reynolds from the federal fraud task force."},
    {"speaker": "receiver", "text": "What? I haven't done anything wrong."}
  ],
  "use_mock": false
}
```

**Analyze response:**
```json
{
  "analysis": {
    "manipulation_vectors": {
      "belief_installation": 40,
      "verification_suppression": 10,
      "urgency_fabrication": 25,
      "authority_hijacking": 85,
      "emotional_flooding": 30,
      "exit_path_closure": 5
    },
    "integrity_score": 67,
    "risk_level": "MEDIUM",
    "explanation": "Caller is claiming law enforcement authority...",
    "recommended_action": "Ask for a badge number and offer to call back..."
  },
  "tools": [
    {
      "type": "authority",
      "data": {
        "organization": "federal fraud task force",
        "is_suspicious": true,
        "warning": "Legitimate law enforcement does not demand immediate payment by phone."
      }
    }
  ]
}
```

---

## Privacy

Every component runs on device. No data leaves the machine.

- Audio is transcribed by faster-whisper on the local CPU
- Model inference runs inside Ollama at `localhost:11434`
- Transcripts exist only in browser memory for the duration of the session
- Verification tools use hardcoded local rule bases with zero network calls
- The model was trained before deployment and does not learn from user sessions

The cloud hosted version at Railway uses mock mode only — no call audio or transcript data is processed or stored server-side.

---

## Troubleshooting

**"Ollama Offline — Mock Mode" in the status bar**
Start Ollama: open the Ollama desktop app or run `ollama serve` in a terminal. If the model has not been registered yet, run `python setup_model.py`.

**Slow analysis (~15-30 seconds)**
Normal on CPU. For faster inference, ensure Ollama detects your GPU. On Windows with an NVIDIA GPU, install the CUDA version of Ollama from ollama.com.

**Tab audio capture shows no transcript**
Make sure you checked "Share audio" in the tab picker (it is unchecked by default). The option only appears when a **Tab** is selected, not a window. Also ensure the audio is actually playing in the source tab before capturing.

**Voice input not working**
Web Speech API requires Chrome or Edge. It does not work in Firefox or Safari. Allow microphone permission when prompted.

**JSON errors in model output**
Occasionally the model produces malformed JSON. The engine retries automatically. If it persists, toggle to mock mode and back, or restart Ollama.

---

## Acknowledgements

- Google DeepMind — Gemma 4 model family
- Unsloth — QLoRA fine-tuning framework
- Ollama — local inference runtime
- SYSTRAN — faster-whisper
