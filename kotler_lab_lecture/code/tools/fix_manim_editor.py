from pathlib import Path
import re

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
        split_thumbnail = sub_section["in_project_thumbnail"].split(".")
        tumb_name = split_thumbnail[0]
        new_thumb = ""
        if re.findall(r'\d+', sub_section["in_project_video"])[0] != \
                re.findall(r'\d+', sub_section["in_project_thumbnail"])[0]:
            continue
        for partial_str in re.split(r"(_)(\d+)(\.)(\w+)$", sub_section["in_project_thumbnail"]):
            if partial_str.isdigit():
                prev_thumb = str(int(partial_str) - 1)
                add_zeroes = "0" * (len(partial_str) - len(prev_thumb))
                partial_str = add_zeroes + prev_thumb
            new_thumb += partial_str
        sub_section["in_project_thumbnail"] = new_thumb
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
