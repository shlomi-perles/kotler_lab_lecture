from pathlib import Path
MAIN_PATH = Path(__file__).resolve().parent.parent.parent.parent
from collections import OrderedDict
import json

PROJECT_NAME = "docs"
JSON_FILE = (MAIN_PATH / PROJECT_NAME / "project.json")

def sort_sections(dict):
    counter = 0
    for section in dict:
        section["sections_len"] = len(section)
        for sub_section in section["sections"]:
            sub_section["in_project_id"] = counter
            counter += 1


def main():
    with open(JSON_FILE, 'r') as fd:
        sections_dict = json.load(fd, object_pairs_hook=OrderedDict)
    with open(str(JSON_FILE) + ".back", 'w') as file:
        file.write(json.dumps(sections_dict, indent=4))

    sort_sections(sections_dict)
    with open(JSON_FILE, 'w') as file:
        file.write(json.dumps(sections_dict, indent=4))

if __name__ == "__main__":
    main()

