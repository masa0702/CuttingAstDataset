import logging
import ast
import os
import json
import Levenshtein
from os import path
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
        return False

def dist2cosSim(distance:int) -> float:
    return 1/(1+distance)

def create_data(save_directory_path, file_name, source_code, target_code, delete_node_count):
    jsonl_path = os.path.join(save_directory_path, f"{file_name}.jsonl")
    
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
    
    pair_data = []
    pair = {
        "index": f"Delete_{delete_node_count}",
        "sourceFilename": file_name,
        "targetFilename": file_name,
        "source": source_code,
        "target": target_code,
        "sourceSizeChar": source_char_length,
        "targetSizeChar": target_char_length,
        "sourceSizeLine": source_line_length,
        "targetSizeLine": target_line_length,
        "levenDistChar": leven_dist_char,
        "levenDistLine": leven_dist_line,
        "deleteNodeCount": delete_node_count,
        "cosSimChar": cos_sim_char,
        "cosSimLine": cos_sim_line,
        "cosSimNodeDel": cos_sim_nodedel
    }
    
    pair_data.append(pair)
    
    with open(jsonl_path, "w") as f:
        for pair in pair_data:
            f.write(json.dumps(pair) + "\n")
    f.close()
    
def  save_to_json_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file)
        
def clear_jsonl_file(filename):
    with open(filename, "w") as file:
        file.write("")

def main(filename):
    with open(path.join(path.dirname(__file__), "input", filename + ".py")) as f:
        code = f.read()
    
    compileable_code(code)
    parser = AParser()
    tree = parser.parse(text=code, lang="python")
    logging.info(RenderTree(tree).by_attr("type"))
    
    operator = AstOperator()
    generator = ACodeGenerator()
    logging.info(generator.generate(root=tree))
    
    dumplicatedTree = deepcopy(tree)
    allNodeList = AstAnalyser.allNodes(dumplicatedTree, "post", True)
    
    temp_json_path = "main/save_jsonl"
    delete_node_count = 0
    
    for subtree in allNodeList:
        editedTree = operator.delete(root=dumplicatedTree, target=subtree)
        # logging.info(generator.generate(root=editedTree))
        restored_code = generator.generate(root=editedTree)
        delete_node_count += 1
        print("delete_node : ",delete_node_count)
        if compileable_code(restored_code):
            
        else:
            pass         
        create_data(save_directory_path, filename, code, restored_code, delete_node_count)
        print("add data")

if __name__ == "__main__":
    main("test")