from collections import deque
from tokeniser import Tokeniser

class Parser:
    def shunting_yard(self, infix_tokens):
        """
        Converts infix order of tokens to postfix using shunting yard algorithm:
        1. If term:
            - enqueue to output queue
        2. If binary operator:
            - pop the higher precedence ones and push to queue
            - the push operator to the stack
        3. If open parens:
            - push to the stack
        4. If close parens:
            - pop operator_stack until you find a opening parens
        5. If unary operator:
            - push to the stack
        Args:
            infix_tokens (list): Infix ordered list of tokens
        Returns:
            output_q (deque): Postfix ordered queue of tokens
        """
        output_q = deque()
        op_st = []
        for token in infix_tokens:
            if Tokeniser.is_value(token):
                output_q.append(token)
            elif Tokeniser.is_binary_op(token):
                while (op_st
                    and not Tokeniser.is_open_paren(op_st[-1])
                    and Tokeniser.precedence[op_st[-1]] > Tokeniser.precedence[token]):
                    output_q.append(op_st.pop())
                op_st.append(token)
            elif Tokeniser.is_open_paren(token) or Tokeniser.is_unary_prefix_op(token):
                op_st.append(token)
            elif Tokeniser.is_close_paren(token):
                while (op_st
                    and not Tokeniser.is_open_paren(op_st[-1])):
                    output_q.append(op_st.pop())
                assert Tokeniser.is_open_paren(op_st[-1])
                op_st.pop()
            else:
                raise Exception(f"Unknown token: '{token}' found")

        # flush out
        while op_st:
            assert not Tokeniser.is_open_paren(op_st[-1])
            output_q.append(op_st.pop())

        return output_q
    
    def to_postfix(self, infix_tokens):
        """
        Parses infix order of tokens into postfix using shunting yard algorithms.
        Args:
            infix_tokens (list): Infix ordered list of tokens
        Returns:
            (deque): Postfix ordered queue of tokens
        """
        return self.shunting_yard(infix_tokens)
