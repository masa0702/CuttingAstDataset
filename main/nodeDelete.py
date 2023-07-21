import logging
import ast
import os
import json
import random
import Levenshtein
from os import path
import pandas as pd
from copy import deepcopy
from astars import AParser, AstAnalyser, AstOperator, ACodeGenerator
from anytree import RenderTree

logging.basicConfig(format='%(asctime)s -\n %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', 
                    level=logging.INFO)

def compileable_code(code):
    try:
        ast.parse(code)
        print("True")
        return True
    except SyntaxError:
        print("False")
        pass
        return False

def dist2cosSim(distance:int) -> float:
    return 1/(1+distance)

def create_data(save_jsonl_path, file_name, source_code, target_code, delete_node_count, jsonLines, jsonlDict):
    if compileable_code(target_code):

        source_char_length = len(source_code)
        target_char_length = len(target_code)
        source_line_length = len(source_code.split("\n"))
        target_line_length = len(target_code.split("\n"))
        leven_dist_char = Levenshtein.distance(source_code, target_code)
        
        source_line = source_code.split("\n")
        target_line = target_code.split("\n")
        leven_dist_line = 0
        for line_a, line_b in zip(source_line, target_line):
            line_distance = Levenshtein.distance(line_a, line_b)
            leven_dist_line += line_distance
        
        cos_sim_char = dist2cosSim(leven_dist_char)
        cos_sim_line = dist2cosSim(leven_dist_line)
        cos_sim_nodedel = dist2cosSim(delete_node_count)
        
        jsonlDict["index"] = f"Delete_{delete_node_count}"
        jsonlDict["Filename"] = file_name
        jsonlDict["source"] = source_code
        jsonlDict["target"] = target_code   
        jsonlDict["sourceSizeChar"] = source_char_length
        jsonlDict["targetSizeChar"] = target_char_length
        jsonlDict["sourceSizeLine"] = source_line_length
        jsonlDict["targetSizeLine"] = target_line_length
        jsonlDict["levenDistChar"] = leven_dist_char
        jsonlDict["levenDistLine"] = leven_dist_line
        jsonlDict["deleteNodeCount"] = delete_node_count
        jsonlDict["cosSimChar"] = cos_sim_char
        jsonlDict["cosSimLine"] = cos_sim_line
        jsonlDict["cosSimNodeDel"] = cos_sim_nodedel
            
        jsonLines.append(jsonlDict)
        
    else:
        pass 
        
    df = pd.DataFrame(jsonLines)
    df.to_json(save_jsonl_path, orient="records", lines=True)
    
def save_data_to_jsonl(data, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'a') as f:
            f.write(data + '\n')
    else:
        with open(file_path, 'w') as f:
            f.write(data + '\n')
        
def clear_jsonl_file(file_path):
    with open(file_path, "w") as file:
        file.write("")

def delete_node_count(allNodeList):
        deleteNodeCount = [len(count.descendants)+1 for count in allNodeList]
        return deleteNodeCount
    
def main(filename):
    with open(path.join(path.dirname(__file__), "input", filename)) as f:
        code = f.read()
    
    compileable_code(code)
    parser = AParser()
    tree = parser.parse(text=code, lang="python")
    logging.info(RenderTree(tree).by_attr("type"))
    
    operator = AstOperator()
    generator = ACodeGenerator()
    logging.info(generator.generate(root=tree))
    
    front_dumplicatedTree = deepcopy(tree)
    back_dumplicatedTree = deepcopy(tree)
    random_dumplicatedTree = deepcopy(tree)
    
    front_allNodeList = AstAnalyser.allNodes(front_dumplicatedTree, "post", False)
    back_allNodeList = AstAnalyser.allNodes(back_dumplicatedTree, "post", True)
    random_allNodeList = AstAnalyser.allNodes(random_dumplicatedTree, "post", False)
    
    front_deleteNodeCount = delete_node_count(front_allNodeList)
    back_deleteNodeCount = delete_node_count(back_allNodeList)
    random_deleteNodeCount = delete_node_count(random_allNodeList)
    
    front_json_path = f"main/dataset/frontSeqDel/front_del_{filename}.jsonl"
    back_json_path = f"main/dataset/backSeqDel/back_del_{filename}.jsonl"
    random_json_path = f"main/dataset/randomDel/random_del_{filename}.jsonl"
    random_json_path_special = f"main/dataset/randomSpeDel/random_del_special_{filename}.jsonl"
    
    # front2del
    front_jsonLines = []
    for subtree, deleteCount in zip(front_allNodeList, front_deleteNodeCount):
        jsonlDict = {}
        
        editedTree = operator.delete(root=front_dumplicatedTree, target=subtree)
        restored_code = generator.generate(root=editedTree)
        
        create_data(front_json_path, filename, code, restored_code, deleteCount, front_jsonLines, jsonlDict)
        
    # back2del
    back_jsonLines = []
    for subtree, deleteCount in zip(back_allNodeList, back_deleteNodeCount):
        jsonlDict = {}
        
        editedTree = operator.delete(root=back_dumplicatedTree, target=subtree)
        restored_code = generator.generate(root=editedTree)
        
        create_data(back_json_path, filename, code, restored_code, deleteCount, back_jsonLines, jsonlDict)
        
    # random2del
    random_jsonLines = []
    sqcial_jsonLines = []
    random_len = int(len(random_allNodeList))
    random_node_list = list(random_allNodeList)

    for subtree, deleteCount in zip(back_allNodeList, random_deleteNodeCount):
        random_node = random.choice(random_node_list)
        deleteCount = random_deleteNodeCount[random_allNodeList.index(random_node)]
        random_dumplicatedTree = deepcopy(tree)
        jsonlDict = {}
        editedTree = operator.delete(root=random_dumplicatedTree, target=random_node)
        restored_code = generator.generate(root=editedTree)

        print("random_delete_node : ", deleteCount)
        
        if random_node.type in ['if', 'for', 'while']:
            create_data(random_json_path_special, filename, code, restored_code, deleteCount, random_jsonLines, jsonlDict)
        else:
            create_data(random_json_path, filename, code, restored_code, deleteCount, random_jsonLines, jsonlDict)
    
    random_node_list.remove(random_node)  # 選択された要素をrandom_node_listから削除
    
if __name__ == "__main__":
    code_list = ["main/shapeData/test.jsonl", "main/shapeData/train.jsonl", "main/shapeData/valid.jsonl"]
    for code in code_list:
        with open(code, "r") as f:
            for line in f:
                data = json.loads(line)
                filename = data["file_path"]
                py_code = data["code"]
                main(py_code)