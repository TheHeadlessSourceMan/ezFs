#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A single item hanging on a filesystem tree
"""
import typing
from abc import abstractmethod
from paths import asUrl,UrlCompatible,URL
if typing.TYPE_CHECKING:
    from ezFs import EzFsFilesystem,EzFsDirectory,WatcherFn


class EzFsItem:
    """
    A single item hanging on a filesystem tree

    TODO: inherit from a tree node
    """

    def __init__(self,
        url:UrlCompatible,
        filesystem:typing.Optional["EzFsFilesystem"]=None):
        """ """
        self.fsId:typing.Optional[str]=None
        self._parent:typing.Optional["EzFsDirectory"]=None
        self._filesystem:typing.Optional[EzFsFilesystem]=filesystem
        self._url:typing.Optional[URL]=URL(url)
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
    @abstractmethod
    def exists(self)->bool:
        """ does the file exist? """

    @property
    def isFile(self)->bool:
        """ is this a file? """
        return self.exists and not self.isDir

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
    def filename(self,toName:UrlCompatible):
        if self.url is not None:
            toName=self.url.sibling(toName)
            self.filesystem.rename(self.url,toName)
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
    def filesystem(self)->"EzFsFilesystem":
        """
        The filesystem this is a part of
        """
        if self._filesystem is None:
            import ezFs._ezFs
            fsItem=ezFs._ezFs.EzFs(self._url) # pylint: disable=protected-access
            self._filesystem=fsItem.workingDirectory.filesystem
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
        watchFn:"WatcherFn",
        pollingInterval:float=30
        )->None:
        """
        add a change watcher to this item
        """

    @abstractmethod
    def removeWatch(self,
        watchFn:"WatcherFn"
        )->None:
        """
        remove a change watcher to this item
        """

    @property
    def root(self)->"EzFsDirectory":
        """
        the root directory for our filesystem
        """
        return self.filesystem.root
    @property
    def parent(self)->"EzFsDirectory":
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
    rm=delete
    remove=delete

    def makePathExist(self,
        directoryLocation:typing.Union[UrlCompatible,"EzFsDirectory"]
        )->"EzFsDirectory":
        """
        Make sure a directory and all of the
        directories leading up to it exists.
        """
        from .ezFsDirectory import EzFsDirectory
        if isinstance(directoryLocation,EzFsDirectory):
            directory=directoryLocation
        else:
            directoryLocation=asUrl(directoryLocation)
            directory=self.filesystem.get(directoryLocation)
        if not isinstance(directory,EzFsDirectory):
            directory=directory.parent
        if not directory.exists:
            parent=self.makePathExist(directory.parent)
            parent.mkdir(directory.name)
        return directory

    def move(self,
        newLocation:UrlCompatible,
        makePathExist:bool=False)->None:
        """
        Move the item somewhere else.
        Can be on the same filesystem or across filesystems.
        """
        from .ezFsDirectory import EzFsDirectory
        newLocation=asUrl(newLocation)
        if makePathExist:
            newLocationDirectory=self.makePathExist(newLocation.parent)
        else:
            newLocationDirectory=EzFsDirectory(
                newLocation.parent,self.filesystem)
            if not newLocationDirectory.exists:
                raise FileNotFoundError(str(newLocationDirectory.url))
        if self.filesystem==newLocationDirectory.filesystem:
            self.filesystem._move(self,newLocation) # pylint: disable=protected-access
        elif newLocation.isDirectory:
            # need to do a recursive move
            raise NotImplementedError()
        else:
            data=self.read()
            newLocationDirectory.write(newLocation,data)
            self.delete()
    mv=move

    def copy(self,
        newLocation:UrlCompatible,
        makePathExist:bool=False)->None:
        """
        Move the item somewhere else.
        Can be on the same filesystem or across filesystems.
        """
        from .ezFsDirectory import EzFsDirectory
        newLocation=asUrl(newLocation)
        if makePathExist:
            newLocationDirectory=self.makePathExist(newLocation.parent)
        else:
            newLocationDirectory=EzFsDirectory(
                newLocation.parent,self.filesystem)
            if not newLocationDirectory.exists:
                raise FileNotFoundError(str(newLocationDirectory.url))
        if self.filesystem==newLocationDirectory.filesystem:
            self.filesystem._copy(self,newLocation) # pylint: disable=protected-access
        elif newLocation.isDirectory:
            # need to do a recursive move
            raise NotImplementedError()
        else:
            data=self.read()
            newLocationDirectory.write(newLocation,data)
    cp=copy

    def rename(self,newName:UrlCompatible)->None:
        """
        Change the name of the item
        """
        if self.url is None:
            raise FileNotFoundError('Unable to rename file [None]')
        newName=asUrl(newName)
        if newName.path and newName.path!=self.url.path:
            # cannot rename to another path location, so move instead
            self.move(newName)
            return
        newName=str(newName)
        self.filesystem._rename(self,str(newName))  # noqa: E501 # pylint: disable=line-too-long,protected-access

    def __repr__(self)->str:
        return str(self.url)
