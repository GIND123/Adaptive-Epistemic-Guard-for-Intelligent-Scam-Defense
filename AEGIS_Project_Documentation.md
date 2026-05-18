# AEGIS — Adaptive Epistemic Guard for Intelligent Scam Defense

> *"Not just detecting scams — modeling how scammers corrupt your ability to think."*

**Competition:** The Gemma 4 Good Hackathon (Kaggle / Google DeepMind)
**Tracks Targeted:** Main Track ($50K) · Safety & Trust Impact ($10K) · Ollama Special Tech ($10K)
**Maximum Prize Potential:** $70,000

---

## 1. The Problem

In 2024, consumers reported losing over $12.5 billion to fraud in the United States alone, with over 2.6 million fraud reports filed to the FTC's Consumer Sentinel Network. Imposter scams — where someone falsely claims to be a romantic interest, a government official, a family member in distress, or a tech support agent — accounted for $2.95 billion of those losses.

But here's what every existing solution misses: **scams are not a content problem. They are an epistemic attack.**

Current anti-scam tools look for keywords ("gift card," "wire transfer," "social security number") or blocklist known phone numbers. These fail for a simple reason — sophisticated scammers don't use flagged words. They manipulate the *structure* of the conversation to systematically disable the victim's capacity for independent judgment. They manufacture urgency to suppress deliberative thinking. They invoke false authority to override skepticism. They isolate the victim from trusted advisors. They create information asymmetry that makes the victim dependent on the scammer's framing of reality.

**AEGIS doesn't detect scam keywords. It detects epistemic manipulation — the real-time corruption of someone's rational decision-making process.**

### Why This Affects Everyone, Not Just the Elderly

The tech is identical regardless of age. Romance scams target people in their 30s. Job scams target people in their 20s. Crypto and investment scams target tech-savvy professionals. Business email compromise targets corporate executives. The underlying detection mechanism is the same across all demographics: real-time conversational pattern analysis for manipulation tactics including urgency fabrication, authority impersonation, isolation directives ("don't tell anyone about this"), and financial extraction.

The reason we frame the video pitch around protecting an elderly person is strategic storytelling — judges score 30 out of 100 points on video pitch and storytelling alone. An elderly person losing their life savings to a scam is universally understood, emotionally resonant, and communicates the stakes immediately. But the product serves everyone.

---

## 2. Our Unique Angle — Epistemic Manipulation Detection

### What Makes AEGIS Different From Every Other Scam Detector

Most approaches treat scam detection as binary classification: is this a scam call, yes or no? AEGIS models the *epistemic dynamics* of the conversation — tracking how the caller is attempting to reshape the victim's belief structure in real time.

We draw on Robert Cialdini's six principles of persuasion (Authority, Scarcity, Reciprocation, Social Proof, Commitment/Consistency, Liking) and extend them into a computational epistemic framework specifically designed for fraud detection.

### The Six Epistemic Manipulation Vectors AEGIS Tracks

**1. Belief Installation**
The caller introduces false premises as established facts. "Your account has been compromised." "Your grandson has been arrested." "You owe back taxes." AEGIS tracks when unverified claims are presented as assumed knowledge.

**2. Verification Suppression**
The caller actively discourages the victim from checking claims independently. "Don't call your bank — their lines are compromised too." "Don't hang up or the warrant will be executed." "This is confidential — you can't discuss this with anyone." AEGIS flags any attempt to prevent independent verification.

**3. Urgency Fabrication**
Artificial time pressure designed to bypass deliberative reasoning. "You must act within the next 30 minutes." "The police are on their way." "This offer expires today." AEGIS measures the urgency escalation curve across the conversation.

**4. Authority Hijacking**
False claims of institutional power. "I'm calling from the IRS." "This is Microsoft Security." "I'm a federal agent." AEGIS cross-references authority claims against known patterns (e.g., the IRS never initiates contact by phone).

