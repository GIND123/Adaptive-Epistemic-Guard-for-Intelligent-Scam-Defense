"""
AEGIS — Flask backend
Run: python app.py  (opens http://localhost:5001)
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from src.aegis.engine import analyze_transcript, is_ollama_running, is_model_loaded
from src.aegis.scenarios import SCENARIOS, get_scenario
from src.aegis.tools import (
    verify_authority_claim,
    check_payment_risk,
    suggest_verification,
)

app = Flask(__name__)


# ── Status ────────────────────────────────────────────────────────────────────

@app.route("/api/status")
def api_status():
    ollama_ok = is_ollama_running()
    model_ok = is_model_loaded() if ollama_ok else False
    return jsonify({"ollama": ollama_ok, "model": model_ok})


# ── Scenarios ─────────────────────────────────────────────────────────────────

@app.route("/api/scenarios")
def api_scenarios():
    return jsonify([
        {
            "id": sid,
            "name": s["name"],
            "icon": s["icon"],
            "description": s["description"],
            "type": s["type"],
            "victim_profile": s["victim_profile"],
            "turn_count": len(s["turns"]),
        }
        for sid, s in SCENARIOS.items()
    ])


@app.route("/api/scenario/<scenario_id>")
def api_scenario(scenario_id):
    return jsonify(get_scenario(scenario_id))


# ── Analysis ──────────────────────────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True) or {}
    transcript = data.get("transcript", [])
    use_mock = data.get("use_mock", False)

    if not transcript:
        return jsonify({"error": "Empty transcript"}), 400

    result = analyze_transcript(transcript, use_mock=use_mock)
    tools = _run_tools(transcript)

    return jsonify({"analysis": result, "tools": tools})


# ── Transcription ─────────────────────────────────────────────────────────────

_whisper_model = None
_whisper_lock  = None


def _get_whisper():
    global _whisper_model, _whisper_lock
    import threading
    if _whisper_lock is None:
        _whisper_lock = threading.Lock()
    with _whisper_lock:
        if _whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                # base gives ~4–5× better accuracy than tiny at ~2s latency per 6s chunk on CPU
                _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            except Exception:
                return None
    return _whisper_model


def _preload_whisper():
    """Download + initialise Whisper in background so first real request is instant."""
    import threading
    threading.Thread(target=_get_whisper, daemon=True).start()


@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file", "text": ""}), 400

    model = _get_whisper()
    if model is None:
        return jsonify({"error": "Whisper not available", "text": ""}), 503

    audio_file = request.files["audio"]
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        segments, _ = model.transcribe(
            tmp_path,
            beam_size=5,                 # higher = better accuracy
            language="en",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
            condition_on_previous_text=False,
        )
        text = " ".join(seg.text.strip() for seg in segments)
        return jsonify({"text": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e), "text": ""}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _run_tools(transcript: list) -> list:
    results = []
    full_text = " ".join(t.get("text", "").lower() for t in transcript)

    for org in ["irs", "microsoft", "social security", "amazon", "apple", "bank", "fbi", "ftc"]:
        if org in full_text:
            tr = verify_authority_claim(org, "phone call")
            if tr.get("is_suspicious"):
                results.append({"type": "authority", "data": tr})
            break

    for pm in ["gift card", "wire transfer", "cryptocurrency", "bitcoin", "zelle", "venmo", "cash app"]:
        if pm in full_text:
            results.append({"type": "payment", "data": check_payment_risk(pm)})
            break

    for claim in ["arrest", "warrant", "police", "marshal"]:
        if claim in full_text:
            results.append({"type": "verification", "data": suggest_verification(claim)})
            break

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    _preload_whisper()   # start downloading/loading base model in background
    print(f"\n  AEGIS running at http://localhost:{port}\n")
    app.run(debug=False, port=port, host="0.0.0.0")
