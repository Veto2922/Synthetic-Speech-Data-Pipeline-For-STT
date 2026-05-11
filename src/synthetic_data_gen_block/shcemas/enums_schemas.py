from enum import Enum


# =========================================================
# ENUMS
# TTS-compatible values
# =========================================================


class Emotion(str, Enum):
    happy = "speak cheerfully and positively"
    sad = "speak sadly with a soft emotional tone"
    angry = "speak angrily with intensity"
    excited = "speak excitedly with enthusiasm"
    neutral = "speak naturally and calmly"
    confused = "speak with confusion and uncertainty"
    sarcastic = "speak sarcastically with a teasing tone"
    fearful = "speak with fear and urgency"


class SpeakerStyle(str, Enum):
    casual = "use a casual conversational tone"
    formal = "use a formal professional tone"
    customer_service = "speak like a polite customer service agent"
    phone_call = "speak like a natural phone conversation"
    street_talk = "use informal street-style dialogue"
    podcast = "speak like a podcast host"
    announcement = "speak like a public announcement"


class SpeakingRate(str, Enum):
    slow = "speaking_rate: slow"
    normal = "speaking_rate: normal"
    fast = "speaking_rate: fast"


class EnergyLevel(str, Enum):
    low = "with low energy"
    medium = "with moderate energy"
    high = "with high energy"


# =========================================================
# Background Noise
# Used later for audio augmentation / mixing
# =========================================================


class BackgroundNoise(str, Enum):
    none = "clean audio"

    street_noise = "background street noise"

    people_noise = "background crowd"

    wind_noise = "light outdoor wind noise"


class Category(str, Enum):
    daily_conversation = "daily_conversation"
    delivery = "delivery"
    shopping = "shopping"
    transportation = "transportation"
    customer_support = "customer_support"
    education = "education"
    healthcare = "healthcare"
    news = "news"
    restaurant = "restaurant"
    emergency = "emergency"
