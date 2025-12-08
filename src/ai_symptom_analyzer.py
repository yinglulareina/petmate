"""
AI-Powered Symptom Analyzer for PetMate

This module uses OpenAI's GPT model to analyze pet symptoms and provide
health insights. Includes mock mode for development to save costs, intelligent
caching to avoid duplicate API calls, and automatic fallback to rule-based
analysis when the API is unavailable.

Author: PetMate Team
Date: November 2025
"""

import json
import time
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from openai import OpenAI

try:
    from src.config import Config, get_api_settings, get_model_params
except ModuleNotFoundError:
    from config import Config, get_api_settings, get_model_params


class SymptomCache:
    """Simple in-memory cache to avoid duplicate API calls."""

    def __init__(self):
        self.cache = {}
        self.timestamps = {}

    def get(self, key: str) -> Optional[Dict]:
        if not Config.ENABLE_CACHE:
            return None

        if key in self.cache:
            age = time.time() - self.timestamps.get(key, 0)
            if age < Config.CACHE_DURATION:
                if Config.DEBUG_MODE:
                    print(f"Cache hit for: {key[:50]}...")
                return self.cache[key]

        return None

    def set(self, key: str, value: Dict):
        if Config.ENABLE_CACHE:
            self.cache[key] = value
            self.timestamps[key] = time.time()
            if Config.DEBUG_MODE:
                print(f"Cached result for: {key[:50]}...")


