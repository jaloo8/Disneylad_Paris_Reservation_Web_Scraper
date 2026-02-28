"""
Disneyland Paris table-service restaurants that accept reservations.
Names should match the official Disneyland Paris site for booking.
Grouped by area for the dropdown; flattened list for config.
Sources: official site, DLP guides, dein-dlrp (2025–2026).
"""

# (Area label, restaurant name) — order matches typical reservation site grouping
RESTAURANTS_BY_AREA: list[tuple[str, str]] = [
    # Disneyland Park
    ("Disneyland Park — Main Street", "Plaza Gardens Restaurant"),
    ("Disneyland Park — Main Street", "Victoria's Homestyle Restaurant"),
    ("Disneyland Park — Main Street", "Walt's - An American Restaurant"),
    ("Disneyland Park — Fantasyland", "Auberge de Cendrillon"),
    ("Disneyland Park — Adventureland", "Captain Jack's - Restaurant des Pirates"),
    ("Disneyland Park — Adventureland", "Restaurant Agrabah Café"),
    ("Disneyland Park — Frontierland", "Silver Spur Steakhouse"),
    ("Disneyland Park — Frontierland", "The Lucky Nugget Saloon"),
    # Walt Disney Studios Park
    ("Walt Disney Studios Park", "Bistrot Chez Rémy"),
    ("Walt Disney Studios Park", "PYM Kitchen"),
    # Disneyland Hotel
    ("Disneyland Hotel", "California Grill"),
    ("Disneyland Hotel", "La Table de Lumière"),
    ("Disneyland Hotel", "Downtown Restaurant"),
    # Other Disney Hotels
    ("Hotel New York - Art of Marvel", "Manhattan Restaurant"),
    ("Disney's Newport Bay Club", "Yacht Club"),
    ("Disney's Sequoia Lodge", "Hunter's Grill"),
    ("Disney's Sequoia Lodge", "Beaver Creek Tavern"),
    ("Disney's Hotel Cheyenne", "Crockett's Tavern"),
    ("Disney's Hotel Cheyenne", "La Cantina"),
    # Disney Village
    ("Disney Village", "Annette's Diner"),
    ("Disney Village", "Billy Bob's Country Western Saloon"),
    ("Disney Village", "Brasserie Rosalie"),
    ("Disney Village", "Rainforest Café"),
    ("Disney Village", "The Steakhouse"),
    ("Disney Village", "The Royal Pub"),
]

# Flat list of names only (for selectbox value and config)
RESTAURANT_NAMES: list[str] = [name for _, name in RESTAURANTS_BY_AREA]

# Dropdown display: "Area — Name" so users can find by land/hotel
RESTAURANT_OPTIONS: list[str] = [f"{area} — {name}" for area, name in RESTAURANTS_BY_AREA]


def display_to_name(display: str) -> str:
    """Convert dropdown label 'Area — Name' back to restaurant name (last part after ' — ')."""
    if " — " in display:
        return display.split(" — ")[-1].strip()
    return display.strip()


def name_to_display(name: str) -> str | None:
    """Convert saved config name to dropdown label if it's in our list."""
    for opt in RESTAURANT_OPTIONS:
        if display_to_name(opt) == name:
            return opt
    return None
