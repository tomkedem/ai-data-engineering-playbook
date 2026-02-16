# setup_data.py
import os
from PIL import Image, ImageDraw

def create_real_assets():
    # 1. Ensure the data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"📂 Data directory ready at: {data_dir}")

    # 2. Create a Real Image File (simulating broken glass)
    # We draw a red square with text to act as a real binary JPG file
    img_path = os.path.join(data_dir, "damage_evidence.jpg")
    img = Image.new('RGB', (400, 300), color=(200, 50, 50)) # Red background
    d = ImageDraw.Draw(img)
    d.text((20, 140), "BROKEN GLASS - SEVERE DAMAGE", fill=(255, 255, 255))
    img.save(img_path)
    print(f"✅ Created real image file: {img_path}")

    # 3. Create a Real Text File (simulating a manifest)
    txt_path = os.path.join(data_dir, "shipping_manifest.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("SHIPMENT ID: LS-2026-X\nCONTENTS: High-End Glassware\nSTATUS: Fragile\nINSURANCE: Full Coverage")
    print(f"✅ Created real text file: {txt_path}")

if __name__ == "__main__":
    create_real_assets()