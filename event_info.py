from materials import *
import sys

mb = MaterialBundle()


def read_event_items(args):
    if (len(args) - 1) % 2 != 0:
        raise(Error, "Must supply name value pairs (<item> <amount> ...) as input arguments")

    mats = {}
    for i in range(1, len(args), 2):
        mats = {mb(args[i]): int(args[i + 1]) for i in range(1, len(args), 2)}

    return mats


def print_ingredient_tree(mat, num_crafts=1, num_tabs=0):

    if mat.to_make is None:
        print(('%7d               ' + ''.join([' - '] * num_tabs)) % (num_crafts), end='')
        print('%s' % (mat.name))
    else:
        seconds = mat.scaled_time * num_crafts / mat.batch
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        print(('%7d - %2d:%02d:%02d:%02d ' + ''.join([' - '] * num_tabs)) % (num_crafts, d, h, m, s), end='')
        print("%s" % (mat.name))

        for ingredient, ingredient_amount in mat.to_make.items():
            print_ingredient_tree(ingredient, num_crafts=ingredient_amount * num_crafts / mat.batch, num_tabs=num_tabs + 1)







if __name__ == "__main__":
    event_items = read_event_items(sys.argv)

    tot_ctime = sum([mat.accu_crafting_time * count for mat,count in event_items.items()])
    m, s = divmod(tot_ctime, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    print('Total crafting time per event round: %d:%02d:%02d:%02d' % (d, h, m, s))
    print('')
    print('Broken down into sub items:')
    for item, count in event_items.items():
        print_ingredient_tree(item, num_crafts=count)

    raw_mats = {}
    for item, count in event_items.items():
        for mat, n_mats in item.raw_mats.items():
            n_mats = n_mats * count
            if mat in raw_mats:
                raw_mats[mat] += n_mats
            else:
                raw_mats[mat] = n_mats

    print('')
    print('Raw materials per event round:')
    for mat, count in raw_mats.items():
        print(mat.name + ': ' + str(count))














