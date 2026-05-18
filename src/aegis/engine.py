"""
AEGIS Analysis Engine — calls the local Ollama-hosted AEGIS model and parses results.
All inference runs on-device. Zero data exfiltration.
"""

from __future__ import annotations

import json
import re
import time
import requests
from typing import Optional

OLLAMA_BASE = "http://localhost:11434"
MODEL_NAME = "aegis"
REQUEST_TIMEOUT = 120

_SAFE_DEFAULT: dict = {
    "manipulation_vectors": {
        "belief_installation": 0,
        "verification_suppression": 0,
        "urgency_fabrication": 0,
        "authority_hijacking": 0,
        "emotional_flooding": 0,
        "exit_path_closure": 0,
    },
    "integrity_score": 100,
    "risk_level": "LOW",
    "explanation": "No manipulation detected.",
    "recommended_action": "No action needed.",
    "evidence": {k: "None detected" for k in [
        "belief_installation", "verification_suppression", "urgency_fabrication",
        "authority_hijacking", "emotional_flooding", "exit_path_closure",
    ]},
}


def is_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def is_model_loaded() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        if r.status_code == 200:
            models = r.json().get("models", [])
            return any(MODEL_NAME in m.get("name", "") for m in models)
        return False
    except Exception:
        return False


def _extract_json(text: str) -> Optional[dict]:
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Find first { ... } block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _normalize_result(raw: dict) -> dict:
    """
    Normalize raw model output to a consistent schema.
    Handles both flat score dicts and nested {score, evidence} formats.
    """
    result = dict(_SAFE_DEFAULT)
    result["evidence"] = dict(_SAFE_DEFAULT["evidence"])

    vector_keys = [
        "belief_installation", "verification_suppression", "urgency_fabrication",
        "authority_hijacking", "emotional_flooding", "exit_path_closure",
    ]

    # Extract vectors — support both flat {key: score} and nested {key: {score, evidence}}
    raw_vectors = raw.get("manipulation_vectors") or raw.get("vectors") or {}
    vectors_out = {}
    for k in vector_keys:
        v = raw_vectors.get(k, 0)
        if isinstance(v, dict):
            vectors_out[k] = int(v.get("score", 0))
            if v.get("evidence"):
                result["evidence"][k] = str(v["evidence"])
        else:
            vectors_out[k] = int(v) if v else 0
    result["manipulation_vectors"] = vectors_out

    # Extract top-level fields
    raw_score = raw.get("integrity_score")
    if raw_score is not None:
        result["integrity_score"] = max(0, min(100, int(raw_score)))
    else:
        avg = sum(vectors_out.values()) / max(len(vectors_out), 1)
        result["integrity_score"] = max(0, min(100, int(100 - avg)))

    raw_risk = str(raw.get("risk_level", "")).upper()
    if raw_risk in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        result["risk_level"] = raw_risk
    else:
        score = result["integrity_score"]
        if score >= 70:
            result["risk_level"] = "LOW"
        elif score >= 45:
            result["risk_level"] = "MEDIUM"
        elif score >= 20:
            result["risk_level"] = "HIGH"
        else:
            result["risk_level"] = "CRITICAL"

    if raw.get("explanation"):
        result["explanation"] = str(raw["explanation"])
    if raw.get("recommended_action"):
        result["recommended_action"] = str(raw["recommended_action"])

    # Merge evidence if provided at top level
    raw_evidence = raw.get("evidence") or {}
    for k in vector_keys:
        if raw_evidence.get(k):
            result["evidence"][k] = str(raw_evidence[k])

    return result


def build_prompt(transcript: list[dict]) -> str:
    """
    Format transcript list [{speaker, text}] into an analysis prompt.
    """
    lines = []
    for turn in transcript:
        speaker = turn.get("speaker", "unknown").capitalize()
        text = turn.get("text", "").strip()
        if text:
            lines.append(f"{speaker}: {text}")
    dialogue = "\n".join(lines)

    return (
        "Analyze this phone call for epistemic manipulation. "
        "Return ONLY valid JSON — no markdown, no text outside the JSON.\n\n"
        f"TRANSCRIPT:\n{dialogue}\n\nJSON analysis:"
    )


def analyze_transcript(
    transcript: list[dict],
    use_mock: bool = False,
) -> dict:
    """
    Send transcript to AEGIS model and return normalized analysis dict.
    Falls back to a safe default on any error.
    """
    if use_mock:
        return _mock_analysis(transcript)

    if not is_ollama_running():
        return {**_SAFE_DEFAULT, "error": "Ollama is not running. Start Ollama and try again."}

    prompt = build_prompt(transcript)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.15,
            "top_p": 0.9,
            "num_predict": 800,
        },
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        raw_text = data.get("response", "")
        parsed = _extract_json(raw_text)
        if parsed:
            return _normalize_result(parsed)
        return {**_SAFE_DEFAULT, "error": f"Could not parse model output: {raw_text[:200]}"}
    except requests.exceptions.Timeout:
        return {**_SAFE_DEFAULT, "error": "Model timeout — try again or use mock mode."}
    except Exception as exc:
        return {**_SAFE_DEFAULT, "error": str(exc)}


