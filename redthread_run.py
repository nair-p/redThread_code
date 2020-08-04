import pickle as pkl
from redthread import RedThread
from argparse import ArgumentParser

def get_args():
	parser = ArgumentParser()
	parser.add_argument("-data","--data_file",default="./sample_data/sampled_data_features.pkl", help="path to the data pickle files containing the freature matrix")
	parser.add_argument("-label","--label_file", default="./sample_data/sampled_data_labels.pkl", help='path to the labels of the data points as a pickle file')
	parser.add_argument("-modality", "--feature_name_file", default="./sample_data/sampled_data_feature_names.pkl", help="path to the feature names of the data as as pickle file")
	parser.add_argument("--data_folder", default="./sample_data/", help="path to the folder containing the different feature files")
	parser.add_argument("--budget", default=100, help='Number of times the model can query the user')
	args = parser.parse_args()
	return args

def iterative_labelling(seed, budget, rt):
	query_counter = 0 # initializing the query counter "b" in the algorithm
	label_hash = rt.label_hash
	rt_graph = rt.get_graph()
	picked_nodes = []
	precision = 0.
	recall = 0.
	num_relevant = sum(list(label_hash.values()))
	 
	while query_counter < budget:
		print("Remaining Number of queries : " + str(budget-query_counter))
		picked_node = rt.infer_redthread() # pick a data point
	
		if picked_node not in list(label_hash.keys()):
			picked_node_label = rt.oracle(picked_node) # querying the user for the label of the picked node
			rt.update_label_hash(picked_node, picked_node_label) # update the label hash based on the oracle output
			query_counter += 1 
		else:
			picked_node_label = label_hash[picked_node]
		rt.update_redthread(picked_node, picked_node_label)
		picked_nodes.append(picked_node)
		if picked_node_label == 1:
			precision += 1
			recall += 1
		#print(label_hash)
	precision /= budget
	recall /= num_relevant
	return precision, recall

def extract_info(args):
	data_file = args.data_file
	label_file = args.label_file
	all_feature_file = args.feature_name_file

	data = pkl.load(open(data_file, "rb"))
	labels = pkl.load(open(label_file, "rb"))
	feature_names = pkl.load(open(all_feature_file, "rb"))
	feature_map = {}
	feature_map["desc_uni"] = pkl.load(open(args.data_folder + "desc_feature_names_uni.pkl","rb"))
	feature_map["desc_bi"] = pkl.load(open(args.data_folder + "desc_feature_names_bi.pkl","rb"))
	feature_map["title_uni"] = pkl.load(open(args.data_folder + "title_feature_names_uni.pkl","rb"))
	feature_map["title_bi"] = pkl.load(open(args.data_folder + "title_feature_names_bi.pkl","rb"))
	feature_map["loc_uni"] = pkl.load(open(args.data_folder + "loc_feature_names.pkl","rb"))

	return data, labels, feature_names, feature_map

if __name__ == "__main__":

	# get command line arguments
	args = get_args()

	# get the data and labels and feature names
	data, labels, feature_names, feature_map = extract_info(args)

	# choose a seed node. Choosing 0th node for now
	seed = 0

	# create a RedThread object
	rt = RedThread(data, labels, seed, feature_names, feature_map)

	precision, recall = iterative_labelling(seed, args.budget, rt)
	f1_score = 2 * precision * recall / (precision + recall)
	print("Precision = " + str(precision))
	print("Recall = " + str(recall))
	print("F1 score = " + str(f1_score))
	print("success")