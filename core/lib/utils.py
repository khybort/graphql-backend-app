import json


def convert_to_dump_lists(lists):
    return [[json.dumps(dict_) for dict_ in list_] for list_ in lists]
