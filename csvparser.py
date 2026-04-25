import csv


def meta_parser(filename, encoding="utf-8") -> list:

    """
    A function to parse metadata from metadata.csv file from SCAT release for further xml files iteration and further convertation.     
    
    :param filename: path to the metadata.csv file
    :param encoding: file encoding, the default is "utf-8"
    :return: a list of dictionaries with metatags
    :rtype: list
    """

    with open(filename, "r", encoding=encoding) as f:
        csv_list = [x for x in csv.reader(f)]

        meta_template = {} # will be updated with the keys from the header
        
        for tag in csv_list[0]:
            meta_template.update({tag: ""})
        
        texts_meta_tags = []

        for i in range(1, len(csv_list)):
            item = 0
            meta_kv = meta_template.copy()
            for k in meta_template.keys():
                meta_kv.update({k : csv_list[i][item]})
                item += 1
            texts_meta_tags.append(meta_kv)
    print("Ok!")
    return texts_meta_tags

if __name__ == "__main__":
    path_to_metadata = str(input("(full) path to the metadata.csv: "))
    meta_tags = meta_parser(path_to_metadata)
    for i in meta_tags:
        print(i)
