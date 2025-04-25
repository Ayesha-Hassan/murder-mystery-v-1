"""
Murder Mystery Game Case Data

This file centralizes all the case information, including:
- Scenario details (title, intro text)
- Victim information
- Clues (descriptions and map positions)
- Suspects (descriptions, testimonies, alibis, and map positions)
- Evidence and solution details
"""

# Murder scenario information
SCENARIO_TITLE = "The Campsite Killing"

SCENARIO_INTRO = """
A group of five friends went camping in the woods for a weekend getaway. 
On the second night, Thomas Miller was found dead near the lake, about 100 yards from the campsite.
His body was discovered at dawn by his friend Alice who had gone for an early morning walk.
The cause of death appears to be blunt force trauma to the head, likely from a large rock found nearby covered in blood.
The time of death is estimated to be between 11PM and 2AM.

As the detective called to the scene, you must investigate the clues and interview the suspects to determine who killed Thomas.
"""

# Victim information
VICTIM = {
    "name": "Thomas Miller",
    "age": 32,
    "description": "An investment banker from the city. Known to be arrogant and competitive.",
    "personality": "Thomas was ambitious and ruthless in his professional life, often stepping on others to get ahead. Despite this, he could be charming and generous with friends. He had a tendency to be condescending to those he felt were beneath him and was known for holding grudges. He was meticulous about his appearance and liked expensive things.",
    "relationships": {
        "Alice": "College friend. They dated briefly 5 years ago.",
        "Bob": "Coworker and longtime rival at the same investment firm.",
        "Charlie": "Thomas's brother-in-law. Married to Thomas's sister who recently filed for divorce."
    }
}

# Clues information with descriptions and map positions
CLUES = [
    {
        "name": "Bloody Rock",
        "description": "A large rock covered in blood, found near the victim's body. The murder weapon.",
        "location": "By the lake shore",
        "insights": "The blood pattern suggests the killer likely got blood on their clothes.",
        "map_position": (3, 7),  # x, y position on the map
        "text": "A large rock covered in blood, found near the victim's body."
    },
    {
        "name": "Torn Jacket Piece",
        "description": "A piece of green fabric torn from a jacket, caught on a branch near the crime scene.",
        "location": "On a thorny bush near the path to the lake",
        "insights": "The fabric matches Charlie's jacket.",
        "map_position": (10, 10),
        "text": "A piece of green fabric torn from a jacket, caught on a branch near the crime scene."
    },
    {
        "name": "Footprints",
        "description": "A set of footprints leading from the campsite to the lake, and then away towards the old hiking trail.",
        "location": "Path between campsite and lake",
        "insights": "The shoe size appears to be around a men's 11.",
        "map_position": (15, 3),
        "text": "A set of footprints leading from the campsite to the lake, and then away."
    },
    {
        "name": "Victim's Phone",
        "description": "Thomas's smartphone with a cracked screen. The last message was to Bob: 'We need to talk about what you did. Meet me by the lake at midnight.'",
        "location": "In the victim's pocket",
        "insights": "Suggests Thomas planned to meet Bob shortly before his estimated time of death.",
        "map_position": (18, 12),
        "text": "Thomas's smartphone with a text to Bob: 'Meet me by the lake at midnight.'"
    },
    {
        "name": "Empty Whiskey Bottle",
        "description": "An empty bottle of expensive whiskey with two sets of fingerprints.",
        "location": "Near the victim's body",
        "insights": "The fingerprints belong to Thomas and Charlie.",
        "map_position": (6, 14),
        "text": "An empty whiskey bottle with fingerprints from Thomas and Charlie."
    }
]

