from pathlib import Path

MAIN_PATH = Path(__file__).resolve().parent.parent.parent.parent
from collections import OrderedDict
import json

PROJECT_NAME = "kotler_lab_lecture/Kotler Lab Lecture 2"
JSON_FILE = (MAIN_PATH / PROJECT_NAME / "project.json")


def sort_sections(dict):
    counter = 0
    last_idx = 0
    last_section_str = ""
    last_section = None
    for section in dict:
        section["sections_len"] = len(section["sections"])
        first_sub_section = section["sections"][0]
        for idx, sub_section in enumerate(section["sections"]):
            if sub_section != first_sub_section:
                sub_section["is_sub_section"] = True
                sub_section["parent_id"] = sub_section["parent_id"]
                last_section_str = Path(sub_section["original_video"]).stem[:-5]
            sub_section["in_project_id"] = counter
            sub_section["id"] = idx
            counter += 1
        last_section = section
        parent_counter = counter


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
