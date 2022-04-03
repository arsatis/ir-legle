from tokeniser import Tokeniser
import heapq, itertools
import pickle
import skip_list

# these two functions are written to separate the intent of what is being loaded.
def load_posting(dictionary, posting_file, term):
    """
    Loads a specified term's posting list from posting file.
    Args:
        dictionary (dict): Dictionary of term's data (frequency, position, size)
        posting_file (file): File object of posting file
        term (str): Target term to retrieve
    Returns:
        postings (skiplist): Skip list of postings (documentIds)
    """
    # Retrieves term's offset position and size
    _, pos, size = dictionary[term]

    posting_file.seek(pos)
    postings = pickle.loads(posting_file.read(size))
    return postings

def load_universe(posting_file, universe_data):
    """
    Loads a universe posting list from posting file.
    Args:
        posting_file (file): File object of posting file
        universe_data (tuple): Universe metadata (frequency, position, size)
    Returns:
        postings (skiplist): Skip list of postings (documentIds)
    """
    # Retrieves universe's offset position and size
    _, pos, size = universe_data

    posting_file.seek(pos)
    postings = pickle.loads(posting_file.read(size))
    return postings

"""
The core of the query processor. Should NOT be initialised and only meant as parent class.
"""
class QueryProcessor:
    def process_skip_AND(self, posting_A, posting_B):
        """
        Processes AND operation using skip list. 
        Merges both posting list if both list contains same documentId.
        Args:
            posting_A (skiplist): Skip list of A's documentIds
            posting_B (skiplist): Skip list of B's documentIds
        Returns:
            answer (skiplist): Skip list of overlap documentIds
        """
        answer = []
        index_A, index_B = 0, 0
        while index_A < len(posting_A) and index_B < len(posting_B):
            node_A, node_B = posting_A[index_A], posting_B[index_B]
            if node_A == node_B:
                answer.append(node_A)
                index_A += 1
                index_B += 1
            elif node_A < node_B:
                if node_A.has_skip_pointer() and posting_A[node_A.skip_pointer] < node_B:
                    index_A = node_A.skip_pointer
                else:
                    index_A += 1
            else:
                if node_B.has_skip_pointer() and posting_B[node_B.skip_pointer] < node_A:
                    index_B = node_B.skip_pointer
                else:
                    index_B += 1

        skip_list.reconstruct_skip_list(answer)
        return answer


    def process_AND(self, posting_A, posting_B):
        """
        Processes AND operation using naive approach. 
        Merges both posting list if both list contains same documentId.
        Args:
            posting_A (skiplist): Skip list of A's documentIds
            posting_B (skiplist): Skip list of B's documentIds
        Returns:
            answer (skiplist): Skip list of overlap documentIds
        """
        answer = []
        index_A, index_B = 0, 0
        while index_A < len(posting_A) and index_B < len(posting_B):
            if posting_A[index_A] == posting_B[index_B]:
                answer.append(posting_A[index_A])
                index_A += 1
                index_B += 1
            elif posting_A[index_A] < posting_B[index_B]:
                index_A += 1
            else:
                index_B += 1

        skip_list.reconstruct_skip_list(answer)
        return answer

    def process_OR(self, posting_A, posting_B):
        """
        Processes OR operation.
        Merges all documentIds from both posting list.
        Args:
            posting_A (skiplist): Skip list of A's documentIds
            posting_B (skiplist): Skip list of B's documentIds
        Returns:
            answer (skiplist): Skip list of all documentIds from both list
        """
        answer = []
        index_A, index_B = 0, 0
        while index_A < len(posting_A) and index_B < len(posting_B):
            if posting_A[index_A] == posting_B[index_B]:
                answer.append(posting_A[index_A])
                index_A += 1
                index_B += 1
            elif posting_A[index_A] < posting_B[index_B]:
                answer.append(posting_A[index_A])
                index_A += 1
            else:
                answer.append(posting_B[index_B])
                index_B += 1

        while index_A < len(posting_A):
            answer.append(posting_A[index_A])
            index_A += 1

        while index_B < len(posting_B):
            answer.append(posting_B[index_B])
            index_B += 1

        skip_list.reconstruct_skip_list(answer)
        return answer

    def process_NOT(self, posting_A, universe):
        """
        Processes NOT operation.
        Retrieves all documentIds that does not exist in posting A.
        Args:
            posting_A (skiplist): Skip list of A's documentIds
            universe (skiplist): Skip list of every documentIds
        Returns:
            answer (skiplist): Skip list of documentIds not in posting A
        """
        answer = []
        index_A, index_B = 0, 0
        while index_A < len(posting_A):
            if posting_A[index_A] == universe[index_B]:
                index_A += 1
                index_B += 1
            elif posting_A[index_A] < universe[index_B]:
                answer.append(universe[index_B])
                index_A += 1
            else:
                answer.append(universe[index_B])
                index_B += 1

        while index_B < len(universe):
            answer.append(universe[index_B])
            index_B += 1

        skip_list.reconstruct_skip_list(answer)
        return answer
    

