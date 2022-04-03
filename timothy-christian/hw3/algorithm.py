from heapq import heappop, heappush

class TopK:
    """
    Maintains the top k elements as the elements are added to the structure.
    """
    def __init__(self, k):
        self.k = k
        self.min_heap = []
    
    def add(self, elem):
        """
        Adds target element into minimum heap
        Args:
            elem (str): Target score-documentId pairs
        """
        heappush(self.min_heap, elem)
        if (len(self.min_heap) > self.k):
            # Too many things, pop the smallest elem (we are interested in top elems)
            heappop(self.min_heap)
    
    def result(self):
        """
        Inverts the elements of minimum heap into descending list
        Returns::
            Descending list of score-documentId pairs
        """
        return reversed(sorted(self.min_heap))
