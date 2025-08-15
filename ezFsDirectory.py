#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A file system item that serves as a container for more items
"""
import typing
from abc import abstractmethod
import os
import re
from paths import asUrl,UrlCompatible,URL
import ezFs


# returns whether the walk should continue or not
FileWalkerCallback=typing.Callable[[
    ezFs.EzFsItem,typing.Optional[typing.Any]
    ],typing.Optional[bool]]


class EzFsDirectory(ezFs.EzFsItem):
    """
    A file system item that serves as a container for more items
    """
    def __init__(self,
        url:UrlCompatible,
        filesystem:"ezFs.EzFsFilesystem"):
        """ """
        ezFs.EzFsItem.__init__(self,url,filesystem)

    @property
    def isDir(self)->bool:
        """ is this a directory? """
        return True

    @property
    def url(self)->typing.Optional[URL]:
        """
        This is a getter/setter because EzFsFilesystem wants to override
        the functionality to change its working directory upon set.
        """
        return self._url
    @url.setter
    def url(self,url:URL):
        if url is not None: # make sure it always ends with '/'
            u=str(url)
            if u[-1]!='/':
                url=asUrl(u+'/')
        self._url=url

    @abstractmethod
    def mount(self,
        location:UrlCompatible,
        otherFs:typing.Optional["ezFs.EzFsFilesystem"]=None
        )->URL:
        r"""
        mount this directory to a location on another filesystem

        :param location: path where to mount
        :param otherFs: filesystem to mount to (this is a virtual mounting
            for ease of logical use only and does not physically mount the file)
            .
            If None, it WILL mount to the local filesystem and it WILL
            be accessible to the rest of the system
            .
            Thus mount('/mnt/mything',None) IS NOT the same thing as mount('/mnt/mything',OsFs())

        TODO: implement this.  See also:
        C:\Users\kurt\AppData\Local\Programs\Python\Python37\Lib\site-packages\fs-0.5.5a1-py3.7.egg\fs\mountfs.py  # noqa: E501 # pylint: disable=line-too-long
        """
    def printTree(self,indent:str='')->None:
        """
        Print the entire directory structure as a tree
        """
        if self.name is not None:
            print(f'{indent}{self.name}')
        indent=indent+'  '
        for child in self.children:
            child.printTree(indent)

    @property
    @abstractmethod
    def children(self)->typing.Iterable[ezFs.EzFsItem]:
        """
        returns a dict of {name:EzFsItem}

        DERIVED CLASSES MUST IMPLEMENT THIS!
        """

    def __len__(self)->int:
        """
        access this like a list
        """
        return len(list(self.children))

    def __iter__(self)->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        access this like a list
        """
        yield from self.children

    def __getitem__(self,idx:typing.Union[int,str])->ezFs.EzFsItem:
        """
        access this like a list or dict
        (idx can be an index or a name)
        """
        if isinstance(idx,int):
            for i,v in enumerate(self.children):
                if i==idx:
                    return v
            raise IndexError()
        else:
            for v in self.children:
                if v.name==idx:
                    return v
            raise IndexError()

    @abstractmethod
    def markDirty(self)->None:
        """
        marks the directory "dirty" and in need of refreshing

        DERIVED CLASSES MUST IMPLEMENT THIS!
        """

    def relative(self,subdir:str)->ezFs.EzFsItem:
        """
        get an item relative to this directory
        """
        # gets a url relative to the current location
        if self.url is None:
            raise Exception('Attempting to get relative directory of an empty location') # noqa: E501 # pylint: disable=line-too-long
        subUrl=self.url.relative(subdir)
        return self.filesystem._getFsItem(subUrl)  # noqa: E501 # pylint: disable=line-too-long,disable=protected-access

    def listdir(self,
        subdir:typing.Optional[str]=None
        )->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        return a list of sub-directory values
        """
        if subdir is not None:
            fsDir=self.get(subdir)
        else:
            fsDir=self
        if isinstance(fsDir,EzFsDirectory):
            yield from fsDir
    ls=listdir
    dir=listdir

    def open(self,
        path:UrlCompatible,
        accessMode:typing.Optional[str]='rw'
        )->ezFs.EzFsFile:
        """
        opens the file at the given path
        """
        fileObj=self.get(path)
        if not isinstance(fileObj,ezFs.EzFsFile):
            raise ezFs.FileAccessException(path)
        return fileObj.open(accessMode)

    def delete(self, # pylint: disable=arguments-differ
        relativePath:typing.Optional[str]=None
        )->None:
        """
        if a relativePath is given, will delete the child

        otherwise, will delete this directory
        """
        if relativePath is not None:
            self.get(relativePath).delete()
        else:
            ezFs.EzFsItem.delete(self)
    rm=delete

    def rename(self, # pylint: disable=arguments-differ
        newName:str,
        relativePath:typing.Optional[str]=None
        )->None:
        """
        if a relativePath is given, will rename the child

        otherwise, will rename this directory
        """
        if relativePath!='.':
            self.get(relativePath).rename(newName)
        else:
            ezFs.EzFsItem.rename(self,newName)

    def regexFind(self,
        expression:typing.Union[str,typing.Pattern],
        ignoreCase:bool=False,
        idx:int=0
        )->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        Find all files that match a given regular expression
        """
        if ignoreCase:
            expression=re.compile(expression,re.IGNORECASE)
        else:
            expression=re.compile(expression)
        # test each child against regular expression
        for item in self.children:
            if not expression.match(item.name):
                continue
            # if it is the end, add it, if there is more, keep searching deeper
            if isinstance(item,EzFsDirectory):
                yield from item.regexFind(expression,ignoreCase,idx+1)
            else:
                yield item

    def glob(self,
        expression:typing.Union[str,typing.List[str]],
        ignoreCase:bool=False,
        idx:int=0
        )->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        returns an iterable object representing all files that match a glob
        expression

        works just like the built-in glob library in that it accepts the tricks
            *, ?, and character ranges expressed with []

        idx is used internally to handle complex expressions like ./*/bin/*.exe
        """
        if isinstance(expression,list):
            pathExpr=expression
        else:
            # convert string expression into a list
            if os.sep!='/':
                expression=expression.replace(os.sep,'/')
            while expression.startswith('./\\'):
                expression=expression[2:]
            pathExpr=expression.split('/')
        exp=pathExpr[idx]
        isLast=len(pathExpr)<=idx+1
        isGlob=exp.find('?')>=0 or exp.find('*')>=0 or exp.find('[')>=0
        if isGlob:
            # convert glob expression to regular expression
            exp=re.escape(exp)
            exp=exp.replace('\\\'\\*\\\'','.*?').replace('\\?','.?')
            exp=exp.replace('\\[','[').replace('\\]',']').replace('\\-','-')
            yield from self.regexFind(exp,ignoreCase,idx)
        else:
            # simply find the next child
            child:typing.Optional[ezFs.EzFsItem]=None
            if ignoreCase:
                exp=exp.lower()
                for c in self.children:
                    name=c.name
                    if name.lower()==exp:
                        child=c
                        break
            elif exp is not None:
                for c in self.children:
                    if c==exp:
                        child=c
                        break
            # if it is the end, add it, if there is more, keep searching deeper
            if child is not None:
                if isLast:
                    yield from self.children
                elif isinstance(child,EzFsDirectory):
                    yield from child.glob(expression,ignoreCase,idx+1)
    find=glob

    def getAll(self,
        subdir:typing.Optional[str]=None,
        _tape:typing.Optional[typing.Dict[ezFs.EzFsItem,None]]=None
        )->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        retrieves all children, grandchildren, etc

        iterates in a breadth-first manner
        guranteed to only return each item once (and will not
        include the starting directory)

        :parameter _tape: # ordered dict used internally for traversal

        """
        weAreTopParent=False
        if _tape is None:
            _tape={}
            weAreTopParent=True
        target:ezFs.EzFsItem=self
        if subdir is not None:
            target=self.relative(subdir)
            if not isinstance(target,EzFsDirectory):
                return
        _tape[target]=None
        # add all children to the search list
        for item in self.children:
            if item not in _tape:
                _tape[item]=None
        if weAreTopParent:
            for item in _tape:
                yield item
                if isinstance(item,EzFsDirectory):
                    # it appends its child items to the end of the tape
                    item.getAll(None,_tape)

    def get(self,
        path:typing.Union[UrlCompatible,typing.List[str]],
        idx:int=0
        )->ezFs.EzFsItem:
        """
        retrieves the file or directory at the given path
        """
        if not isinstance(path,list):
            # if we are in the midst of a traversal, this would already
            # be split. Since it is not, we need to.
            strPath=asUrl(path).url.split('://',1)[-1]
            path=strPath.split('/')
            if not path[0] and not self.isRoot:
                # started with /, so go for root
                return self.filesystem.root.get(path,1)
        # by now path is always a list
        if len(path)<=idx:
            return self
        # process the next step in the path
        pathStep:str=path[idx]
        if not pathStep or pathStep=='.':
            # indicates current directory
            return self.get(path,idx+1)
        if pathStep=='..':
            if self.parent is None:
                raise FileNotFoundError('attempt to traverse past root')
            return self.parent.get(path,idx+1)
        children:typing.List[ezFs.EzFsItem]=list(self.children)
        child:typing.Optional[ezFs.EzFsItem]=None
        # try the simple match first
        for c in children:
            if pathStep==c.name:
                child=c
            break
        if child is None and not self.filesystem.caseSensitive:
            # need to do a case-insensitive search
            pathStep=pathStep.lower()
            for c in children:
                if str(c.name).lower()==pathStep:
                    child=c
                    break
        if child is None: # nothing matched!
            print(f'not found {pathStep} in {[c.name for c in children]}')
            raise FileNotFoundError(os.sep.join(path))
        if len(path)==idx+1:
            # if it is the last item in the path, then this
            # is finally what we were looking for
            return child
        # navigate into the found child directory
        if isinstance(child,EzFsDirectory):
            return child.get(path,idx+1)
        # still an error if we are a file, but wanting to be
        # traversed like a directory
        raise FileNotFoundError(path)

    def walk(self,
        filesCb:typing.Optional[FileWalkerCallback]=None,
        context:typing.Any=None,
        algo:typing.Optional[str]=None,
        tape:typing.Optional[typing.Any]=None
        )->typing.Optional[bool]:
        """
        a file tree walker

        filesCb(EzFsFile,context)

        NOTE: will recieve directories too, plus some items are a file acting
        as a directory, so you may want to be thoughtful about checking
        for what you want

        algo - search algorithm.  One of:
            'NEAREST' - start with all nodes 1 directory away,
                then all 2 away, etc (useful when searching)
            'TREE' - follow the file tree in order (useful for printing)
            'DEAPTH-FIRST' - like TREE, but visit the deepest leaves first
                (useful when renaming)
        (default is TREE)

        tape - used to keep track of traversal

        if either returns anything besides None, will cancel
        the walk with that value

        :return: whether a calling walk should continue or not
        """
        if algo is None:
            algo='TREE'
        top=tape is None
        if algo=='NEAREST':
            if top:
                class Tape:
                    """
                    A computational machine tape
                    """
                    def __init__(self):
                        self.next=[]
                tape=Tape()
            for c in self.children:
                if filesCb is not None:
                    result=filesCb(c,context)
                    if result is not None:
                        return result
            if top:
                tape=typing.cast(Tape,tape)
                while tape.next:
                    nextItem=tape.next.pop(0)
                    nextItem.walk(filesCb,context,algo,tape)
        elif algo=='TREE':
            if not top:
                if filesCb is not None:
                    result=filesCb(self,context)
                if result is not None:
                    return result
            for c in self.children:
                if isinstance(c,EzFsDirectory):
                    result=c.walk(filesCb,context,algo,True)
                else:
                    if filesCb is not None:
                        result=filesCb(c,context)
                if result is not None:
                    return result
        elif algo=='DEAPTH-FIRST':
            for c in self.children:
                if isinstance(c,EzFsDirectory):
                    result=c.walk(filesCb,context,algo,True)
                else:
                    if filesCb is not None:
                        result=filesCb(c,context)
                if result is not None:
                    return result
            if not top:
                if filesCb is not None:
                    result=filesCb(self,context)
                if result is not None:
                    return result
        return None
