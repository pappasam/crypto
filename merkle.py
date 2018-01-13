'''Playing around with Merkle Trees

This is based on my reading on Bitcoin.
Implemented as binary trees from bottom to top.

Tree is considered immutable after creation, so the mutability
of the tree after the __init__ method is avoided by design

Author: Samuel Roeca <samuel.roeca@gmail.com>
Date Started: 2017-01-13
'''

import hashlib
import json
import itertools
from collections import OrderedDict
from typing import List, Dict, NamedTuple, Optional
from pprint import pprint


def hash_alg(inval: str) -> str:
    '''Hash a given input value'''
    return hashlib.sha3_256(inval.encode()).hexdigest()


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


class Node:
    '''A node within a MerkleTree'''

    def __init__(
            self,
            left: Optional['Node'] = None,
            right: Optional['Node'] = None,
            value: Optional[str] = None,
    ) -> None:
        bool_no_children = left is None and right is None
        bool_children = left is not None and right is not None
        if not (bool_no_children or bool_children):
            raise ValueError(
                'Children must both be Nodes or both be None'
            )
        elif bool_no_children and value is None:
            raise ValueError('Must have a Value if Children are None')
        elif bool_children and value is not None:
            raise ValueError('Must NOT have a value if Children are not None')

        self.left = left
        self.right = right
        self.parent = None  # type: Optional[Node]
        self.value = value if bool_no_children else hash_alg(
            self.left.value + self.right.value
        )

        if bool_children:
            self.left.parent = self
            self.right.parent = self


class MerkleTree:
    '''The Merkle tree data structure'''

    def __init__(self, transactions_hashed: List[str]):
        '''Initializer

        :param transactions: transaction hashes to be placed in initial tree
        '''
        self.base_nodes = OrderedDict([
            (transaction, Node(value=transaction))
            for transaction in transactions_hashed
        ])
        if len(self.base_nodes) != len(transactions_hashed):
            raise ValueError('Transactions must be a unique list')
        self.root_node = self._get_root_node()
        self._str = None  # type: Optional[str]

    def _get_root_node(self) -> Node:
        '''Construct the Merkle Tree, culminating at the root Node'''
        node_stack = list(self.base_nodes.values())
        while True:
            if len(node_stack) is 1:
                return node_stack[0]
            temp_node_stack = []
            for left, right in grouper(node_stack, 2):
                if right is None:
                    temp_node_stack.append(left)
                else:
                    temp_node_stack.append(Node(left=left, right=right))
            node_stack = temp_node_stack.copy()

    @property
    def root_hash(self) -> str:
        '''Obtain root hash'''
        return self.root_node.value

    def is_valid_leaf(self, root_hash: str, leaf_value: str) -> bool:
        '''Check that a hashed value of a leaf is valid

        This still a work in progress; not sure if this actually solves
        the problem
        '''
        return leaf_value in self.base_nodes and root_hash == self.root_hash

    def __str__(self) -> str:
        '''The string representation of the hash tree

        Might consider constructing this from bottom-to-top,
        just like the tree itself
        '''

if __name__ == '__main__':
    transactions = ['hello', 'world', 'my', 'favorite', 'person']
    hash_transactions = [hash_alg(t) for t in transactions]
    m = MerkleTree(hash_transactions)
    print('root hash: ', m.root_hash)
    print('real transactions: ', transactions)
    print('hash transactions:', hash_transactions)
