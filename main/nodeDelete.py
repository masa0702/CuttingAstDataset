import logging
import ast
import os
import Levenshtein
from os import path
from copy import deepcopy
from astars import AParser, AstAnalyser, AstOperator, ACodeGenerator
from anytree import RenderTree

logging.basicConfig(format='%(asctime)s -\n %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', 
                    level=logging.INFO)

def compileabe_code(code):
    try:
        ast.parse(code)
        print("True")
        return True
    except SyntaxError:
        print("False")
        return False

def create_data(save_directory_path, file_name, source_code, target_code, delete_node_count):
    jsonl_path = os.path.join(save_directory_path, f"{file_name}.jsonl")
    
    source_char_length = len(source_code)
    target_char_length = len(target_code)
    source_line_length = len(source_code.split("\n"))
    target_line_length = len(target_code.split("\n"))
    leven_dist_char = Levenshtein.distance(source_code, target_code)
    
    source_line = source_code.split("\n")
    target_line = target_code.split("\n")
    for line_a, line_b in zip(source_line, target_line):
        line_distance = Levenshtein.distance(line_a, line_b)
        leven_dist_line += line_distance
        
    data = {
        "index": "Delete_{delete_node_count}",
        "sourceFilename": file_name,
        "targetFilename": file_name,
        "source": source_code,
        "target": target_code,
        "sourceSizeChar": source_char_length,
        "targetSizeChar": target_char_length,
        "levenDistChar": leven_dist_char,
        "levenDistLine": leven_dist_line,
        "deleteNodeCount": delete_node_count
    }
    
    

def main():
    with open(path.join(path.dirname(__file__), "input", "test.py")) as f:
        code = f.read()
    
    compileabe_code(code)
    parser = AParser()
    tree = parser.parse(text=code, lang="python")
    logging.info(RenderTree(tree).by_attr("type"))
    
    operator = AstOperator()
    generator = ACodeGenerator()
    logging.info(generator.generate(root=tree))
    
    dumplicatedTree = deepcopy(tree)
    allNodeList = AstAnalyser.allNodes(dumplicatedTree, "post", True)
    
    for subtree in allNodeList:
        editedTree = operator.delete(root=dumplicatedTree, target=subtree)
        # logging.info(generator.generate(root=editedTree))
        restored_code = generator.generate(root=editedTree)
        
        if compileabe_code(restored_code):
            pass           

if __name__ == "__main__":
    main()