import json
import pdb

KEEP_STOCK_TIME_RATIO = 0.25


class Material:
    def __init__(self, raw_mat_dict):
        self.source = raw_mat_dict['source']
        self.to_make = None
        self.time = 0
        self.value = None
        self.accu_crafting_time = None
        self.batch = 1
        self.stock_per_acc_c_hrs = 0
        self.stock_to_keep = 0

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

    def get_accu_crafting_time(self, mats, crafters):

        if self.accu_crafting_time is None:
            accu_crafting_time = self.time \
                / int(crafters[self.source]['amount'])
            if self.to_make is not None:
                for mat in self.to_make:
                    accu_crafting_time += \
                        mats[mat].get_accu_crafting_time(mats, crafters) \
                        * self.to_make[mat]
            accu_crafting_time = accu_crafting_time / self.batch
            self.accu_crafting_time = accu_crafting_time
            if accu_crafting_time != 0:
                self.stock_per_acc_c_hrs = 1 * 60 * 60 / self.accu_crafting_time

        return self.accu_crafting_time

    def update_stock_to_keep(self, mats, crafters, amount=None):
        if amount is None:
            amount = self.stock_per_acc_c_hrs

        if self.time / int(crafters[self.source]['amount']) > KEEP_STOCK_TIME_RATIO * self.accu_crafting_time:
            keep_stock = True
        else:
            keep_stock = False

        if keep_stock:
            self.stock_to_keep += amount
        else:
            if self.to_make is not None:
                for mat in self.to_make:
                    mats[mat].update_stock_to_keep(
                        mats, crafters, self.to_make[mat] * amount / self.batch)


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

for m in mats:
    mats[m].get_accu_crafting_time(mats, crafters)

for m in mats:
    mats[m].update_stock_to_keep(mats, crafters)


mats_sorted = sorted(mats.items(), key=lambda x: x[1].accu_crafting_time)

with open('crafting_hours.csv', 'w') as f:
    f.write('Material,Source,Accumulated crafting time,Amount (1 chrs),Stock to keep (1 chrs),Amount (7cdays),Stock to keep (7cdays)\n')
    for m in mats_sorted:
        try:
            crafting_hr_amount = 60 * 60 / m[1].accu_crafting_time
            f.write(str(m[0]) + ',' + str(m[1].source) + ',' + str(m[1].accu_crafting_time) + ',' + str(crafting_hr_amount) + ',' + str(
                m[1].stock_to_keep) + ',' + str(7 * 24 * crafting_hr_amount) + ',' + str(m[1].stock_to_keep * 7 * 24) + '\n')
        except ZeroDivisionError:
            pass