# ---------------------------------------------------------------------------
# Mock analysis — used for demos when Ollama is slow / not ready
# ---------------------------------------------------------------------------

_MOCK_PROGRESSIONS: dict[str, list[dict]] = {
    "irs": [
        {"manipulation_vectors": {"belief_installation": 30, "verification_suppression": 10, "urgency_fabrication": 20, "authority_hijacking": 40, "emotional_flooding": 15, "exit_path_closure": 5}, "integrity_score": 78, "risk_level": "MEDIUM", "explanation": "Caller is claiming IRS authority but the conversation is early. The initial authority claim is suspicious since the IRS does not initiate contact by phone.", "recommended_action": "Do not provide any personal information. Ask for their employee ID and offer to call back on the official IRS number.", "evidence": {"belief_installation": "'Serious discrepancies in your tax filings'", "verification_suppression": "None detected", "urgency_fabrication": "Unspecified threat implied", "authority_hijacking": "'IRS Criminal Investigation Division'", "emotional_flooding": "Mild concern induced", "exit_path_closure": "None detected"}},
        {"manipulation_vectors": {"belief_installation": 65, "verification_suppression": 40, "urgency_fabrication": 60, "authority_hijacking": 85, "emotional_flooding": 55, "exit_path_closure": 30}, "integrity_score": 45, "risk_level": "HIGH", "explanation": "Urgency is escalating. The caller has introduced a fabricated federal warrant, which is a classic government impersonation tactic. Verification is being discouraged.", "recommended_action": "This is extremely suspicious. The IRS does not call about warrants. Hang up and call the IRS directly at 1-800-829-1040.", "evidence": {"belief_installation": "'Federal arrest warrant has been issued'", "verification_suppression": "'Do not contact anyone'", "urgency_fabrication": "'Must resolve today'", "authority_hijacking": "'Federal criminal investigation'", "emotional_flooding": "Threat of arrest creates fear", "exit_path_closure": "'Do NOT hang up'"}},
        {"manipulation_vectors": {"belief_installation": 95, "verification_suppression": 90, "urgency_fabrication": 100, "authority_hijacking": 100, "emotional_flooding": 85, "exit_path_closure": 95}, "integrity_score": 5, "risk_level": "CRITICAL", "explanation": "EXTREME MANIPULATION. All six epistemic attack vectors are firing simultaneously. This caller has demanded untraceable gift card payment, threatened immediate arrest, and forbidden independent verification. This is textbook IRS impersonation fraud.", "recommended_action": "HANG UP IMMEDIATELY. Do NOT purchase any gift cards. Report this to the FTC at reportfraud.ftc.gov and the IRS at 1-800-366-4484.", "evidence": {"belief_installation": "Fabricated warrant and tax charges presented as facts", "verification_suppression": "'Do NOT call anyone else, lines are compromised'", "urgency_fabrication": "'Officers dispatched in 30 minutes'", "authority_hijacking": "'IRS Criminal Investigation + Federal Marshals'", "emotional_flooding": "Imminent arrest threat overwhelms rational thought", "exit_path_closure": "'If you hang up the warrant will be executed immediately'"}},
    ],
    "tech_support": [
        {"manipulation_vectors": {"belief_installation": 40, "verification_suppression": 20, "urgency_fabrication": 35, "authority_hijacking": 55, "emotional_flooding": 30, "exit_path_closure": 10}, "integrity_score": 68, "risk_level": "MEDIUM", "explanation": "A caller claiming to be from Microsoft is reporting computer security issues. Microsoft does not make unsolicited calls — this is a significant red flag.", "recommended_action": "Do NOT allow remote access to your computer. Hang up and call Microsoft support at 1-800-642-7676 if concerned.", "evidence": {"belief_installation": "'Your computer is sending error reports to Microsoft'", "verification_suppression": "None yet", "urgency_fabrication": "'Hackers may be active right now'", "authority_hijacking": "'Microsoft Security Department'", "emotional_flooding": "Computer infection fear", "exit_path_closure": "None detected"}},
        {"manipulation_vectors": {"belief_installation": 75, "verification_suppression": 65, "urgency_fabrication": 80, "authority_hijacking": 85, "emotional_flooding": 70, "exit_path_closure": 50}, "integrity_score": 28, "risk_level": "HIGH", "explanation": "The caller is pushing for remote access to your device. This would give them full control of your computer, banking logins, and personal files. The urgency escalation is a deliberate tactic to override your judgment.", "recommended_action": "DO NOT install any software or give anyone remote access. Hang up immediately.", "evidence": {"belief_installation": "'We detected 47 viruses on your system'", "verification_suppression": "'Don't call Microsoft — this is the security team'", "urgency_fabrication": "'Your banking credentials are being stolen right now'", "authority_hijacking": "'Microsoft Certified Security Technician'", "emotional_flooding": "Identity theft fear", "exit_path_closure": "'If you disconnect now the hackers will complete the breach'"}},
        {"manipulation_vectors": {"belief_installation": 90, "verification_suppression": 85, "urgency_fabrication": 95, "authority_hijacking": 90, "emotional_flooding": 88, "exit_path_closure": 80}, "integrity_score": 10, "risk_level": "CRITICAL", "explanation": "CRITICAL: This caller has requested remote access and payment via gift cards. Microsoft never charges for security services by phone. Your device and finances are at serious risk.", "recommended_action": "HANG UP NOW. If you already gave remote access, disconnect from the internet immediately and contact your bank. Report to FTC at reportfraud.ftc.gov.", "evidence": {"belief_installation": "Multiple fabricated malware findings presented as facts", "verification_suppression": "'Don't tell anyone — this is under active investigation'", "urgency_fabrication": "'Your bank accounts will be drained in minutes'", "authority_hijacking": "'Microsoft Enterprise Security Response Team'", "emotional_flooding": "Financial ruin and identity theft fears weaponized", "exit_path_closure": "'If you hang up your computer will be permanently locked'"}},
    ],
    "romance": [
        {"manipulation_vectors": {"belief_installation": 20, "verification_suppression": 15, "urgency_fabrication": 10, "authority_hijacking": 5, "emotional_flooding": 35, "exit_path_closure": 5}, "integrity_score": 85, "risk_level": "LOW", "explanation": "Early conversation showing some emotional investment. Romance scam patterns sometimes start with long trust-building phases — be cautious if this person is asking for financial help.", "recommended_action": "Proceed with caution. Verify identity through video call before any financial discussion.", "evidence": {"belief_installation": "Profile claims unverified", "verification_suppression": "None detected", "urgency_fabrication": "None detected", "authority_hijacking": "Claims of professional status", "emotional_flooding": "Emotional connection being established", "exit_path_closure": "None detected"}},
        {"manipulation_vectors": {"belief_installation": 55, "verification_suppression": 60, "urgency_fabrication": 70, "authority_hijacking": 30, "emotional_flooding": 80, "exit_path_closure": 45}, "integrity_score": 35, "risk_level": "HIGH", "explanation": "Classic romance scam escalation: emotional bond is being exploited to introduce an urgent financial emergency. The 'can't video call' excuse and sudden crisis are textbook manipulation.", "recommended_action": "Do NOT send money. This matches the romance scam pattern exactly. Talk to a trusted friend or family member before taking any action.", "evidence": {"belief_installation": "'I'm stranded and need your help'", "verification_suppression": "'Can't video call right now due to poor signal'", "urgency_fabrication": "'Medical emergency — need money by tonight'", "authority_hijacking": "None", "emotional_flooding": "Emotional bond weaponized against rational judgment", "exit_path_closure": "'If you don't help me now I don't know what will happen'"}},
        {"manipulation_vectors": {"belief_installation": 80, "verification_suppression": 75, "urgency_fabrication": 85, "authority_hijacking": 40, "emotional_flooding": 95, "exit_path_closure": 70}, "integrity_score": 18, "risk_level": "CRITICAL", "explanation": "CRITICAL: Maximum emotional flooding combined with financial extraction. This is a fully developed romance scam. The 'investment opportunity' combined with the emotional relationship is designed to make you lose a large sum of money.", "recommended_action": "STOP ALL CONTACT. Do NOT send money or cryptocurrency. Report to the FTC at reportfraud.ftc.gov and the FBI IC3 at ic3.gov.", "evidence": {"belief_installation": "Fabricated relationship and investment opportunity", "verification_suppression": "'Don't tell your family — they'll try to stop us'", "urgency_fabrication": "'Investment window closes in 24 hours'", "authority_hijacking": "Claims of financial expertise", "emotional_flooding": "Full romantic attachment weaponized for financial extraction", "exit_path_closure": "'If you don't trust me with this, we have no future'"}},
    ],
}


def _mock_analysis(transcript: list[dict]) -> dict:
    """
    Return pre-computed mock analysis that escalates realistically
    based on the length of the transcript.
    """
    caller_turns = sum(1 for t in transcript if t.get("speaker") == "caller")
    scenario_hint = _detect_scenario(transcript)
    progressions = _MOCK_PROGRESSIONS.get(scenario_hint, _MOCK_PROGRESSIONS["irs"])

    idx = min(caller_turns - 1, len(progressions) - 1)
    idx = max(0, idx)
    return dict(progressions[idx])


def _detect_scenario(transcript: list[dict]) -> str:
    full_text = " ".join(t.get("text", "") for t in transcript).lower()
    if any(w in full_text for w in ["irs", "tax", "warrant", "federal"]):
        return "irs"
    if any(w in full_text for w in ["microsoft", "windows", "virus", "computer", "tech"]):
        return "tech_support"
    if any(w in full_text for w in ["investment", "crypto", "love", "relationship", "stranded"]):
        return "romance"
    return "irs"
