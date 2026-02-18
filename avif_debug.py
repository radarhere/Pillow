import os
import subprocess
from PIL import Image

SOURCE = "1_trns.png"

def test_isolation():
    if not os.path.exists(SOURCE):
        print(f"Error: Could not find {SOURCE}")
        return

    # We use the width that crashed previously for the test
    killer_width = 974
    print(f"\n--- Testing Isolation (Width: {killer_width}px) ---")

    # Step 1: Create the 'Killer' PNG
    with Image.open(SOURCE) as img:
        temp_rgba = img.convert("RGBA").resize((killer_width, 623))
        temp_rgba.save("/tmp/killer_input.png")
        print(f"1. Prepared RGBA file: killer_input.png ({killer_width}x623)")

    # Step 3: Test via Pillow
    print("3. Attempting conversion via Pillow...", end=" ", flush=True)
    try:
        with Image.open("/tmp/killer_input.png") as p_img:
            p_img.save("/tmp/pillow_output.avif", speed=6)
            print("✅ Pillow SUCCESS")
    except Exception as e:
        print(f"❌ Pillow FAILED/CRASHED")


if __name__ == "__main__":
    test_isolation()
