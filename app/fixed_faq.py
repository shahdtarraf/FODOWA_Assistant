"""
Fixed FAQ questions with PRIORITY override.
These 4 questions ALWAYS take precedence over any other matching.
"""

# Fixed priority FAQ questions - ALWAYS returned first when matched
FIXED_FAQ_QUESTIONS = [
    {
        "id": "fixed_1",
        "question": "ما هي منصة فودوا؟",
        "answer": "فودوا هي منصة ذكية متكاملة تقدم حلولاً تقنية متقدمة للشركات والأفراد. توفر المنصة خدمات متعددة تشمل إدارة المشاريع، التحليلات الذكية، وأدوات التعاون الجماعي.",
        "keywords": ["فودوا", "منصة", "fodowa", "platform", "ما هي"]
    },
    {
        "id": "fixed_2",
        "question": "ما هي اللغات المتوفرة؟",
        "answer": "المنصة تدعم اللغة العربية والإنجليزية، مع إمكانية إضافة لغات أخرى في المستقبل.",
        "keywords": ["لغات", "لغة", "languages", "متوفرة", "عربية", "انجليزية"]
    },
    {
        "id": "fixed_3",
        "question": "هل الموقع آمن؟",
        "answer": "نعم، الموقع آمن تماماً. نستخدم تقنيات تشفير متقدمة (SSL/TLS) لحماية بياناتك وعملياتك.",
        "keywords": ["آمن", "امن", "security", "حماية", "أمان", "تشفير"]
    },
    {
        "id": "fixed_4",
        "question": "كيف أبدأ؟",
        "answer": "للبدء، قم بإنشاء حساب مجاني بالنقر على 'إنشاء حساب'، ثم أدخل بياناتك الأساسية وفعّل حسابك. بعد ذلك يمكنك تصفح المنصة ونشر المنتجات أو الخدمات.",
        "keywords": ["أبدأ", "ابدأ", "start", "كيف", "بداية", "تسجيل"]
    }
]

# Keywords for quick matching (normalized)
FIXED_KEYWORDS_MAP = {
    # Question 1: ما هي منصة فودوا
    "فودوا": "fixed_1",
    "fodowa": "fixed_1",
    "منصة فودوا": "fixed_1",
    
    # Question 2: ما هي اللغات المتوفرة
    "لغات": "fixed_2",
    "لغة": "fixed_2",
    "languages": "fixed_2",
    
    # Question 3: هل الموقع آمن
    "آمن": "fixed_3",
    "امن": "fixed_3",
    "أمان": "fixed_3",
    "حماية": "fixed_3",
    
    # Question 4: كيف أبدأ
    "أبدأ": "fixed_4",
    "ابدأ": "fixed_4",
    "كيف أبدأ": "fixed_4",
    "كيف ابدأ": "fixed_4",
}


def check_fixed_faq(user_input: str) -> dict:
    """
    Check if user input matches any fixed FAQ question.
    Returns the matched FAQ entry or None.
    
    This function has PRIORITY over all other matching.
    
    Args:
        user_input: User's question
        
    Returns:
        dict with 'matched', 'question', 'answer', 'confidence' or None
    """
    import string
    
    if not user_input:
        return None
    
    # Normalize input
    normalized = user_input.lower().strip()
    normalized = normalized.translate(str.maketrans('', '', string.punctuation))
    
    # Direct keyword match (highest priority)
    for keyword, faq_id in FIXED_KEYWORDS_MAP.items():
        if keyword in normalized:
            for faq in FIXED_FAQ_QUESTIONS:
                if faq["id"] == faq_id:
                    return {
                        "matched": True,
                        "question": faq["question"],
                        "answer": faq["answer"],
                        "confidence": 1.0,
                        "source": "fixed_faq",
                        "faq_id": faq_id
                    }
    
    # Fuzzy match against fixed questions
    import difflib
    best_match = None
    best_score = 0.0
    
    for faq in FIXED_FAQ_QUESTIONS:
        faq_question = faq["question"].lower().strip()
        matcher = difflib.SequenceMatcher(None, normalized, faq_question)
        score = matcher.ratio()
        
        if score > best_score and score >= 0.5:
            best_score = score
            best_match = faq
    
    if best_match:
        return {
            "matched": True,
            "question": best_match["question"],
            "answer": best_match["answer"],
            "confidence": best_score,
            "source": "fixed_faq",
            "faq_id": best_match["id"]
        }
    
    return None


def get_all_fixed_faqs() -> list:
    """Return all fixed FAQ questions."""
    return FIXED_FAQ_QUESTIONS.copy()
