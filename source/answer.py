import csv
import time
from pathlib import Path
from PIL import Image
from google.api_core.exceptions import ResourceExhausted
from gemini_client import get_model
from prompts import QA_PROMPT_PREFIX

model = get_model()


def answer_question(image_path, question):
    print(f"Answering question for {image_path.stem}: {question[:60]}...")
    img = Image.open(image_path)
    full_prompt = QA_PROMPT_PREFIX + question
    
    for attempt in range(5):
        try:
            response = model.generate_content([full_prompt, img])
            return response.text.strip()
        except ResourceExhausted as e:
            wait = 20 * (attempt + 1)
            print(f"  Rate limited. Waiting {wait}s before retry {attempt+1}/5...")
            time.sleep(wait)
    
    print(f"  Failed after 5 retries for {image_path.stem}")
    return "Error: rate limit exceeded"

def main():
    base_dir = Path(__file__).parent.parent
    
    # Use test bills directory
    bills_dir = base_dir / "test" / "test" / "bills"
    if not bills_dir.exists():
        bills_dir = base_dir / "test" / "bills"
        
    level2_csv_input = base_dir / "test" / "test" / "csv" / "level2.csv"
    
    if not level2_csv_input.exists():
        print(f"Input file not found at {level2_csv_input}.")
        print("Please ensure you have downloaded the test data and placed it in the correct folder structure.")
        return

    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    output_csv = output_dir / "level2.csv"
    
    results = []
    
    with open(level2_csv_input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bill_id = row['bill_id']
            question_id = row['question_id']
            question = row['question']
            
            # Find the corresponding image
            img_path = None
            for ext in [".jpg", ".png"]:
                potential_path = bills_dir / (bill_id + ext)
                if potential_path.exists():
                    img_path = potential_path
                    break
            
            if img_path:
                answer = answer_question(img_path, question)
                row['answer'] = answer
                time.sleep(5)  # Stay under 15 RPM rate limit
            else:
                print(f"Warning: Could not find image for {bill_id}")
                row['answer'] = "Image not found."
                
            results.append(row)

    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["bill_id", "question_id", "question", "answer"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"Successfully wrote {len(results)} answers to {output_csv}")

if __name__ == "__main__":
    main()
