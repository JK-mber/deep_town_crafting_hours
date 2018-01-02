import json

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
        self.stock_to_keep = 0;

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
        if self.accu_crafting_time is None:
            accu_crafting_time = self.time / int(crafters[self.source]['amount'])
            if self.to_make is not None:
                for mat in self.to_make:
                    # if (print_level): print()
                    # if (print_level): print(accu_crafting_time)
                    accu_crafting_time += \
                        mat_dict[mat].get_accu_crafting_time(mat_dict, crafters) \
                        * self.to_make[mat]
                    # if (print_level): print(accu_crafting_time)

            self.accu_crafting_time = accu_crafting_time / self.batch
            if accu_crafting_time != 0:
                self.stock_per_acc_c_hrs = 1*60*60/accu_crafting_time

        return self.accu_crafting_time

    def update_stock_to_keep(self, mat_dict, crafters, amount=None):
        if amount is None:
            amount = self.stock_per_acc_c_hrs

        if self.time/int(crafters[self.source]['amount']) > KEEP_STOCK_TIME_RATIO * self.accu_crafting_time:
            keep_stock = True
        else:
            keep_stock = False
        # print('amount: ' + str(amount))
        # print('stock_to_keep: ' + str(self.stock_to_keep))
        if keep_stock:
            self.stock_to_keep += amount
        else:
            if self.to_make is not None:
                for mat in self.to_make:
                    # print('mat: ' + mat)
                    # print('self.to_make: ' + str(self.to_make))
                    mat_dict[mat].update_stock_to_keep(mat_dict, crafters, self.to_make[mat] * amount)


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

for m in mats:
    # print('Callling update_stock_to_keep() for mat: ' + m)
    mats[m].update_stock_to_keep(mats, crafters)
    # import pdb; pdb.set_trace()


mats_sorted = sorted(mats.items(), key=lambda x: x[1].accu_crafting_time)
for mat in mats_sorted:
    # pass
    if mat[1].accu_crafting_time != 0:
        print(mat[0] + ": " + str(60*60*250/mat[1].accu_crafting_time))


with open('crafting_hours.csv','w') as f:
    f.write('Material,Accumulated crafting time,Amount (1 crafting hour),Stock to keep (1 crafting hr),Amount (250 crafting hours),Stock to keep (250 crafting hrs)\n')
    for m in mats_sorted:
        try:
            crafting_hr_amount = 60*60/m[1].accu_crafting_time
        except ZeroDivisionError:
            crafting_hr_amount = 0

        f.write(str(m[0]) +','+ str(m[1].accu_crafting_time) +','+ str(crafting_hr_amount)  +','+ str(m[1].stock_to_keep) +','+ str(250*crafting_hr_amount)  +','+ str(m[1].stock_to_keep*250) + '\n')

import pdb; pdb.set_trace()
# return mats


# load_mats();
# print(mats[1].name)
