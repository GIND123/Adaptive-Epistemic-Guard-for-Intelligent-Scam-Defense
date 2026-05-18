"""
AEGIS local knowledge base — all verification runs on-device with no network calls.
"""

from __future__ import annotations

AUTHORITY_RULES: dict[str, dict] = {
    "irs": {
        "full_name": "Internal Revenue Service",
        "fact": "The IRS never initiates contact by phone, text, or email to demand immediate payment. They always send written notices by USPS mail first. They will never threaten immediate arrest.",
        "safe_contact": "irs.gov or call 1-800-829-1040",
        "never_does": ["call demanding immediate payment", "threaten arrest over the phone", "demand gift card payment", "require wire transfers", "ask for cryptocurrency"],
    },
    "ssa": {
        "full_name": "Social Security Administration",
        "fact": "The SSA will never call to threaten suspension of your Social Security number or demand immediate payment to avoid arrest.",
        "safe_contact": "ssa.gov or call 1-800-772-1213",
        "never_does": ["suspend your SSN over the phone", "demand immediate payment", "threaten arrest", "ask for gift cards"],
    },
    "medicare": {
        "full_name": "Medicare",
        "fact": "Medicare will never call you unexpectedly to sell you anything or ask for personal information unless you called them first.",
        "safe_contact": "medicare.gov or call 1-800-633-4227",
        "never_does": ["call unexpectedly asking for Medicare number", "offer free equipment in exchange for your Medicare number"],
    },
    "microsoft": {
        "full_name": "Microsoft",
        "fact": "Microsoft does not make unsolicited calls about your computer security or viruses. Windows error messages never include a phone number to call.",
        "safe_contact": "support.microsoft.com or call 1-800-642-7676",
        "never_does": ["call about virus alerts", "request remote access unsolicited", "ask for gift card payment for tech support"],
    },
    "apple": {
        "full_name": "Apple",
        "fact": "Apple will never call you about a compromised Apple ID or ask you to install remote access software. They communicate via email and the Settings app.",
        "safe_contact": "apple.com/support or call 1-800-275-2273",
        "never_does": ["call about account compromise unsolicited", "ask you to buy gift cards", "request remote access to your device"],
    },
    "amazon": {
        "full_name": "Amazon",
        "fact": "Amazon does not call about suspicious orders or account problems without you initiating contact first.",
        "safe_contact": "amazon.com/help or call 1-888-280-4331",
        "never_does": ["call about suspicious orders unprompted", "ask for gift card payment", "request remote access"],
    },
    "bank": {
        "full_name": "Your Bank",
        "fact": "Your bank will never ask for your full password, full PIN, or ask you to transfer money to a 'safe account'. If in doubt, hang up and call the number on the back of your card.",
        "safe_contact": "Call the number on the back of your card",
        "never_does": ["ask for your full password or PIN", "ask you to move money to a 'safe account'", "send someone to collect your bank card"],
    },
    "fbi": {
        "full_name": "Federal Bureau of Investigation",
        "fact": "The FBI does not call individuals demanding immediate payment to avoid arrest. They communicate through official channels and in-person visits.",
        "safe_contact": "fbi.gov or your local FBI field office",
        "never_does": ["call demanding payment to avoid arrest", "accept gift card payment", "conduct investigations over the phone"],
    },
    "ftc": {
        "full_name": "Federal Trade Commission",
        "fact": "The FTC does not call to collect money or threaten you with arrest. They investigate consumer complaints — they are not a law enforcement agency that makes arrests.",
        "safe_contact": "ftc.gov or 1-877-382-4357",
        "never_does": ["demand payment over the phone", "threaten arrest", "collect fines by phone"],
    },
    "utility": {
        "full_name": "Utility Company",
        "fact": "Legitimate utility companies send written notices before disconnection. They do not demand same-day payment in gift cards or cryptocurrency to avoid shutoff.",
        "safe_contact": "Call the number on your utility bill",
        "never_does": ["demand immediate gift card payment", "give 30-minute deadlines for payment", "send someone immediately if you don't pay now"],
    },
}

