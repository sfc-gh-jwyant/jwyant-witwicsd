"""Dynamic clue generation using Snowflake Cortex AI."""

import random
from typing import Optional
import uuid

from ..models import Location, Landmark, Suspect, Clue, DIFFICULTY_CONFIG
from ..models.clue import ClueType, DIFFICULTY_CLARITY
from ..database.connection import safe_complete, get_session


class ClueGenerator:
    """Generates clues dynamically using Cortex AI."""
    
    def __init__(self):
        """Initialize the clue generator."""
        pass
    
    def generate_destination_clue(
        self, 
        next_location: Location, 
        difficulty: int,
        landmark: Optional[Landmark] = None
    ) -> Clue:
        """
        Generate a clue hinting at the next destination.
        
        Uses Cortex AI to create contextual, difficulty-appropriate clues.
        Falls back to template-based clues if AI is unavailable.
        """
        clarity = DIFFICULTY_CLARITY.get(difficulty, "clear")
        
        # Build context for AI prompt
        landmark_context = ""
        if landmark and landmark.clue_facts:
            facts = landmark.clue_facts[:2]  # Use first 2 facts
            landmark_context = f"You may reference this landmark: {landmark.name}. Facts: {', '.join(facts)}"
        
        prompt = f"""
Generate a {clarity} clue that hints the suspect is heading to {next_location.city}, {next_location.country}.

The clue should reference: landmarks, geography, culture, cuisine, or famous facts about the destination.
Do NOT mention the city or country name directly.
{landmark_context}

Format: A witness quote in 1-2 sentences, spoken in first person.
Example: "I heard them mention something about wanting to see that famous iron tower..."

Generate ONLY the quote, no other text.
"""
        
        try:
            clue_text = safe_complete(prompt)
            clue_text = clue_text.strip().strip('"').strip("'")
        except Exception:
            # Fallback to template-based clue
            clue_text = self._fallback_destination_clue(next_location, difficulty)
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type=ClueType.DESTINATION,
            text=clue_text,
            source=self._random_witness(),
            location_id=next_location.id,
        )
    
    def generate_suspect_clue(
        self, 
        suspect: Suspect, 
        difficulty: int,
        trait_to_reveal: Optional[str] = None
    ) -> Clue:
        """
        Generate a clue about the suspect's appearance or habits.
        
        Args:
            suspect: The suspect to generate clue about
            difficulty: Game difficulty level (affects clarity)
            trait_to_reveal: Specific trait to hint at, or random if None
        """
        clarity = DIFFICULTY_CLARITY.get(difficulty, "clear")
        
        # Choose which trait to reveal
        traits = suspect.traits
        if trait_to_reveal and trait_to_reveal in traits:
            chosen_trait = trait_to_reveal
            trait_value = traits[trait_to_reveal]
        else:
            # Pick a random trait
            chosen_trait = random.choice(list(traits.keys()))
            trait_value = traits[chosen_trait]
        
        prompt = f"""
A witness saw the suspect. Generate a {clarity} clue describing someone with:
- {chosen_trait}: {trait_value}

The clue should describe what the witness noticed about this trait.
Format: A witness quote in 1 sentence, spoken in first person.
Example: "The person I saw had the most striking blue eyes..."

Generate ONLY the quote, no other text.
"""
        
        try:
            clue_text = safe_complete(prompt)
            clue_text = clue_text.strip().strip('"').strip("'")
        except Exception:
            # Fallback to template-based clue
            clue_text = self._fallback_suspect_clue(chosen_trait, trait_value, difficulty)
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type=ClueType.SUSPECT,
            text=clue_text,
            source=self._random_witness(),
        )
    
    def generate_red_herring(
        self, 
        wrong_location: Location, 
        difficulty: int
    ) -> Clue:
        """
        Generate a misleading clue that points to a wrong destination.
        
        Red herrings become more convincing at higher difficulties.
        """
        clarity = DIFFICULTY_CLARITY.get(min(difficulty - 1, 1), "very obvious")
        
        prompt = f"""
Generate a {clarity} MISLEADING clue that falsely suggests the suspect might be heading to {wrong_location.city}, {wrong_location.country}.

This is a red herring - it should sound plausible but lead to the wrong place.
Do NOT mention the city or country name directly.

Format: A witness quote in 1-2 sentences, spoken in first person.
The witness sounds less certain than normal clues.
Example: "I think I might have heard them say something about beaches... or was it mountains?"

Generate ONLY the quote, no other text.
"""
        
        try:
            clue_text = safe_complete(prompt)
            clue_text = clue_text.strip().strip('"').strip("'")
        except Exception:
            clue_text = self._fallback_red_herring(wrong_location)
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type=ClueType.RED_HERRING,
            text=clue_text,
            source=self._random_unreliable_witness(),
        )
    
    def generate_clues_for_location(
        self,
        current_location: Location,
        next_location: Location,
        suspect: Suspect,
        difficulty: int,
        all_locations: list[Location],
    ) -> list[Clue]:
        """
        Generate a set of clues for investigating at a location.
        
        Returns 2-4 clues based on difficulty:
        - Always 1 destination clue
        - 1 suspect clue
        - 0-2 red herrings based on difficulty
        """
        config = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG[1])
        num_red_herrings = config.get("red_herrings", 0)
        
        clues = []
        
        # Get a landmark from current location for context
        landmark = None
        if current_location.landmarks:
            landmark = random.choice(current_location.landmarks)
        
        # Generate destination clue
        dest_clue = self.generate_destination_clue(next_location, difficulty, landmark)
        clues.append(dest_clue)
        
        # Generate suspect clue
        suspect_clue = self.generate_suspect_clue(suspect, difficulty)
        clues.append(suspect_clue)
        
        # Generate red herrings
        wrong_locations = [loc for loc in all_locations 
                         if loc.id != next_location.id and loc.id != current_location.id]
        
        for _ in range(min(num_red_herrings, len(wrong_locations))):
            wrong_loc = random.choice(wrong_locations)
            wrong_locations.remove(wrong_loc)
            red_herring = self.generate_red_herring(wrong_loc, difficulty)
            clues.append(red_herring)
        
        # Shuffle clues so red herrings aren't always last
        random.shuffle(clues)
        
        return clues
    
    def _fallback_destination_clue(self, location: Location, difficulty: int) -> str:
        """Generate a template-based destination clue as fallback."""
        templates = {
            1: [  # Very obvious
                f"They said they're heading to a city in {location.country}!",
                f"I heard them mention {location.continent} as their next stop.",
                f"They were looking at pictures of {location.country} on their phone.",
            ],
            2: [  # Clear
                f"They seemed excited about visiting somewhere in {location.continent}.",
                f"I noticed a guidebook about {location.country} in their bag.",
                f"They asked about flights heading toward {location.continent}.",
            ],
            3: [  # Cryptic
                f"Something about their destination reminded me of {location.continent}...",
                f"They mentioned a place where they speak the local language.",
                f"I heard something about famous landmarks in that region.",
            ],
            4: [  # Very cryptic
                f"The winds seemed to call them toward distant lands...",
                f"They spoke of ancient wonders and modern marvels.",
                f"Their eyes sparkled when someone mentioned that continent.",
            ],
            5: [  # Riddles
                f"Where old meets new, where past meets future, there they go.",
                f"Follow the path of history to find them.",
                f"The answer lies where cultures converge.",
            ],
        }
        
        level_templates = templates.get(difficulty, templates[2])
        return random.choice(level_templates)
    
    def _fallback_suspect_clue(self, trait: str, value: str, difficulty: int) -> str:
        """Generate a template-based suspect clue as fallback."""
        if difficulty <= 2:
            return f"The person I saw had {value.lower()} for their {trait.lower()}."
        elif difficulty <= 4:
            return f"I noticed something distinctive about their {trait.lower()}..."
        else:
            return f"There was something memorable about them, but I can't quite place it..."
    
    def _fallback_red_herring(self, location: Location) -> str:
        """Generate a template-based red herring as fallback."""
        templates = [
            f"I think maybe they mentioned something about {location.continent}?",
            f"Was it {location.country}? I'm not entirely sure...",
            f"They might have said something about traveling that direction...",
        ]
        return random.choice(templates)
    
    def _random_witness(self) -> str:
        """Get a random witness name/type."""
        witnesses = [
            "Hotel Concierge",
            "Taxi Driver",
            "Street Vendor",
            "Museum Guard",
            "Local Guide",
            "Airport Worker",
            "Restaurant Owner",
            "Shop Keeper",
            "Police Officer",
            "Tour Guide",
        ]
        return random.choice(witnesses)
    
    def _random_unreliable_witness(self) -> str:
        """Get a random unreliable witness for red herrings."""
        witnesses = [
            "Confused Tourist",
            "Sleepy Security Guard",
            "Distracted Pedestrian",
            "Forgetful Local",
            "Uncertain Bystander",
        ]
        return random.choice(witnesses)

