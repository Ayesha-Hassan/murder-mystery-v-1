"""
Set API Key Script

This script allows users to set their Groq API key without modifying the source code.
It creates a .env file that will be loaded by the game.
"""

import os
import sys

def set_api_key():
    """
    Ask the user for their Groq API key and save it to a .env file.
    """
    print("=" * 60)
    print("               GROQ API KEY SETUP")
    print("=" * 60)
    print("\nThis script will save your Groq API key to a .env file.")
    print("This key is required for the dynamic layout generation feature.")
    print("You can get a Groq API key by signing up at https://console.groq.com/\n")
    
    # Check if .env file already exists
    env_file = ".env"
    existing_key = None
    
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("GROQ_API_KEY="):
                        existing_key = line.strip().split("=", 1)[1].strip('"\'')
                        break
        except Exception as e:
            print(f"Error reading existing .env file: {e}")
    
    # Show existing key if available
    if existing_key:
        print(f"Current API key: {existing_key[:4]}{'*' * (len(existing_key) - 8)}{existing_key[-4:]}")
        update = input("Do you want to update this key? (y/n): ").lower()
        if update != 'y':
            print("Keeping existing API key. Setup complete.")
            return
    
    # Get new API key from user
    api_key = input("\nEnter your Groq API key: ").strip()
    
    if not api_key:
        print("No API key provided. Exiting setup.")
        return
    
    # Save to .env file
    try:
        with open(env_file, "w") as f:
            f.write(f"GROQ_API_KEY={api_key}\n")
        print("\nAPI key saved successfully to .env file.")
        print("You can now run the game with dynamic layout generation.")
    except Exception as e:
        print(f"Error saving API key: {e}")
        
    print("\nSetup complete!")

if __name__ == "__main__":
    set_api_key() 