PAYMENT_RISK: dict[str, dict] = {
    "gift card": {
        "risk": "CRITICAL",
        "reason": "Gift cards are completely untraceable once redeemed. No legitimate business, government agency, or individual will ever ask you to pay with gift cards. This is the #1 scam payment method.",
        "examples": ["iTunes gift cards", "Google Play cards", "Amazon gift cards", "Steam cards", "Vanilla Visa prepaid cards"],
    },
    "wire transfer": {
        "risk": "CRITICAL",
        "reason": "Wire transfers are nearly impossible to reverse once sent. Scammers favor wire transfers because the money leaves your bank immediately and cannot be recalled.",
        "examples": ["Western Union", "MoneyGram", "bank wire", "SWIFT transfer"],
    },
    "cryptocurrency": {
        "risk": "CRITICAL",
        "reason": "Cryptocurrency payments are irreversible and completely anonymous. Once sent to a scammer's wallet, funds cannot be recovered.",
        "examples": ["Bitcoin", "Ethereum", "USDT", "crypto ATM"],
    },
    "zelle": {
        "risk": "HIGH",
        "reason": "Zelle transfers are instant and very difficult to reverse. Unlike credit cards, Zelle offers no fraud protection for authorized transfers.",
        "examples": ["Zelle bank transfer"],
    },
    "venmo": {
        "risk": "HIGH",
        "reason": "Venmo payments to unknown parties are difficult to reverse and offer limited fraud protection.",
        "examples": ["Venmo transfer"],
    },
    "cashapp": {
        "risk": "HIGH",
        "reason": "Cash App transfers are instant and very difficult to reverse. Cash App does not offer strong fraud protection.",
        "examples": ["Cash App", "$cashtag"],
    },
    "money order": {
        "risk": "HIGH",
        "reason": "Money orders are essentially cash — once sent they are very difficult to recover. Legitimate organizations rarely require payment by money order.",
        "examples": ["postal money order", "bank money order"],
    },
    "check": {
        "risk": "MEDIUM",
        "reason": "Personal checks expose your bank account and routing number. In some scams, you are sent a fake check and asked to wire back the difference.",
        "examples": ["personal check", "cashier's check", "certified check"],
    },
    "credit card": {
        "risk": "LOW",
        "reason": "Credit cards have robust fraud protection, chargeback options, and purchase protections. This is one of the safest payment methods.",
        "examples": ["Visa", "Mastercard", "American Express", "Discover"],
    },
    "debit card": {
        "risk": "MEDIUM",
        "reason": "Debit cards offer less fraud protection than credit cards. Disputes take longer and the money is drawn from your account immediately.",
        "examples": ["debit card", "bank card"],
    },
}

SCAM_PATTERNS: dict[str, dict] = {
    "irs_arrest": {
        "type": "Government Impersonation",
        "description": "Caller claims to be IRS, threatens arrest for unpaid taxes, demands immediate payment",
        "red_flags": ["IRS calling by phone", "threatened arrest", "gift card payment", "do not hang up"],
        "ftc_report": "reportfraud.ftc.gov",
    },
    "tech_support": {
        "type": "Tech Support Scam",
        "description": "Caller claims your computer is infected or compromised, asks for remote access and payment",
        "red_flags": ["computer virus warning", "remote access request", "Microsoft/Apple calling unprompted", "gift card payment"],
        "ftc_report": "reportfraud.ftc.gov",
    },
    "romance": {
        "type": "Romance Scam",
        "description": "Online relationship develops, person eventually asks for money for emergency or investment",
        "red_flags": ["never met in person", "requests money for emergency", "cryptocurrency investment opportunity", "can't video call"],
        "ftc_report": "reportfraud.ftc.gov",
    },
    "grandparent": {
        "type": "Grandparent/Family Emergency Scam",
        "description": "Caller claims to be grandchild or family member in legal trouble, needs immediate money bail",
        "red_flags": ["family member in trouble", "urgent bail money needed", "keep it secret", "send cash"],
        "ftc_report": "reportfraud.ftc.gov",
    },
    "lottery": {
        "type": "Lottery/Prize Scam",
        "description": "Caller claims you've won a prize but must pay taxes or fees first to collect",
        "red_flags": ["you've won", "pay fees first", "foreign lottery", "keep it confidential"],
        "ftc_report": "reportfraud.ftc.gov",
    },
    "investment": {
        "type": "Investment/Crypto Scam",
        "description": "Caller offers guaranteed returns on investment, often cryptocurrency",
        "red_flags": ["guaranteed returns", "crypto investment", "limited time offer", "insider information"],
        "ftc_report": "reportfraud.ftc.gov",
    },
    "utility_shutoff": {
        "type": "Utility Shutoff Scam",
        "description": "Caller claims utility will be shut off unless immediate payment is made today",
        "red_flags": ["service shutoff today", "immediate payment", "gift card accepted", "technician on the way"],
        "ftc_report": "reportfraud.ftc.gov",
    },
}


def verify_authority_claim(organization: str, contact_method: str) -> dict:
    """Check if an organization actually contacts people in the described way."""
    org_lower = organization.lower()
    matched_key = None
    for key in AUTHORITY_RULES:
        if key in org_lower or org_lower in key:
            matched_key = key
            break
    if matched_key is None:
        if any(w in org_lower for w in ["bank", "credit union", "financial"]):
            matched_key = "bank"
        elif any(w in org_lower for w in ["power", "electric", "gas", "water", "utility"]):
            matched_key = "utility"

    if matched_key:
        rule = AUTHORITY_RULES[matched_key]
        is_suspicious = any(
            forbidden.lower() in contact_method.lower()
            for forbidden in rule["never_does"]
        ) or "phone" in contact_method.lower()
        return {
            "organization": rule["full_name"],
            "verified_fact": rule["fact"],
            "safe_contact": rule["safe_contact"],
            "is_suspicious": is_suspicious,
            "warning": f"⚠ {rule['full_name']} never {rule['never_does'][0]}." if is_suspicious else "No specific warning found.",
        }

    return {
        "organization": organization,
        "verified_fact": "This organization is not in our local database. When in doubt, find the official number independently and call back.",
        "safe_contact": "Search official website independently — never use numbers provided by the caller",
        "is_suspicious": True,
        "warning": "⚠ Cannot verify this organization. Always find official contact info independently.",
    }


