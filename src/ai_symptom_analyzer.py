"""
AI-Powered Symptom Analyzer for PetMate

This module uses OpenAI's GPT model to analyze pet symptoms and provide
health insights. Includes mock mode for development to save costs.

Author: PetMate Team
Date: November 2025
"""

import json
import time
from typing import Dict, List, Optional
from openai import OpenAI

# Support both direct execution and module import
try:
    from src.config import Config, get_api_settings, get_model_params
except ModuleNotFoundError:
    from config import Config, get_api_settings, get_model_params


class SymptomCache:
    """
    Simple in-memory cache to avoid duplicate API calls.
    """

    def __init__(self):
        self.cache = {}
        self.timestamps = {}

    def get(self, key: str) -> Optional[Dict]:
        """
        Get cached result if not expired.

        Args:
            key: Cache key (symptom text)

        Returns:
            Cached result or None
        """
        if not Config.ENABLE_CACHE:
            return None

        if key in self.cache:
            # Check if expired
            age = time.time() - self.timestamps.get(key, 0)
            if age < Config.CACHE_DURATION:
                if Config.DEBUG_MODE:
                    print(f"✅ Cache hit for: {key[:50]}...")
                return self.cache[key]

        return None

    def set(self, key: str, value: Dict):
        """
        Store result in cache.

        Args:
            key: Cache key
            value: Result to cache
        """
        if Config.ENABLE_CACHE:
            self.cache[key] = value
            self.timestamps[key] = time.time()
            if Config.DEBUG_MODE:
                print(f"💾 Cached result for: {key[:50]}...")


