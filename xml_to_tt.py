import csv
import os
import logging
from csvparser import meta_parser
from xml.etree import ElementTree

"""
Идея: парсим текст из TEI XML файла, извлекаем структурные теги и парсим в них теги и текст,
в итоге должны получить файл формата .tt такого содержания:

<structure_tag structure_attr="value1", structure_attr2="value2">
text_from_w_tag pos msd lemma   norm
text_from_w_tag pos msd lemma   norm
text_from_w_tag pos msd lemma   norm
<structure_tag_2 ...>
text_from_w_tag pos msd lemma   norm
text_from_w_tag pos msd lemma   norm
...
</structure_tag_2 ...>
</structure_tag>
"""

logger = logging.getLogger(__name__)


def import_xml_and_normalize(filename, encoding="utf-8") -> list:
    
    with open(filename, "r", encoding=encoding) as f:
        file = [x.lstrip().replace("\n", "") for x in f.readlines()]
    return file

# optional function until the handling of the non-pair tags is resolved
def delete_tags_after_import(imported_xml) -> list:
    lb_pb_list = ["<lb", "</lb", "<pb", "</pb"]
    new_list = []
    for line in imported_xml:
        if any(elem in line for elem in lb_pb_list) == False:
            new_list.append(line)
    return new_list

# join <w> tags for further handing
def normalize_w_tags_content(imported_xml) -> list:
    new_list = []
    position = 0
    while position < len(imported_xml):
        line = imported_xml[position]
        if line.startswith("<") and (bool(line.startswith("</w>") == False)):
            if ("<w" in line) and ("</w>" not in line):
                look_forward = 0
                new_line = line
                while position + look_forward + 1 < len(imported_xml) and "</w>" not in imported_xml[position + look_forward]:
                    look_forward += 1
                    new_line = new_line + imported_xml[position + look_forward]
                new_list.append(new_line)
                position += look_forward + 1
            else:
                new_list.append(line) 
                position += 1
        else:
            new_list.append(line)
            position += 1
    return new_list

# the tagset is hardset for now
# TODO: add custom tags handling with accordance to TEI guidelines
def tt_transformation(imported_xml) -> list:
    new_list = []
    content = False
    for line in imported_xml:

        template = {
            "token" : " ",
            "pos": " ",
            "msd": " ",
            "lemma": " ",
            "norm": " ",
            "{http://www.w3.org/XML/1998/namespace}id": " "
        }

        # tags that are written as tab separated values
        tt_tags = ["<w", "<pc", "<c"]

        if content == False:
            if line.startswith("<text>"):
                content = True
                continue
            else:
                continue
        elif content == True:
            if line.startswith("</text>"):
                content = False
                break
            if any(elem in line for elem in tt_tags) == True:
                try:
                    tree = ElementTree.fromstring(line)
                    template.update(tree.attrib)
                    template.update({"token": tree.text}) 
                    final = f"{template["token"]}\t{template["pos"]}\t{template["msd"]}\t{template["lemma"]}\t{template["norm"]}\t{template["{http://www.w3.org/XML/1998/namespace}id"]}"
                    new_list.append(final)
                except ElementTree.ParseError as e:
                    logger.info(f"A problem occured while parsing the line: {line}\n{e}")
                    continue
            elif line.startswith("<note"):
                continue # we skip all the <note> tags as they are not part of the original texts
            else:
                new_list.append(line)
    return new_list

def main():

    logging.basicConfig(filename="scat.log", level=logging.INFO)

    path_to_metadata = str(input("(full) path to the metadata.csv: "))
    meta_tags = meta_parser(path_to_metadata) # receive a list with all the texts from corpus to parse
    for i in meta_tags:
        print(i)
    path_to_corpus = str(input("path to the folder with corpus .xml files: "))
    output_path = str(input("output folder: "))
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for text in meta_tags: # now we parse all ids
        imported_xml = import_xml_and_normalize(f"{path_to_corpus}{text['id']}.xml")

        deleted = delete_tags_after_import(imported_xml)

        w_tags = normalize_w_tags_content(deleted)

        tt = tt_transformation(w_tags)

        with open(f"{output_path}/{text['id']}.tt", "w", encoding="utf-8") as f:
            f.writelines(f'<doc id="{text['id']}" title="{text['title']}" century="{text['century']}" morphology="{text['morphology']}" text_structure="{text['text_structure']}">\n') # we also add meta information
            for line in tt:
                f.writelines(line + "\n")
            f.writelines("</doc>") #closing meta tag

if __name__ == "__main__":
    main()
