"""
PetMate Source Package

Core modules for PetMate application:
- config: Configuration and environment management
- ai_symptom_analyzer: AI-powered pet symptom analysis
- vet_locator: Veterinary hospital location and recommendations

Author: PetMate Team
Date: November 2025
"""

__version__ = "0.2.0"
__all__ = ["ai_symptom_analyzer", "vet_locator", "config"]

# Quick imports for convenience
from src.ai_symptom_analyzer import AISymptomAnalyzer, analyze_pet_symptoms
from src.vet_locator import VetLocator, find_nearby_vets
from src.config import Config