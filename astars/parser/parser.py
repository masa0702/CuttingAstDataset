import anytree
from os import path
from ..nodes.node import ANode
from tree_sitter import Language, Parser, Node

from ._nodeAdd import _addNode

LIB_PATH = path.join(path.dirname(__file__), "grammar", "tree-sitter", "languages.so")
Language.build_library(
    LIB_PATH,
    [
        path.join(path.dirname(__file__), "grammar", "tree-sitter", "tree-sitter-python"),
        path.join(path.dirname(__file__), "grammar", "tree-sitter", "tree-sitter-c"),
        path.join(path.dirname(__file__), "grammar", "tree-sitter", "tree-sitter-cpp"),
    ]
)

class AParser:
    def __init__(self) -> None:
        pass
    
    def parse(self, text:str, lang:str) -> None:
        ANY_LANGUAGE = Language(LIB_PATH, lang)
        parser = Parser()
        parser.set_language(ANY_LANGUAGE)

        self.tree = parser.parse(bytes(text, "utf8"))
        self.textList = self._splitText(text)
        self.cst = self._ts2Anytree(source=self.tree.root_node, parent=None, textList=self.textList)

        return self.cst

    def _ts2Anytree(self, source, parent:ANode=None, textList:list=None) -> None:
        if parent == None:
            target = _addNode(source=source, textList=textList)
        else:
            target = _addNode(source=source, parent=parent)

        for child in source.children:
            self._ts2Anytree(child, target)

        return target

    def _splitText(self, text:str) -> list:
        lineText = text.splitlines()
        textList = []
        for splitLine in lineText:
            if splitLine == lineText[-1]:
                textList.append(list(splitLine))
            else:
                textList.append(list(splitLine)+["\n"])
        return textList