class AISymptomAnalyzer:
    """
    AI-powered symptom analyzer with mock mode support.

    Features:
    - Mock mode using symptom database (no API costs)
    - Real OpenAI API integration
    - Input validation with gibberish detection
    - Result caching
    """

    def __init__(self, symptom_db_path: str = "data/symptoms_database.json"):
        """Initialize analyzer with OpenAI client and symptom database."""
        self.cache = SymptomCache()
        self.client = None

        # Load symptom database for mock mode
        self.symptom_db = self._load_symptom_database(symptom_db_path)

        # Initialize OpenAI client only if not in mock mode
        if not Config.USE_MOCK_AI:
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when USE_MOCK_AI=False")

            self.client = OpenAI(**get_api_settings())

        # Track API usage
        self.api_calls = 0
        self.total_tokens = 0

    def _load_symptom_database(self, db_path: str) -> Dict:
        """
        Load symptom database from JSON file.

        Args:
            db_path: Path to symptom database JSON

        Returns:
            Dictionary with symptom conditions
        """
        path = Path(db_path)

        if not path.exists():
            print(f"Warning: Symptom database not found at {db_path}")
            print("Using fallback keyword matching")
            return {"conditions": {}}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if Config.DEBUG_MODE:
                num_conditions = len(data.get("conditions", {}))
                print(f"Loaded {num_conditions} conditions from symptom database")

            return data

        except Exception as e:
            print(f"Error loading symptom database: {e}")
            return {"conditions": {}}

    # ========== Input Validation ==========

    @staticmethod
    def validate_symptom_input(symptom_text: str) -> Tuple[bool, str]:
        """
        Validate user symptom input and detect invalid/nonsense input.

        Performs 5-level validation:
        1. Not empty
        2. Minimum length (10 chars)
        3. Has meaningful words (not single gibberish word)
        4. No keyboard mashing (repeated characters)
        5. Valid vowel ratio (15%+ vowels)

        Args:
            symptom_text: User input to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if input passes all checks
            - error_message: Description of validation error (empty if valid)

        Example:
            >>> is_valid, msg = AISymptomAnalyzer.validate_symptom_input("vomiting")
            >>> print(is_valid, msg)
            True, ""

            >>> is_valid, msg = AISymptomAnalyzer.validate_symptom_input("asdfghjkl")
            >>> print(is_valid)
            False
        """
        text = symptom_text.strip()

        # Check 1: Not empty
        if not text:
            return False, "Please describe the symptoms first."

        # Check 2: Minimum length
        if len(text) < 10:
            return False, "Please provide more details (at least 10 characters)"

        # Check 3: Detect nonsense/gibberish input
        # Check if input has at least one space (real descriptions usually have spaces)
        if " " not in text:
            # Single word might be valid (e.g., "vomiting"), check if meaningful
            text_lower = text.lower()

            # List of common valid single-word symptoms
            valid_single_words = [
                "vomit", "vomiting", "cough", "coughing", "limp", "limping",
                "sneeze", "sneezing", "scratch", "scratching", "tired", "lethargy"
            ]

            if not any(word in text_lower for word in valid_single_words):
                return False, "Invalid input. Please describe your pet's symptoms in detail."

        # Check 4: Detect keyboard mashing (repeated characters)
        # If more than 5 consecutive identical characters, likely gibberish
        if re.search(r'(.)\1{4,}', text):
            return False, "Invalid input. Please provide a meaningful description."

        # Check 5: Detect excessive random characters
        # If text has less than 15% vowels, might be gibberish
        vowels = sum(1 for c in text.lower() if c in 'aeiou')
        total_letters = sum(1 for c in text if c.isalpha())

        if total_letters > 0 and (vowels / total_letters) < 0.15:
            return False, "Invalid input. Please describe your pet's symptoms clearly."

        return True, ""

    # ========== Analyze Methods ==========

    def analyze_symptoms(
            self,
            symptom_text: str,
            pet_type: str = "dog"
    ) -> Dict:
        """
        Analyze pet symptoms and return health insights.

        This is the main function that handles all symptom analysis requests.
        It implements a smart workflow: validate input, check cache, analyze
        (using either mock or real API), then cache the result for future use.

        Args:
            symptom_text (str): Description of pet symptoms.
                Example: "My dog has been vomiting all day"
            pet_type (str): Type of pet - "dog" or "cat". Default is "dog".

        Returns:
            Dict: Analysis results with these fields:
                - condition_name: Primary health concern
                - confidence: Reliability score (0.0-1.0)
                - description: Explanation of the condition
                - severity: "mild", "moderate", or "severe"
                - recommended_action: What the owner should do
                - urgent: True if needs immediate vet care
                - mode: "mock", "real_api", or "fallback"
        """
        # Input validation
        if not symptom_text or not symptom_text.strip():
            raise ValueError("Symptom text cannot be empty")

        # Check cache
        cache_key = f"{pet_type}:{symptom_text.lower().strip()}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        # Use mock or real API
        if Config.USE_MOCK_AI:
            result = self._mock_analyze(symptom_text, pet_type)
        else:
            result = self._real_analyze(symptom_text, pet_type)

        # Cache result
        self.cache.set(cache_key, result)

        return result

    def _mock_analyze(self, symptom_text: str, pet_type: str) -> Dict:
        """
        Mock analysis using symptom database with flexible keyword matching.
        """
        text_lower = symptom_text.lower()

        # Get conditions from database
        conditions = self.symptom_db.get("conditions", {})

        # Match symptoms against database
        for condition_name, condition_data in conditions.items():
            keywords = condition_data.get("keywords", [])

            # Use flexible keyword matching
            if self._match_keywords(text_lower, keywords):

                # Check if pet type is supported
                supported_pets = condition_data.get("pet_types", ["dog", "cat"])
                if pet_type not in supported_pets:
                    continue

                # Check for urgent keywords
                urgent_keywords = condition_data.get("urgent_keywords", [])
                is_urgent = self._match_keywords(text_lower, urgent_keywords)

                if Config.DEBUG_MODE:
                    print(f"Mock analysis matched: {condition_name}")

                return {
                    "condition_name": condition_name,
                    "confidence": 0.75,
                    "description": condition_data.get("description", ""),
                    "severity": "severe" if is_urgent else condition_data.get("severity", "moderate"),
                    "recommended_action": condition_data.get("recommended_action",
                                                             f"Consult veterinarian about your {pet_type}"),
                    "urgent": is_urgent,
                    "mode": "mock",
                    "source": "Symptom Database"
                }

        # No match found
        if Config.DEBUG_MODE:
            print(f"Mock analysis: No match found for: {symptom_text[:50]}")

        return {
            "condition_name": "General Health Concern",
            "confidence": 0.70,
            "description": "Symptoms require veterinary evaluation",
            "severity": "moderate",
            "recommended_action": f"Consult veterinarian about your {pet_type} for proper diagnosis",
            "urgent": False,
            "mode": "mock",
            "source": "Default Response"
        }

    def _match_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Flexible keyword matching for symptom recognition.

        Handles variations like:
        - "throw up" matches "throwing up"
        - "vomit" matches "vomiting"
        - "cough" matches "coughing"

        Args:
            text: Lowercased symptom text
            keywords: List of keywords from database

        Returns:
            True if any keyword matches
        """
        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Single-word keyword: check if any word starts with it
            if " " not in keyword_lower:
                # Direct match or word-start match
                if keyword_lower in text:
                    return True

                # Check if any word in text starts with keyword
                # This handles: "vomit" -> "vomiting"
                text_words = text.split()
                if any(word.startswith(keyword_lower) for word in text_words):
                    return True

            # Multi-word phrase: check if all parts appear
            else:
                keyword_parts = keyword_lower.split()
                text_words = text.split()

                # Check if all keyword parts have matching words in text
                all_parts_match = True
                for part in keyword_parts:
                    # Check if this part matches any word (or word start)
                    part_found = any(
                        word == part or word.startswith(part)
                        for word in text_words
                    )
                    if not part_found:
                        all_parts_match = False
                        break

                if all_parts_match:
                    return True

        return False

    def _real_analyze(self, symptom_text: str, pet_type: str) -> Dict:
        """
        Perform AI analysis using OpenAI GPT API.

        This method connects to OpenAI's language model to analyze pet symptoms
        intelligently. It handles prompt building, API communication, cost tracking,
        and automatic fallback if the API fails.

        Args:
            symptom_text (str): Symptom description from user
            pet_type (str): "dog" or "cat"

        Returns:
            Dict: Analysis result with condition, severity, recommendations, etc.
                Includes "mode": "real_api" if successful, "fallback" if API failed

        """

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(symptom_text, pet_type)

        try:
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
                cost = tokens_used * 0.000002
                print(f"API Call #{self.api_calls}: {tokens_used} tokens (~${cost:.6f})")

            # Parse response
            content = response.choices[0].message.content
            result = self._parse_ai_response(content, pet_type)
            result["mode"] = "real_api"
            result["source"] = "OpenAI GPT Analysis"

            return result

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"API Error: {e}")
                print("Falling back to rule-based analysis")

            # Fallback to database-based analysis
            fallback_result = self._mock_analyze(symptom_text, pet_type)
            fallback_result["mode"] = "fallback"
            fallback_result["source"] = "Symptom Database (API Error)"

            return fallback_result

    def _build_system_prompt(self) -> str:
        """Build system prompt for real API."""
        return """You are a veterinary medical assistant analyzing pet symptoms.

