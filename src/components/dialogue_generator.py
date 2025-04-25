"""
Dialogue Generator for Murder Mystery Game

This module uses the Groq API with Llama 3 to dynamically
generate dialogue for suspects based on their personalities.
It falls back to pre-written dialogue if the API is not available.
"""

import os
import json
import random
from typing import Dict, Any, Optional

# Get API key from environment variable or use a placeholder for development
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")

# Only import Groq if we have an API key
has_groq = GROQ_API_KEY != "your_groq_api_key_here"
client = None

if has_groq:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        print("Groq client initialized successfully.")
    except ImportError:
        has_groq = False
        print("Groq package not found. Using fallback dialogue.")
    except Exception as e:
        has_groq = False
        print(f"Error initializing Groq client: {e}")

class DialogueGenerator:
    def __init__(self):
        # Store previously generated dialogue to avoid repetition
        self.dialogue_cache = {}
        
        # Set API availability
        self.api_available = has_groq and client is not None
        
        if not self.api_available:
            print("Warning: No Groq API key found or client initialization failed. Using fallback dialogue generation.")
        else:
            print("AI dialogue generation enabled with Groq API.")
    
    def generate_dialogue(self, 
                          suspect_name: str, 
                          suspect_data: Dict[str, Any], 
                          scenario_info: Dict[str, Any],
                          interaction_count: int = 0) -> Dict[str, str]:
        """
        Generate dialogue for a suspect using the Groq API with Llama 3.
        Falls back to pre-written dialogue if API is unavailable.
        
        Args:
            suspect_name: Name of the suspect
            suspect_data: Dictionary containing suspect details
            scenario_info: Dictionary containing scenario info
            interaction_count: Number of times player has talked to this suspect
            
        Returns:
            Dictionary with dialogue components (alibi, testimony, additional remarks)
        """
        # Check if we have a cached dialogue for this suspect and interaction count
        cache_key = f"{suspect_name}_{interaction_count}"
        if cache_key in self.dialogue_cache:
            print(f"Using cached dialogue for {suspect_name}")
            return self.dialogue_cache[cache_key]
        
        # If API not available or suspect data missing, use fallback dialogue
        if not self.api_available or not suspect_data:
            print(f"Using fallback dialogue for {suspect_name} (API available: {self.api_available})")
            return self._generate_fallback_dialogue(suspect_name, suspect_data, interaction_count)
        
        try:
            print(f"Generating AI dialogue for {suspect_name}...")
            
            # Create personality description for the prompt
            personality = suspect_data.get("personality", "")
            appearance = suspect_data.get("appearance", "")
            speech_pattern = suspect_data.get("speech_pattern", "")
            testimony = suspect_data.get("testimony", "")
            alibi = suspect_data.get("alibi", "")
            guilty = suspect_data.get("guilty", False)
            
            # Create a prompt for the LLM
            system_message = f"""
            You are a dialogue writer for a murder mystery game. You need to generate realistic dialogue for a suspect being interviewed by a detective.
            
            THE MURDER SCENARIO:
            {scenario_info.get('title', 'A murder has occurred.')}
            {scenario_info.get('intro', '')}
            
            THE SUSPECT:
            Name: {suspect_name}
            Personality: {personality}
            Appearance: {appearance}
            Speech pattern: {speech_pattern}
            Alibi (core facts that must remain consistent): {alibi}
            Testimony (core facts that must remain consistent): {testimony}
            Guilty: {"Yes" if guilty else "No"} (This is secret information - the suspect does not know you know this)
            
            Instructions:
            1. Generate dialogue that reflects the suspect's personality, speech pattern, and emotional state
            2. The dialogue should include their alibi and testimony, but expressed in their own voice/style
            3. Add some behavioral details about how they act during questioning (nervous tics, body language, etc.)
            4. The dialogue should be believable and natural, as if from a detective novel
            5. Don't make the guilty suspect obviously guilty or innocent suspects clearly innocent
            6. This is interaction #{interaction_count+1} with the detective - make it progressively more revealing
            
            Additional details for continuity:
            - If guilty, the suspect should subtly avoid certain topics or be defensive in specific ways
            - If innocent, they should still have reasons to be nervous or hiding something unrelated to the murder
            """
            
            user_message = f"""
            Generate dialogue for {suspect_name} being interviewed about the murder of Thomas Miller.
            
            This is the detective's interaction #{interaction_count+1} with this suspect.
            
            Format the response as a JSON object with these fields:
            1. "alibi": How they describe their whereabouts during the murder (matching their alibi but in their own voice)
            2. "testimony": What they say they saw or know about the crime (matching their testimony but in their own voice)
            3. "behavioral_cue": A subtle behavioral detail the detective notices during the conversation
            4. "additional_remark": Something extra they mention that might be a clue or red herring
            5. "emotional_state": How they appear emotionally during this specific conversation
            
            VERY IMPORTANT: Format must be valid JSON with proper commas between fields.
            Keep each response concise - 1-2 sentences per field maximum.
            Remember to write in the character's unique voice/speech pattern.
            """
            
            try:
                # Call the Groq API with Llama 3
                from groq import Groq
                api_client = Groq(api_key=GROQ_API_KEY)
                response = api_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                )
                
                # Extract and parse the JSON from the response
                result_text = response.choices[0].message.content
                print(f"Raw API response: {result_text[:100]}...")  # Print first 100 chars for debugging
                
                # Try different approaches to extract valid JSON
                
                # Approach 1: Find JSON between curly braces
                start_index = result_text.find('{')
                end_index = result_text.rfind('}') + 1
                
                if start_index >= 0 and end_index > start_index:
                    json_str = result_text[start_index:end_index]
                    print(f"Extracted JSON substring: {json_str[:50]}...")
                    
                    # Clean up any comments or invalid JSON elements
                    json_str = self._clean_json_string(json_str)
                    print(f"Cleaned JSON: {json_str[:50]}...")
                    
                    import json
                    try:
                        dialogue_data = json.loads(json_str)
                        print("Successfully parsed JSON!")
                    except json.JSONDecodeError as e:
                        print(f"JSON parse error after cleaning: {e}")
                        # Fall back to regex extraction as a last resort
                        dialogue_data = {}
                        fields = ["alibi", "testimony", "behavioral_cue", "additional_remark", "emotional_state"]
                        import re
                        for field in fields:
                            # Use a more flexible pattern that can handle multi-line values
                            # and doesn't stop at the first quote
                            pattern = fr'"{field}"\s*:\s*"(.*?)(?:"|$)'
                            match = re.search(pattern, json_str, re.DOTALL)
                            if match:
                                # Get the captured text and clean up any escaped quotes
                                value = match.group(1).replace('\\"', '"')
                                # Clean up newlines and excessive whitespace
                                value = re.sub(r'\s+', ' ', value).strip()
                                dialogue_data[field] = value
                                print(f"Found {field} via regex: {value[:30]}...")
                        
                        if not dialogue_data:
                            raise ValueError("Could not extract any dialogue fields from response")
                    
                    # Create the dialogue dictionary, falling back to original data if missing
                    dialogue = {
                        "alibi": dialogue_data.get("alibi", alibi),
                        "testimony": dialogue_data.get("testimony", testimony),
                        "behavioral_cue": dialogue_data.get("behavioral_cue", ""),
                        "additional_remark": dialogue_data.get("additional_remark", ""),
                        "emotional_state": dialogue_data.get("emotional_state", "")
                    }
                    
                    # Cache the dialogue
                    self.dialogue_cache[cache_key] = dialogue
                    
                    return dialogue
                else:
                    print(f"Could not find JSON object in response for {suspect_name}")
                    return self._generate_fallback_dialogue(suspect_name, suspect_data, interaction_count)
                    
            except Exception as api_error:
                print(f"Error calling Groq API: {api_error}")
                return self._generate_fallback_dialogue(suspect_name, suspect_data, interaction_count)
                
        except Exception as e:
            print(f"Error generating dialogue with LLM: {e}")
            return self._generate_fallback_dialogue(suspect_name, suspect_data, interaction_count)
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean a JSON string that might contain comments or invalid syntax"""
        import re
        
        # Remove JavaScript/JSON comments
        json_str = re.sub(r'//.*?(\n|$)', '', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Replace single quotes with double quotes
        json_str = json_str.replace("'", '"')
        
        # Fix common JSON issues with missing commas between key-value pairs
        # Look for patterns like "key": "value" "nextKey":
        json_str = re.sub(r'"\s*:\s*"([^"]*?)"\s+"([^"]+?)"', r'": "\1", "\2"', json_str)
        
        # Fix missing commas after nested objects or arrays
        json_str = re.sub(r'}\s*"', '}, "', json_str)
        json_str = re.sub(r']\s*"', '], "', json_str)
        
        # Try to handle any remaining issues with a more aggressive approach
        try:
            import json
            # First attempt to parse as is
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            # If it fails, try a more aggressive cleaning
            print(f"Initial JSON parsing failed: {e}, attempting more aggressive cleaning")
            
            # Extract individual fields we know should be in the response
            fields = ["alibi", "testimony", "behavioral_cue", "additional_remark", "emotional_state"]
            result = {}
            
            for field in fields:
                # Use a more flexible pattern that can capture until the next field or end of string
                pattern = fr'"{field}"\s*:\s*"(.*?)(?:"\s*,\s*"|"\s*}}|$)'
                match = re.search(pattern, json_str, re.DOTALL)
                if match:
                    # Get the captured text and clean up any escaped quotes
                    value = match.group(1).replace('\\"', '"')
                    # Clean up newlines and excessive whitespace
                    value = re.sub(r'\s+', ' ', value).strip()
                    result[field] = value
            
            # If we found any fields, convert back to a JSON string
            if result:
                return json.dumps(result)
            
            # Last resort: create a minimal valid JSON with empty strings
            fallback = {field: "" for field in fields}
            return json.dumps(fallback)
    
    def _generate_fallback_dialogue(self, 
                                   suspect_name: str, 
                                   suspect_data: Dict[str, Any],
                                   interaction_count: int) -> Dict[str, str]:
        """Generate fallback dialogue when API is not available"""
        alibi = suspect_data.get("alibi", "I don't remember where I was.")
        testimony = suspect_data.get("testimony", "I don't know anything about it.")
        
        # Enhanced fallback behavioral cues based on suspect
        behavioral_cues = {
            "Alice Cooper": [
                "She tucks her hair behind her ear nervously.",
                "Her eyes dart away when mentioning Thomas.",
                "She speaks with careful precision, weighing each word.",
                "You notice her shoulders tense up when you mention the time of death.",
                "She fidgets with her pen, clicking it repeatedly during your questions."
            ],
            "Bob Johnson": [
                "He straightens his expensive watch with a practiced gesture.",
                "A flash of anger crosses his face before he composes himself.",
                "He shifts the conversation away from work topics quickly.",
                "His smile never quite reaches his eyes as he speaks.",
                "You notice him glancing at his phone as if expecting an important call."
            ],
            "Charlie Miller": [
                "His hands shake slightly as he pulls at his collar.",
                "He runs his hand through his unkempt hair repeatedly.",
                "The smell of alcohol lingers faintly on his breath.",
                "He can't seem to maintain eye contact for more than a few seconds.",
                "There's a nervous twitch at the corner of his mouth when you mention the murder weapon."
            ]
        }
        
        # Enhanced fallback additional remarks
        additional_remarks = {
            "Alice Cooper": [
                "I always thought Thomas was too reckless with people's feelings.",
                "We were all tired of his arrogance, to be honest.",
                "I keep thinking if I had checked on him earlier that night...",
                "Thomas mentioned receiving threatening emails recently, but wouldn't say from whom.",
                "The last time I saw him alive, he was arguing with someone on the phone."
            ],
            "Bob Johnson": [
                "Thomas never understood that sometimes rules need to be... flexible in business.",
                "He was going to ruin everything I worked for over a technicality.",
                "Look, everyone at the firm cuts corners. Thomas was no saint either.",
                "I heard he was planning to meet with a journalist the day after he died.",
                "His office was searched before the police arrived - someone was looking for something."
            ],
            "Charlie Miller": [
                "I might've hated him for a while, but family is family in the end.",
                "The divorce was ugly, but I wouldn't kill over it.",
                "We actually made peace over that bottle of whiskey. Ironic, isn't it?",
                "Thomas called me the night he died, sounding paranoid about something he'd discovered.",
                "I saw someone lurking outside his house when I left - thought it was just a neighbor."
            ]
        }
        
        # Enhanced fallback emotional states
        emotional_states = {
            "Alice Cooper": [
                "Composed but with underlying tension",
                "Analytical and deliberately calm",
                "Quietly distraught beneath a professional veneer",
                "Slightly defensive when discussing her whereabouts",
                "Maintaining a practiced professional detachment"
            ],
            "Bob Johnson": [
                "Confidently defensive",
                "Irritated beneath a thin smile",
                "Dismissive with flashes of concern",
                "Impatient and slightly condescending",
                "Calculated and measuring each response carefully"
            ],
            "Charlie Miller": [
                "Emotionally raw and unfiltered",
                "Griefstricken with moments of anger",
                "Exhausted and resigned",
                "Fluctuating between defensive and vulnerable",
                "Struggling to maintain composure through obvious distress"
            ]
        }
        
        # Get appropriate fallbacks based on suspect name
        cues = behavioral_cues.get(suspect_name, ["They seem uncomfortable."])
        remarks = additional_remarks.get(suspect_name, ["I don't know what else to tell you."])
        states = emotional_states.get(suspect_name, ["Nervous"])
        
        # Select based on interaction count (cycling if needed)
        index = interaction_count % len(cues)
        
        return {
            "alibi": alibi,
            "testimony": testimony,
            "behavioral_cue": cues[index],
            "additional_remark": remarks[index],
            "emotional_state": states[index]
        }

# Create a singleton instance
dialogue_generator = DialogueGenerator() 