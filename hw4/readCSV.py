import csv
import sys

maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

filename = 'dataset.csv'
filename_write = open('data_100.csv', 'w')
writer = csv.writer(filename_write)

with open(filename, 'r') as f:
    count = 0
    reader = csv.reader(f) # read rows into a dictionary format
    for row in reader:
        writer.writerow(row)

        # splitter = row[2].split("Judgment:")
        # if len(splitter) < 2:
        #     continue
        # print(row[0], splitter[1])
        # print(row)

        count += 1

        if count == 100:
            break