**5. Emotional Flooding**
Deliberate emotional manipulation to overwhelm rational processing — fear, guilt, excitement, romantic attachment. AEGIS tracks emotional intensity spikes and correlates them with extraction attempts.

**6. Exit Path Closure**
Systematic elimination of the victim's options for disengagement. "If you hang up, there will be consequences." "You've already started this process and you can't stop it." "You agreed to this, so you're committed." AEGIS detects when the caller is closing off the victim's ability to disengage.

### The Epistemic State Dashboard

Rather than a simple "scam/not scam" binary, AEGIS maintains a real-time **Epistemic Integrity Score** — a composite metric showing how much of the victim's rational decision-making capacity has been compromised during the conversation. The dashboard shows each manipulation vector with its current intensity, how they're interacting, and an overall risk assessment with plain-language explanations like:

> "The caller has made 3 unverifiable claims, discouraged you from contacting your bank, and is escalating time pressure. Your ability to independently verify what they're saying has been significantly restricted. Epistemic Integrity: 23/100. **Recommendation: End the call and independently verify all claims.**"

---

## 3. System Architecture

### High-Level Pipeline

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────────────┐
│  AUDIO INPUT │───▶│  TRANSCRIPTION  │───▶│  EPISTEMIC ANALYSIS  │
│  (Mic / Call) │    │  (Whisper.cpp)  │    │  (Gemma 4 E4B        │
│              │    │  Local, real-time│    │   Fine-tuned via     │
│              │    │                 │    │   Unsloth)           │
└──────────────┘    └─────────────────┘    └──────────┬───────────┘
                                                      │
                    ┌─────────────────┐    ┌──────────▼───────────┐
                    │  TOOL OUTPUTS   │◀───│  FUNCTION CALLING    │
                    │  (Verification  │    │  (Gemma 4 Native     │
                    │   results)      │    │   Tool Use)          │
                    └────────┬────────┘    └──────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  USER INTERFACE │
                    │  - Risk Score   │
                    │  - Manipulation │
                    │    vectors      │
                    │  - Plain-lang.  │
                    │    explanation  │
                    │  - Recommended  │
                    │    action       │
                    └─────────────────┘
