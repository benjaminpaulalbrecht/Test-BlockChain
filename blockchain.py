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
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest() 

    def __init__(self):

        self.nodes = set() 

        # stores all the blocks in the entire blockchain 
        self.chain = [] 

        # temporarily stores the transactions for the current block 
        self.current_transactions = [] 


        # create the genesis block with a specific fixed hash 
        # of previous block genesis block starts with 0 
        genesis_hash = self.hash_block("genesis_block") 
        self.append_block( 
            hash_of_previous_block = genesis_hash, 
            nonce = self.proof_of_work(0, genesis_hash, []) 
        )

    # //? allows a new node to be added to the nodes member. 
    def add_node(self,address): 
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        print(parsed_url.netloc) 

    # use PoW to find the none for the current block 
    def proof_of_work(self, index, hash_of_previous_block, transactions): 
        #try with nonce = 0 
        nonce = 0 

        # try hashing the nonce together with the hash of the previous block until it's valid
        while self.valid_proof(index, hash_of_previous_block, transactions,nonce) is False: 
            nonce += 1
        return nonce 

    # //? determine if a given blockchain is valid 
        # 1. the valid_chain() method validates that a given blockchain is valid by performing the following checks: 
        # checks each block in the bc and hashes each block to verify that the hash of each block is correctly recorded in the nect block 
        # 2. verifies that the nonce in each block is valid
    def valid_chain(self, chain): 

        last_block = chain[0] # the genesis block 
        current_index = 1 # starts with the second block 

        while current_index < len(chain0): 
            block = chain[current_index]
            if block['hash_of_previous_block'] != self.hash_block(last_block): 
                return False
            
            # check for vaild nonce 
            if not self.valid_proof(
                current_index,
                block['hash_of_previous_block'],
                block['transactions'],
                block['nonce']):
                return flase 

            # move on to the next block on the chain 
            last_block = block
            currentindex += 1


        #the chain is valid 
        return True 

    def valid_proof(self, index, hash_of_previous_block, transactions, nonce): 

        # create a string containing the hash of the previous block and the block content, including the nonce. 
        content =  f'{index}{hash_of_previous_block}{transactions}{nonce}'.encode() 
        
        #hash using sha256 
        content_hash = hashlib.sha256(content).hexdigest() 

        # check if the hash meets the difficulty target 
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target

    #//? creates a new block and adds it to the blockchain 
    def append_block(self, nonce, hash_of_previous_block): 
        block = { 
            'index': len(self.chain),
            'timestamp': time(), 
            'transactions': self.current_transactions,
            'nonce': nonce, 
            'hash_of_previous_block': hash_of_previous_block
        }

        # reset the current list of transactions 
        self.current_transactions = [] 

        # add the new block to the blockchain 
        self.chain.append(block)
        return block 

        #//* When the block is added to the blockchain, the current timestamp is also added to the block. 

    def update_blockchain(self):
        # gets the nodes around us that have been registered
        neighbors = self.nodes
        new_chain = None 

        # grab and verify the chains from all of the nodes in our network 
        for node in neighbors: 
            # get the blockchain from the other nodes
            response = requests.get(f'http://{node}/blockchain') 

            if response.status_code == 200: 
                length = repsonse.json()['length']
                chain = response.json()['chain']

            # check to see if the length is longer and the chain is valid
            if length > max_length and self.valid(chain): 
                max_length = length 
                new_chain = chain 
            # replace our chain if a new, valid chain exists and is longer than ours
            if new_chain: 
                self.chain = new_chain 
                return True
        return False 

    #//? add_transaction: 
    # This method adds a new transactions to the current list of transactions.
    # it then gets the indexof the last block in the blockchain and adds one to it. 
    # this new index will the block that the current transaction will be added to.  
    def add_transaction(self, sender, recipient, amount): 
        self.current_transactions.append({
            'amount':amount,
            'recipient': recipient, 
            'sender': sender,
        })
        return self.last_block['index'] + 1 

    @property 
    def last_block(self): 
        #//? returns the last block in the blockchain 
        return self.chain[-1] 



app = Flask(__name__)

#//? generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', "")

#//? instantiate the Blockchain 
blockchain = Blockchain() 

#//? return the entire blockchain 
@app.route('/blockchain', methods=['GET'])
def full_chain(): 
    response = { 
        'chain': blockchain.chain, 
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200 

# //? perform mining 

@app.route('/mine', methods=['GET'])
def mine_block(): 
    blockchain.add_transaction( 
        sender="0",
        recipient = node_identifier,
        amount=1,
    )

    #obtain the hash of the last block in the blockchain 
    last_block_hash = blockchain.hash_block(blockchain.last_block) 

    # using PoW, get the nonce for the new block to be added to the blockchain 
    index = len(blockchain.chain) 
    nonce = blockchain.proof_of_work(index, last_block_hash, blockchain.current_transactions) 

    # add the new block to the blockchain using the last block hash and the current nonce
    block = blockchain.append_block(nonce, last_block_hash) 
    response = { 
        'message': "New Block Minded!", 
        'index': block['index'],
        'hash_or_previous_block': 
            block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'transactions': block['transactions'],
    }
    return jsonify(response), 200 


    # //? Adding Transactions 
    @app.route('/transactions/new', methods=['POST']) 
    def new_transaction(): 
        # get the value passed in from the client
        values = request.get_json() 

        # cehck that the required fields are in the POST'd data
        required_fields = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required_fields):
            return ('Missing fields'), 400 

        # create a new transaction
        index = blockchain.add_transaction( 
            values['sender'],
            values['recipient'],
            values['amount']
        )    

        response = {'message': f'Transaction will be added to the block {index} Rejoice.'}
        return (jsonify(response), 201) 


# //? the /nodes/add_nodes route allows a node to register one or more neighboring nodes. 
@app.route('/nodes/add_nodes', methods=['POST'])
def add_nodes(): 
    # get the nodes passed in from the client
    values = request.get_json() 
    nodes = values.get('nodes')

    if nodes is None: 
        return "Error: Missing Nodes info", 400 
    response = { 
        'message': 'New Nodes added', 
        'nodes':list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/sync', methods=[GET])
def sync(): 
    updated = blockchain.update_blockchain() 
    if updated: 
        response = { 
            'message': 'The blockchain has been updated to the latest', 
            'blockchain': blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
