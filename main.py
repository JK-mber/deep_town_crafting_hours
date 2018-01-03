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

    def get_accu_crafting_time(self, mat_dict, crafters, debug_this=False):

        if debug_this:
            print("get_accu_crafting_time() called")
        if self.accu_crafting_time is None:
            accu_crafting_time = self.time \
                / int(crafters[self.source]['amount'])
            if self.to_make is not None:
                for mat in self.to_make:
                    # if (print_level): print()
                    # if (print_level): print(accu_crafting_time)
                    if debug_this:
                        print('Running nested get_accu_crafting_time for mat ' + m)
                    accu_crafting_time += \
                        mat_dict[mat].get_accu_crafting_time(mat_dict, crafters, debug_this) \
                        * self.to_make[mat]
                    # if (print_level): print(accu_crafting_time)
            accu_crafting_time = accu_crafting_time / self.batch
            self.accu_crafting_time = accu_crafting_time
            if accu_crafting_time != 0:
                self.stock_per_acc_c_hrs = 1 * 60 * 60 / self.accu_crafting_time
                if debug_this:
                    print("Calculated stock: " + str(self.stock_per_acc_c_hrs))

        if debug_this:
            pdb.set_trace()
        return self.accu_crafting_time

    def update_stock_to_keep(self, mat_dict, crafters, amount=None, debug_this=False):

        if debug_this:
            print("update_stock_to_keep called")

        if amount is None:
            amount = self.stock_per_acc_c_hrs

            if debug_this:
                print("amount set: " + str(amount))
        else:

            if debug_this:
                print("amount inherited: " + str(amount))


        if self.time / int(crafters[self.source]['amount']) > KEEP_STOCK_TIME_RATIO * self.accu_crafting_time:
            keep_stock = True
        else:
            keep_stock = False

        if debug_this:
            print("Keep stock set: " + str(keep_stock))

        # print('amount: ' + str(amount))
        # print('stock_to_keep: ' + str(self.stock_to_keep))
        if keep_stock:
            self.stock_to_keep += amount
        else:
            if self.to_make is not None:
                for mat in self.to_make:
                    if debug_this:
                        print(">>>")
                    # print('mat: ' + mat)
                    # print('self.to_make: ' + str(self.to_make))
                    mat_dict[mat].update_stock_to_keep(
                        mat_dict, crafters, self.to_make[mat] * amount / self.batch, debug_this)
                    if debug_this:
                        print("<<<")

        if debug_this:
            print("update_stock_to_keep done. self.__dict__:")
            print(self.__dict__)


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
    debug_this = False
    mats[m].get_accu_crafting_time(mats, crafters, debug_this)
    # print(m + ': ' + str(mats[m].get_accu_crafting_time(mats)))

print(mats['sulfuricAcid'].__dict__)

for m in mats:
    # print('Callling update_stock_to_keep() for mat: ' + m)
    debug_this = m == "gunpowder"
    if debug_this:
        print("Debugging update_stock_to_keep() for mat " + m)
    mats[m].update_stock_to_keep(mats, crafters, debug_this=debug_this)
    # import pdb; pdb.set_trace()


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


# pdb.set_trace()
# return mats


# load_mats();
# print(mats[1].name)
