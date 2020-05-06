def compute_mods(bidders):
	matching = compute_maximum_matching(bidders)
	N = set(range(n))
	matched_bidders = set([m[0] for m in matching])
	unmatched_bidders = N - matched_bidders
	if len(unmatched_bidders) == 0:
		return matching 
	i = next(iter(unmatched_bidders))
	mod_set = i.demand_set
	od_set = set([])

	while len(mod_set) != 0:
		mod_set_matched_bidders = [m[0] for m in matching if m[1] in mod_set]
		od_set = od_set | mod_set
		mod_set = set([])
		for j in mod_set_matched_bidders:
			mod_set = mod_set | j.demand_set
		mod_set = mod_set - od_set

	min_set = set([])
	mod_set = od_set

	for a in od_set:
		mod_set = mod_set - set([a])
		mod_set_matched_bidders = [i for i in bidders if i.demand_set <= (min_set | mod_set)]
		trunc_bidders = [bidders[i] for i in mod_set_matched_bidders]
		trunc_matching = compute_maximum_matching(trunc_bidders)
		k = len(trunc_matching)
		if k == len(mod_set_matched_bidders):
			min_set = min_set | set([a])

	return min_set
