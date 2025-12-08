"""
Veterinary Hospital Locator for PetMate

This module provides functionality to find and recommend nearby veterinary
hospitals based on user location, ratings, and other criteria.

Author: PetMate Team
Date: November 2025
"""

import json
import math
import requests
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# Support both direct execution and module import
try:
    from src.config import Config
except ModuleNotFoundError:
    from config import Config


class VetLocator:
    """
    Veterinary hospital locator with intelligent geocoding and filtering.

    Features:
    - Intelligent geocoding with 3-tier fallback strategy
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

        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get("hospitals", [])

    # ========== NEW: Geocoding Methods ==========

    def geocode(
        self,
        location_name: str,
        timeout: int = 10
    ) -> Tuple[float, float]:
        """
        Convert location name to coordinates with intelligent fallback.

        Strategy:
        1. Try OpenStreetMap API (external geocoding)
        2. Try local hospital database city matching
        3. Use first available city as fallback

        Args:
            location_name: City name or address
            timeout: API request timeout in seconds

        Returns:
            (latitude, longitude) tuple

        Raises:
            ValueError: If no valid location can be determined
        """
        # Strategy 1: External API
        coords = self._geocode_via_api(location_name, timeout)
        if coords:
            return coords

        # Strategy 2: Local database
        coords = self._geocode_via_database(location_name)
        if coords:
            return coords

        # Strategy 3: Fallback to first available city
        available_cities = self.get_available_cities()
        if available_cities:
            coords = self.get_city_center(available_cities[0])
            if coords:
                return coords

        # Last resort: raise error
        raise ValueError(
            f"Could not determine coordinates for '{location_name}'. "
            f"Available cities: {', '.join(available_cities)}"
        )

    def _geocode_via_api(
        self,
        location_name: str,
        timeout: int
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenStreetMap Nominatim API.

        Args:
            location_name: Location to geocode
            timeout: Request timeout

        Returns:
            (lat, lon) tuple or None if failed
        """
        try:
            # Preprocess location name
            clean_name = self._preprocess_location(location_name)

            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": clean_name, "format": "json", "limit": 1}
            headers = {"User-Agent": "PetMate-CS5001-Project"}

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            data = response.json()

            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))

            # Try original input if preprocessing failed
            params["q"] = location_name
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            data = response.json()

            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))

            return None

        except Exception:
            # Log error but don't raise - we have fallback strategies
            return None

    def _geocode_via_database(
        self,
        location_name: str
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode using local hospital database.

        Args:
            location_name: Location to find

        Returns:
            (lat, lon) tuple or None if not found
        """
        return self.get_city_center(location_name)

    def _preprocess_location(self, text: str) -> str:
        """
        Normalize location input for better API matching.

        Handles:
        - camelCase: "sanJose" -> "San Jose"
        - No spaces: "BostonMA" -> "Boston MA"
        - Multiple spaces: "San   Jose" -> "San Jose"

        Args:
            text: Raw location input

        Returns:
            Cleaned location string
        """
        # Insert space before capital letters (camelCase)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

        # Insert space before state codes (e.g., "BostonMA" -> "Boston MA")
        text = re.sub(r'([a-z])([A-Z]{2})', r'\1 \2', text)

        # Title case for consistency
        text = text.title()

        # Clean multiple spaces
        text = ' '.join(text.split())

        return text

    def get_city_coverage(self) -> Dict[str, List[Dict]]:
        """
        Group hospitals by city/region.

        Returns:
            Dictionary mapping city names to hospital lists
        """
        city_map = {}

        for hospital in self.hospitals:
            address = hospital.get("address", "")

            # Extract city from address (format: "..., City, State ...")
            parts = address.split(",")
            if len(parts) >= 2:
                city = parts[-2].strip()

                if city not in city_map:
                    city_map[city] = []
                city_map[city].append(hospital)

        return city_map

    def get_city_center(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        Get approximate center coordinates for a city.

        Calculates centroid of all hospitals in the city.

        Args:
            city_name: Name of city

        Returns:
            (latitude, longitude) tuple or None if city not found
        """
        city_coverage = self.get_city_coverage()

        # Fuzzy match: case-insensitive, partial match
        city_name_lower = city_name.lower()

        for city, hospitals in city_coverage.items():
            if city_name_lower in city.lower() or city.lower() in city_name_lower:
                if hospitals:
                    avg_lat = sum(h["latitude"] for h in hospitals) / len(hospitals)
                    avg_lon = sum(h["longitude"] for h in hospitals) / len(hospitals)
                    return (round(avg_lat, 4), round(avg_lon, 4))

        return None

    def get_available_cities(self) -> List[str]:
        """
        Get list of cities with hospital coverage.

        Returns:
            Sorted list of city names
        """
        city_coverage = self.get_city_coverage()
        return sorted(city_coverage.keys())

    def get_geocode_info(self, location_name: str) -> Dict:
        """
        Get detailed geocoding information (useful for UI feedback).

        Args:
            location_name: Location to geocode

        Returns:
            Dictionary with coordinates, source, and metadata
        """
        result = {
            "success": False,
            "coordinates": None,
            "source": None,
            "message": "",
            "available_cities": self.get_available_cities()
        }

        try:
            # Try API
            coords = self._geocode_via_api(location_name, timeout=10)
            if coords:
                result["success"] = True
                result["coordinates"] = coords
                result["source"] = "api"
                result["message"] = f"Found location via geocoding service"
                return result

            # Try database
            coords = self._geocode_via_database(location_name)
            if coords:
                city_coverage = self.get_city_coverage()
                matched_city = None
                for city in city_coverage.keys():
                    if location_name.lower() in city.lower():
                        matched_city = city
                        break

                result["success"] = True
                result["coordinates"] = coords
                result["source"] = "database"
                result["message"] = (
                    f"Matched to '{matched_city}' from hospital database "
                    f"({len(city_coverage.get(matched_city, []))} hospitals)"
                )
                return result

            # Fallback
            available_cities = self.get_available_cities()
            if available_cities:
                coords = self.get_city_center(available_cities[0])
                if coords:
                    result["success"] = True
                    result["coordinates"] = coords
                    result["source"] = "fallback"
                    result["message"] = (
                        f"'{location_name}' not found. "
                        f"Showing results for {available_cities[0]} instead."
                    )
                    return result

            result["message"] = f"Location not found"
            return result

        except Exception as e:
            result["message"] = f"Error: {str(e)}"
            return result

    # ========== Existing Methods (Keep unchanged) ==========

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
        emergency_badge = "[24/7 Emergency]" if hospital.get("is_emergency") else ""

        output = f"""
{hospital['name']}
   Address: {hospital['address']}
   Rating: {hospital['rating']}/5.0
   Phone: {hospital['phone']}
   Distance: {hospital.get('distance', 'N/A')} km
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
    print("Testing VetLocator...\n")

    # Test geocoding
    locator = VetLocator()

    print("Test 1: Geocoding")
    print("=" * 60)
    test_cities = ["Boston", "San Jose", "Oakland", "InvalidCity"]

    for city in test_cities:
        info = locator.get_geocode_info(city)
        print(f"{city}: {info['source']} - {info['message']}")

    print("\nTest 2: Available cities")
    print("=" * 60)
    print(f"Cities: {', '.join(locator.get_available_cities())}")

    print("\nAll tests complete!")