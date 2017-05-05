import json
import re


class AsterixField(object):

    def __init__(self, fields):
        self._fields = fields
        self._round_floats()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__hash__() == other.__hash__()
            # my_keys = set(self._fields.keys())
            # other_keys = set(other._fields.keys())
            # mutual_keys = my_keys | other_keys
            # if len(mutual_keys) == len(my_keys) and len(mutual_keys) == len(other_keys):
            #     for key in mutual_keys:
            #         if not self._fields[key] == other._fields[key]:
            #             return False
            # else:
            #     return False
            # return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            cat = self._cat_to_int(self._fields["CAT"])
            sub_cat = self._cat_to_int(self._fields["DI"])
            other_cat = self._cat_to_int(other._fields["CAT"])
            other_sub_cat = self._cat_to_int(other._fields["DI"])
            my_val = 1000 * cat + sub_cat
            other_val = 1000 * other_cat + other_sub_cat
            return my_val < other_val
        return False

    def __hash__(self):
        non_zero_items = list(filter(lambda k_v: not (isinstance(k_v[1], int) and k_v[1] == 0), self._fields.items()))
        return hash(tuple(sorted(non_zero_items)))

    def __repr__(self):
        return str(self._fields)

    def _round_floats(self):
        for k, v in self._fields.items():
            if isinstance(v, float):
                self._fields[k] = round(v, 2)

    def _cat_to_int(self, str_cat):
        i = 0
        while str_cat[i] == 0:
            i += 1
        return int(str_cat[i:])


def convert_to_json(filename):
    with open(filename, "r") as f:
        return set(map(lambda line: AsterixField(json.loads(line)), f.readlines()))


def convert_to_mirons_format(filename):
    with open(filename, "r") as f:
        cro_json = eval(re.sub("\n", "", f.read()))
        json_miron_fields = set()
        for field in cro_json:
            category = str(field.get('category'))
            category_name = '0' * (3 - len(category)) + category
            sub_categories = list(filter(lambda k: re.match("I\d{3}", k), field.keys()))
            for sub_category in sub_categories:
                miron_field = {"CAT": category_name, "DI": sub_category[1:]}
                for key, val in field[sub_category].items():
                    miron_field.update({key: val['val']})
                json_miron_fields.add(AsterixField(miron_field))
    return json_miron_fields


def compare_asterix(miron_asterix, cro_asterix):
    miron_json = convert_to_json(miron_asterix)
    cro_json = convert_to_mirons_format(cro_asterix)
    miron_diff = miron_json - cro_json
    cro_diff = cro_json - miron_json
    print("is in miron and not in cro:")
    print(miron_diff)
    print("diff len: " + str(len(miron_diff)))
    print("is in cro and not in miron:")
    print(cro_diff)
    print("diff len: " + str(len(cro_diff)))

if __name__ == "__main__":
    miron_asterix = "../asterix-parser/generator/outcat62.json"
    cro_asterix = "./outcat62.json"
    compare_asterix(miron_asterix, cro_asterix)
    #af1 = AsterixField({'CAT': '062', 'DI': '105', 'Lat': 44.73441302776337, 'Lon': 13.0415278673172})
    #af2 = AsterixField({'CAT': '062', 'DI': '105', 'Lat': 44.73, 'Lon': 13.04})
    #print(AsterixField({'CAT': '062', 'DI': '200', 'TRANSA': 0, 'LONGA': 2, 'VERTA': 2, 'ADF': 0}).__hash__())
    #print(AsterixField({'CAT': '062', 'DI': '200', 'TRANSA': 0, 'LONGA': 2, 'VERTA': 2, 'ADF': 0, 'spare': 0}).__hash__())