def check_payment_risk(payment_method: str) -> dict:
    """Assess the risk level of a requested payment method."""
    method_lower = payment_method.lower()
    matched_key = None
    for key in PAYMENT_RISK:
        if key in method_lower:
            matched_key = key
            break
    if matched_key is None:
        for key, data in PAYMENT_RISK.items():
            if any(ex.lower() in method_lower for ex in data.get("examples", [])):
                matched_key = key
                break

    if matched_key:
        data = PAYMENT_RISK[matched_key]
        return {
            "payment_method": payment_method,
            "risk_level": data["risk"],
            "reason": data["reason"],
            "warning": f"🚨 {data['risk']} RISK: {data['reason']}" if data["risk"] in ("CRITICAL", "HIGH") else data["reason"],
        }

    return {
        "payment_method": payment_method,
        "risk_level": "UNKNOWN",
        "reason": "This payment method is not in our database. Exercise caution with any payment requested by an unsolicited caller.",
        "warning": "⚠ Unknown payment method. Be cautious.",
    }


def suggest_verification(claim: str) -> dict:
    """Return the safe way to independently verify a specific claim."""
    claim_lower = claim.lower()

    if any(w in claim_lower for w in ["irs", "tax", "taxes"]):
        return {
            "claim": claim,
            "action": "Hang up. Call the IRS directly at 1-800-829-1040 or visit irs.gov. Check your mail for any official IRS notices.",
            "key_fact": "The IRS communicates via USPS mail first — never by phone demanding immediate payment.",
        }
    if any(w in claim_lower for w in ["social security", "ssn", "ssa"]):
        return {
            "claim": claim,
            "action": "Hang up. Call the SSA Office of the Inspector General at 1-800-269-0271 to report the call.",
            "key_fact": "The SSA will never suspend your Social Security number or demand payment to avoid arrest.",
        }
    if any(w in claim_lower for w in ["microsoft", "windows", "computer", "virus", "tech support"]):
        return {
            "claim": claim,
            "action": "Hang up immediately. Do NOT give anyone remote access to your computer. Run your existing antivirus software.",
            "key_fact": "Microsoft never calls you about viruses on your computer.",
        }
    if any(w in claim_lower for w in ["bank", "account", "fraud", "suspicious charge"]):
        return {
            "claim": claim,
            "action": "Hang up. Call the number on the BACK OF YOUR CARD — never the number the caller gives you.",
            "key_fact": "Your bank will never ask you to move money to a 'safe account' or give them your full PIN.",
        }
    if any(w in claim_lower for w in ["arrest", "warrant", "police", "law enforcement", "fbi"]):
        return {
            "claim": claim,
            "action": "Hang up. Real law enforcement serves warrants in person — they do not call demanding payment to cancel an arrest.",
            "key_fact": "You cannot pay to make a real warrant go away. This is a scam.",
        }
    if any(w in claim_lower for w in ["lottery", "prize", "won", "winner"]):
        return {
            "claim": claim,
            "action": "Hang up. Legitimate lotteries do not require you to pay taxes or fees upfront to collect winnings.",
            "key_fact": "If you have to pay to receive a prize, it is a scam.",
        }

    return {
        "claim": claim,
        "action": "Do not act on any claim from an unsolicited caller. Hang up, then independently look up the organization's official contact information and call back.",
        "key_fact": "Never act on information from an unsolicited call. Always verify independently.",
    }


def check_known_scam_pattern(description: str) -> dict:
    """Match a description against known scam patterns from FTC data."""
    desc_lower = description.lower()
    matches = []
    for key, pattern in SCAM_PATTERNS.items():
        score = sum(1 for flag in pattern["red_flags"] if flag.lower() in desc_lower)
        if score > 0:
            matches.append((score, pattern))

    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        best = matches[0][1]
        return {
            "match_found": True,
            "scam_type": best["type"],
            "description": best["description"],
            "red_flags_present": [f for f in best["red_flags"] if f.lower() in desc_lower],
            "report_to": best["ftc_report"],
            "warning": f"🚨 This matches a known scam pattern: {best['type']}",
        }

    return {
        "match_found": False,
        "warning": "Pattern not matched in database, but always be cautious with unsolicited callers.",
        "report_to": "reportfraud.ftc.gov",
    }
