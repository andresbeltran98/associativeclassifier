import collections
from collections import OrderedDict
from itertools import chain, combinations

ROOT_NODE = 'ROOT'
HT_COUNT = 'count'
HT_LINK_NODES = 'nodes'


class Pattern:
    """
    Represents a pattern or transaction (items -> sup_count)
    """
    def __init__(self, items, count):
        self.items = items
        self.sup_count = count

    def add_item(self, item):
        self.items.append(item)

    def __str__(self):
        return str(self.items) + '->' + str(self.sup_count)

    def __repr__(self):
        return self.__str__()


class AssociationRule:
    """
    Represents an association rule {ant}->{cons} (s=, c=)
    """
    def __init__(self, ant, cons, sup, conf):
        self.ant = ant
        self.cons = cons
        self.sup = sup
        self.conf = conf

    def __str__(self):
        return str(self.ant) + '->' + str(self.cons) + ' (s=' + str(self.sup) + ' c=' + str(round(self.conf, 2)) + ')'

    def __repr__(self):
        return self.__str__()


class TreeNode:
    """
    Represents a node in a FPTree
    """
    def __init__(self, name, count, parent):
        self.name = name
        self.count = count
        self.parent = parent
        self.children = []

    def is_root(self):
        return self.name == ROOT_NODE

    def add_child(self, tree_node):
        self.children.append(tree_node)

    def get_child_node(self, name):
        for node in self.children:
            if node.name == name:
                return node
        return None

    def children_names(self):
        names = []
        for child in self.children:
            names.append(child.name)
        return names

    def __str__(self):
        return 'Name: ' + self.name + ' Count: ' + str(self.count) + ' Children:' + str(self.children)

    def __repr__(self):
        return self.__str__()


class FPTree:
    """
    Represents a FPTree, initially with an empty root node
    """
    def __init__(self):
        self.root = TreeNode(ROOT_NODE, 0, None)

    def is_empty(self):
        return len(self.root.children) == 0

    def has_single_path(self):
        ptr = self.root
        while ptr.children:
            if len(ptr.children) > 1:
                return False
            ptr = ptr.children[0]

        return True

    def insert(self, data, header_table):
        for trans in data:
            self.__insert_trans(trans.items, trans.sup_count, header_table)

    def __insert_trans(self, items, trans_count, header_table):
        root = self.root
        for item in items:
            root = self.__insert_item(root, item, trans_count, header_table)

    def __insert_item(self, root, item, count, header_table):
        if item not in root.children_names():
            # Create a new node in the tree and link it to the header table
            new_child = TreeNode(item, count, root)
            root.add_child(new_child)
            header_table[item][HT_LINK_NODES].append(new_child)
            return new_child
        else:
            # Increment count
            node = root.get_child_node(item)
            node.count += count
            return node

    def all_final_nodes(self, SUP_COUNT):
        # Returns all nodes for a conditional FP-Tree whose count >= SUP_COUNT
        nodes = []
        ptr = self.root
        while ptr.children:
            node = ptr.children[0]
            if node.count < SUP_COUNT:
                ptr.children.pop(0)
                return
            nodes.append(node)
            ptr = node
        return nodes


# METHODS #
def data_to_trans(data):
    """
    Converts initial dataset to Pattern objects
    :param data: initial dataset
    :return: list of Patterns
    """
    dataset = []
    for tran in data:
        dataset.append(Pattern(tran, 1))
    return dataset


def header_table(trans, sup_count):
    """
    Creates a header table with items sorted in descending order
    :param trans: a list of transactions of type Pattern
    :param sup_count: minimum support count
    :return: a dictionary mapping item -> {count, link_nodes}
    """
    items = collections.defaultdict(dict)
    for tran in trans:
        count = tran.sup_count
        for item in tran.items:
            if item not in items:
                items[item][HT_COUNT] = count
                items[item][HT_LINK_NODES] = []
            else:
                items[item][HT_COUNT] += count

    # Sort items by their count in descending order
    ordered = OrderedDict(sorted(items.items(), key=lambda i: i[1][HT_COUNT], reverse=True))

    # Remove items from header table if the count is < sup_count
    keys = []
    for key in ordered:
        if ordered[key][HT_COUNT] < sup_count:
            keys.append(key)
    list(map(ordered.pop, keys))

    return ordered


def sort_transactions(data, header):
    """
    Sorts transactions according to a header table
    :param data: data containing all transactions
    :param header: header table
    """
    for trans in data:
        new_items = []
        for key, _ in header.items():
            if key in trans.items:
                new_items.append(key)
        trans.items = new_items


