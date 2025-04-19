import pygame
import os

# Initialize pygame
pygame.init()

# Create the output directory if it doesn't exist
output_dir = "content/images"
os.makedirs(output_dir, exist_ok=True)

# Generate clue image (simple magnifying glass icon)
clue_size = (32, 32)
clue_surface = pygame.Surface(clue_size, pygame.SRCALPHA)
clue_surface.fill((0, 0, 0, 0))  # Transparent background

# Draw magnifying glass shape
pygame.draw.circle(clue_surface, (255, 255, 0), (12, 12), 10, 2)  # Yellow circle
pygame.draw.line(clue_surface, (255, 255, 0), (19, 19), (26, 26), 3)  # Handle

# Save the clue image
pygame.image.save(clue_surface, os.path.join(output_dir, "clue.png"))
print(f"Generated clue.png")

# Create suspect images by adding color tints to the player image
if os.path.exists(os.path.join(output_dir, "player.png")):
    player_img = pygame.image.load(os.path.join(output_dir, "player.png"))
    
    # Create a copy for each suspect with different color tints
    # Alice - Red tint
    alice_img = player_img.copy()
    red_overlay = pygame.Surface(alice_img.get_size(), pygame.SRCALPHA)
    red_overlay.fill((255, 0, 0, 100))  # Semi-transparent red
    alice_img.blit(red_overlay, (0, 0))
    pygame.image.save(alice_img, os.path.join(output_dir, "suspect_alice.png"))
    print(f"Generated suspect_alice.png")
    
    # Bob - Blue tint
    bob_img = player_img.copy()
    blue_overlay = pygame.Surface(bob_img.get_size(), pygame.SRCALPHA)
    blue_overlay.fill((0, 0, 255, 100))  # Semi-transparent blue
    bob_img.blit(blue_overlay, (0, 0))
    pygame.image.save(bob_img, os.path.join(output_dir, "suspect_bob.png"))
    print(f"Generated suspect_bob.png")
    
    # Charlie - Green tint
    charlie_img = player_img.copy()
    green_overlay = pygame.Surface(charlie_img.get_size(), pygame.SRCALPHA)
    green_overlay.fill((0, 255, 0, 100))  # Semi-transparent green
    charlie_img.blit(green_overlay, (0, 0))
    pygame.image.save(charlie_img, os.path.join(output_dir, "suspect_charlie.png"))
    print(f"Generated suspect_charlie.png")
else:
    print("Warning: player.png not found, skipping suspect image generation")

print("Asset generation complete!")

# Instructions
print("\nTo use these assets:")
print("1. Update your map files to use the correct images:")
print("   - suspects: 'suspect_alice.png', 'suspect_bob.png', 'suspect_charlie.png'")
print("2. Run the game with: python src/main.py") 