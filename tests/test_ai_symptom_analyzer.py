"""
Unit tests for AI Symptom Analyzer

Tests run in mock mode by default to avoid API costs during development.

Author: PetMate Team
Date: November 2025
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai_symptom_analyzer import AISymptomAnalyzer, analyze_pet_symptoms
from src.config import Config


class TestAISymptomAnalyzer:
    """Test suite for AISymptomAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = AISymptomAnalyzer()

    def test_initialization(self):
        """Test that analyzer initializes correctly."""
        assert self.analyzer is not None
        assert self.analyzer.cache is not None
        assert self.analyzer.api_calls == 0
        assert self.analyzer.total_tokens == 0

    def test_analyze_symptoms_basic(self):
        """Test basic symptom analysis."""
        result = self.analyzer.analyze_symptoms(
            "My dog is vomiting",
            "dog"
        )

        # Check required fields exist
        assert "condition_name" in result
        assert "confidence" in result
        assert "description" in result
        assert "severity" in result
        assert "recommended_action" in result
        assert "urgent" in result

        # Check field types
        assert isinstance(result["condition_name"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["description"], str)
        assert isinstance(result["severity"], str)
        assert isinstance(result["recommended_action"], str)
        assert isinstance(result["urgent"], bool)

    def test_analyze_symptoms_vomiting(self):
        """Test vomiting symptom recognition."""
        result = self.analyzer.analyze_symptoms(
            "My dog has been throwing up all day",
            "dog"
        )

        # In mock mode, should recognize vomiting
        assert "digest" in result["condition_name"].lower() or \
               "vomit" in result["description"].lower() or \
               "stomach" in result["description"].lower()

    def test_analyze_symptoms_limping(self):
        """Test limping symptom recognition."""
        result = self.analyzer.analyze_symptoms(
            "Cat is limping on back leg",
            "cat"
        )

        # Should recognize leg issue
        assert "leg" in result["condition_name"].lower() or \
               "leg" in result["description"].lower() or \
               "limp" in result["description"].lower()

    def test_analyze_symptoms_coughing(self):
        """Test respiratory symptom recognition."""
        result = self.analyzer.analyze_symptoms(
            "My pet has been coughing",
            "dog"
        )

        # Should recognize respiratory issue
        assert "respirat" in result["condition_name"].lower() or \
               "cough" in result["description"].lower() or \
               "breath" in result["description"].lower()

    def test_empty_symptom_text(self):
        """Test that empty symptom text raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            self.analyzer.analyze_symptoms("", "dog")

    def test_whitespace_only_symptom_text(self):
        """Test that whitespace-only text raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            self.analyzer.analyze_symptoms("   ", "dog")

    def test_different_pet_types(self):
        """Test analysis works for different pet types."""
        pet_types = ["dog", "cat"]  # Only support dog and cat

        for pet_type in pet_types:
            result = self.analyzer.analyze_symptoms(
                "Not eating well",
                pet_type
            )
            assert result is not None
            assert result["condition_name"]

    def test_cache_functionality(self):
        """Test that caching works correctly."""
        if not Config.ENABLE_CACHE:
            pytest.skip("Cache disabled in config")

        symptom = "My dog is sneezing"

        # First call
        result1 = self.analyzer.analyze_symptoms(symptom, "dog")

        # Second call should use cache
        result2 = self.analyzer.analyze_symptoms(symptom, "dog")

        # Results should be identical
        assert result1 == result2

    def test_confidence_range(self):
        """Test that confidence is within valid range."""
        result = self.analyzer.analyze_symptoms(
            "Pet is scratching a lot",
            "cat"
        )

        assert 0.0 <= result["confidence"] <= 1.0

    def test_severity_values(self):
        """Test that severity has valid values."""
        result = self.analyzer.analyze_symptoms(
            "Pet seems tired",
            "dog"
        )

        valid_severities = ["mild", "moderate", "severe"]
        assert result["severity"] in valid_severities

    def test_mock_mode_indicator(self):
        """Test that mock mode is correctly indicated."""
        result = self.analyzer.analyze_symptoms(
            "Test symptom",
            "dog"
        )

        if Config.USE_MOCK_AI:
            assert result.get("mode") == "mock"

    def test_usage_stats(self):
        """Test usage statistics tracking."""
        # Make a few calls
        for _ in range(3):
            self.analyzer.analyze_symptoms("Test symptom", "dog")

        stats = self.analyzer.get_usage_stats()

        assert "api_calls" in stats
        assert "total_tokens" in stats
        assert "estimated_cost" in stats
        assert "mode" in stats

        # In mock mode, calls are tracked but tokens should be 0
        if Config.USE_MOCK_AI:
            assert stats["total_tokens"] == 0
            assert stats["mode"] == "mock"


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_analyze_pet_symptoms_function(self):
        """Test that convenience function works."""
        result = analyze_pet_symptoms(
            "My dog is not eating",
            "dog"
        )

        assert result is not None
        assert "condition_name" in result

    def test_default_pet_type(self):
        """Test that default pet type is 'dog'."""
        result = analyze_pet_symptoms("Coughing")

        assert result is not None
        # Should work with default pet type


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_long_symptom_text(self):
        """Test handling of very long symptom descriptions."""
        analyzer = AISymptomAnalyzer()

        long_text = "symptom " * 100  # Very long text
        result = analyzer.analyze_symptoms(long_text, "dog")

        assert result is not None
        assert result["condition_name"]

    def test_special_characters(self):
        """Test handling of special characters."""
        analyzer = AISymptomAnalyzer()

        result = analyzer.analyze_symptoms(
            "My dog has been sick!!! @#$%",
            "dog"
        )

        assert result is not None

    def test_mixed_case(self):
        """Test case-insensitive symptom matching."""
        analyzer = AISymptomAnalyzer()

        result1 = analyzer.analyze_symptoms("VOMITING", "dog")
        result2 = analyzer.analyze_symptoms("vomiting", "dog")
        result3 = analyzer.analyze_symptoms("Vomiting", "dog")

        # All should recognize the symptom
        assert result1["condition_name"]
        assert result2["condition_name"]
        assert result3["condition_name"]


# Integration test (only run if explicitly requested)
@pytest.mark.integration
def test_real_api_integration():
    """
    Integration test with real API.

    This test is skipped by default to avoid API costs.
    Run with: pytest -m integration
    """
    if Config.USE_MOCK_AI:
        pytest.skip("Skipping real API test in mock mode")

    analyzer = AISymptomAnalyzer()
    result = analyzer.analyze_symptoms(
        "My dog has been vomiting and won't eat",
        "dog"
    )

    assert result is not None
    assert result.get("mode") == "real_api"
    assert analyzer.api_calls > 0
    assert analyzer.total_tokens > 0


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])