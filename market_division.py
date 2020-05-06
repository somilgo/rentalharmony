from bidders import Bidder

def compute_maximum_matching(bidders, n):
	room_edges = {}
	bidder_edges = {}
	for i in range(n):
		room_edges[i] = set([])
	for i in range(len(bidders)):
		bidder_edges[i] = bidders[i].demand_set
		for room in bidders[i].demand_set:
			room_edges[room].add(i)

	flow = {(i,j) : 0 for i in range(len(bidders)) for j in range(n)}

	unsaturated_bidders = set(range(len(bidders)))
	unsaturated_rooms = set(range(n))

	while True:
		bidder_q = list(unsaturated_bidders)
		room_q = []
		room_paths = {}
		bidder_paths = {}
		while len(bidder_q) != 0 or len(room_q) != 0:
			if len(room_q) > 0:
				v = room_q.pop()
				if v in unsaturated_rooms:
					room_paths[-1] = v
					unsaturated_rooms.remove(v)
					break
				for bidder in room_edges[v]:
					if bidder not in bidder_paths and flow[(bidder, v)] > 0:
						bidder_q.append(bidder)
						bidder_paths[bidder] = v
			elif len(bidder_q) > 0:
				v = bidder_q.pop()
				if v not in bidder_paths:
					bidder_paths[v] = -1
				for room in bidder_edges[v]:
					if room not in room_paths and flow[(v,room)] <= 0:
						room_q.append(room)
						room_paths[room] = v
			else:
				raise BaseException
		if room_paths.get(-1) == None:
			break
		else:
			curr_room = True
			curr = room_paths[-1]
			while True:
				if curr_room:
					new_curr = room_paths[curr]
				else:
					new_curr = bidder_paths.get(curr)
					if new_curr == -1:
						unsaturated_bidders.remove(curr)
						break
				
				if curr_room:
					flow[(new_curr, curr)] += 1
				else:
					flow[(curr, new_curr)] -= 1
				curr_room = not curr_room
				curr = new_curr
	matching = set([])
	for edge in flow:
		if flow[edge] == 1:
			matching.add(edge)
	return matching

def compute_mods(bidders):
	n = len(bidders)
	new_bidders = []
	for b in bidders:
		if len(b.demand_set) != 0:
			new_bidders.append(b)
	bidders = new_bidders
	if len(bidders) == 0:
		return set([])
	matching = compute_maximum_matching(bidders, n)
	N = set(range(len(bidders)))
	matched_bidders = set([m[0] for m in matching])
	unmatched_bidders = N - matched_bidders
	if len(unmatched_bidders) == 0:
		return set([])
	i = next(iter(unmatched_bidders))
	mod_set = bidders[i].demand_set
	od_set = set([])

	while len(mod_set) != 0:
		mod_set_matched_bidders = [m[0] for m in matching if m[1] in mod_set]
		od_set = od_set | mod_set
		mod_set = set([])
		for j in mod_set_matched_bidders:
			mod_set = mod_set | bidders[j].demand_set
		mod_set = mod_set - od_set

	min_set = set([])
	mod_set = od_set

	for a in od_set:
		mod_set = mod_set - set([a])
		mod_set_matched_bidders = [i for i in bidders if i.demand_set <= (min_set | mod_set)]
		trunc_bidders = [i for i in mod_set_matched_bidders]
		trunc_matching = compute_maximum_matching(trunc_bidders, n)
		k = len(trunc_matching)
		if k == len(mod_set_matched_bidders):
			min_set = min_set | set([a])

	return min_set

def compute_ODS(bidders):
	mod = compute_mods(bidders)
	od = mod
	while len(mod) > 0:
		for b in bidders:
			b.demand_set = b.demand_set - mod
		mod = compute_mods(bidders)
		od = od | mod
	return od

def compute_price_differential(od, bidders, prices):
	if len(od) == 0:
		return 0
	overly_demanding_bidders = [b for b in bidders if b.demand_set <= od]
	potential_differentials = []
	for bidder in overly_demanding_bidders:
		indirect_utility = bidder.indirect_utility(prices)
		under_demanded_utilities = []
		for s in range(len(bidders)):
			if s not in od:
				under_demanded_utilities.append(bidder.utility(s, prices))
		potential_differentials.append(indirect_utility - max(under_demanded_utilities))

	return min(potential_differentials)


def conduct_discrete_price_auction(bidders, C):
	n = len(bidders)
	prices = [C/n] * n
	
	while True:
		for bidder in bidders:
			bidder.recompute_demand_set(prices)

		od = compute_ODS(bidders)
		for bidder in bidders:
			bidder.recompute_demand_set(prices)

		if len(od) == 0:
			return compute_maximum_matching(bidders, n), prices
		
		x = compute_price_differential(od, bidders, prices)

		for r in range(n):
			if r not in od:
				prices[r] -= len(od) * x / n
			else:
				prices[r] += (n - len(od)) * x / n

bidders = [Bidder() for b in range(6)]
bidders[0].initialize_valuations([15, 18, 10, 15, 24, 28])
bidders[1].initialize_valuations([18, 25,  3, 18, 25, 15])
bidders[2].initialize_valuations([ 6, 25, 15, 18, 18, 25])
bidders[3].initialize_valuations([15,  5, 18, 12,  9, 25])
bidders[4].initialize_valuations([ 6, 22,  5,  5, 10, 12])
bidders[5].initialize_valuations([ 6,  9,  2, 21, 25,  9])
C = 60

print(conduct_discrete_price_auction(bidders, C))
