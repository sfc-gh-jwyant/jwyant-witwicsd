"""Location and Landmark models."""

from dataclasses import dataclass, field
from typing import Optional
import math


@dataclass
class Landmark:
    """A notable landmark within a location."""
    id: str
    location_id: str
    name: str
    landmark_type: str
    clue_facts: list[str] = field(default_factory=list)
    image_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Landmark":
        """Create Landmark from database row dict."""
        return cls(
            id=data.get("LANDMARK_ID", ""),
            location_id=data.get("LOCATION_ID", ""),
            name=data.get("NAME", ""),
            landmark_type=data.get("LANDMARK_TYPE", ""),
            clue_facts=data.get("CLUE_FACTS", []) or [],
            image_url=data.get("IMAGE_URL"),
        )


@dataclass
class Location:
    """A city/location in the game world."""
    id: str
    city: str
    country: str
    continent: str
    latitude: float
    longitude: float
    description: str = ""
    image_url: Optional[str] = None
    landmarks: list[Landmark] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        """Create Location from database row dict."""
        return cls(
            id=data.get("LOCATION_ID", ""),
            city=data.get("CITY", ""),
            country=data.get("COUNTRY", ""),
            continent=data.get("CONTINENT", ""),
            latitude=data.get("LATITUDE", 0.0),
            longitude=data.get("LONGITUDE", 0.0),
            description=data.get("DESCRIPTION", ""),
            image_url=data.get("IMAGE_URL"),
        )
    
    def get_travel_time_to(self, other: "Location") -> int:
        """
        Calculate travel time in hours based on great-circle distance.
        
        Uses a simplified model:
        - Up to 500 km: 2 hours (short flight/train)
        - 500-2000 km: 4 hours (medium flight)
        - 2000-5000 km: 8 hours (long flight)
        - 5000-10000 km: 12 hours (intercontinental)
        - 10000+ km: 16 hours (opposite side of world)
        """
        distance = self._haversine_distance(other)
        
        if distance < 500:
            return 2
        elif distance < 2000:
            return 4
        elif distance < 5000:
            return 8
        elif distance < 10000:
            return 12
        else:
            return 16
    
    def _haversine_distance(self, other: "Location") -> float:
        """Calculate great-circle distance between two locations in km."""
        R = 6371  # Earth's radius in km
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return f"{self.city}, {self.country}"

