# Associative Classifier
### Andres Beltran mxb774

* Used Python 3.8.6
* The output can be seen in "output.txt"

## Input dataset:

The input dataset is in `main.py` (a list of lists).

I used the FPGrowth algorithm to generate the frequent itemsets.
The association rules are generated using class labels.
The rule with the highest confidence value is used to predict the class label of a novel example.

## To run it:
1) Create a virtual environment if needed.
2) To install dependencies:
   
        pip install -r requirements.txt
3) To run the program
   
        python main.py
