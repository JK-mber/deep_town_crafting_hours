import json


class Material:
    def __init__(self, raw_mat_dict):
        self.source = raw_mat_dict['source']
        self.to_make = None
        self.time = 0
        self.value = None
        self.accu_crafting_time = None
        self.batch = 1

        if 'toMake' in raw_mat_dict:
            self.to_make = {}
            for d in raw_mat_dict['toMake']:
                self.to_make[d['thing']] = int(d['quantity'])

        if 'time' in raw_mat_dict:
            self.time = int(raw_mat_dict['time'])

        if 'value' in raw_mat_dict:
            self.value = raw_mat_dict['value']

        if 'batch' in raw_mat_dict:
            self.batch = int(raw_mat_dict['batch'])

    def get_accu_crafting_time(self, mat_dict, crafters):
        accu_crafting_time = self.time / \
            int(crafters[self.source]['amount']) / self.batch
        if self.to_make is not None:
            for mat in self.to_make:
                # if (print_level): print()
                # if (print_level): print(accu_crafting_time)
                accu_crafting_time += \
                    mat_dict[mat].get_accu_crafting_time(mat_dict, crafters) \
                    * self.to_make[mat]
                # if (print_level): print(accu_crafting_time)

        self.accu_crafting_time = accu_crafting_time
        return self.accu_crafting_time


def load_mats():
    mats_file = open('materials.json', 'r')
    mats_dict = json.loads(mats_file.read())

    mats = {}
    for mat in mats_dict:
        mats[mat['name']] = Material(mat)

    # print(mats)
    return mats


def load_crafters():
    crafters_file = open('crafters.json', 'r')
    crafters = json.loads(crafters_file.read())
    return crafters

mats = load_mats()
crafters = load_crafters()


# print('Accumulated crafting time:')
for m in mats:
    # print(m)
    mats[m].get_accu_crafting_time(mats, crafters)
    # print(m + ': ' + str(mats[m].get_accu_crafting_time(mats)))

mats_sorted = sorted(mats.items(), key=lambda x: x[1].accu_crafting_time)
for mat in mats_sorted:
    # pass
    if mat[1].accu_crafting_time != 0:
        print(mat[0] + ": " + str(60*60*250/mat[1].accu_crafting_time))



import pdb; pdb.set_trace()
# return mats


# load_mats();
# print(mats[1].name)
