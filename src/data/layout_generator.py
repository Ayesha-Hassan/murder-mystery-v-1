"""
Layout Generator for Murder Mystery Game

This module uses the Groq API with Llama 3 to dynamically
generate layouts for suspects and clues in the murder mystery game.
"""

import os
import json
import random
import re
from groq import Groq
from typing import List, Dict, Tuple, Any

# Get API key from environment variable or use a placeholder for development
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")

# Debug output for API key detection
if GROQ_API_KEY == "your_groq_api_key_here":
    print("Warning: Using placeholder API key - LLM layout generation will be disabled")
else:
    masked_key = f"{GROQ_API_KEY[:4]}{'*' * (len(GROQ_API_KEY) - 8)}{GROQ_API_KEY[-4:]}" if len(GROQ_API_KEY) > 8 else "****"
    print(f"Using Groq API key: {masked_key}")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def clean_json_string(json_str: str) -> str:
    """
    Clean a JSON string that might contain comments or other non-standard elements.
    
    Args:
        json_str: The JSON string to clean
        
    Returns:
        A cleaned JSON string
    """
    # Remove JavaScript/JSON comments (both // and /* */)
    json_str = re.sub(r'//.*?(\n|$)', '', json_str)  # Remove // comments
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)  # Remove /* */ comments
    
    # Remove any trailing commas before closing brackets
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Clean up any other invalid characters
    json_str = json_str.replace("'", '"')  # Replace single quotes with double quotes
    
    return json_str

def get_map_dimensions(map_file: str) -> Tuple[int, int]:
    """
    Determine the dimensions of the map from the map file.
    
    Args:
        map_file: Path to the map file
        
    Returns:
        Tuple of (width, height) in tile units
    """
    try:
        map_path = f"content/maps/{map_file}"
        with open(map_path, "r") as f:
            content = f.read()
            
        # Split the map into the tile section
        tile_section = content.split('-')[0].strip()
        lines = tile_section.strip().split('\n')
        
        height = len(lines)
        width = max(len(line) for line in lines)
        
        return width, height
    except Exception as e:
        print(f"Error getting map dimensions: {e}")
        # Default fallback dimensions if we can't read the map
        return 25, 20

def is_valid_position(x: int, y: int, width: int, height: int, occupied_positions: List[Tuple[int, int]]) -> bool:
    """
    Check if a position is valid (within bounds and not occupied).
    
    Args:
        x, y: Position to check
        width, height: Map dimensions
        occupied_positions: List of already occupied positions
        
    Returns:
        True if position is valid, False otherwise
    """
    # Check bounds
    if x < 0 or y < 0 or x >= width or y >= height:
        return False
        
    # Check if position is already occupied
    if (x, y) in occupied_positions:
        return False
        
    return True