class AISymptomAnalyzer:
    """
    AI-powered symptom analyzer with mock mode support.

    Features:
    - Mock mode for development (no API costs)
    - Real OpenAI API integration
    - Result caching
    - Cost-optimized prompts
    """

    def __init__(self):
        """Initialize the analyzer with OpenAI client and cache."""
        self.cache = SymptomCache()
        self.client = None

        # Initialize OpenAI client only if not in mock mode
        if not Config.USE_MOCK_AI:
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when USE_MOCK_AI=False")

            self.client = OpenAI(**get_api_settings())

        # Track API usage for cost monitoring
        self.api_calls = 0
        self.total_tokens = 0

    def analyze_symptoms(
            self,
            symptom_text: str,
            pet_type: str = "dog"
    ) -> Dict:
        """
        Analyze pet symptoms and return health insights.

        Args:
            symptom_text: User's description of symptoms
            pet_type: Type of pet ("dog" or "cat")

        Returns:
            Dictionary with analysis results:
            {
                "condition_name": str,
                "confidence": float (0-1),
                "description": str,
                "severity": str (mild/moderate/severe),
                "recommended_action": str,
                "urgent": bool
            }
        """
        # Input validation
        if not symptom_text or not symptom_text.strip():
            raise ValueError("Symptom text cannot be empty")

        # Check cache first
        cache_key = f"{pet_type}:{symptom_text.lower().strip()}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        # Use mock or real API based on config
        if Config.USE_MOCK_AI:
            result = self._mock_analyze(symptom_text, pet_type)
        else:
            result = self._real_analyze(symptom_text, pet_type)

        # Cache the result
        self.cache.set(cache_key, result)

        return result

    def _mock_analyze(self, symptom_text: str, pet_type: str) -> Dict:
        """
        Mock analysis for development (no API cost).

        Returns realistic-looking results based on keywords.
        """
        text_lower = symptom_text.lower()

        # Simple keyword matching for mock
        # Check for digestive issues
        if any(word in text_lower for word in ["vomit", "throw", "sick", "nausea", "stomach", "diarrhea"]):
            condition = "Digestive Upset"
            description = "Possible gastric irritation or dietary issue"
            severity = "moderate"
            urgent = False
        # Check for leg/mobility issues
        elif any(word in text_lower for word in ["limp", "leg", "pain", "walk", "lame"]):
            condition = "Leg Injury"
            description = "Possible sprain, strain, or joint issue"
            severity = "moderate"
            urgent = False
        # Check for respiratory issues
        elif any(word in text_lower for word in ["cough", "sneez", "breath", "wheez"]):
            condition = "Respiratory Issue"
            description = "Possible upper respiratory infection"
            severity = "mild"
            urgent = False
        # Check for skin issues
        elif any(word in text_lower for word in ["scratch", "itch", "skin", "rash", "fur", "hair loss"]):
            condition = "Skin Irritation"
            description = "Possible allergic reaction or parasite"
            severity = "mild"
            urgent = False
        # Check for eye issues
        elif any(word in text_lower for word in ["eye", "squint", "discharge", "red eye"]):
            condition = "Eye Problem"
            description = "Eye infection, injury, or irritation"
            severity = "moderate"
            urgent = False
        # Check for ear issues
        elif any(word in text_lower for word in ["ear", "head shak", "tilt"]):
            condition = "Ear Problem"
            description = "Ear infection or mite infestation"
            severity = "mild"
            urgent = False
        # Check for lethargy
        elif any(word in text_lower for word in ["tired", "sleep", "energy", "weak", "lethar", "depress"]):
            condition = "Lethargy"
            description = "Unusual tiredness or lack of energy"
            severity = "moderate"
            urgent = False
        # Check for appetite issues
        elif any(word in text_lower for word in ["eat", "food", "appetite", "hungry"]):
            condition = "Loss of Appetite"
            description = "Decreased or absent appetite"
            severity = "moderate"
            urgent = False
        else:
            condition = "General Health Concern"
            description = "Symptoms require veterinary evaluation"
            severity = "moderate"
            urgent = False

        if Config.DEBUG_MODE:
            print(f"🤖 Mock analysis for: {symptom_text[:50]}...")

        return {
            "condition_name": condition,
            "confidence": 0.75,
            "description": description,
            "severity": severity,
            "recommended_action": f"Monitor your {pet_type} and consult vet if symptoms persist",
            "urgent": urgent,
            "mode": "mock"
        }

    def _real_analyze(self, symptom_text: str, pet_type: str) -> Dict:
        """
        Real OpenAI API analysis (costs money).

        Uses optimized prompts to minimize token usage.
        """
        # Build cost-optimized prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(symptom_text, pet_type)

        try:
            # Make API call
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **get_model_params()
            )

            # Track usage
            self.api_calls += 1
            tokens_used = response.usage.total_tokens
            self.total_tokens += tokens_used

            if Config.LOG_API_USAGE:
                cost = tokens_used * 0.000002  # Approximate cost
                print(f"💰 API Call #{self.api_calls}: {tokens_used} tokens (~${cost:.6f})")

            # Parse response
            content = response.choices[0].message.content
            result = self._parse_ai_response(content, pet_type)
            result["mode"] = "real_api"

            return result

        except Exception as e:
            print(f"❌ API Error: {e}")
            # Fallback to mock on error
            print("⚠️  Falling back to mock analysis")
            return self._mock_analyze(symptom_text, pet_type)

    def _build_system_prompt(self) -> str:
        """
        Build concise system prompt (saves tokens).
        """
        return (
            "You are a pet health assistant. Analyze symptoms briefly. "
            "Return JSON: {condition, severity, description, action, urgent}. "
            "Keep responses under 100 words."
        )

    def _build_user_prompt(self, symptom_text: str, pet_type: str) -> str:
        """
        Build concise user prompt (saves tokens).
        """
        return f"Pet: {pet_type}. Symptoms: {symptom_text}. Analyze briefly."

    def _parse_ai_response(self, content: str, pet_type: str) -> Dict:
        """
        Parse AI response into structured format.

        Handles both JSON and plain text responses.
        """
        try:
            # Try to parse as JSON
            data = json.loads(content)

            return {
                "condition_name": data.get("condition", "Unknown"),
                "confidence": 0.8,  # AI responses are generally reliable
                "description": data.get("description", ""),
                "severity": data.get("severity", "moderate"),
                "recommended_action": data.get("action", f"Consult veterinarian about your {pet_type}"),
                "urgent": data.get("urgent", False)
            }

        except json.JSONDecodeError:
            # Fallback: parse plain text
            lines = content.strip().split('\n')

            return {
                "condition_name": "AI Analysis",
                "confidence": 0.8,
                "description": content[:200],
                "severity": "moderate",
                "recommended_action": f"Consult veterinarian about your {pet_type}",
                "urgent": False
            }

    def get_usage_stats(self) -> Dict:
        """
        Get API usage statistics.

        Returns:
            Dictionary with usage stats and cost estimate
        """
        estimated_cost = self.total_tokens * 0.000002

        return {
            "api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
            "estimated_cost": f"${estimated_cost:.6f}",
            "mode": "mock" if Config.USE_MOCK_AI else "real_api"
        }


# Convenience function
def analyze_pet_symptoms(symptom_text: str, pet_type: str = "dog") -> Dict:
    """
    Quick function to analyze symptoms.

    Args:
        symptom_text: Description of symptoms
        pet_type: Type of pet ("dog" or "cat")

    Returns:
        Analysis results dictionary
    """
    analyzer = AISymptomAnalyzer()
    return analyzer.analyze_symptoms(symptom_text, pet_type)


# Testing
if __name__ == "__main__":
    print("🧪 Testing AISymptomAnalyzer...\n")

    # Test cases for dogs and cats only
    test_cases = [
        ("My dog has been vomiting all day", "dog"),
        ("Cat is limping on front paw", "cat"),
        ("My dog won't stop scratching", "dog"),
        ("Cat has eye discharge", "cat"),
    ]

    analyzer = AISymptomAnalyzer()

    for symptom, pet in test_cases:
        print(f"Test: {symptom}")
        result = analyzer.analyze_symptoms(symptom, pet)
        print(f"  Condition: {result['condition_name']}")
        print(f"  Severity: {result['severity']}")
        print(f"  Mode: {result['mode']}")
        print()

    # Print usage stats
    print("Usage Statistics:")
    stats = analyzer.get_usage_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")