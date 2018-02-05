import json
import pdb

KEEP_STOCK_TIME_RATIO = 0.25
KEEP_CDAYS_STOCK = 7


class Material:
    def __init__(self, raw_mat_dict, name=''):
        self.source = raw_mat_dict['source']
        self.name = name
        self.to_make_raw = None
        self.to_make = None
        self.crafting_slots = 1
        self.time = 0
        self.batch = 1
        self.value = None
        self.stock_to_keep = 0

        self._accu_crafting_time = None

        if 'to_make' in raw_mat_dict:
            self.to_make_raw = raw_mat_dict['to_make']

        if 'time' in raw_mat_dict:
            self.time = int(raw_mat_dict['time'])

        if 'value' in raw_mat_dict:
            self.value = raw_mat_dict['value']

        if 'batch' in raw_mat_dict:
            self.batch = int(raw_mat_dict['batch'])

    @property
    def accu_crafting_time(self):
        if self._accu_crafting_time is None:
            total_time = self.scaled_time
            if self.to_make is not None:
                for ingredient in self.to_make:
                    total_time += (ingredient[0].accu_crafting_time * ingredient[1])

            total_time = total_time / self.batch
            self._accu_crafting_time = total_time

        return self._accu_crafting_time

    @property
    def scaled_time(self):
        return self.time / self.crafting_slots

    def update_stock_to_keep(self, amount=None):
        if self.accu_crafting_time == 0:
            return
        if amount is None:
            secs_per_day = 60 * 60 * 24
            amount = 1 / self.accu_crafting_time * KEEP_CDAYS_STOCK * secs_per_day

        # If the time to craft this item is larger than xx% of the total time, keep this item in stock
        if self.scaled_time > self.accu_crafting_time * KEEP_STOCK_TIME_RATIO:
            self.stock_to_keep += amount
        else:
            n_crafts = amount / self.batch
            for ingredient in self.to_make:
                ingredient[0].update_stock_to_keep(n_crafts * ingredient[1])


class MaterialBundle:
    def __init__(self, mats_file_name='materials.json', crafters_file_name='crafters.json'):
        self._materials = {}

        with open(mats_file_name, 'r') as mats_file:
            mats_dict = json.loads(mats_file.read())

            for mat in mats_dict:
                self.add_material(mat)

        with open(crafters_file_name, 'r') as crafters_file:
            crafters_dict = json.loads(crafters_file.read())
            for mat in self._materials.values():
                if mat.source not in ('Mining', 'ChemicalMining', 'Shop', 'WaterCollection', 'OilPumping'):
                    mat.crafting_slots = int(crafters_dict[mat.source]['amount'])

        self.update_nested_material_list()
        self.update_stock_to_keep()

    def __call__(self, material):
        if isinstance(material, str):
            return self._materials[material]
        else:
            name = material['name']

            if name in self._materials:
                return self._materials[name]
            else:
                # print(material)
                self.add_material(material)
                return self._materials[name]

    def add_material(self, raw_mat_dict):
        self._materials[raw_mat_dict['name']] = Material(raw_mat_dict, name=raw_mat_dict['name'])

    def update_nested_material_list(self):
        for mat in self._materials.values():
            if mat.to_make_raw is not None:
                mat.to_make = [(self._materials[d['thing']], int(d['quantity'])) for d in mat.to_make_raw]

    def update_stock_to_keep(self, amount = None):
        for mat in self._materials.values():
            mat.update_stock_to_keep()

    def print_all_mats(self, save_to_csv=False):
        table_lines = []
        for name in self._materials:
            mat = self._materials[name]
            if mat.source not in ('Mining', 'ChemicalMining', 'Shop', 'WaterCollection', 'OilPumping'):
                table_lines.append([
                    name,
                    mat.source,
                    mat.accu_crafting_time,
                    round(mat.stock_to_keep)
                ])

        table_lines.sort(key=lambda l: (l[1], l[3]), reverse=True)

        if save_to_csv:
            with open('crafting_hours.csv', 'w') as f:
                f.write('Material,Source,Tot. Scaled c-time (s),Stock to keep (7 c-days)\n')
                for line in table_lines:
                    f.write(','.join([str(i) for i in line]) + '\n')

        sz = [20, 15, 15, 17]
        print('Item'.ljust(sz[0]) +
            'Source'.ljust(sz[1]) +
            'Tot. ctime (s)'.rjust(sz[2]) +
            'Stock to keep'.rjust(sz[3]))
        print(''.join(['-']*(sum(sz))))
        for line in table_lines:
            print(line[0].ljust(sz[0]) +
                  line[1].ljust(sz[1]) +
                  str(line[2]).rjust(sz[2]) +
                  str(line[3]).rjust(sz[3]))





if __name__ == "__main__":
    material_bundle = MaterialBundle()
    mb = material_bundle

    mb.print_all_mats(save_to_csv=True)





    import pdb; pdb.set_trace()  # breakpoint 6d600ce3 //





























# for m in mats:
#     mats[m].get_accu_crafting_time(mats, crafters)

# for m in mats:
#     mats[m].update_stock_to_keep(mats, crafters)


# mats_sorted = sorted(mats.items(), key=lambda x: x[1].accu_crafting_time)

# with open('crafting_hours.csv', 'w') as f:
#     f.write('Material,Source,Accumulated crafting time,Amount (1 chrs),Stock to keep (1 chrs),Amount (7cdays),Stock to keep (7cdays)\n')
#     for m in mats_sorted:
#         try:
#             crafting_hr_amount = 60 * 60 / m[1].accu_crafting_time
#             f.write(str(m[0]) + ',' + str(m[1].source) + ',' + str(m[1].accu_crafting_time) + ',' + str(crafting_hr_amount) + ',' + str(
#                 m[1].stock_to_keep) + ',' + str(7 * 24 * crafting_hr_amount) + ',' + str(m[1].stock_to_keep * 7 * 24) + '\n')
#         except ZeroDivisionError:
#             pass
