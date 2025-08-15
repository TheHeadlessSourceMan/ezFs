#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A single item hanging on a filesystem tree
"""
import typing
from abc import abstractmethod
from paths import asUrl,UrlCompatible,URL
import ezFs


class EzFsItem:
    """
    A single item hanging on a filesystem tree

    TODO: inherit from a tree node
    """

    def __init__(self,
        url:UrlCompatible,
        filesystem:typing.Optional["ezFs.EzFsFilesystem"]=None):
        """ """
        self.fsId:typing.Optional[str]=None
        self._parent:typing.Optional["ezFs.EzFsDirectory"]=None
        self._filesystem:typing.Optional[ezFs.EzFsFilesystem]=filesystem
        self._url:typing.Optional[URL]=asUrl(url)
        self.canWatch:bool=False

    @property
    def isRoot(self)->bool:
        """
        is this the root of the filesystem tree?
        """
        return False

    @property
    @abstractmethod
    def isDir(self)->bool:
        """ is this a directory? """
    @property
    def isFile(self)->bool:
        """ is this a file? """
        return not self.isDir

    def __hash__(self)->int:
        """
        return a hash value for sorting
        """
        return self.url.__hash__()

    def __eq__(self,
        other:typing.Union["EzFsItem",UrlCompatible,object]
        )->bool:
        """
        Compare two items for equality
        """
        if other is None:
            return False
        if isinstance(other,EzFsItem):
            other=str(other.url)
        return str(self.url)==other

    @property
    def path(self)->typing.Optional[str]:
        """
        the path
        """
        if self.url is None:
            return None
        return self.url.path

    @property
    def abspath(self)->typing.Optional[str]:
        """
        absolute path to this item
        """
        return self.path

    @property
    def filename(self)->str:
        """
        the file name
        """
        if self.url is None:
            return ''
        return self.url.filename
    @filename.setter
    def filename(self,toName:str):
        if self.url is not None:
            toName=self.url.sibling(toName)
            self.filesystem._rename(self.url,toName) # noqa: E501 # pylint: disable=line-too-long,disable=protected-access
    @property
    def name(self)->str:
        """
        this is the short name of the file
        """
        if self.url is None or self.url.resource is None:
            return ''
        return self.url.resource
    @name.setter
    def name(self,name:str):
        if self.url is not None:
            self.url.resource=name

    @property
    def filesystem(self)->"ezFs.EzFsFilesystem":
        """
        The filesystem this is a part of
        """
        if self._filesystem is None:
            import ezFs._ezFs
            self._filesystem=ezFs._ezFs.EzFs(self._url)\
                .workingDirectory\
                .filesystem  # pylint: disable=protected-access
        return self._filesystem

    @property
    def url(self)->typing.Optional[URL]:
        """
        This is a getter/setter because EzFsFilesystem wants to override
        the functionality to change its working directory upon set.
        """
        return self._url
    @url.setter
    def url(self,url:UrlCompatible):
        if isinstance(url,URL):
            url=url.copy()
        else:
            url=asUrl(url)
        self._url=url

    def read(self)->str:
        """
        Read this file
        """
        if self.url is None:
            raise FileNotFoundError('None')
        return self.url.read()

    @abstractmethod
    def addWatch(self,
        watchFn:ezFs.WatcherFn,
        pollingInterval:float=30
        )->None:
        """
        add a change watcher to this item
        """

    @abstractmethod
    def removeWatch(self,
        watchFn:ezFs.WatcherFn
        )->None:
        """
        remove a change watcher to this item
        """

    @property
    def root(self)->"ezFs.EzFsDirectory":
        """
        the root directory for our filesystem
        """
        return self.filesystem.root
    @property
    def parent(self)->"ezFs.EzFsDirectory":
        """
        parent directory
        """
        if self._parent is None:
            from ezFs import EzFsDirectory
            if self.url is None or self.url.parent is None:
                raise FileNotFoundError()
            parentItem=self.filesystem.get(self.url.parent)
            self._parent=typing.cast(EzFsDirectory,parentItem)
        return self._parent

    def printTree(self,indent:str='')->None:
        """
        print(the item's tree)
        """
        print(indent+self.name)

    def delete(self)->None:
        """
        delete the item from the system
        """
        self.filesystem._delete(self) # pylint: disable=protected-access

    def rename(self,newName:str)->None:
        """
        Change the name of the item
        """
        self.filesystem._rename(self,newName)  # noqa: E501 # pylint: disable=line-too-long,protected-access

    def __repr__(self)->str:
        return str(self.url)
