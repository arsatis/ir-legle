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
    "3": ["4273155", "3243674", "2702938"],
    "comp_1" : ["3992148", "2225598", "6807771", "4001247", "6017101", "2491447", "2881982", "2753029", "2654334", "6058463"],
    "comp_2" : ["2713720",  "3965827",  "2225651", "2225598", "2621151", "2886949", "3988910", "3974455", "3383594", "2145566"],
    "comp_3" : ['2128079', '2884850', '2743282', '3752148', '3926753', '2621079', '6801089', '2705783', '2881916', '6709004'],
    "comp_4" : ['2702938', '4273155', '6079409', '6709605', '3243674', '6707679', '6709476', '3752282', '3752306', '3752202'],
    "comp_5" : ['3984147', '2763746', '3752368', '3750577', '2225598', '2225491', '2620743', '3984152', '2254567', '6927452'],
    "comp_6" : ['2748529', '3752204', '2211154', '2253593', '2621721', '2851048', '6708332', '246771', '2707154', '2407977']
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