for ys in year_seqs:
	seq_to_check = ys
	start_id = year_seqs[seq_to_check]['start_id']
	end_id = year_seqs[seq_to_check]['end_id']
	start_year = year_seqs[seq_to_check]['start_year']
	end_year = year_seqs[seq_to_check]['end_year']
	search_query = year_seqs[seq_to_check]['search_query']
	
	entities_full.update(get_entities([start_id]))
	count = 1
	next_id = start_id

	print('starting at the beginning of the chain')
	while True:
		try:
			next_id = entities_full[next_id]['claims']['P156'][0]['mainsnak']['datavalue']['value']['id']
			entities_full.update(get_entities([next_id]))
			count += 1
			item_label = get_label(entities_full[next_id])
			print(count, next_id, item_label)
		except Exception as e:
			print(e)
			print('first gap starts at', next_id)
			gap_start = next_id
			if 'P585' in entities_full[next_id]['claims']:
			    gap_start_year = int(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
			else:
			    gap_start_year = start_year
			    check_years(year_seqs[seq_to_check])
			print(gap_start)
			break


	entities_full.update(get_entities([end_id]))
	count = 1
	next_id = end_id

	print('starting at the end of the chain')
	while True:
		try:
			next_id = entities_full[next_id]['claims']['P155'][0]['mainsnak']['datavalue']['value']['id']
			entities_full.update(get_entities([next_id]))
			count += 1
			item_label = get_label(entities_full[next_id])
			print(count, next_id, item_label)
		except Exception as e:
			print(e)
			print('last gap ends at', next_id)
			gap_end = next_id
			if 'P585' in entities_full[next_id]['claims']:
			    gap_end_year = int(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
			else:
			    gap_end_year = end_year
			    check_years(year_seqs[seq_to_check])
			print(gap_end)
			break

	with open('seq_entities_full.json', 'w') as efile:
		json.dump(entities_full, efile, indent=4)

	search_results = []

	print('checking the gaps')
	if gap_start_year < gap_end_year:
		for y in range(gap_start_year - 1, gap_end_year + 1):
			search_results.append(search_year_item(y, search_query))
			time.sleep(0.2)

	with open('gap_search_results.json', 'w') as gapfile:
		json.dump(search_results, gapfile, indent=4)

	ids = []

	for result in search_results:
		if len(result['search']) == 1:
			result_id = result['search'][0]['id']
			ids.append(result_id)
			if result_id not in entities_full:
			    entities_full.update(get_entities([result_id]))
			    time.sleep(0.1)
		elif len(result['search']) == 0:
			print('no results for', result)
		elif len(result['search']) > 1:
			print('multiple results for', result)

