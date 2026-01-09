"""World map component using pydeck for visualization."""

import streamlit as st
import pydeck as pdk
from typing import Optional

from ...models import Location


def render_world_map(
    current_location: Location,
    available_destinations: list[Location],
    visited_locations: list[str],
    suspect_path: Optional[list[Location]] = None,
    show_path: bool = False,
) -> Optional[str]:
    """
    Render an interactive world map with locations.
    
    Args:
        current_location: Player's current location
        available_destinations: Locations player can travel to
        visited_locations: IDs of locations already visited
        suspect_path: The suspect's actual path (for debug/reveal)
        show_path: Whether to show the suspect's path
    
    Returns:
        ID of selected destination if clicked, None otherwise
    """
    # Prepare location data for layers
    current_data = [{
        "name": current_location.city,
        "lat": current_location.latitude,
        "lon": current_location.longitude,
        "color": [196, 163, 90, 255],  # Gold for current
        "size": 50000,
    }]
    
    destination_data = []
    visited_data = []
    
    for loc in available_destinations:
        point = {
            "id": loc.id,
            "name": loc.city,
            "country": loc.country,
            "lat": loc.latitude,
            "lon": loc.longitude,
        }
        
        if loc.id in visited_locations:
            point["color"] = [100, 100, 100, 200]  # Gray for visited
            point["size"] = 25000
            visited_data.append(point)
        else:
            point["color"] = [74, 124, 124, 255]  # Teal for available
            point["size"] = 35000
            destination_data.append(point)
    
    # Create layers
    layers = []
    
    # Visited locations layer
    if visited_data:
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=visited_data,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius="size",
            pickable=False,
            opacity=0.6,
        ))
    
    # Available destinations layer
    if destination_data:
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=destination_data,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius="size",
            pickable=True,
            opacity=0.8,
        ))
    
    # Current location layer (on top)
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=current_data,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius="size",
        pickable=False,
        opacity=1.0,
    ))
    
    # Travel lines from current to available destinations
    arc_data = []
    for loc in available_destinations:
        if loc.id not in visited_locations:
            arc_data.append({
                "source_lat": current_location.latitude,
                "source_lon": current_location.longitude,
                "target_lat": loc.latitude,
                "target_lon": loc.longitude,
            })
    
    if arc_data:
        layers.append(pdk.Layer(
            "ArcLayer",
            data=arc_data,
            get_source_position=["source_lon", "source_lat"],
            get_target_position=["target_lon", "target_lat"],
            get_source_color=[196, 163, 90, 100],
            get_target_color=[74, 124, 124, 150],
            get_width=2,
        ))
    
    # Set view state centered on current location
    view_state = pdk.ViewState(
        latitude=current_location.latitude,
        longitude=current_location.longitude,
        zoom=2,
        pitch=30,
    )
    
    # Create deck with custom styling
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={
            "text": "{name}, {country}",
            "style": {
                "backgroundColor": "#2A1810",
                "color": "#F5E6D3",
                "fontFamily": "Georgia, serif",
            }
        },
    )
    
    # Render the map
    st.pydeck_chart(deck, use_container_width=True)
    
    return None  # pydeck doesn't support click events directly in Streamlit


def render_travel_options(
    current_location: Location,
    destinations: list[Location],
    visited_locations: list[str],
) -> Optional[str]:
    """
    Render travel destination options as a list.
    
    Returns the ID of the selected destination.
    """
    st.markdown("""
    <div style="
        background: #3D2817;
        padding: 12px 16px;
        border-radius: 8px 8px 0 0;
        margin-top: 16px;
    ">
        <h4 style="
            color: #C4A35A;
            margin: 0;
            font-family: 'Playfair Display', serif;
        ">
            ✈️ Available Destinations
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    selected_destination = None
    
    # Sort destinations by distance
    destinations_with_time = []
    for dest in destinations:
        travel_time = current_location.get_travel_time_to(dest)
        destinations_with_time.append((dest, travel_time))
    
    destinations_with_time.sort(key=lambda x: x[1])
    
    for dest, travel_time in destinations_with_time:
        is_visited = dest.id in visited_locations
        
        # Style based on visited status
        bg_color = "#D4B896" if not is_visited else "#999"
        text_color = "#2A1810" if not is_visited else "#555"
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: {bg_color};
                padding: 12px;
                margin: 4px 0;
                border-radius: 4px;
                border-left: 4px solid {'#C4A35A' if not is_visited else '#666'};
            ">
                <div style="color: {text_color}; font-weight: bold;">
                    {dest.city}, {dest.country}
                </div>
                <div style="color: {text_color}; font-size: 12px; opacity: 0.8;">
                    {dest.continent} • {travel_time} hours
                    {'(visited)' if is_visited else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✈️ Go", key=f"travel_{dest.id}", disabled=is_visited):
                selected_destination = dest.id
    
    return selected_destination


def render_mini_map(
    current_location: Location,
    visited_locations: list[Location],
) -> None:
    """Render a small overview map for the header."""
    # Simplified version for header display
    all_points = [{
        "lat": current_location.latitude,
        "lon": current_location.longitude,
        "color": [196, 163, 90, 255],
        "size": 30000,
    }]
    
    for loc in visited_locations:
        if loc.id != current_location.id:
            all_points.append({
                "lat": loc.latitude,
                "lon": loc.longitude,
                "color": [100, 100, 100, 150],
                "size": 15000,
            })
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=all_points,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius="size",
    )
    
    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=0.5,
        pitch=0,
    )
    
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        height=150,
    )
    
    st.pydeck_chart(deck, use_container_width=True)