Provide your analysis in JSON format:
{
  "condition": "Primary diagnosis",
  "severity": "mild" | "moderate" | "severe",
  "description": "Brief explanation",
  "action": "Recommended next steps",
  "urgent": true | false
}

Be professional, accurate, and helpful."""

    def _build_user_prompt(self, symptom_text: str, pet_type: str) -> str:
        """Build user prompt for real API."""
        return f"""Pet: {pet_type.capitalize()}
Symptoms: {symptom_text}

Analyze and provide JSON with condition, severity, description, action, and urgent flag."""

    def _parse_ai_response(self, content: str, pet_type: str) -> Dict:
        """Parse AI response."""
        try:
            data = json.loads(content)

            return {
                "condition_name": data.get("condition", "Unknown"),
                "confidence": 0.8,
                "description": data.get("description", ""),
                "severity": data.get("severity", "moderate"),
                "recommended_action": data.get("action", f"Consult veterinarian about your {pet_type}"),
                "urgent": data.get("urgent", False)
            }

        except json.JSONDecodeError:
            return {
                "condition_name": "AI Analysis",
                "confidence": 0.8,
                "description": content[:200],
                "severity": "moderate",
                "recommended_action": f"Consult veterinarian about your {pet_type}",
                "urgent": False
            }

    def get_usage_stats(self) -> Dict:
        """Get API usage statistics."""
        estimated_cost = self.total_tokens * 0.000002

        return {
            "api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
            "estimated_cost": f"${estimated_cost:.6f}",
            "mode": "mock" if Config.USE_MOCK_AI else "real_api"
        }


# Convenience function
def analyze_pet_symptoms(symptom_text: str, pet_type: str = "dog") -> Dict:
    """Quick function to analyze symptoms."""
    analyzer = AISymptomAnalyzer()
    return analyzer.analyze_symptoms(symptom_text, pet_type)


# Testing
if __name__ == "__main__":
    print("Testing AISymptomAnalyzer...\n")

    # Test validation
    print("=" * 60)
    print("Test: Input Validation")
    print("=" * 60)

    validation_tests = [
        ("My dog is vomiting", True),
        ("", False),
        ("short", False),
        ("asdfghjkl", False),
        ("aaaaaaaaa", False),
    ]

    for text, expected_valid in validation_tests:
        is_valid, msg = AISymptomAnalyzer.validate_symptom_input(text)
        status = "PASS" if is_valid == expected_valid else "FAIL"
        print(f"{status}: '{text}' -> {is_valid} ({msg})")

    print("\n" + "=" * 60)
    print("Test: Symptom Analysis")
    print("=" * 60)

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
        print(f"  Source: {result.get('source', 'N/A')}")
        print()

    # Print stats
    print("Usage Statistics:")
    stats = analyzer.get_usage_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