```

### Component Breakdown

**Layer 1: Audio Capture & Transcription**
- **Tool:** Whisper.cpp (C++ port of OpenAI Whisper, runs locally)
- **Model:** `whisper-base.en` or `whisper-small.en` for English; `whisper-small` for multilingual
- **Why Whisper.cpp and not the Python Whisper:** Significantly lower latency, runs on CPU with acceptable speed, no Python overhead
- **Setup:** Captures system audio (the phone call) and streams chunks to Whisper for continuous transcription
- **Output:** Rolling text transcript with timestamps

**Layer 2: Epistemic Analysis Engine (Core)**
- **Model:** Gemma 4 E4B-it, fine-tuned via Unsloth on scam transcript data with epistemic manipulation annotations
- **Runtime:** Ollama (local inference, no data leaves the device)
- **Input:** Rolling transcript window (last ~2000 tokens of conversation)
- **Prompt Structure:** System prompt defines the six epistemic manipulation vectors, instructs the model to output structured JSON analysis
- **Output:** JSON object containing manipulation vector scores, identified tactics, epistemic integrity score, and plain-language explanation

**Layer 3: Function Calling / Verification Tools**
- **Leverages:** Gemma 4's native function-calling support
- **Tools Available:**
  - `verify_authority_claim(entity, claim)` — checks if institutions actually contact people this way (e.g., IRS never calls demanding immediate payment)
  - `check_known_scam_pattern(description)` — matches against FTC's reported scam patterns
  - `suggest_verification_action(claim)` — returns the correct way to verify a claim independently (e.g., "Call your bank's number from the back of your card, not any number the caller gives you")
  - `flag_financial_extraction(method)` — identifies high-risk payment methods (gift cards, cryptocurrency, wire transfers)

**Layer 4: User Interface**
- **Framework:** Gradio or Streamlit (Python-based, quick to build)
- **Layout:** Split-screen — live transcript on the left, epistemic analysis dashboard on the right
- **Dashboard Elements:**
  - Six manipulation vector gauges (0-100 each)
  - Overall Epistemic Integrity Score (100 = fully intact, 0 = fully compromised)
  - Timeline showing manipulation intensity over the call duration
  - Plain-language alert banner with recommended action
  - One-tap verification suggestions

---

## 4. Privacy & Security Architecture

> This is the first question judges will ask. AEGIS treats privacy as a core architectural constraint, not an afterthought.

### The Zero-Exfiltration Guarantee

**Every component runs locally. No data ever leaves the device.**

- **Audio processing:** Whisper.cpp runs entirely on-device. No cloud API calls.
- **Transcription storage:** Transcripts are held only in volatile memory (RAM). Nothing is written to disk unless the user explicitly chooses to save a report.
- **Model inference:** Gemma 4 runs via Ollama locally. No API keys, no cloud endpoints, no telemetry.
- **Function calling tools:** All verification tools use hardcoded local knowledge bases (e.g., "the IRS never calls demanding payment" is a local rule, not an API call). No external network requests during analysis.

### Privacy-by-Design Principles

**1. No Persistent Recording**
AEGIS does NOT record calls. It processes audio in a streaming buffer that is continuously overwritten. The transcript exists only as a rolling window in RAM. When the call ends, the data is gone.

**2. User-Controlled Data Lifecycle**
If a user wants to save a scam report (to file with the FTC, for example), they must explicitly press a "Save Report" button. The saved report contains only the analysis metadata — manipulation vectors detected, risk score, recommended actions. The raw transcript is NOT included in saved reports by default.

**3. No Model Training on User Data**
The fine-tuned model is trained before deployment on public datasets. It does not learn from user calls. There is no feedback loop that sends data anywhere.

**4. On-Device Isolation**
The application runs in a sandboxed process. It does not access contacts, messages, browsing history, or any other device data. It only accesses the microphone input during active monitoring.

### Addressing the "But What About..." Questions

| Concern | AEGIS Response |
|---|---|
| "Could someone misuse this to spy on calls?" | AEGIS has no storage, no export, no network transmission. It is architecturally incapable of surveillance. The analysis is ephemeral. |
| "What about legal wiretapping concerns?" | AEGIS is a local processing tool analogous to a hearing aid or real-time captioning. It processes audio locally for the user's own benefit. No recording occurs. Jurisdiction-specific consent laws apply to call recording, not to local audio processing. |
| "Could the model be tricked into ignoring a scam?" | Possible with adversarial inputs, but the model analyzes conversational dynamics, not just content. An adversary would need to change the *structure* of their manipulation, not just avoid keywords. |
| "What if it produces false positives on legitimate calls?" | The system provides a score and explanation, not a block. It never prevents communication — it only alerts. Users always make the final decision. |

---

## 5. Models & Technical Stack

### Primary Model: Gemma 4 E4B-it

- **HuggingFace:** `google/gemma-4-E4B-it`
- **Link:** https://huggingface.co/google/gemma-4-E4B-it
- **Why E4B over E2B:** E4B has ~4.3B effective parameters vs E2B's ~2.3B. The additional capacity is meaningful for nuanced epistemic reasoning. E4B supports native audio, image, and text multimodality. E4B fits comfortably on your RTX 3060 (8GB VRAM) at Q4 quantization (~3.5GB VRAM).
- **Why not 26B/31B:** Would not run on your demo hardware. Also, demonstrating that sophisticated epistemic reasoning works on an edge-deployable model is itself technically impressive and aligned with the competition's emphasis on accessible AI.
- **Context Window:** 128K tokens (more than sufficient for any phone call)
- **Key Feature Used:** Native function calling support for the verification tool layer

### Fine-Tuning Framework: Unsloth

- **Documentation:** https://unsloth.ai/docs/models/gemma-4/train
- **GGUF exports:** https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF
- **Why Unsloth:** 2x faster training, up to 70% less VRAM than standard HuggingFace training. E4B QLoRA fine-tuning works on free Colab T4 — your A100 is more than enough. Direct GGUF export for Ollama deployment.
- **Kaggle notebook reference:** https://www.kaggle.com/code/gpreda/fine-tune-gemma-4-e2b-with-unsloth

### Local Inference: Ollama

- **Website:** https://ollama.com
- **Installation:** `curl -fsSL https://ollama.com/install.sh | sh` (Linux) or download .exe (Windows)
- **Run command:** `ollama run gemma4:e4b`
- **VRAM on your RTX 3060:** E4B at Q4_K_M uses ~3.5GB. Leaves plenty of headroom.
- **API endpoint:** `http://localhost:11434` — your Gradio/Streamlit app calls this

