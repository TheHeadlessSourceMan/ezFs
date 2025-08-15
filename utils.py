#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
ezFS base classes
"""
#import typing
import ezFs


PATH_SEP='/'


def printTree(treeItem:ezFs.EzFsItem)->None:
    """
    print(out a file tree)
    """
    def _treeStr(treeItem,indent=''):
        """
        recursive print routine
        """
        if treeItem.name is None:
            ret=['']
        else:
            ret=[treeItem.name]
        #print(ret)
        for c in list(treeItem.children.values()):
            ret.append(_treeStr(c,indent+'  |'))
        return ('\n'+indent+'- ').join(ret)
    print(_treeStr(treeItem))