# Suspects information with alibis, testimonies, map positions, and guilt status
SUSPECTS = [
    {
        "name": "Alice Cooper", 
        "alibi": "I was in my tent reading until I fell asleep around 10:30PM.",
        "testimony": "I heard Thomas arguing with someone around 10PM, but couldn't make out who it was. I found his body in the morning when I went for a walk.",
        "additional_info": "Thomas broke my heart years ago. We've been just friends since, but it was sometimes awkward.",
        "personality": "Alice is reserved and intellectual, preferring books to social gatherings. She has a strong moral compass and believes in justice, which is why she became an environmental lawyer. While generally calm and composed, she can be deeply emotional about past relationships. She's observant and analytical, often noticing details others miss. Despite her outward confidence, she harbors insecurities about her past failed relationship with Thomas.",
        "appearance": "Mid-30s woman with shoulder-length brown hair typically worn in a practical ponytail. She dresses in casual, outdoorsy clothing and wears minimal makeup. She's physically fit from regular hiking and yoga.",
        "speech_pattern": "Speaks carefully and precisely, using proper grammar and sometimes technical terms. Tends to pause before answering difficult questions, as if carefully weighing her words.",
        "guilty": False,
        "image": "suspect_alice.png",
        "map_position": (4, 4)
    },
    {
        "name": "Bob Johnson",
        "alibi": "I was fishing at the other side of the lake until around midnight, then went straight to sleep.",
        "testimony": "Thomas was threatening to report some... creative accounting I did that made us both look good. He suddenly grew a conscience.",
        "additional_info": "Thomas and I were competing for the same promotion. He found out I fudged some numbers.",
        "personality": "Bob is ambitious and ruthlessly competitive, willing to bend rules to get ahead. He's charming and sociable on the surface but harbors deep insecurities about his status. He's easily threatened by others' success and has a quick temper when challenged. Despite his cutthroat nature in business, he can be generous and loyal to friends who don't compete with him. He's driven by a fear of failure and will go to great lengths to maintain his image of success.",
        "appearance": "Mid-30s man with perfectly styled short blonde hair and an expensive haircut. Always dressed impeccably in designer outdoor gear that looks barely used. Maintains a fit physique through regular gym sessions.",
        "speech_pattern": "Speaks confidently and quickly, often using business jargon and industry terms. Has a habit of deflecting uncomfortable questions with humor or counter-questions. Occasionally stutters when genuinely nervous.",
        "guilty": True,  # Bob is the murderer
        "image": "suspect_bob.png",
        "map_position": (9, 9)
    },
    {
        "name": "Charlie Miller",
        "alibi": "I was drinking with Thomas until around 11PM, then went to sleep in my tent.",
        "testimony": "We actually had a good talk and cleared the air about my divorce. I'm sad we finally made peace just before he died.",
        "additional_info": "I was angry at him for taking my wife's side in our divorce, but we made peace that night.",
        "personality": "Charlie is emotionally volatile with a tendency to hold grudges, though he genuinely tries to be a good person. He struggles with alcohol when under stress, which can make his emotions even more unpredictable. He values family deeply and was devastated by his divorce and the perceived betrayal from Thomas. He's generally honest to a fault, wearing his emotions on his sleeve. Despite his rough exterior, he's surprisingly sensitive and can be deeply hurt by criticism or rejection.",
        "appearance": "Late 30s man with unkempt dark hair and a perpetual five o'clock shadow. Usually dressed in worn jeans and flannel shirts, with a distinctive green jacket he's had for years. Physically strong from his construction work.",
        "speech_pattern": "Speaks in a gruff, direct manner with occasional profanity. His voice often reveals his emotional state - rising when upset and softening when reflective. Tends to speak in shorter sentences and simple terms.",
        "guilty": False,
        "image": "suspect_charlie.png",
        "map_position": (14, 14)
    }
]

# Evidence that points to each suspect
SUSPECT_EVIDENCE = {
    "Alice Cooper": [
        "Had past romantic history with Thomas that ended badly",
        "Was the first to find the body",
        "Has no confirmed alibi for the time of murder"
    ],
    "Bob Johnson": [
        "Had clear motive - Thomas was threatening to expose his fraud",
        "The victim's phone shows they were supposed to meet at the time of death",
        "Shoe size matches the footprints found at the scene (size 11)",
        "Claims to have been fishing, but no one can verify his whereabouts"
    ],
    "Charlie Miller": [
        "His green jacket has a torn piece matching the fabric found near the scene",
        "His fingerprints were on the whiskey bottle found near the body",
        "Had a history of arguments with Thomas over the divorce"
    ]
}

# Solution to the murder with explanation
SOLUTION = """
Bob Johnson is the murderer. The evidence points to him:

1. Thomas's text message shows they were meeting by the lake at midnight, placing Bob at the scene
2. Bob had a strong motive - Thomas was going to expose his fraudulent accounting
3. The footprints at the scene match Bob's shoe size
4. Bob's alibi of fishing alone at night is suspicious and unverifiable

Bob met Thomas as requested, argued about the accounting fraud, and in fear of losing his career, 
grabbed a rock and struck Thomas in the head. He then tried to make it look like a robbery gone wrong.
"""

# Character relationships and dynamics
CHARACTER_DYNAMICS = {
    "History": """
    Thomas, Alice, and Bob went to college together, where Thomas and Alice dated briefly. 
    Bob was always envious of Thomas's success and charisma, though they maintained a friendship.
    Charlie met Thomas when he married Thomas's sister five years ago, but their relationship 
    became strained during the divorce proceedings when Thomas sided with his sister.
    """,
    
    "Recent Tensions": """
    In the weeks before the camping trip, tensions were high:
    - Bob and Thomas were competing for the same promotion at work
    - Charlie's divorce from Thomas's sister had just been finalized
    - Alice had been avoiding Thomas since he made unwelcome advances at a previous gathering
    """,
    
    "Camping Trip Dynamics": """
    The camping trip was organized by Alice as a way to get the group together 
    one last time before Bob and Thomas would find out who got the promotion.
    During the trip, Charlie and Thomas were seen arguing on the first night, but 
    seemed to make peace on the second day. Bob remained outwardly friendly with Thomas
    but witnesses noticed tension whenever work was discussed.
    """
}

# Function to generate map entities for clues and suspects
def generate_map_entities():
    """
    Returns a list of entity definitions that can be added to a map file.
    Each string follows the format expected by the map loader.
    """
    entities = []
    
    # Add clues
    for clue in CLUES:
        x, y = clue["map_position"]
        entities.append(f"7,{x},{y},{clue['text']},{clue['name']}")
    
    # Add suspects
    for suspect in SUSPECTS:
        x, y = suspect["map_position"]
        guilty_str = "true" if suspect["guilty"] else "false"
        entities.append(f"8,{x},{y},{suspect['name']},{suspect['alibi']},{suspect['testimony']},{guilty_str},{suspect['image']}")
    
    return entities 