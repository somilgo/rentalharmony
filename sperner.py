import numpy as np
import itertools
import copy
from functools import partial

class Edge:

	def __init__(self, neighbor, data):
		self.neighbor = neighbor
		self.data = data

	def __str__(self):
		return str(self.data)
	def __unicode__(self):
		return str(self.data)
	def __repr__(self):
		return "Edge: " + str(self.data)

class Vertex:

	def __init__(self, coords):
		self.coords = coords
		self.edges = []

	def add_edge(self, neighbor, data):
		self.edges.append(Edge(neighbor, data))
		neighbor.edges.append(Edge(self, data))

	def __hash__(self):
		if self.coords == None:
			return 0
		return hash(frozenset(self.coords))

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __str__(self):
		return str(self.coords)
	def __unicode__(self):
		return str(self.coords)
	def __repr__(self):
		return "Vertex: " + str(self.coords)

class Bidder: 

	def __init__(self, name, valuation):
		self.name = name
		self.valuation = valuation

	def pref(self, prices):
		show=False
		for p in range(len(prices)):
			if prices[p] == 1:
				out = len(prices)-1 if p==0 else p-1
				return out
			if prices[p] != 0:
				break
		for i in range(len(prices)):
			if prices[i] == 0:
				return i
		utility = [value - price for value, price in zip(self.valuation, prices)]
		return utility.index(max(utility))

def generate_graph(sub_divs):
	verts = {}
	vertstest = {}
	n = len(sub_divs[0])
	count = 0
	for sub_div in sub_divs:
		sub_div = [tuple(round(x, 7) for x in y) for y in sub_div]
		count += 1
		new_vert = Vertex(sub_div)
		for x in range(n):
			hashed_edge = frozenset([sub_div[a] for a in range(n) if a != x])
			for vert in verts.get(hashed_edge, []):
				new_vert.add_edge(vert, hashed_edge)
			if verts.get(hashed_edge):
				verts[hashed_edge].append(new_vert)
			else:
				verts[hashed_edge] = [new_vert]
	return verts


def subdivide_wrapper(simplex_points, iterations):

	def subdivide(p, iterations):
		if iterations == 0:
			return [p]
		n = len(p)
		perms = itertools.permutations(p)
		sub_divs = []
		for perm in perms:
			sub_verts = []
			for i in range(n):
				v = [0] * n
				for j in range(i+1):
					v = [v[k] + perm[j][k] for k in range(n)]
				v = tuple([x / (i+1) for x in v])
				sub_verts.append(v)
			sub_divs.append(sub_verts)

		all_sub_divs = []
		for sub_div in sub_divs:
			all_sub_divs += subdivide(sub_div, iterations-1)
		return all_sub_divs

	print("Subdividing...")
	sub_divs = subdivide(simplex_points, iterations)

	print("Done Subdividing!")
	return generate_graph(sub_divs)

def assign_owners(start_vert, gg):
	n = len(start_vert.coords)
	owner_labels = {}
	for label, coord in zip(range(n),start_vert.coords):
		if owner_labels.get(coord):
			raise BaseException
		owner_labels[coord] = label

	labeled = set()
	labeled.add(start_vert)
	to_label = []
	for e in start_vert.edges:
		to_label.append(e.neighbor)
	while len(to_label) > 0:
		vert = to_label.pop(0)
		if vert in labeled:
			continue
		unlabeled_coord = None
		found_unlabeled = False
		unused_labels = set(range(n))
		for coord in vert.coords:
			label = owner_labels.get(coord)
			if label == None:
				if found_unlabeled:
					raise BaseException
				unlabeled_coord = coord
				found_unlabeled = True
			else:
				unused_labels.remove(label)

		if found_unlabeled and (len(unused_labels) == 1):
			owner_labels[unlabeled_coord] = unused_labels.pop()
		labeled.add(vert)
		for e in vert.edges:
			if e.neighbor not in labeled:
				to_label.append(e.neighbor)

	return owner_labels

