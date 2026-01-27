from analyzer.services.analysis_service import TranscriptAnalyzer

# Test cases
test_cases = [
    ("Hello this is English text", "Should be English"),
    ("नमस्ते यह हिंदी टेक्स्ट है", "Should be Hindi"),
    ("Hello नमस्ते mixed text", "Should be Hindi (has Hindi chars)"),
    ("Python programming tutorial", "Should be English"),
    ("पाइथन प्रोग्रामिंग ट्यूटोरियल", "Should be Hindi"),
]

analyzer = TranscriptAnalyzer()

for text, description in test_cases:
    result = analyzer.detect_language(text)
    print(f"{description}: '{text[:20]}...' → {result}")