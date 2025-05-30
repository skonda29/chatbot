import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
from typing import List

CRISIS_KEYWORDS: List[str] = [
    "suicidal", "suicide", "kill myself", "want to die", "hopeless", "worthless",
    "can't go on", "give up", "ending it all", "no reason to live"
]

SAFETY_MESSAGE = (
    "💡 It sounds like you're going through a really tough time. "
    "You're not alone, and there are people who want to help you. "
    "Please consider reaching out to a mental health professional or contacting a helpline:\n\n"
    "📞 **In the USA**: 911\n"
    "📞 **Crisis Text Line**: Text HOME to 741741\n"
    "📞 **National Suicide Prevention Lifeline**: 988\n\n"
    "Your life has value, and there are people who care about you."
)

def contains_crisis_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CRISIS_KEYWORDS)