class NaiveQueryProcessor(QueryProcessor):
    """"
    Naive approach to query operations.
    """
    def process(self, query, dictionary, posting_file, universe_data):
        """
        Processes a query of postfix tokens, extracting the posting list data using a dictionary,
        posting file handler, and universe.
        Args:
            query (deque): Tokenised queue of postfix query
            dictionary (dict): Dictionary of term's data (frequency, position, size)
            posting_file (file): File object of posting file
            universe_data (tuple): Universe metadata (frequency, position, size)
        Returns:
            (skiplist): Processed skip list of postings
        """
        post_st = []
        for item in query:
            if Tokeniser.is_binary_op(item):
                post_A = post_st.pop()
                post_B = post_st.pop()
                if item == Tokeniser.AND:
                    new_post = self.process_AND(post_A, post_B)
                elif item == Tokeniser.OR:
                    new_post = self.process_OR(post_A, post_B)
                post_st.append(new_post)
            elif Tokeniser.is_unary_prefix_op(item):
                post_A = post_st.pop()
                universe_post = load_universe(posting_file, universe_data)
                new_post = self.process_NOT(post_A, universe_post)
                post_st.append(new_post)
            else:
                if item not in dictionary:
                    post_st.append([])
                else:
                    post = load_posting(dictionary, posting_file, item)
                    post_st.append(post)

        return post_st.pop()


class OptimisedQueryProcessor(QueryProcessor):
    """
    Optimised approach to query operations.
    Optimisations are: 
    - Multiple AND (unparenthesised), from lowest freq
    - Cancelling Multiple NOTs
    """
    def process(self, query, dictionary, posting_file, universe_data):
        """
        Processes a query of postfix tokens, extracting the posting list data using a dictionary,
        posting file handler, and universe.
        Args:
            query (deque): Tokenised queue of postfix query
            dictionary (dict): Dictionary of term's data (frequency, position, size)
            posting_file (file): File object of posting file
            universe_data (tuple): Universe metadata (frequency, position, size)
        Returns:
            (skiplist): Processed skip list of postings
        """
        post_st = []
        idx = 0 # some optimisations might skip few idxes
        while idx < len(query):
            item = query[idx]
            if Tokeniser.is_binary_op(item):
                if item == Tokeniser.AND:
                    # do optimisation
                    idx, new_post = self.optimised_multi_AND(idx, query, post_st)
                elif item == Tokeniser.OR:
                    post_A = post_st.pop()
                    post_B = post_st.pop()
                    new_post = self.process_OR(post_A, post_B)
                post_st.append(new_post)
            elif Tokeniser.is_unary_prefix_op(item):
                # currently only has NOT as a unary prefix
                universe_post = load_universe(posting_file, universe_data)
                idx, new_post = self.optimised_multi_NOT(idx, query, post_st, universe_post)
                post_st.append(new_post)
            else:
                if item not in dictionary:
                    post_st.append([])
                else:
                    post = load_posting(dictionary, posting_file, item)
                    post_st.append(post)
            
            idx += 1

        return post_st.pop()
    
    def optimised_multi_AND(self, idx, query, post_st):
        """
        Optimises multiple AND operations using document frequency. Orders terms in pairs of increasing frequency.
        Excludes case when parenthesis exist in query e.g. 'x1 AND (x2 AND x3) AND x4'
        Args:
            idx (int): Current index of query queue
            query (list): Tokenised queue of postfix query 
            post_st (list): Stack of posting skip list
        ReturnsL
            idx (int): Next index of query queue
            new_post (skiplist): AND processed skip list of postings
        """
        assert query[idx] == Tokeniser.AND
        running_counter = itertools.count() # used for tiebreaking purpose
        # stored as triple (df, running_counter, posting)
        pq = []
        # minimally, we have these two to evaluate
        assert len(post_st) >= 2
        for _ in range(2):
            post = post_st.pop()
            heapq.heappush(pq, (len(post), next(running_counter), post))

        # potentially have more to evaluate
        while (idx+1 < len(query) and query[idx+1] == Tokeniser.AND):
            post = post_st.pop()
            heapq.heappush(pq, (len(post), next(running_counter), post))
            idx += 1
        
        while (len(pq) > 1):
            _, _, post_A = heapq.heappop(pq)
            _, _, post_B = heapq.heappop(pq)
            post = self.process_skip_AND(post_A, post_B)
            heapq.heappush(pq, (len(post), next(running_counter), post))
        
        assert len(pq) == 1
        _, _, new_post = pq[0]
        return idx, new_post
    
    def optimised_multi_NOT(self, idx, query, post_st, universe_post):
        """
        Optimises multiple NOT operations, skips evaluation of every NOT.
        e.g. 'NOT NOT NOT NOT NOT NOT x'
        Args:
            idx (int): Current index of query queue
            query (deque): Tokenised queue of postfix query 
            post_st (list): Stack of skip list of postings
            universe_post (list): Skip list of every postings
        Returns:
            idx (int): Next index of query queue
            new_post (skiplist): NOT processed skip list of postings
        """
        new_post = post = post_st.pop()
        should_apply_not = True 
        while (idx+1 < len(query) and query[idx+1] == Tokeniser.NOT):
            should_apply_not = not should_apply_not
            idx += 1
        
        if should_apply_not:
            new_post = self.process_NOT(post, universe_post)
        
        return idx, new_post