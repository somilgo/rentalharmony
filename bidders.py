import random

class Bidder:

	def initialize_valuations(self, valuations):
		self.n = len(valuations)
		self.valuations = valuations

	def initialize_simplex_valuations(self, n):
		self.n = n
		random_list = []
		for i in range(n-1):
			random_list.append(random.random())
		random_list.append(0.)
		random_list.append(1.)
		list.sort(random_list)
		valuations = []
		for i in range(len(random_list)-1):
			valuations.append(random_list[i+1] - random_list[i])
		self.valuations = valuations

	def initialize_random_valuations(self, n, max_price_per_room = 1.0):
		self.n = n
		valuations = []
		for i in range(n):
			valuations.append(max_price_per_room * random.random())
		self.valuatinos = valuations

	def initialize_random_int_valuations(self, n, max_price_per_room = 100):
		assert(int(max_price_per_room) == max_price_per_room)
		self.n = n
		valuations = []
		for i in range(n):
			valuations.append(random.randint(0,max_price_per_room))
		self.valuatinos = valuations

	def recompute_demand_set(self, prices):
		max_utility = -1e9
		demand_set = []
		n = self.n
		self.prices = prices
		for i in range(n):
			curr_utility = self.valuations[i] - self.prices[i]
			if curr_utility > max_utility:
				max_utility = curr_utility
				demand_set = [ i ]
			elif curr_utility == max_utility:
				demand_set.append(i)
		self.demand_set = set(demand_set)

	def indirect_utility(self, prices):
		max_utility = -1e9
		n = self.n
		for i in range(n):
			curr_utility = self.valuations[i] - self.prices[i]
			if curr_utility > max_utility:
				max_utility = curr_utility
		return max_utility

	def utility(self, i, prices):
		return self.valuations[i] - self.prices[i]


class BidderGroup:

	def __init__(self, n, valuation_scheme = "simplex", max_val=0):
		bidders = [Bidder() for i in range(n)]
		for bidder in bidders:
			if valuation_scheme == "simplex":
				b.initialize_simplex_valuations(n)
			elif valuation_scheme == "random":
				b.initialize_random_valuations(n, max_price_per_room = max_val)
			elif valuation_scheme == "random_int":
				b.initialize_random_int_valuations(n, max_price_per_room = max_val)
		self.bidders = bidders
			