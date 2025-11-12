"""
Veterinary Hospital Locator for PetMate

This module provides functionality to find and recommend nearby veterinary
hospitals based on user location, ratings, and other criteria.

Author: PetMate Team
Date: November 2025
"""

import json
import math
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# Support both direct execution and module import
try:
    from src.config import Config
except ModuleNotFoundError:
    from config import Config


class VetLocator:
    """
    Veterinary hospital locator with filtering and sorting capabilities.

    Features:
    - Distance calculation using Haversine formula
    - Filter by distance, rating, and emergency services
    - Sort by distance or rating
    - Support for dogs and cats
    """

    # Constants
    EARTH_RADIUS_KM = 6371  # Earth's radius in kilometers
    MAX_SEARCH_RADIUS = 100  # Maximum search radius in km
    DEFAULT_SEARCH_RADIUS = 50  # Default search radius in km
    DEFAULT_MIN_RATING = 4.0  # Default minimum rating

    def __init__(self, hospital_db_path: str = "data/vet_hospitals.json"):
        """
        Initialize VetLocator with hospital database.

        Args:
            hospital_db_path: Path to hospital JSON database
        """
        self.hospital_db_path = hospital_db_path
        self.hospitals = self._load_hospitals()

    def _load_hospitals(self) -> List[Dict]:
        """
        Load hospital data from JSON file.

        Returns:
            List of hospital dictionaries

        Raises:
            FileNotFoundError: If database file not found
        """
        db_path = Path(self.hospital_db_path)

        if not db_path.exists():
            raise FileNotFoundError(
                f"Hospital database not found at {self.hospital_db_path}"
            )

        with open(db_path, 'r') as f:
            data = json.load(f)

        return data.get("hospitals", [])

    def calculate_distance(
            self,
            location1: Tuple[float, float],
            location2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            location1: (latitude, longitude) of first location
            location2: (latitude, longitude) of second location

        Returns:
            Distance in kilometers

        Example:
            >>> locator = VetLocator()
            >>> loc1 = (42.3601, -71.0589)  # Boston
            >>> loc2 = (42.3736, -71.1097)  # Cambridge
            >>> distance = locator.calculate_distance(loc1, loc2)
            >>> print(f"{distance:.2f} km")
            4.82 km
        """
        lat1, lon1 = location1
        lat2, lon2 = location2

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)

        c = 2 * math.asin(math.sqrt(a))

        distance = self.EARTH_RADIUS_KM * c

        return round(distance, 2)

    def get_nearby_hospitals(
            self,
            user_location: Tuple[float, float],
            search_radius: float = None,
            min_rating: float = None,
            is_emergency: Optional[bool] = None,
            pet_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get list of hospitals within specified radius and criteria.

        Args:
            user_location: (latitude, longitude) of user
            search_radius: Search radius in km (default: 50)
            min_rating: Minimum hospital rating (default: 4.0)
            is_emergency: Filter for 24/7 emergency service (optional)
            pet_type: Filter by pet type specialization (optional)

        Returns:
            List of hospital dictionaries with distance added

        Raises:
            ValueError: If location format is invalid or radius out of range
        """
        # Validate inputs
        if not isinstance(user_location, tuple) or len(user_location) != 2:
            raise ValueError("Location must be a tuple of (latitude, longitude)")

        # Set defaults
        if search_radius is None:
            search_radius = self.DEFAULT_SEARCH_RADIUS
        if min_rating is None:
            min_rating = self.DEFAULT_MIN_RATING

        # Validate radius
        if not (1 <= search_radius <= self.MAX_SEARCH_RADIUS):
            raise ValueError(
                f"Search radius must be between 1 and {self.MAX_SEARCH_RADIUS} km"
            )

        # Validate rating
        if not (1.0 <= min_rating <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0")

        nearby_hospitals = []

        for hospital in self.hospitals:
            # Calculate distance
            hospital_location = (
                hospital["latitude"],
                hospital["longitude"]
            )
            distance = self.calculate_distance(user_location, hospital_location)

            # Check if within radius
            if distance > search_radius:
                continue

            # Check rating
            if hospital["rating"] < min_rating:
                continue

            # Check emergency service filter
            if is_emergency is not None:
                if hospital.get("is_emergency", False) != is_emergency:
                    continue

            # Check pet type specialization
            if pet_type is not None:
                specialties = hospital.get("specialties", [])
                pet_specialties = [s.lower() for s in specialties]

                # Check if hospital handles this pet type
                if pet_type == "dog" and "canine" not in pet_specialties:
                    if "general" not in pet_specialties:
                        continue
                elif pet_type == "cat" and "feline" not in pet_specialties:
                    if "general" not in pet_specialties:
                        continue

            # Add distance to hospital info
            hospital_with_distance = hospital.copy()
            hospital_with_distance["distance"] = distance
            nearby_hospitals.append(hospital_with_distance)

        return nearby_hospitals

    def sort_by_distance(self, hospitals: List[Dict]) -> List[Dict]:
        """
        Sort hospitals by distance (ascending).

        Args:
            hospitals: List of hospitals with 'distance' field

        Returns:
            Sorted list of hospitals
        """
        return sorted(hospitals, key=lambda h: h.get("distance", float('inf')))

    def sort_by_rating(self, hospitals: List[Dict]) -> List[Dict]:
        """
        Sort hospitals by rating (descending).

        Args:
            hospitals: List of hospitals with 'rating' field

        Returns:
            Sorted list of hospitals
        """
        return sorted(hospitals, key=lambda h: h.get("rating", 0), reverse=True)

    def filter_by_rating(self, hospitals: List[Dict], min_rating: float) -> List[Dict]:
        """
        Filter hospitals by minimum rating.

        Args:
            hospitals: List of hospitals
            min_rating: Minimum acceptable rating

        Returns:
            Filtered list of hospitals
        """
        return [h for h in hospitals if h.get("rating", 0) >= min_rating]

    def get_recommendations(
            self,
            user_location: Tuple[float, float],
            search_radius: float = None,
            min_rating: float = None,
            max_results: int = 5,
            sort_by: str = "distance"
    ) -> List[Dict]:
        """
        Get top hospital recommendations based on criteria.

        Args:
            user_location: User's (latitude, longitude)
            search_radius: Search radius in km
            min_rating: Minimum hospital rating
            max_results: Maximum number of results (default: 5)
            sort_by: Sort method - "distance" or "rating"

        Returns:
            List of top recommended hospitals
        """
        # Get nearby hospitals
        nearby = self.get_nearby_hospitals(
            user_location,
            search_radius,
            min_rating
        )

        # Sort based on preference
        if sort_by == "rating":
            sorted_hospitals = self.sort_by_rating(nearby)
        else:  # default to distance
            sorted_hospitals = self.sort_by_distance(nearby)

        # Return top results
        return sorted_hospitals[:max_results]

    def format_hospital_info(self, hospital: Dict) -> str:
        """
        Format hospital information for display.

        Args:
            hospital: Hospital dictionary

        Returns:
            Formatted string with hospital details
        """
        emergency_badge = "🚨 24/7 Emergency" if hospital.get("is_emergency") else ""

        output = f"""
🏥 {hospital['name']}
   📍 Address: {hospital['address']}
   ⭐ Rating: {hospital['rating']}/5.0
   📞 Phone: {hospital['phone']}
   📏 Distance: {hospital.get('distance', 'N/A')} km
   {emergency_badge}
   Specialties: {', '.join(hospital.get('specialties', []))}
        """.strip()

        return output


# Convenience function
def find_nearby_vets(
        user_location: Tuple[float, float],
        radius: float = 50,
        min_rating: float = 4.0
) -> List[Dict]:
    """
    Quick function to find nearby veterinary hospitals.

    Args:
        user_location: (latitude, longitude)
        radius: Search radius in km
        min_rating: Minimum acceptable rating

    Returns:
        List of nearby hospitals
    """
    locator = VetLocator()
    return locator.get_recommendations(user_location, radius, min_rating)


# Testing
if __name__ == "__main__":
    print("🧪 Testing VetLocator...\n")

    # Test location: Boston, MA
    boston_location = (42.3601, -71.0589)

    # Initialize locator
    locator = VetLocator()

    print(f"Total hospitals in database: {len(locator.hospitals)}")
    print(f"Search location: Boston, MA {boston_location}")
    print()

    # Test 1: Find nearby hospitals
    print("=" * 60)
    print("Test 1: Find hospitals within 50km, rating >= 4.0")
    print("=" * 60)

    recommendations = locator.get_recommendations(
        boston_location,
        search_radius=50,
        min_rating=4.0,
        max_results=5
    )

    print(f"\nFound {len(recommendations)} hospitals:\n")

    for i, hospital in enumerate(recommendations, 1):
        print(f"{i}. {locator.format_hospital_info(hospital)}")
        print()

    # Test 2: Emergency hospitals only
    print("=" * 60)
    print("Test 2: Emergency hospitals only")
    print("=" * 60)

    emergency_hospitals = locator.get_nearby_hospitals(
        boston_location,
        search_radius=50,
        is_emergency=True
    )

    print(f"\nFound {len(emergency_hospitals)} emergency hospitals\n")

    # Test 3: Distance calculation
    print("=" * 60)
    print("Test 3: Distance calculation")
    print("=" * 60)

    cambridge_location = (42.3736, -71.1097)
    distance = locator.calculate_distance(boston_location, cambridge_location)
    print(f"\nBoston to Cambridge: {distance} km")

    print("\n✅ All tests complete!")