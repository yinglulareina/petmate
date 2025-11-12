"""
Unit tests for Vet Locator

Tests the veterinary hospital location and recommendation functionality.

Author: PetMate Team
Date: November 2025
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vet_locator import VetLocator, find_nearby_vets


class TestVetLocator:
    """Test suite for VetLocator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.locator = VetLocator()
        # Boston location for testing
        self.boston_location = (42.3601, -71.0589)
        # Cambridge location for testing
        self.cambridge_location = (42.3736, -71.1097)

    def test_initialization(self):
        """Test that VetLocator initializes correctly."""
        assert self.locator is not None
        assert self.locator.hospitals is not None
        assert isinstance(self.locator.hospitals, list)
        assert len(self.locator.hospitals) > 0

    def test_load_hospitals(self):
        """Test that hospital data loads correctly."""
        hospitals = self.locator.hospitals

        # Check that we have data
        assert len(hospitals) > 0

        # Check first hospital has required fields
        hospital = hospitals[0]
        required_fields = [
            "hospital_id", "name", "address", "latitude",
            "longitude", "phone", "rating", "is_emergency"
        ]

        for field in required_fields:
            assert field in hospital, f"Missing field: {field}"

    def test_calculate_distance_same_location(self):
        """Test distance calculation for same location."""
        distance = self.locator.calculate_distance(
            self.boston_location,
            self.boston_location
        )

        assert distance == 0.0

    def test_calculate_distance_different_locations(self):
        """Test distance calculation between Boston and Cambridge."""
        distance = self.locator.calculate_distance(
            self.boston_location,
            self.cambridge_location
        )

        # Distance should be positive
        assert distance > 0

        # Boston to Cambridge is approximately 4-5 km
        assert 3 <= distance <= 7

    def test_calculate_distance_symmetry(self):
        """Test that distance A->B equals distance B->A."""
        distance1 = self.locator.calculate_distance(
            self.boston_location,
            self.cambridge_location
        )
        distance2 = self.locator.calculate_distance(
            self.cambridge_location,
            self.boston_location
        )

        assert distance1 == distance2

    def test_get_nearby_hospitals_basic(self):
        """Test basic nearby hospital search."""
        nearby = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            min_rating=4.0
        )

        assert isinstance(nearby, list)
        assert len(nearby) > 0

        # All results should have distance field
        for hospital in nearby:
            assert "distance" in hospital
            assert hospital["distance"] <= 50

    def test_get_nearby_hospitals_filters_by_radius(self):
        """Test that radius filter works correctly."""
        # Small radius
        nearby_small = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=5,
            min_rating=1.0
        )

        # Large radius
        nearby_large = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            min_rating=1.0
        )

        # Larger radius should find more or equal hospitals
        assert len(nearby_large) >= len(nearby_small)

        # All hospitals in small radius should be within 5km
        for hospital in nearby_small:
            assert hospital["distance"] <= 5

    def test_get_nearby_hospitals_filters_by_rating(self):
        """Test that rating filter works correctly."""
        # Low rating threshold
        low_rating = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            min_rating=3.0
        )

        # High rating threshold
        high_rating = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            min_rating=4.5
        )

        # Low threshold should find more or equal hospitals
        assert len(low_rating) >= len(high_rating)

        # All hospitals should meet rating requirement
        for hospital in high_rating:
            assert hospital["rating"] >= 4.5

    def test_get_nearby_hospitals_emergency_filter(self):
        """Test emergency service filter."""
        # Only emergency hospitals
        emergency = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            is_emergency=True
        )

        # All should be emergency
        for hospital in emergency:
            assert hospital["is_emergency"] is True

        # Only non-emergency hospitals
        non_emergency = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            is_emergency=False
        )

        # All should be non-emergency
        for hospital in non_emergency:
            assert hospital["is_emergency"] is False

    def test_get_nearby_hospitals_invalid_location(self):
        """Test that invalid location raises error."""
        with pytest.raises(ValueError, match="must be a tuple"):
            self.locator.get_nearby_hospitals("invalid", 50)

        with pytest.raises(ValueError, match="must be a tuple"):
            self.locator.get_nearby_hospitals([42.36, -71.05], 50)

    def test_get_nearby_hospitals_invalid_radius(self):
        """Test that invalid radius raises error."""
        # Radius too small
        with pytest.raises(ValueError, match="between 1 and"):
            self.locator.get_nearby_hospitals(self.boston_location, 0)

        # Radius too large
        with pytest.raises(ValueError, match="between 1 and"):
            self.locator.get_nearby_hospitals(self.boston_location, 200)

    def test_get_nearby_hospitals_invalid_rating(self):
        """Test that invalid rating raises error."""
        # Rating too low
        with pytest.raises(ValueError, match="between 1.0 and 5.0"):
            self.locator.get_nearby_hospitals(
                self.boston_location,
                min_rating=0.5
            )

        # Rating too high
        with pytest.raises(ValueError, match="between 1.0 and 5.0"):
            self.locator.get_nearby_hospitals(
                self.boston_location,
                min_rating=6.0
            )

    def test_sort_by_distance(self):
        """Test sorting hospitals by distance."""
        nearby = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50
        )

        sorted_hospitals = self.locator.sort_by_distance(nearby)

        # Check that list is sorted
        for i in range(len(sorted_hospitals) - 1):
            assert sorted_hospitals[i]["distance"] <= sorted_hospitals[i + 1]["distance"]

    def test_sort_by_rating(self):
        """Test sorting hospitals by rating."""
        nearby = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50
        )

        sorted_hospitals = self.locator.sort_by_rating(nearby)

        # Check that list is sorted (descending)
        for i in range(len(sorted_hospitals) - 1):
            assert sorted_hospitals[i]["rating"] >= sorted_hospitals[i + 1]["rating"]

    def test_filter_by_rating(self):
        """Test filtering hospitals by rating."""
        nearby = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50,
            min_rating=1.0
        )

        filtered = self.locator.filter_by_rating(nearby, 4.5)

        # All filtered hospitals should meet rating
        for hospital in filtered:
            assert hospital["rating"] >= 4.5

        # Should have fewer or equal hospitals
        assert len(filtered) <= len(nearby)

    def test_get_recommendations_default(self):
        """Test getting recommendations with default parameters."""
        recommendations = self.locator.get_recommendations(
            self.boston_location
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5  # Default max_results

        # Should be sorted by distance (default)
        for i in range(len(recommendations) - 1):
            assert recommendations[i]["distance"] <= recommendations[i + 1]["distance"]

    def test_get_recommendations_sort_by_rating(self):
        """Test recommendations sorted by rating."""
        recommendations = self.locator.get_recommendations(
            self.boston_location,
            sort_by="rating"
        )

        # Should be sorted by rating (descending)
        for i in range(len(recommendations) - 1):
            assert recommendations[i]["rating"] >= recommendations[i + 1]["rating"]

    def test_get_recommendations_max_results(self):
        """Test max_results parameter."""
        # Get top 3
        top_3 = self.locator.get_recommendations(
            self.boston_location,
            max_results=3
        )

        assert len(top_3) <= 3

        # Get top 10
        top_10 = self.locator.get_recommendations(
            self.boston_location,
            max_results=10
        )

        # Should have more or equal results
        assert len(top_10) >= len(top_3)

    def test_format_hospital_info(self):
        """Test hospital information formatting."""
        nearby = self.locator.get_nearby_hospitals(
            self.boston_location,
            search_radius=50
        )

        if nearby:
            hospital = nearby[0]
            formatted = self.locator.format_hospital_info(hospital)

            # Check that key information is included
            assert hospital["name"] in formatted
            assert hospital["address"] in formatted
            assert hospital["phone"] in formatted
            assert str(hospital["rating"]) in formatted

    def test_no_hospitals_in_range(self):
        """Test when no hospitals are found in range."""
        # Use a location far from Boston (e.g., middle of ocean)
        ocean_location = (40.0, -70.0)

        nearby = self.locator.get_nearby_hospitals(
            ocean_location,
            search_radius=5,
            min_rating=4.0
        )

        # Should return empty list, not error
        assert isinstance(nearby, list)
        assert len(nearby) == 0


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_find_nearby_vets(self):
        """Test find_nearby_vets convenience function."""
        boston_location = (42.3601, -71.0589)

        results = find_nearby_vets(boston_location)

        assert isinstance(results, list)
        # Should have results for Boston
        assert len(results) > 0


class TestDataQuality:
    """Test data quality in hospital database."""

    def test_all_hospitals_have_coordinates(self):
        """Test that all hospitals have valid coordinates."""
        locator = VetLocator()

        for hospital in locator.hospitals:
            assert "latitude" in hospital
            assert "longitude" in hospital

            # Boston area coordinates (rough bounds)
            assert 41 <= hospital["latitude"] <= 43
            assert -72 <= hospital["longitude"] <= -70

    def test_all_hospitals_have_ratings(self):
        """Test that all hospitals have valid ratings."""
        locator = VetLocator()

        for hospital in locator.hospitals:
            assert "rating" in hospital
            assert 1.0 <= hospital["rating"] <= 5.0

    def test_all_hospitals_have_contact_info(self):
        """Test that all hospitals have contact information."""
        locator = VetLocator()

        for hospital in locator.hospitals:
            assert "phone" in hospital
            assert len(hospital["phone"]) > 0

            assert "address" in hospital
            assert len(hospital["address"]) > 0

    def test_specialties_format(self):
        """Test that specialties are properly formatted."""
        locator = VetLocator()

        for hospital in locator.hospitals:
            if "specialties" in hospital:
                assert isinstance(hospital["specialties"], list)

                # All supported pets should have general or specific specialty
                specialties_lower = [s.lower() for s in hospital["specialties"]]
                assert "general" in specialties_lower or \
                       "canine" in specialties_lower or \
                       "feline" in specialties_lower


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])