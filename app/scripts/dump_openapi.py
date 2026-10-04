import json
from app.main import app

if __name__ == "__main__":
    with open("docs.json", "w", encoding="utf-8") as f:
        json.dump(app.openapi(), f, ensure_ascii=False, indent=2)
    print("docs.json succesfully created")