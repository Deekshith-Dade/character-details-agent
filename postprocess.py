import json
from uuid import uuid4
import csv

def main():
    book_id = "74dd0968-f85f-4c12-a335-939d8ca41aae"
    file_path = "books/dreammachine"
    
    with open(f"{file_path}/final_characters.json", "r") as f:
        final_characters = json.load(f)
     
    headers = ["character_id", "book_id", "name", "description", "extra_info"]
    
    with open(f"{file_path}/characters.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        # Write each character as a row
        for character in final_characters:
            character_id = str(uuid4())
            character_info = {
                "character_id": character_id,
                "book_id": book_id,
                "name": character["name"], 
                "description": character["description"],
                "extra_info": json.dumps({
                    "bio": character["bio"],
                    "arcs": character["arcs"]["arcs"],
                    "quotes": character["quotes"]["quotes"],
                    "traits": character["traits"],
                    "relationships": character["relationships"]["relations"],
                    "isAiGenerated": True
                })
            }
            writer.writerow(character_info)
        
        
        
    # fiels = ["character_id", "book_id", "name", "description", "extra_info"]
    # extra_info = {"bio", "arcs": [{title, description}], "quotes": [], "traits": [], isAiGenerated: true, "relationships": [{"name", "relation", "description"}]}
    

if __name__ == "__main__":
    main()