import argparse
from collections import defaultdict
import itertools as it


def hash(num1, num2):
  ''' Hash function for the hash table '''
  return (num1 ^ num2) % 1000


def create_bitmap(hash_table, threshold):
  ''' Convert the hash table into a bitmap '''
  bit_map = []
  for key, value in hash_table.items():
    if value < threshold:
      bit_map.insert(key, 0)
    else:
      bit_map.insert(key, 1)

  return bit_map

def create_candidate_item_set(dataset_file):
  ''' Create a dictionary of all candidate item sets from the data set with their corresponding count '''
  
  candidate_item_list = defaultdict(int)
  baskets = []

  buckets = {}

  with open(dataset_file) as file:
    for line in file:
      ##
      # Create the candidate item set
      ##
      num_list = map(int, line.split())
      # create a list of all baskets
      baskets.append(num_list)
      # create a dictionary with a count of each individual item
      for item in num_list:
        candidate_item_list[item] += 1

      ##
      # Create pairs of unique items in each bucket
      ##
      pairs = list(it.combinations(num_list, 2))
      for pair in pairs:
        index = hash(pair[0], pair[1]) 
        buckets[index] = 1 if index not in buckets else buckets[index]+1

  return candidate_item_list, baskets, buckets


def create_frequent_item_set(item_list, min_threshold):
  ''' Return the frequent items from the candidate_item_list that meet the min_support '''

  # delete items that dont meet min threshold
  for key, value in item_list.items():
    if value < min_threshold:
      del item_list[key]

  return item_list.keys()


def count(item_list, baskets):
  ''' Count the number of frequent item sets in the baskets '''
  count = dict(zip(item_list, [1]*len(item_list)))

  for basket in baskets:
    for key in count.iterkeys():
      if set(list(key)) < set(basket):
        count[key] += 1 

  return count


def join(freq_item_sets, k):
  ''' Generate the joint transactions from candidate sets of size k '''
  
  # k is the size of each item set
  if k <= 2: 
    return list(it.combinations(freq_item_sets, k))
  else:
    return list(it.combinations(set(a for b in freq_item_sets for a in b),k))



def apriori(dataset_file, threshold):  
  
  C1, baskets, buckets = create_candidate_item_set(dataset_file)
  bitmap = create_bitmap(buckets, threshold)
  F1_items = create_frequent_item_set(C1, threshold)

  # hash each frequent item into the bitmap and remove non frequent pairs
  frequent_pairs = join(F1_items, 2)
  for pair in frequent_pairs:
    hash_value = hash(pair[0], pair[1])
    if bitmap[hash_value] is not 1:
      frequent_pairs.remove(pair)

  if not frequent_pairs:
    return None
  else:
    # Initialize with possible frequent pairs
    L = [frequent_pairs]
    items = count(L[0], baskets)
    # check which frequent pairs meet minimum threshold value
    L[0] = create_frequent_item_set(items, threshold)

    k = 3
    while(True):
      new_list = join(L[k-3], k)
      items = count(new_list, baskets)

      Fk_items = create_frequent_item_set(items, threshold)
      if len(Fk_items) > 0:
        L.append(Fk_items)
        k+=1
      else:
        break
    
    
    return L[k-3]

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='APriori Algorithm')
  parser.add_argument('datafile', help='Dataset File')
  parser.add_argument('threshold', help='Threshold Value')

  args = parser.parse_args()

  print 'Frequent Item Sets with threshold:', args.threshold  
  print apriori(args.datafile, int(args.threshold))

