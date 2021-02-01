import hashlib
import random
import string
import json
import binascii
import numpy as np
import pandas as pd
import pylab as pl
import logging
import datetime
import collections

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


'''
Simulation that serves the purpose to educate about the working of the blockchain.
The simulation generates clients, transactions, a blockchain consisting of blocks and a miner.
Each block in the blockchain represents one transaction. 
The validation process of each transaction is left out in the simulation, but it is mentioned when it shoud occur.
Based on the Python Blockchain Tutorial on TutorialsPoint (https://www.tutorialspoint.com/python_blockchain/index.htm).
'''


transactions = []  # Transaction queue
last_block_hash = ''


class Client:
	def __init__(self):
		random = Crypto.Random.new().read
		self._private_key = RSA.generate(1024, random)
		self._public_key = self._private_key.publickey()
		self._signer = PKCS1_v1_5.new(self._private_key)

	@property
	def identity(self):  # Return the generated public key in its HEX representation
		return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')
		

class Transaction:
	def __init__(self, sender, recipient, value):
		self.sender = sender  # Sender's client object
		self.recipient = recipient  # Recipient's public key
		self.value = value  # Transaction amount
		self.time = datetime.datetime.now()  # Time of transaction


	# Returns Transaction's instance variables in a dictionary object
	def to_dict(self):
		if self.sender == 'Genesis':  # If the sender is the first block in the blockchain
			identity = 'Genesis'
		else:
			identity = self.sender.identity

		return collections.OrderedDict({
			'sender': identity,
			'recipient': self.recipient,
			'value': self.value,
			'time': self.time})


	# Sign dictionary object using the private key of the sender
	def sign_transaction(self):
		private_key = self.sender._private_key
		signer = PKCS1_v1_5.new(private_key)
		hash = SHA.new(str(self.to_dict()).encode('utf8'))
		return binascii.hexlify(signer.sign(hash)).decode('ascii')


class Block:
	def __init__(self):
		self.verified_transaction = ''  # Each block consists of an arbitrary amount of transactions, in this case just one
		self.previous_block_hash = ''  # Hash of the previous block in the chain
		self.Nonce = ''  # Value that miners have to calculate 


class Blockchain:
	def __init__(self):
		self.chain = []


	def display_blockchain(self):
		print('Number of blocks in chain: ' + str(len(self.chain)) + '\n')
		for x in range(len(self.chain)):
			block_temp = self.chain[x]
			print('Block #' + str(x))
			print('--------------')
			transaction = block_temp.verified_transaction
			display_transaction(transaction)
			print('=====================================')


class Miner:
	def __init__(self):
		pass

	def sha256(self, message):
		return hashlib.sha256(message.encode('ascii')).hexdigest()


	def mine(self, message, difficulty = 1):
		assert difficulty >= 1
		prefix = '1' * difficulty

		for i in range(1000):
			digest = self.sha256(str(hash(message)) + str(i))
			if digest.startswith(prefix):
				print('After ' + str(i) + ' iterations found nonce: ' + digest)
			return digest


def display_transaction(transaction):
	dict = transaction.to_dict()
	print('Sender: ' + dict['sender'])
	print('Recipient: ' + dict['recipient'])
	print('Value: ' + str(dict['value']))
	print('Time: ' + str(dict['time']))


def simulation():
	last_transaction_index = 0  # Tracks the total number of messages already mined

	# Initialize blockchain
	blockchain = Blockchain()

	# Initialize clients
	Nathan = Client()
	Steven = Client()
	Alex = Client()
	Michelle = Client()

	# Setup the Genesis block
	genesis_transaction = Transaction(
		'Genesis', 
		Nathan.identity, 
		0)
	genesis_block = Block()
	genesis_block.previous_block_hash = None
	genesis_block.Nonce = None

	# Add the Genesis block
	genesis_block.verified_transaction = genesis_transaction
	digest = hash(genesis_block)
	last_block_hash = digest
	blockchain.chain.append(genesis_block)

	# Generate transactions
	t1 = Transaction(
		Nathan,
		Alex.identity,
		125)
	t1.sign_transaction()
	transactions.append(t1)
	t2 = Transaction(
		Michelle,
		Steven.identity,
		750)
	t2.sign_transaction()
	transactions.append(t2)
	t3 = Transaction(
		Nathan,
		Steven.identity,
		50)
	t3.sign_transaction()
	transactions.append(t3)
	t4 = Transaction(
		Steven,
		Alex.identity,
		1000)
	t4.sign_transaction()
	transactions.append(t4)
	t5 = Transaction(
		Alex,
		Nathan.identity,
		250)
	t5.sign_transaction()
	transactions.append(t5)

	# Initialize miner
	miner = Miner()

	# Adding more blocks
	while last_transaction_index < len(transactions):  # For each transaction in the transaction queue
		block = Block()  # Initialize block
		transaction = transactions[last_transaction_index]
		# At this point in the process, the transaction would be validated, which is not included in this sumulation
		# If transaction is valid, proceed:
		block.verified_transaction = transaction
		last_transaction_index += 1

		block.previous_block_hash = last_block_hash
		block.Nonce = miner.mine(block, 2)
		digest = hash(block)
		blockchain.chain.append(block)
		last_block_hash = digest

	blockchain.display_blockchain()


if __name__ == '__main__':
	simulation()