import glob
import json
import csv
from pathlib import Path
from PIL import Image
from gemini_client import get_model
from prompts import EXTRACTION_PROMPT

model = get_model()



def extract_bill_data(image_path):
    print(f"Processing: {image_path}")
    img = Image.open(image_path)
    response = model.generate_content([EXTRACTION_PROMPT, img])
    
    response_text = response.text.strip()
    # Remove markdown formatting if any
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON for {image_path}: {e}")
        print(f"Raw output: {response_text}")
        return None

def main():
    base_dir = Path(__file__).parent.parent
    
    # Use test bills directory
    bills_dir = base_dir / "test" / "test" / "bills"
    if not bills_dir.exists():
        bills_dir = base_dir / "test" / "bills"
        
    if not bills_dir.exists():
        print(f"Could not find bills directory at {bills_dir}")
        return
        
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_csv = output_dir / "level1.csv"
    
    image_files = []
    for ext in ["*.jpg", "*.png"]:
        image_files.extend(glob.glob(str(bills_dir / ext)))
        
    image_files.sort()
    
    results = []
    for img_path in image_files:
        bill_id = Path(img_path).stem
        data = extract_bill_data(img_path)
        if data:
            results.append({
                "bill_id": bill_id,
                "json": json.dumps(data)
            })
            
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["bill_id", "json"], quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for row in results:
                # The csv module handles quoting automatically
                writer.writerow(row)
        print(f"Successfully wrote {len(results)} records to {output_csv}")
    else:
        print("No valid data extracted.")

if __name__ == "__main__":
    main()
