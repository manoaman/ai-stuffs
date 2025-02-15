#!/usr/bin/env python3

import os
import argparse
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm

def generate_caption(image_path, processor, model):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption.replace(" ", "_")[:50]  # Limit filename length

def main():
    parser = argparse.ArgumentParser(description="Rename PNG files based on AI-generated descriptions.")
    parser.add_argument("image_dir", type=str, help="Directory containing PNG images.")
    parser.add_argument("--dry-run", action="store_true", help="Test without renaming files.")
    args = parser.parse_args()

    image_dir = args.image_dir

    # Load BLIP model
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("mps" if torch.backends.mps.is_available() else "cpu")

    # Create a new directory for renamed files
    renamed_dir = os.path.join(image_dir, "renamed_pngs")
    os.makedirs(renamed_dir, exist_ok=True)

    # Process and rename PNG files
    png_files = [f for f in os.listdir(image_dir) if f.lower().endswith(".png")]
    for filename in tqdm(png_files, desc="Processing images"):
        file_path = os.path.join(image_dir, filename)
        new_name = generate_caption(file_path, processor, model) + ".png"
        new_path = os.path.join(renamed_dir, new_name)
        
        if args.dry_run:
            print(f"[DRY RUN] Would rename: {filename} -> {new_name}", flush=True)
        else:
            os.rename(file_path, new_path)
            print(f"Renamed: {filename} -> {new_name}", flush=True)

if __name__ == "__main__":
    main()