def fp_growth(tree, header, pattern_items, patt_list, SUP_COUNT):
    """
    Implements the recursive fp_growth algorithm
    :param tree: FP-tree
    :param header: header table
    :param pattern_items: alpha
    :param patt_list: stores the resulting frequent itemsets
    :param SUP_COUNT: minimum sup count
    """
    if tree.has_single_path():
        all_nodes = tree.all_final_nodes(SUP_COUNT)
        all_patterns = powerset(all_nodes)

        for pattern in all_patterns:
            new_items = []
            min_sup_count = float('inf')
            for node in pattern:
                new_items.append(node.name)
                if node.count < min_sup_count:
                    min_sup_count = node.count

            new_items.extend(pattern_items)
            new_patt = Pattern(new_items, min_sup_count)
            patt_list.append(new_patt)

    else:
        for key, _ in header.items():
            # Generate new pattern
            new_l = list(pattern_items)
            new_l.insert(0, key)
            new_patt = Pattern(new_l, header[key][HT_COUNT])
            patt_list.append(new_patt)

            # Generate conditional pattern base
            cpt = cond_patt_base(header, key)
            ht = header_table(cpt, SUP_COUNT)
            if not ht:
                continue

            sort_transactions(cpt, ht)
            cond_tree = FPTree()
            cond_tree.insert(cpt, ht)

            if not cond_tree.is_empty():
                fp_growth(cond_tree, ht, new_patt.items, patt_list, SUP_COUNT)


def cond_patt_base(header, item):
    """
    Generates a conditional pattern base for a given item
    :param header: header table
    :param item: specific item
    """
    data = []

    for node in header[item][HT_LINK_NODES]:
        trans = []
        sup_count = node.count

        # Traverse the tree upwards using the parent reference
        ptr = node.parent
        while not ptr.is_root():
            trans.insert(0, ptr.name)
            ptr = ptr.parent

        if trans:
            data.append(Pattern(trans, sup_count))

    return data


def sup_conf_values(antecedent, dataset, cl_labels):
    """
    Calculates support and confidence values for a given antecedent
    :param antecedent: antecedent itemset
    :param dataset: original dataset
    :param cl_labels: class labels
    :return: total count, count of positives, confidence of positive
    """
    count = 0
    count_yes = 0

    for i in range(len(dataset)):
        if all(elem in dataset[i] for elem in antecedent):
            count += 1
            if cl_labels[i]:
                count_yes += 1

    conf_yes = 0 if count == 0 else (count_yes/count)
    return count, count_yes, conf_yes


def association_rules(freq_itemset, dataset, cls_labels, MIN_SUP_COUNT, MIN_CONF):
    """
    Generate association rules sorted by confidence from frequent itemsets
    :param freq_itemset: a list of frequent itemsets
    :param dataset: original dataset
    :param MIN_CONF: minimum confidence value
    :return: a list of Association Rules
    """
    rules = []
    N = len(dataset)

    for pattern in freq_itemset:
        ant_list = pattern.items
        total, sup_yes, conf_yes = sup_conf_values(ant_list, dataset, cls_labels)
        sup_no = total - sup_yes
        conf_no = 1 - conf_yes
        if sup_yes >= MIN_SUP_COUNT and conf_yes >= MIN_CONF:
            rules.append(AssociationRule(list(ant_list), ['yes'],
                                         sup_count_to_sup(sup_yes, N), conf_yes))
        if sup_no >= MIN_SUP_COUNT and conf_no >= MIN_CONF:
            rules.append(AssociationRule(list(ant_list), ['no'],
                                         sup_count_to_sup(sup_no, N), conf_no))

    rules.sort(key=lambda x: x.conf, reverse=True)
    return rules


def predict(example, as_rules):
    """
    Classifies a novel example
    :param example: novel example
    :param as_rules: list of sorted association rules
    :return: predicted class label
    """
    for ar in as_rules:
        if all(elem in example for elem in ar.ant):
            return ar.cons[0], ar
    return None


def powerset(collection):
    """
    Returns all subsets (powerset) of a given collection
    :param collection: input collection
    :return: a list of all subsets
    """
    return list(chain.from_iterable(combinations(collection, r) for r in range(1, len(collection) + 1)))


def sup_count(pattern, dataset):
    """
    Returns the support count for a given pattern
    :param pattern: input patter
    :param dataset: original dataset
    :return: the count for a given pattern
    """
    count = 0
    for tran in dataset:
        if all(elem in tran for elem in pattern):
            count += 1
    return count


def sup_count_to_sup(count, n):
    """
    Converts a support count to support value
    """
    return round(count/n, 2)

