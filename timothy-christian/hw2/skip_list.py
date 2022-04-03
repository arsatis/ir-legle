import math

"""
An abstraction over a regular node - it can be a regular node with just posting list
or it can be a node that can skip to a next node
"""
class SkipNode:
    def __init__(self, doc_id, skip_pointer=None):
        self.doc_id = doc_id
        self.skip_pointer = skip_pointer # either None or the index in the list to what it skips to
    
    def has_skip_pointer(self):
        return self.skip_pointer != None
    
    def set_skip_pointer(self, skip_pointer):
        self.skip_pointer = skip_pointer
    
    def __eq__(self, other):
        if not isinstance(other, SkipNode):
            return False

        return self.doc_id == other.doc_id
    
    def __lt__(self, other):
        if not isinstance(other, SkipNode):
            return False

        return self.doc_id < other.doc_id

    def __gt__(self, other):
        if not isinstance(other, SkipNode):
            return False

        return self.doc_id > other.doc_id
    
    def __str__(self):
        return f"{self.doc_id}"
    
    def __repr__(self):
        return f"({self.doc_id=}, {self.skip_pointer=})"


def create_skip_list_from_docid_list(doc_ids):
    """
    Creates skip list given a list of documentIds (posting list).
    Args:
        doc_ids (list): List of documentIds
    Returns:
        skip_list (skiplist): Skip list of documentIds
    """
    n = len(doc_ids)
    step = int(math.sqrt(n))
    skip_list = []

    for i, doc_id in enumerate(doc_ids):
        if i % step == 0 and (i + step < n):
            skip_list.append(SkipNode(doc_id, i + step))
        else:
            skip_list.append(SkipNode(doc_id))
    
    return skip_list


def reconstruct_skip_list(skip_list):
    """
    Modifies skip list given a recently merged skip list.
    Recalculates and set new skip pointers based on a new length of list.
    Args:
        skip_list (skiplist): Skip list of documentIds 
    """
    n = len(skip_list)
    step = int(math.sqrt(n))
    
    for i, skip_node in enumerate(skip_list):
        if i % step == 0 and (i + step < n):
            skip_node.set_skip_pointer(i + step)
        else:
            skip_node.set_skip_pointer(None)