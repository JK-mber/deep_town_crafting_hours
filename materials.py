import json
import pdb
import pathlib

KEEP_STOCK_TIME_RATIO = 0.25
KEEP_CDAYS_STOCK = 1
RAW_MAT_SOURCES = ('Mining', 'ChemicalMining', 'Shop', 'WaterCollection', 'OilPumping')

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
        self.total_count = 0

        self._raw_mats = None
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
                    total_time += (ingredient.accu_crafting_time * self.to_make[ingredient])

            total_time = total_time / self.batch
            self._accu_crafting_time = total_time

        return self._accu_crafting_time

    @property
    def scaled_time(self):
        return self.time / self.crafting_slots

    @property
    def raw_mats(self):
        return self.get_raw_mats()

    @property
    def all_ingredients(self):
        if self.to_make is not None:
            for mat, count in self.to_make:
                yield 1


    def get_raw_mats(self, num_crafts=1):
        if self._raw_mats is None:
            raw_mats = {}
            if self.to_make is not None:
                for ingredient in self.to_make:
                    for ingredient_mat, ingredient_amount in ingredient.get_raw_mats(self.to_make[ingredient]).items():
                        if ingredient_mat not in raw_mats:
                            raw_mats[ingredient_mat] = ingredient_amount * num_crafts
                        else:
                            raw_mats[ingredient_mat] += ingredient_amount * num_crafts

            else:
                raw_mats[self] = num_crafts
            self._raw_mats = raw_mats
        return self._raw_mats

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
            for ingredient, ingredient_count in self.to_make.items():
                ingredient.update_stock_to_keep(n_crafts * ingredient_count)

    def increment_nested_count(self):
        self.total_count += 1
        if self.to_make is not None:
            for ingredient in self.to_make:
                ingredient.increment_nested_count()





class MaterialBundle:
    def __init__(self, mats_file_name='materials.json', crafters_file_name='crafters.json'):
        self._materials = {}
        mats_file_path = pathlib.Path(__file__).parent / mats_file_name;
        with open(mats_file_path, 'r') as mats_file:
            mats_dict = json.loads(mats_file.read())
            for mat in mats_dict:
                self.add_material(mat)

        crafters_file_path = pathlib.Path(__file__).parent / crafters_file_name;
        with open(crafters_file_path, 'r') as crafters_file:
            crafters_dict = json.loads(crafters_file.read())
            for mat in self._materials.values():
                if mat.source not in RAW_MAT_SOURCES:
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
                mat.to_make = {self._materials[d['thing']]: int(d['quantity']) for d in mat.to_make_raw}

    def update_stock_to_keep(self, amount = None):
        for mat in self._materials.values():
            mat.update_stock_to_keep(amount)

    def print_mat_stocks(self, csv_file=None, output_to_console = False):
        table_lines = []
        for name in self._materials:
            mat = self._materials[name]
            if mat.source not in RAW_MAT_SOURCES:
                table_lines.append([
                    name,
                    mat.source,
                    mat.accu_crafting_time,
                    round(mat.stock_to_keep)
                ])

        table_lines.sort(key=lambda l: (l[1], l[3]), reverse=True)

        if csv_file is not None:
            with open(csv_file, 'w') as f:
                f.write(f'Material,Source,Tot. Scaled c-time (s),Stock to keep ({KEEP_CDAYS_STOCK} c-days)\n')
                for line in table_lines:
                    f.write(','.join([str(i) for i in line]) + '\n')

        if output_to_console is True:
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

    def print_material_list(self, csv_file=None):
        items = []
        for mat in self._materials.values():
            if mat.source not in RAW_MAT_SOURCES:
                items.append((mat.name, mat.source, mat.time, mat.batch))
        items.sort(key=lambda x: (x[1], x[0]))
        if csv_file is not None:
            with open(csv_file, 'w') as f:
                f.write('Item,Source,Crafting time [s],Amount per craft\n')
                for item in items:
                    f.write(item[0])
                    for k in item[1:]:
                        f.write(',' + str(k))
                    f.write('\n')

    def print_crafter_list(self, csv_file=None):
        crafters = []
        for mat in self._materials.values():
            if mat.source not in RAW_MAT_SOURCES and mat.source not in [k[0] for k in crafters]:
                crafters.append((mat.source, mat.crafting_slots))
        crafters.sort(key=lambda x: (x[0]))
        if csv_file is not None:
            with open(csv_file, 'w') as f:
                f.write('Crafter type,# slots\n')
                for item in crafters:
                    f.write(item[0] + ',' + str(item[1]) +'\n')

    def print_all_recipes(self, csv_file=None):
        if csv_file is not None:
            with open(csv_file, 'w') as f:
                for mat in self._materials.values():
                    if mat.source not in RAW_MAT_SOURCES:
                        # pass
                        to_make = [item.name+','+str(amount) for item, amount in mat.to_make.items()]
                        f.write(mat.name+',')
                        f.write(str(mat.batch)+',')
                        f.write(','.join(to_make))
                        f.write('\n')

        # for item in items:




if __name__ == "__main__":
    material_bundle = MaterialBundle()
    mb = material_bundle

    mb.print_mat_stocks('crafting_hours.csv', output_to_console = True)
    mb.print_material_list('material_properties.csv')
    mb.print_crafter_list('crafter_properties.csv')
    mb.print_all_recipes('recipes.csv')


    # import pdb; pdb.set_trace()  # breakpoint 6d600ce3 //





























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
