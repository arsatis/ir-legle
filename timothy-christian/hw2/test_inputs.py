test1 = ['(', 'me', 'AND', 'you', ')']
test2 = ['(', 'A', 'OR', 'B', 'AND', 'C', ')']
test3 = ['(', 'A', 'AND', 'B', 'OR', 'C', ')']
# bill OR Gates AND (vista OR XP) AND NOT mac
# test4 has no 'NOT
test4 = ['bill', 'OR', 'Gates', 'AND', '(', 'vista', 'OR', 'XP', ')', 'AND', 'mac']
test5 = ['bill', 'OR', 'Gates', 'AND', '(', 'vista', 'OR', 'XP', ')', 'AND', 'NOT', 'mac']

query1 = 'Brutus AND Caesar AND Calpurnia'
query2 = 'Brutus AND Caesar AND Calpurnia AND John'
query3 = 'Brutus AND Caesar AND Calpurnia AND John OR cena'
query4 = 'Brutus AND Caesar AND Calpurnia AND (John OR cena)'
query5 = '(x1 OR y1) AND (x2 OR y2) AND (x3 OR y3)'
query6 = '(x1 OR y1) AND (x2 OR y2 OR z3) AND (x3 OR y3)'
query7 = 'a AND (b AND c) AND d'
query8 = 'NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT NOT of'
query9 = 'x1 AND NOT x2 AND NOT x3'
query10 = 'NOT x1 AND x2 AND NOT x3'