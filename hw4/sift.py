import sys
import getopt

"""
Usage:
python3 sift.py -o <output_file> -q <query num>

eg
python3 sift.py -o output.txt -q 2
this will look for the output.txt file, 
and return the indices of the relevant docs in q2 in output.txt
"""

maps = {
    "1": ["6807771", "3992148", "4001247"],
    "2": ["2211154", "2748529"],
    "3": ["4273155", "3243674", "2702938"]
}

def main():
    with open(output_file, 'r') as f:
        for line in f:
            a = line
    
    b = a.split(" ")
    for doc in maps[query_num]:
        print(f"{doc} at index: {b.index(doc)}")
    
try:
    opts, args = getopt.getopt(sys.argv[1:], 'o:q:')
except getopt.GetoptError:
    sys.exit(2)

for o, a in opts:
    if o == '-q':
        query_num = a
    elif o == '-o':
        output_file = a

if __name__ == "__main__":
    main()