def traverse_trap_doors(graph, owner_labels, bidders):
	n = len(next(iter(graph.values()))[0].coords)

	def get_trap_doors():
		trans_owner_labels = {}
		trap_doors = []
		for i in range(n):
			border_simplex = []
			trunc_bidders = []
			for edge_set in graph:
				if all([c[i]==0 for c in edge_set]):
					border_simplex.append(edge_set)
			simplex_graph = generate_graph(border_simplex)
			output = traverse_trap_doors(simplex_graph, owner_labels, bidders)
			for o in output:
				trap_doors.append(frozenset(o.coords))
		return trap_doors


	def check_if_trap_door(edge):
		unused_prefs = set(range(n))
		for coord in edge.data:
			pref = bidders[owner_labels[coord]].pref(coord)
			if pref in unused_prefs:
				unused_prefs.remove(pref)
		return len(unused_prefs) == 1

	def check_if_disparate(vertex):
		used_prefs = set()
		for coord in vertex.coords:
			pref = bidders[owner_labels[coord]].pref(coord)
			used_prefs.add(pref)
		return len(used_prefs) == n
	
	disparates = set()
	full_disparates = set()
	
	if n == 2:
		for vertices in graph.values():
			for vertex in vertices:
				if check_if_disparate(vertex):
					disparates.add(vertex)
	else:
		#For testing purposes - brute force comparison
		# for vertices in graph.values():
		# 	for vertex in vertices:
		# 		if check_if_disparate(vertex):
		# 			full_disparates.add(vertex)
		# return full_disparates
		starting_edges = get_trap_doors()
		traversed = set()
		to_traverse = []
		to_traverse += starting_edges
		while len(to_traverse) != 0:
			edge = to_traverse.pop()
			vertices = graph[edge]
			for vertex in vertices:
				if vertex in traversed:
					continue
				if check_if_disparate(vertex):
					disparates.add(vertex)
				for e in vertex.edges:
					if check_if_trap_door(e):
						to_traverse.append(e.data)
				traversed.add(vertex)
	return disparates

def compute_average_solution(v):
	n = len(v.coords)
	average_sol = [0.] * n
	for coord in v.coords:
		average_sol = [average_sol[i] + coord[i] for i in range(n)]
	average_sol = [x / n for x in average_sol]

	return average_sol

def check_solution_quality(v, bidders = []):
	n = len(v.coords)
	#Compute average solution from approximate
	average_sol = compute_average_solution(v)

	#Make sure everyone prefers a different room
	used_prefs = set()
	social_welfare = 0.
	total_utility = 0.
	for bidder in bidders:
		pref = bidder.pref(average_sol)
		social_welfare += bidder.valuation[pref]
		total_utility += bidder.valuation[pref] - average_sol[pref]
		used_prefs.add(pref)

	if len(used_prefs) != n:
		return -1e9, -1e9 #This solution is not envy free
	return social_welfare, total_utility


print("Creating Graph via Semper Triangle...")
graph = subdivide_wrapper([np.array([1,0,0,0]), np.array([0,0,1,0]), np.array([0,1,0,0]), np.array([0,0,0,1])], 4)
print("Done creating graph!")
print("Labelling the Semper Triangle with owners...")
owner_labels = assign_owners(next(iter(graph.values()))[0], graph)

print("Done Labelling!")
print("Solving for approximate solution...")
bidders3 = [Bidder(0,[0.34, 0.35, 0.33]), Bidder(1,[0.5, 0.20, 0.35]), Bidder(2,[0.75, 0.2, 0.05])]
bidders4 = [Bidder(0,[0.25, 0.25, 0.25, 0.25]), 
			Bidder(1,[0.5, 0.5/3, 0.5/3, 0.5/3]), 
			Bidder(2,[.2, 0.3, 0.1, 0.4]),
			Bidder(3,[0.8, .1, .07, .03])]
bidders = bidders4
solutions = traverse_trap_doors(graph, owner_labels,bidders)
print("Solved! Computed", len(solutions), "solutions.")
best_solution = max(solutions, key=partial(check_solution_quality, bidders=bidders))
print("Best Solution:", compute_average_solution(best_solution), 
		"with (social welfare, total_utility)", check_solution_quality(best_solution, bidders=bidders))

