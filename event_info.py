from materials import *
import sys

mb = MaterialBundle()

SECS_PER_DAY = 60*60


def read_event_items(args):
    if (len(args) - 1) % 2 != 0:
        raise(Error, "Must supply name value pairs (item amount ...) as input arguments")

    mats = []
    for i in range(1, len(args), 2):
        mats.append((mb(args[i]), int(args[i + 1])))

    return mats


def print_ingredient_tree(mat, num_crafts=1, num_tabs=0):
    print(''.join(['|  '] * num_tabs), end='')
    print("%s: %.0f" % (mat[0].name, mat[0].scaled_time * mat[1] * num_crafts / mat[0].batch / SECS_PER_DAY))
    # print("%s: %.0f" % (mat[0].name, mat[0].accu_crafting_time * mat[1] * num_crafts / SECS_PER_DAY))
    for ingredient in mat[0].to_make:
        if ingredient[0].source not in ('Mining', 'ChemicalMining', 'Shop', 'WaterCollection', 'OilPumping'):
            print_ingredient_tree(ingredient, num_crafts=mat[1] * num_crafts / mat[0].batch, num_tabs=num_tabs + 1)

def get_ingredient_list(event_items, item_list=None):
    if item_list is None:
        item_list = []

    # for event_item in event_items:











if __name__ == "__main__":
    mats = read_event_items(sys.argv)

    tot_ctime = sum([mat[0].accu_crafting_time * mat[1] for mat in mats])
    tot_cdays = tot_ctime / (SECS_PER_DAY)

    print('Total amount of hours crafting per event round: %.0f' % tot_cdays)
    print('')
    print('Broken down into sub items:')
    for event_item in mats:
        print_ingredient_tree(event_item)