def generate_layout_with_llm(clues: List[Dict[str, Any]], suspects: List[Dict[str, Any]], map_file: str = "start.map") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Use the Groq API with Llama 3 to generate positions for clues and suspects.
    
    Args:
        clues: List of clue dictionaries
        suspects: List of suspect dictionaries
        map_file: The map file to use for dimensions
        
    Returns:
        Updated lists of clues and suspects with new positions
    """
    
    # First try to use the LLM to generate a layout
    try:
        if GROQ_API_KEY == "your_groq_api_key_here":
            print("No valid Groq API key found. Using fallback random layout generation.")
            return generate_random_layout(clues, suspects, map_file)
            
        print("Attempting to generate layout with Llama 3 via Groq API...")
        # Get map dimensions
        width, height = get_map_dimensions(map_file)
        
        # Create a prompt for the LLM
        scenario_description = "\n".join([
            clue["description"] for clue in clues
        ]) + "\n" + "\n".join([
            f"{suspect['name']}: {suspect['testimony']}" for suspect in suspects
        ])
        
        # Create a system message that explains the task
        system_message = f"""
        You are a game layout designer for a murder mystery game. 
        The game takes place on a 2D map of size {width}x{height} tiles.
        
        You need to place {len(clues)} clues and {len(suspects)} suspects on the map in logical locations.
        
        Here's information about the murder case:
        {scenario_description}
        
        The murder took place near a lake. Suspects should be positioned in separate areas.
        Clues should be distributed logically based on the scenario.
        
        The output should be a JSON object with two arrays:
        1. "clue_positions": array of [x, y] coordinates for each clue
        2. "suspect_positions": array of [x, y] coordinates for each suspect
        
        Ensure all positions are within the map boundaries (0 to {width-1} for x, 0 to {height-1} for y).
        Positions should make logical sense based on the murder scenario.
        """
        
        # User message requesting the layout
        user_message = f"""
        Create a layout for the following case elements:
        
        Clues:
        {json.dumps([{"name": clue["name"], "description": clue["description"]} for clue in clues], indent=2)}
        
        Suspects:
        {json.dumps([{"name": suspect["name"], "alibi": suspect["alibi"]} for suspect in suspects], indent=2)}
        
        Please output ONLY the JSON object with the positions, nothing else.
        """
        
        print("Sending request to Groq API...")
        try:
            # Call the Groq API with Llama 3
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            print("Successfully received response from Groq API")
        except Exception as api_error:
            print(f"Error calling Groq API: {api_error}")
            return generate_random_layout(clues, suspects, map_file)
        
        # Extract and parse the JSON from the response
        result_text = response.choices[0].message.content
        print(f"Raw API response: {result_text[:100]}{'...' if len(result_text) > 100 else ''}")
        
        # Clean up the response to extract just the JSON
        start_index = result_text.find('{')
        end_index = result_text.rfind('}') + 1
        
        if start_index >= 0 and end_index > start_index:
            json_str = result_text[start_index:end_index]
            print(f"Extracted JSON: {json_str[:100]}{'...' if len(json_str) > 100 else ''}")
            
            try:
                # Clean the JSON string to remove comments
                cleaned_json = clean_json_string(json_str)
                print(f"Cleaned JSON: {cleaned_json[:100]}{'...' if len(cleaned_json) > 100 else ''}")
                
                layout_data = json.loads(cleaned_json)
                print(f"Parsed JSON successfully with keys: {list(layout_data.keys())}")
                
                # Update clue positions
                if "clue_positions" in layout_data and len(layout_data["clue_positions"]) == len(clues):
                    for i, clue in enumerate(clues):
                        x, y = layout_data["clue_positions"][i]
                        clue["map_position"] = (x, y)
                        
                # Update suspect positions
                if "suspect_positions" in layout_data and len(layout_data["suspect_positions"]) == len(suspects):
                    for i, suspect in enumerate(suspects):
                        x, y = layout_data["suspect_positions"][i]
                        suspect["map_position"] = (x, y)
                        
                print("Successfully generated layout with Llama 3!")
                return clues, suspects
            except json.JSONDecodeError as json_error:
                print(f"Error parsing JSON from LLM response: {json_error}")
                print("Using fallback random layout generation.")
                return generate_random_layout(clues, suspects, map_file)
        else:
            print(f"Could not extract valid JSON from LLM response. Start index: {start_index}, End index: {end_index}")
            print("Using fallback method.")
            return generate_random_layout(clues, suspects, map_file)
            
    except Exception as e:
        print(f"Error generating layout with LLM: {e}")
        import traceback
        traceback.print_exc()
        print("Using fallback random layout generation.")
        return generate_random_layout(clues, suspects, map_file)

def generate_random_layout(clues: List[Dict[str, Any]], suspects: List[Dict[str, Any]], map_file: str = "start.map") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate random positions for clues and suspects as a fallback.
    
    Args:
        clues: List of clue dictionaries
        suspects: List of suspect dictionaries
        map_file: The map file to use for dimensions
        
    Returns:
        Updated lists of clues and suspects with new positions
    """
    width, height = get_map_dimensions(map_file)
    occupied_positions = []
    
    # Assign positions to suspects (more important for gameplay)
    for suspect in suspects:
        for _ in range(20):  # Try up to 20 times to find a valid position
            x = random.randint(3, width - 4)  # Keep away from edges
            y = random.randint(3, height - 4)
            
            if is_valid_position(x, y, width, height, occupied_positions):
                suspect["map_position"] = (x, y)
                occupied_positions.append((x, y))
                break
        else:
            # Fallback if we couldn't find a valid position
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            suspect["map_position"] = (x, y)
            occupied_positions.append((x, y))
    
    # Assign positions to clues
    for clue in clues:
        for _ in range(20):  # Try up to 20 times to find a valid position
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            if is_valid_position(x, y, width, height, occupied_positions):
                clue["map_position"] = (x, y)
                occupied_positions.append((x, y))
                break
        else:
            # Fallback if we couldn't find a valid position
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            clue["map_position"] = (x, y)
            occupied_positions.append((x, y))
    
    print("Generated random layout as fallback.")
    return clues, suspects

def update_case_with_dynamic_layout(case_data_module: str = "data.case_data"):
    """
    Update the case data with dynamically generated layout positions.
    
    Args:
        case_data_module: Python module path to case data
    """
    try:
        # Import the case data module dynamically
        import importlib
        case_module = importlib.import_module(case_data_module)
        
        # Generate new layout
        updated_clues, updated_suspects = generate_layout_with_llm(
            case_module.CLUES.copy(), 
            case_module.SUSPECTS.copy()
        )
        
        # Update the module's global variables
        # Note: This doesn't modify the actual file, only the runtime values
        case_module.CLUES = updated_clues
        case_module.SUSPECTS = updated_suspects
        
        print("Case data updated with dynamic layout.")
        
        # Print out the new positions for debugging
        print("\nNew clue positions:")
        for clue in case_module.CLUES:
            print(f"  {clue['name']}: {clue['map_position']}")
            
        print("\nNew suspect positions:")
        for suspect in case_module.SUSPECTS:
            print(f"  {suspect['name']}: {suspect['map_position']}")
            
    except Exception as e:
        print(f"Error updating case data: {e}")

# Function to call from main.py before initializing the area
def initialize_dynamic_layout():
    """
    Initialize the dynamic layout for the game.
    Call this before creating the Area instance.
    """
    update_case_with_dynamic_layout() 