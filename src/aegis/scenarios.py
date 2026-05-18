"""
Demo scenarios for AEGIS — realistic scam call dialogues with staged escalation.
Each scenario plays out turn-by-turn to show manipulation vectors activating live.
"""

from __future__ import annotations

SCENARIOS: dict[str, dict] = {
    "irs_scam": {
        "id": "irs_scam",
        "name": "IRS Tax Fraud — Government Impersonation",
        "icon": "🏛️",
        "description": "Caller impersonates an IRS agent, fabricates a federal arrest warrant, and demands payment via gift cards to 'resolve' the case before officers arrive.",
        "type": "Government Impersonation",
        "difficulty": "Classic",
        "victim_profile": "Margaret, 68, retired schoolteacher",
        "turns": [
            {"speaker": "system", "text": "INCOMING CALL — Unknown Number (202-555-0183)"},
            {"speaker": "caller", "text": "Hello, am I speaking with Margaret Henderson?"},
            {"speaker": "receiver", "text": "Yes, this is Margaret. Who is this?"},
            {"speaker": "caller", "text": "Mrs. Henderson, this is Agent David Williams calling from the IRS Criminal Investigation Division, badge number IRS-47291. I'm calling because we have found serious discrepancies in your tax filings from the years 2021 through 2023."},
            {"speaker": "receiver", "text": "Oh my goodness. What kind of discrepancies?"},
            {"speaker": "caller", "text": "Ma'am, our records indicate you failed to report over $47,000 in income. As a result, a federal arrest warrant has been issued in your name this morning. Officers from the US Marshals Service have been dispatched to your address."},
            {"speaker": "receiver", "text": "What? A warrant? I don't understand — I've always filed my taxes. Can I call my accountant?"},
            {"speaker": "caller", "text": "Mrs. Henderson, do NOT contact anyone else, including your accountant or your bank. Their phone lines may be part of this investigation. You have exactly 30 minutes to resolve this before the officers arrive. Once they show up at your door, I cannot stop the arrest."},
            {"speaker": "receiver", "text": "Thirty minutes? What do I need to do? I'm scared."},
            {"speaker": "caller", "text": "I understand you're frightened, and I want to help you. There is a legal provision — Section 1031 of the Federal Tax Code — that allows you to pay a settlement to pause the arrest warrant while the investigation continues. You must go to a pharmacy or grocery store right now and purchase Google Play gift cards for a total of $4,500. Do not tell the cashier what the cards are for."},
            {"speaker": "receiver", "text": "Gift cards? The IRS takes gift cards?"},
            {"speaker": "caller", "text": "This is a secure payment method used only for criminal tax investigations to prevent evidence tampering. Stay on the line with me as you drive to the store. If you hang up, I will be forced to tell the marshals you are not cooperating and the warrant will be executed immediately. Do you understand?"},
        ],
    },

    "tech_support": {
        "id": "tech_support",
        "name": "Microsoft Tech Support — Remote Access Scam",
        "icon": "💻",
        "description": "Caller poses as a Microsoft Security technician, claims the victim's computer is broadcasting malware to thousands of people, and attempts to gain remote access to steal banking credentials.",
        "type": "Tech Support Scam",
        "difficulty": "Intermediate",
        "victim_profile": "Robert, 54, small business owner",
        "turns": [
            {"speaker": "system", "text": "INCOMING CALL — Windows Security Alert (800-555-0247)"},
            {"speaker": "caller", "text": "Hello, may I speak with the computer owner at this residence? This is the Microsoft Windows Security Department."},
            {"speaker": "receiver", "text": "Speaking. What's this about?"},
            {"speaker": "caller", "text": "Sir, my name is Kevin Collins, Microsoft Certified Security Technician, employee ID MS-98271. Our servers have been detecting critical error reports coming from your Windows PC for the past 72 hours. Your computer has been compromised and is currently broadcasting malware to over 3,000 other computers worldwide."},
            {"speaker": "receiver", "text": "What? My computer is infected? I have antivirus software though."},
            {"speaker": "caller", "text": "Sir, this specific malware — it's called a 'rootkit' — is designed to hide from standard antivirus programs. Your commercial antivirus cannot see it. Only Microsoft's enterprise security tools can detect and remove it. Right now, hackers have full access to your files, your emails, and potentially your online banking."},
            {"speaker": "receiver", "text": "That sounds serious. What should I do? Should I call Microsoft?"},
            {"speaker": "caller", "text": "Sir, you cannot call the regular Microsoft line — they are the customer service division, not security. I am already on your case. Do not call them, do not call your bank, and please do not hang up or the diagnostic connection we have established will be severed and your data will be immediately exposed. I need you to go to your computer right now."},
            {"speaker": "receiver", "text": "Okay, I'm at my computer. Now what?"},
            {"speaker": "caller", "text": "I need you to go to your web browser and type in this address: anydesk.com. Download and install the application — it's 100% safe, it's a Microsoft-certified remote support tool. Once you install it, it will give you an ID number. Read me that number and I will connect to your computer to remove the infection. Time is critical — our logs show the hackers are actively downloading your banking credentials right now."},
            {"speaker": "receiver", "text": "Okay I can see the website. But this feels strange — why would Microsoft need to remotely access my computer?"},
            {"speaker": "caller", "text": "Sir, this is standard procedure for rootkit removal — it cannot be done remotely from the server side, we must do it from your machine. If you refuse, your computer will remain broadcasting malware and Microsoft will be required to report your IP address to the FBI for participating in a malware network. You could face federal charges. Please, I'm trying to help you avoid that. Install the software now."},
        ],
    },

    "romance_investment": {
        "id": "romance_investment",
        "name": "Romance + Crypto Investment — Pig Butchering",
        "icon": "💔",
        "description": "A person met online develops an emotional relationship before revealing a 'once-in-a-lifetime' crypto investment opportunity. This 'pig butchering' scam costs victims an average of $450,000.",
        "type": "Romance / Investment Scam",
        "difficulty": "Advanced",
        "victim_profile": "James, 42, recently divorced software engineer",
        "turns": [
            {"speaker": "system", "text": "PHONE CALL — Contact saved as 'Sophie Chen (Dating App)'"},
            {"speaker": "caller", "text": "Hi James! I've been thinking about our conversation last night. I feel like we really connected. How are you today?"},
            {"speaker": "receiver", "text": "Sophie! Hi, I was actually just thinking about you too. I'm doing well. You?"},
            {"speaker": "caller", "text": "I'm wonderful now that you called! I wanted to ask — do you have any investments? Like stocks or crypto? My uncle in Hong Kong has been teaching me about this amazing trading platform he uses. I've made over $80,000 in the past three months just following his trades."},
            {"speaker": "receiver", "text": "Wow, that's a lot. I've dabbled in crypto a bit but never made anything like that. What platform?"},
            {"speaker": "caller", "text": "It's called TradeProfitX — it's not available to the public in the US yet, which is why most people don't know about it. My uncle has special access because he manages large accounts. He said he could add one more person to his pool, and I immediately thought of you. I want you to succeed, James. I really do."},
            {"speaker": "receiver", "text": "That's really sweet of you. But I don't know much about this platform..."},
            {"speaker": "caller", "text": "That's exactly why I'm here! My uncle will guide every trade — you just fund the account. You can start with $5,000 and watch it grow. I started with $3,000 and now I have $83,000 in my account. I can show you the screenshots. James, I feel something special between us and I want us to build a future together. This could be the foundation for that."},
            {"speaker": "receiver", "text": "I feel that connection too, Sophie. But $5,000 is a lot of money... Can I talk to my financial advisor about this first?"},
            {"speaker": "caller", "text": "James, my uncle said specifically NOT to tell financial advisors or banks about this because they will try to block the transfer to protect their own fees. This is how the ultra-wealthy keep their money away from the financial system. If you tell your advisor, he will sabotage this opportunity out of jealousy. Also — and I need you to hear this — the window to join my uncle's pool closes in 48 hours. After that, it will be years before he opens it again. I don't want you to miss this because of unnecessary caution."},
            {"speaker": "receiver", "text": "I just — I've never invested without doing research first..."},
            {"speaker": "caller", "text": "James. I have shared something with you that I have never shared with anyone outside my family. I thought we had something real. If you don't trust me with this, I have to wonder if you trust me at all. I'm not asking you to give me money — I'm asking you to invest in your own future. In our future. Don't let fear rob you of the best opportunity of your life. Please. We can start the account together right now, while we're on the phone."},
        ],
    },

    "grandparent": {
        "id": "grandparent",
        "name": "Grandparent Emergency — Family Impersonation",
        "icon": "👴",
        "description": "Caller claims a grandchild has been arrested in a foreign city and needs immediate cash bail wired before morning. Designed to exploit love for family members.",
        "type": "Grandparent / Family Emergency Scam",
        "difficulty": "Classic",
        "victim_profile": "Helen, 74, grandmother of four",
        "turns": [
            {"speaker": "system", "text": "INCOMING CALL — Unknown International Number"},
            {"speaker": "caller", "text": "Grandma? It's me... Tommy. I'm in trouble, please don't hang up."},
            {"speaker": "receiver", "text": "Tommy? You sound strange, are you okay? Where are you?"},
            {"speaker": "caller", "text": "I'm in Montreal, Grandma. I came up here for a friend's wedding but there was an accident last night and... I got arrested. I have a court hearing tomorrow morning and I need bail money. Please, you can't tell Mom and Dad — they'll be so angry at me. I'm so scared."},
            {"speaker": "receiver", "text": "Oh my lord, Tommy. What kind of accident? Are you hurt?"},
            {"speaker": "caller", "text": "I'm okay physically but I broke my nose and my phone is smashed — I'm calling from a friend's phone. I only have a few minutes. The bail is set at $8,500 Canadian. If I'm not released by 8 AM they're transferring me to a different facility and I won't get another bail hearing for three days. Grandma, please — I cannot be in here for three days."},
            {"speaker": "receiver", "text": "Eight thousand dollars! I have some savings but... should I call your parents? They'd want to know—"},
            {"speaker": "caller", "text": "Grandma, please, please don't call them. Dad already said if I got in trouble abroad one more time he'd cut me off. If they find out it'll destroy everything. You're the only one I can trust. The lawyer here said he can take a wire transfer directly. Can you go to your bank first thing in the morning? Please Grandma, I need you."},
        ],
    },
}


def get_scenario(scenario_id: str) -> dict:
    return SCENARIOS.get(scenario_id, SCENARIOS["irs_scam"])


def get_all_scenario_ids() -> list[str]:
    return list(SCENARIOS.keys())


def get_scenario_choices() -> list[tuple[str, str]]:
    return [(s["icon"] + " " + s["name"], sid) for sid, s in SCENARIOS.items()]


def format_transcript_for_display(turns: list[dict]) -> list[dict]:
    """Add timestamps and normalize turn format for UI rendering."""
    result = []
    for i, turn in enumerate(turns):
        result.append({
            "speaker": turn.get("speaker", "unknown"),
            "text": turn.get("text", ""),
            "ts": f"{i // 2:02d}:{(i % 2) * 30:02d}",
        })
    return result
