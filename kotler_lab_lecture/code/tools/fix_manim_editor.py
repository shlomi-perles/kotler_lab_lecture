from pathlib import Path
MAIN_PATH = Path(__file__).resolve().parent.parent.parent.parent
from collections import OrderedDict
import json

PROJECT_NAME = "docs"
JSON_FILE = (MAIN_PATH / PROJECT_NAME / "project.json")

def sort_sections(dict):
    counter = 0
    last_idx = 0
    last_section_str = ""
    last_section = None
    for section in dict:
        section["sections_len"] = len(section)
        for idx, sub_section in enumerate(section["sections"]):
            if idx ==0:
                last_section_str = Path(sub_section["original_video"]).stem[:-5]
            sub_section["in_project_id"] = counter
            counter += 1
        last_section = section
        last_idx = idx


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

