import logging
from os import path
from copy import deepcopy
from astars import AParser, AstAnalyser, AstOperator, ACodeGenerator
from anytree import RenderTree

logging.basicConfig(format='%(asctime)s -\n %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', 
                    level=logging.INFO)

def main():
    with open(path.join(path.dirname(__file__), "input", "test.py")) as f:
        code = f.read()
        
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
        logging.info(generator.generate(root=editedTree))
        
if __name__ == "__main__":
    main()
    
    