### Audio Transcription: Whisper.cpp

- **GitHub:** https://github.com/ggerganov/whisper.cpp
- **Model:** `ggml-base.en.bin` (~148MB) for English-only, or `ggml-small.bin` (~488MB) for multilingual
- **Real-time streaming:** Use the `stream` example in whisper.cpp for continuous mic capture
- **Alternative:** `faster-whisper` Python library (https://github.com/SYSTRAN/faster-whisper) if you prefer Python integration

### UI Framework

- **Option A — Gradio:** `pip install gradio` — fastest to prototype, built-in audio input widgets, easy to make look polished for demo video
- **Option B — Streamlit:** `pip install streamlit` — better for dashboard-style layouts with multiple updating panels
- **Recommendation:** Gradio for speed. You can build a working demo UI in 2-3 hours.

---

## 6. Datasets

### Primary Training Datasets

**1. Scam Call Transcripts (Kaggle)**

| Dataset | Link | Description |
|---|---|---|
| Scam and Non-Scam Call Conversations | https://www.kaggle.com/datasets/teeconnie/scam-and-non-scam-call-conversation-dataset | Labeled multi-turn dialogues of scam vs legitimate calls |
| Call Transcripts Scam Determinations | https://www.kaggle.com/datasets/mealss/call-transcripts-scam-determinations | Call transcripts with scam/not-scam labels |
| Augmented Scam Call Transcripts | https://www.kaggle.com/datasets/yingzisilver/augmented-scam-call-transcript | Expanded scam transcript dataset |
| YouTube Scam Phone Call Transcripts | https://www.kaggle.com/datasets/rivalcults/youtube-scam-phone-call-transcripts | Transcripts from scam-baiting YouTube channels (Kitboga, ScammerPayback, etc.) |
| Scam Dataset | https://www.kaggle.com/datasets/divanshu22/scam-dataset | General scam communication dataset |

**2. Multi-Turn Scam Dialogues (HuggingFace)**

| Dataset | Link | Description |
|---|---|---|
| Multi-Agent Scam Conversation | https://huggingface.co/datasets/BothBosu/multi-agent-scam-conversation | Synthetic multi-turn scam/non-scam dialogues with varied receiver personalities. Includes SSN scams, refund scams, tech support scams. |
| Scam Dialogue | https://huggingface.co/datasets/BothBosu/scam-dialogue | Labeled scam dialogues for classification |
| Spam Messages (SMS/Email) | https://huggingface.co/datasets/mshenoda/spam-messages | Merged dataset from SMS Spam Collection, Telegram Spam, Enron Spam |

**3. Government / Institutional Data**

| Source | Link | Description |
|---|---|---|
| FTC Consumer Sentinel Network Data | https://www.ftc.gov/news-events/data-visualizations | Annual fraud report data — complaint narratives, scam types, contact methods, demographics |
| FTC Sentinel Data Book 2024 (PDF) | https://www.ftc.gov/reports/consumer-sentinel-network-data-book-2024 | Comprehensive annual fraud statistics |
| FTC Data Sets (DNC complaints) | https://www.ftc.gov/policy-notices/open-government/data-sets | Do Not Call complaint data with call metadata |
| FCC Consumer Complaints | https://www.fcc.gov/consumer-complaints-center-data | Weekly updated complaint data including unwanted calls |
| CFPB Consumer Complaint Database | https://www.consumerfinance.gov/data-research/consumer-complaints/ | Financial fraud complaints with consumer narratives — downloadable as CSV/JSON |

**4. Academic / Research Datasets**

| Paper / Source | Link | Relevance |
|---|---|---|
| "Analysis of scam baiting calls" (Wood et al., Macquarie University) | https://arxiv.org/pdf/2307.01965 | Methodology for analyzing scam call stages and scripts. Identifies social engineering techniques and scripted progressions. Directly applicable to our epistemic vector framework. |
| "Persuasion and Phishing" (Khadka, U. of Canberra) | https://arxiv.org/pdf/2412.18485 | Maps Cialdini's persuasion principles to phishing attacks. Provides the theoretical grounding for our manipulation vector taxonomy. |
| SEADer++ (Social Engineering Attack Detection) | https://www.tandfonline.com/doi/full/10.1080/24751839.2020.1747001 | NLP-based social engineering detection using Cialdini's principles. Prior art we extend with epistemic modeling. |
| SemEval 2024 Task 4 — Persuasion Detection | https://propaganda.math.unipd.it/semeval2024task4/ | Shared task on detecting persuasion techniques in memes and text. Provides annotation schemas we can adapt. |

### Data Preparation Pipeline

**Step 1:** Merge all transcript datasets into a unified format:
```json
{
  "conversation_id": "unique_id",
  "turns": [
    {"speaker": "caller", "text": "..."},
    {"speaker": "receiver", "text": "..."}
  ],
  "label": "scam" | "legitimate",
  "scam_type": "tech_support" | "irs" | "romance" | "investment" | ...
}
```

**Step 2:** Annotate with epistemic manipulation vectors. For each scam conversation, use Gemma 4 31B (via Google AI Studio, free) to pre-annotate which of the six vectors are present in each caller turn. Then human-review a sample for quality.

**Step 3:** Convert to Unsloth training format (Alpaca-style):
```json
{
  "instruction": "Analyze the following phone conversation for epistemic manipulation tactics. For each caller turn, identify which manipulation vectors are active and provide an overall Epistemic Integrity Score.",
  "input": "[conversation transcript]",
  "output": "[structured JSON analysis with vector scores, explanations, and overall score]"
}
```

**Target:** 500-1000 annotated conversations. With the datasets above combined, you have more than enough raw material.

---

## 7. Fine-Tuning Procedure

### Environment: Google Colab A100

```python
# Install Unsloth
!pip install unsloth

# Load model
from unsloth import FastModel
import torch

model, tokenizer = FastModel.from_pretrained(
    model_name="unsloth/gemma-4-E4B-it",
    dtype=None,                    # Auto-detect
    max_seq_length=4096,           # Sufficient for phone call windows
    load_in_4bit=True,             # QLoRA
    full_finetuning=False,
)

# Apply LoRA adapters
model = FastModel.get_peft_model(
    model,
    r=16,                          # LoRA rank
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)
```

### Training Configuration

```python
from trl import SFTTrainer, SFTConfig

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=SFTConfig(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        output_dir="outputs",
        optim="adamw_8bit",
        seed=3407,
    ),
)

trainer.train()
```

### Export to GGUF for Ollama

```python
# Save as GGUF for local deployment
model.save_pretrained_gguf(
    "aegis-gemma4-e4b",
    tokenizer,
    quantization_method="q4_k_m"  # Best balance for 8GB VRAM
)
```

### Import into Ollama

```bash
# Create Modelfile
cat > Modelfile << 'EOF'
FROM ./aegis-gemma4-e4b-Q4_K_M.gguf

SYSTEM """You are AEGIS, an epistemic manipulation detection system.
Analyze conversations for six manipulation vectors:
1. Belief Installation 2. Verification Suppression
3. Urgency Fabrication 4. Authority Hijacking
5. Emotional Flooding 6. Exit Path Closure
Output structured JSON with vector scores (0-100),
identified tactics, overall Epistemic Integrity Score,
and a plain-language explanation for the user."""

PARAMETER temperature 0.3
PARAMETER top_p 0.9
EOF

# Create the model in Ollama
ollama create aegis -f Modelfile

# Run it
ollama run aegis
```

---

## 8. Hardware Requirements & Demo Setup

### Your Hardware

| Component | Spec | Role |
|---|---|---|
| GPU 1 (Cloud) | Google Colab A100 (40GB) | Fine-tuning via Unsloth. More than sufficient for E4B QLoRA. |
| GPU 2 (Local) | RTX 3060 8GB VRAM | Running the fine-tuned model via Ollama for the demo. E4B Q4_K_M needs ~3.5GB VRAM — fits comfortably with room to spare. |
| CPU | Any modern CPU | Whisper.cpp transcription runs on CPU. The `base.en` model transcribes in real time on most CPUs. |
| RAM | 16GB recommended | OS + Ollama + Whisper.cpp + Gradio UI running simultaneously |
| Storage | ~10GB free | Model weights (~3GB), Whisper model (~150MB), application code, datasets |

### Demo Recording Setup

1. Run Ollama with your fine-tuned AEGIS model on the laptop
2. Run Whisper.cpp in streaming mode capturing system audio
3. Run the Gradio UI showing the live dashboard
4. Play a pre-recorded scam call scenario through the speakers (or use a second device)
5. Screen record the entire session using OBS Studio (free)
6. The video captures: transcript appearing in real time on the left, epistemic analysis updating on the right, risk score climbing as manipulation intensifies, alert triggering when score crosses the danger threshold

---

## 9. Function Calling Implementation

Gemma 4 has native function-calling support. Here's how the verification tools work:

```python
tools = [
    {
        "name": "verify_authority_claim",
        "description": "Check if an organization actually contacts people in the way the caller claims.",
        "parameters": {
            "type": "object",
            "properties": {
                "organization": {
                    "type": "string",
                    "description": "The organization the caller claims to represent"
                },
                "contact_method": {
                    "type": "string",
                    "description": "How the caller says they're reaching out"
                }
            }
        }
    },
    {
        "name": "check_payment_risk",
        "description": "Assess the risk level of a requested payment method.",
        "parameters": {
            "type": "object",
            "properties": {
                "payment_method": {
                    "type": "string",
                    "description": "The payment method requested (gift card, wire, crypto, etc.)"
                }
            }
        }
    },
    {
        "name": "suggest_verification",
        "description": "Provide the user with a safe way to independently verify a claim.",
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The specific claim that should be verified"
                }
            }
        }
    }
]

# Example local knowledge base (no network calls)
AUTHORITY_RULES = {
    "irs": "The IRS never initiates contact by phone, text, or email to demand immediate payment. They always send written notices by mail first.",
    "social_security": "The Social Security Administration will never call to threaten your benefits or demand payment.",
    "microsoft": "Microsoft does not make unsolicited calls about computer viruses or security issues.",
    "amazon": "Amazon does not call about suspicious orders or account problems.",
    "bank": "Your bank will never ask for your full password, PIN, or ask you to transfer money to a 'safe account'.",
}

PAYMENT_RISK = {
    "gift_card": {"risk": "CRITICAL", "reason": "Gift cards are untraceable. No legitimate organization accepts gift cards as payment."},
    "wire_transfer": {"risk": "CRITICAL", "reason": "Wire transfers are nearly impossible to reverse once sent."},
    "cryptocurrency": {"risk": "CRITICAL", "reason": "Cryptocurrency payments are irreversible and untraceable."},
    "zelle": {"risk": "HIGH", "reason": "Zelle transfers are instant and difficult to reverse."},
    "credit_card": {"risk": "LOW", "reason": "Credit cards have fraud protections and chargeback options."},
}
```

---

## 10. Evaluation Strategy

### Quantitative Metrics

- **Scam Detection Accuracy:** Precision, recall, and F1 on held-out scam/non-scam conversations
- **Manipulation Vector Accuracy:** Per-vector precision against human annotations
- **Latency:** Time from utterance to analysis output (target: <3 seconds)
- **False Positive Rate:** Critical metric — too many false alarms on legitimate calls destroys trust

### Qualitative Evaluation

- **Explainability:** Are the plain-language explanations actually helpful and accurate?
- **Actionability:** Do the recommended actions make sense for the detected threat?
- **Emotional Calibration:** Are alerts appropriately urgent without being alarmist?

### Benchmarks to Report

Run the fine-tuned model against the base Gemma 4 E4B-it (no fine-tuning) on the same test set to demonstrate the value of domain-specific fine-tuning. Report the delta on all metrics.

---

## 11. Team Task Breakdown (2-Day Sprint)

### Day 1

| Task | Owner | Hours | Deliverable |
|---|---|---|---|
| Download and merge all datasets (Kaggle + HuggingFace) | Data Team (2-3 people) | 3h | Unified conversation dataset in JSON |
| Annotate ~500 conversations with epistemic vectors (use GPT-4 / Claude for pre-annotation, human review sample) | Data Team | 5h | Training dataset with vector labels |
| Set up Unsloth on Colab A100, run initial fine-tuning | ML Team (2-3 people) | 4h | First checkpoint of AEGIS model |
| Build Gradio UI with mock data — layout, dashboard, all visual elements | Frontend Team (2 people) | 6h | Working UI with placeholder data |
| Set up Whisper.cpp streaming on laptop, verify real-time transcription works | Infra Team (1-2 people) | 3h | Working audio-to-text pipeline |
| Implement function calling tools (authority verification, payment risk, etc.) | Backend Team (1-2 people) | 3h | Working tool functions |

### Day 2

| Task | Owner | Hours | Deliverable |
|---|---|---|---|
| Iterate on fine-tuning (adjust data, hyperparameters) based on Day 1 results | ML Team | 4h | Final AEGIS model |
| Export to GGUF, load into Ollama on laptop, verify inference | ML Team + Infra | 2h | Model running locally |
| Connect all components: Whisper → AEGIS → Tools → UI | Full Backend Team | 4h | End-to-end working pipeline |
| Record demo video — set up scenarios, record screen, add narration | Video Team (2-3 people) | 5h | Raw demo footage |
| Edit demo video — add intro, transitions, captions, music | Video Team | 3h | Final 3-5 min video |
| Write submission writeup — problem, approach, architecture, results | Writer (1-2 people) | 4h | Submission text |
| Prepare code repository — clean, document, README | All | 2h | GitHub repo ready |

---

## 12. Video Script Outline

**[0:00-0:30] The Hook**
Open with a statistic: "$12.5 billion lost to fraud in 2024. One phone call at a time." Show a montage of news headlines about scam victims. End with: "What if your phone could think for you — before you lose everything?"

**[0:30-1:30] The Problem**
Show a simulated scam call in progress. An elderly woman receives a call from "the IRS." Walk through how the scammer systematically disables her judgment — manufacturing urgency, invoking authority, preventing her from hanging up to verify. Narrate the epistemic manipulation in real time: "Watch what's really happening. This isn't just a lie. It's a systematic attack on her ability to think clearly."

**[1:30-3:00] The Solution — AEGIS in Action**
Replay the same call, but now with AEGIS running. Show the split-screen dashboard. The transcript appears on the left. On the right, the manipulation vectors light up in real time. The epistemic integrity score drops as the scammer escalates. At 35/100, AEGIS surfaces an alert: "This caller claims to be from the IRS, but the IRS never initiates contact by phone. They are using urgency tactics to prevent you from verifying their claims. Consider ending this call and calling the IRS directly at their official number."

**[3:00-4:00] The Technology**
Brief walkthrough of the architecture. Emphasize: runs entirely on-device, no data leaves the phone, powered by Gemma 4's native function calling and multimodal capabilities, fine-tuned with Unsloth, deployed via Ollama. Show the model running on a laptop with an RTX 3060 — proving this works on consumer hardware.

**[4:00-4:30] The Vision**
"AEGIS isn't just a scam detector. It's the first AI system that models how your thinking is being attacked — not just what words are being said. It protects everyone — from grandparents to tech professionals — because manipulation tactics are universal, even when the scam changes."

**[4:30-5:00] Call to Action**
"In a world where AI can be used to deceive, AEGIS uses AI to defend the one thing that matters most — your ability to think for yourself."

---

## 13. Submission Checklist

- [ ] Fine-tuned Gemma 4 E4B model weights published on HuggingFace
- [ ] Training code and data preparation pipeline on GitHub
- [ ] Application source code (Gradio UI + Whisper pipeline + function calling tools) on GitHub
- [ ] Comprehensive README with setup instructions
- [ ] Benchmarks: base model vs fine-tuned model performance comparison
- [ ] Demo video (3-5 minutes)
- [ ] Written submission on Kaggle describing problem, approach, architecture, and results
- [ ] Model card documenting training data, intended use, limitations, and ethical considerations

---

## 14. Key Links Reference

| Resource | URL |
|---|---|
| **Gemma 4 E4B-it (Base Model)** | https://huggingface.co/google/gemma-4-E4B-it |
| **Gemma 4 E4B GGUF (Unsloth)** | https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF |
| **Gemma 4 E2B-it (Smaller Alternative)** | https://huggingface.co/google/gemma-4-E2B-it |
| **Unsloth Fine-Tuning Docs** | https://unsloth.ai/docs/models/gemma-4/train |
| **Unsloth GitHub** | https://github.com/unslothai/unsloth |
| **Ollama** | https://ollama.com |
| **Whisper.cpp** | https://github.com/ggerganov/whisper.cpp |
| **Faster-Whisper** | https://github.com/SYSTRAN/faster-whisper |
| **Gradio** | https://www.gradio.app |
| **Streamlit** | https://streamlit.io |
| **Kaggle Fine-Tune Notebook** | https://www.kaggle.com/code/gpreda/fine-tune-gemma-4-e2b-with-unsloth |
| **FTC Data Visualizations** | https://www.ftc.gov/news-events/data-visualizations |
| **FTC Sentinel Data Book 2024** | https://www.ftc.gov/reports/consumer-sentinel-network-data-book-2024 |
| **CFPB Complaint Database** | https://www.consumerfinance.gov/data-research/consumer-complaints/ |
| **OBS Studio (Screen Recording)** | https://obsproject.com |
| **Competition Page** | https://kaggle.com/competitions/gemma-4-good-hackathon |

---

## 15. Why AEGIS Wins

**Impact & Vision (40 pts):** $12.5B/year problem affecting every demographic. Our epistemic framing elevates this from "another scam detector" to a novel contribution to AI safety — we're modeling how human rationality is attacked, not just what words are used.

**Video Pitch & Storytelling (30 pts):** The before/after structure (scam call without AEGIS vs with AEGIS) is cinematically compelling. The real-time dashboard with manipulation vectors lighting up is visually dramatic. The elderly victim scenario is universally empathetic.

**Technical Depth & Execution (30 pts):** Fine-tuned Gemma 4 with Unsloth (special tech track eligibility), native function calling, on-device deployment via Ollama, real-time audio pipeline, novel epistemic analysis framework grounded in persuasion research literature. This isn't a wrapper around an API — it's a genuinely engineered system.

**Multi-Track Eligibility:** Main Track + Safety & Trust Impact + Ollama Special Technology. Three shots at prizes from a single, cohesive project.

---

*AEGIS: Because the most dangerous attack isn't the one you can see — it's the one that changes how you see.*
