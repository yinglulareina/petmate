"""
Configuration Manager for PetMate

This module loads and manages all environment variables and configuration
settings, especially those related to cost-saving for OpenAI API usage.

Author: PetMate Team
Date: November 2025
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to manage all application settings.

    This centralizes configuration management and provides easy access
    to environment variables throughout the application.
    """

    # ============================================
    # OpenAI API Configuration
    # ============================================

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")

    # ============================================
    # Cost-Saving Settings
    # ============================================

    # Mock mode: Use fake responses instead of real API calls
    USE_MOCK_AI = os.getenv("USE_MOCK_AI", "True").lower() == "true"

    # Enable caching to avoid duplicate API calls
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"

    # Cache duration in seconds
    CACHE_DURATION = int(os.getenv("CACHE_DURATION", "3600"))

    # ============================================
    # Model Configuration (Optimized for Cost)
    # ============================================

    # Model name (gpt-3.5-turbo is cheapest)
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Maximum tokens per response (lower = cheaper)
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "150"))

    # Temperature (lower = more deterministic and shorter)
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

    # ============================================
    # API Settings
    # ============================================

    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
    API_RETRY_ATTEMPTS = int(os.getenv("API_RETRY_ATTEMPTS", "2"))
    API_RETRY_DELAY = int(os.getenv("API_RETRY_DELAY", "1"))

    # ============================================
    # Application Settings
    # ============================================

    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    LOG_API_USAGE = os.getenv("LOG_API_USAGE", "True").lower() == "true"

    # ============================================
    # Validation
    # ============================================

    @classmethod
    def validate(cls):
        """
        Validate that all required configuration is present.

        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.USE_MOCK_AI and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when USE_MOCK_AI=False. "
                "Please set it in your .env file."
            )

    @classmethod
    def get_mode(cls):
        """
        Get current operation mode.

        Returns:
            str: 'DEVELOPMENT' or 'PRODUCTION'
        """
        return "DEVELOPMENT (Mock)" if cls.USE_MOCK_AI else "PRODUCTION (Real API)"

    @classmethod
    def get_cost_info(cls):
        """
        Get information about current cost-saving settings.

        Returns:
            dict: Cost-saving configuration details
        """
        return {
            "mode": cls.get_mode(),
            "use_mock": cls.USE_MOCK_AI,
            "cache_enabled": cls.ENABLE_CACHE,
            "max_tokens": cls.OPENAI_MAX_TOKENS,
            "temperature": cls.OPENAI_TEMPERATURE,
            "estimated_cost_per_call": "$0.0002" if not cls.USE_MOCK_AI else "$0",
        }

    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)."""
        print("=" * 50)
        print("PetMate Configuration")
        print("=" * 50)
        print(f"Mode: {cls.get_mode()}")
        print(f"Use Mock AI: {cls.USE_MOCK_AI}")
        print(f"Cache Enabled: {cls.ENABLE_CACHE}")
        print(f"Model: {cls.OPENAI_MODEL}")
        print(f"Max Tokens: {cls.OPENAI_MAX_TOKENS}")
        print(f"Temperature: {cls.OPENAI_TEMPERATURE}")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print(f"API Key Present: {'Yes' if cls.OPENAI_API_KEY else 'No'}")
        print("=" * 50)


# Validate configuration on import
Config.validate()


# Quick access functions
def is_mock_mode():
    """Check if application is in mock mode."""
    return Config.USE_MOCK_AI


def is_cache_enabled():
    """Check if caching is enabled."""
    return Config.ENABLE_CACHE


def get_api_settings():
    """
    Get OpenAI API settings.

    Returns:
        dict: API configuration for OpenAI client
    """
    return {
        "api_key": Config.OPENAI_API_KEY,
        "timeout": Config.API_TIMEOUT,
        "max_retries": Config.API_RETRY_ATTEMPTS,
    }


def get_model_params():
    """
    Get model parameters for API calls.

    Returns:
        dict: Model parameters optimized for cost
    """
    return {
        "model": Config.OPENAI_MODEL,
        "max_tokens": Config.OPENAI_MAX_TOKENS,
        "temperature": Config.OPENAI_TEMPERATURE,
    }


# For testing
if __name__ == "__main__":
    Config.print_config()
    print("\nCost Info:")
    for key, value in Config.get_cost_info().items():
        print(f"  {key}: {value}")