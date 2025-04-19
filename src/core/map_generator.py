"""
Map generator for the murder mystery game.

This module handles generating map files from the case data.
"""

from data.case_data import CLUES, SUSPECTS

def generate_entity_section(base_entities):
    """
    Generates the entity section for a map file based on base entities and case data.
    
    Args:
        base_entities: List of base entities for the map (trees, rocks, teleporters, etc.)
        
    Returns:
        The entity section as a string
    """
    entity_lines = list(base_entities)  # Copy base entities
    
    # Add clues
    for clue in CLUES:
        x, y = clue["map_position"]
        entity_lines.append(f"7,{x},{y},{clue['text']},{clue['name']}")
    
    # Add suspects - match the format expected by the entity factory
    # The expected format is: 8,x,y,name,alibi,testimony,guilty,image
    for suspect in SUSPECTS:
        x, y = suspect["map_position"]
        guilty_str = "true" if suspect["guilty"] else "false"
        suspect_line = f"8,{x},{y},{suspect['name']},{suspect['alibi']},{suspect['testimony']},{guilty_str},{suspect['image']}"
        entity_lines.append(suspect_line)
    
    return "\n".join(entity_lines)

def update_map_file(map_file, base_entities_only=False):
    """
    Updates a map file with entities from the case data.
    
    Args:
        map_file: Path to the map file
        base_entities_only: If True, only include base entities (not clues or suspects)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the map file
        with open(f"content/maps/{map_file}", "r") as f:
            content = f.read()
        
        # Split the map into the map section and entity section
        sections = content.split('-')
        if len(sections) != 2:
            print(f"Error: Map file {map_file} has an invalid format.")
            return False
        
        map_section = sections[0]
        entity_section = sections[1].strip().split('\n')
        
        # Filter out clues and suspects from the entity section
        base_entities = []
        for line in entity_section:
            if line and not line.startswith("7,") and not line.startswith("8,"):
                base_entities.append(line)
        
        # Generate the new entity section
        if base_entities_only:
            new_entity_section = "\n".join(base_entities)
        else:
            new_entity_section = generate_entity_section(base_entities)
        
        # Write the updated map file
        with open(f"content/maps/{map_file}", "w") as f:
            f.write(map_section)
            f.write("-\n")
            f.write(new_entity_section)
        
        return True
    except Exception as e:
        print(f"Error updating map file: {e}")
        return False

def generate_map_files():
    """
    Updates all map files in the content/maps directory.
    Only the main map (start.map) will have the clues and suspects.
    """
    import os
    
    # Get a list of all map files
    map_files = [f for f in os.listdir("content/maps") if f.endswith(".map")]
    
    for map_file in map_files:
        # Only add clues and suspects to start.map
        base_entities_only = (map_file != "start.map")
        update_map_file(map_file, base_entities_only)
        
        print(f"Updated map file: {map_file}") 