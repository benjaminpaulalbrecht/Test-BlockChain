import sys

import hashlib
import json 

from time import time 
from uuid import uuid4 

from flask import Flask, jsonify, request 

import requests 
from urllib.parse import urlparse 

class Blockchain(object): 

    difficulty_target = "0000"

    def hash_block(self, block): 
        block_encoded = json.dumps(block, sort_keys=True).endcode()
        return hashlib.sha256(block_encoded).hexdigest() 

    def __init__(self): 
        # stores all the blocks in the entire blockchain 
        self.chain = [] 

        # temporarily stores the transactions for the current block 
        self.current_transactions = [] 


        # create the genesis block with a specific fixed hash 
        # of previous block genesis block starts with 0 
        genesis_hash = self.hash_block("genesis_block") 
        self.append_block( 
            hash_of_previous_block = genesis_hash, 
            nonce = self.proof_of_work(0, gensis_hash, []) 
        )

        