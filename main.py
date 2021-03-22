from classifier import *

AGE_30 = 'Age≤30'
AGE_31 = 'Age31-40'
AGE_40 = 'Age>40'
INC_H = 'IncomeHigh'
INC_M = 'IncomeMed'
INC_L = 'IncomeLow'
ST_Y = 'StudentYes'
ST_N = 'StudentNo'
CR_F = 'CRfair'
CR_E = 'CRexc'


# Input dataset and class labels
dataset = [[AGE_30, INC_H, ST_N, CR_F],
           [AGE_30, INC_H, ST_N, CR_E],
           [AGE_31, INC_H, ST_N, CR_F],
           [AGE_40, INC_M, ST_N, CR_F],
           [AGE_40, INC_L, ST_Y, CR_F],
           [AGE_40, INC_L, ST_Y, CR_E],
           [AGE_31, INC_L, ST_Y, CR_E],
           [AGE_30, INC_M, ST_N, CR_F],
           [AGE_30, INC_L, ST_Y, CR_F],
           [AGE_40, INC_M, ST_Y, CR_F],
           [AGE_30, INC_M, ST_Y, CR_E],
           [AGE_31, INC_M, ST_N, CR_E],
           [AGE_31, INC_H, ST_Y, CR_F],
           [AGE_40, INC_M, ST_N, CR_E]]
cls_labels = [0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0]

SUP_COUNT = 2  # same as sup=10% for this dataset
MIN_CONF = 0.6

data = data_to_trans(dataset)

# Create header table
ordered = header_table(data, SUP_COUNT)

# Sort transactions based on header table
sort_transactions(data, ordered)

# Construct FPTree
t = FPTree()
t.insert(data, ordered)

# Perform fp_growth algorithm
freq_itemset = []
fp_growth(t, ordered, [], freq_itemset, SUP_COUNT)
print('FPTree Algorithm')
print('Frequent items: ', len(freq_itemset))
for x in freq_itemset:
    print(x)

# Create association rules
print('\nAssociation Rules:')
r = association_rules(freq_itemset, dataset, cls_labels, SUP_COUNT, MIN_CONF)
for rule in r:
    print(rule)

# Classify novel example
ex = [AGE_30, INC_M, ST_Y, CR_F]
lbl, rule = predict(ex, r)
print('\nPrediction: ', lbl, '\nRule used: ', rule)

