from materials import *
import csv


mb = MaterialBundle()

SECS_PER_DAY = 60 * 60

all_event_items = []
with open('event_list_post_sept.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        for i in range(1, 8, 2):
            all_event_items.append(row[i])

for material in all_event_items:
    mb(material).increment_nested_count()



mat_count = {mat.name: mat.total_count for mat in mb._materials.values()}
mat_count.sort()

import pdb; pdb.set_trace()  # breakpoint 71572fbe //
