#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A filesystem
"""
import typing
from abc import abstractmethod
from paths import asUrl,UrlCompatible,URL,MimeTypeCompatible
import ezFs


class EzFsFilesystem(ezFs.EzFsDirectory):
    """
    A filesystem

    NOTE: Doing directory listings, etc on the EzFsFilesystem
    is NOT operating upon the filesystem root
    but upon the workingDirectory
    """

    URL_PROTOCOLS:typing.List[str]=[] # list of url protocols we support ('http://', 'ftp://', etc) # noqa: E501 # pylint: disable=line-too-long

    def __init__(self,
        url:typing.Optional[UrlCompatible]=None,
        caseSensitive:bool=True):
        """
        """
        if url is None:
            url='/'
        ezFs.EzFsDirectory.__init__(self,url,self)
        self.caseSensitive:bool=caseSensitive # are filenames case-sensitive?
        self._workingDirectory:typing.Optional[ezFs.EzFsDirectory]=None
        self._ezFs:typing.Optional[ezFs.EzFs]=None

    @property
    def isRoot(self)->bool:
        """
        is this the root of the filesystem tree?
        """
        return True

    @property
    def url(self)->URL:
        """
        Url object of the full location of this item

        Setting it will cause the working directory to be reset
        """
        return self._url
    @url.setter
    def url(self,url:UrlCompatible):
        self._url=URL(url)
        self._workingDirectory=None # need to re-fetch before use

    @classmethod
    def supportsUrl(cls,url:UrlCompatible)->bool:
        """
        Returns True if it supports urls of the given type

        This does not imply the url is actually valid, just that
        we support that protocol.
        """
        urlObj=asUrl(url)
        if urlObj.protocol is None or not urlObj.protocol:
            return urlObj.protocol in cls.URL_PROTOCOLS
        return urlObj.protocol+'://' in cls.URL_PROTOCOLS

    def open(self,
        path:UrlCompatible,
        accessMode:typing.Optional[str]=None
        )->ezFs.EzFsFile:
        """
        pass-through to working directory
        """
        return self.workingDirectory.open(path,accessMode)

    def rename(self,newName:str,relativePath:typing.Optional[str]=None):
        """
        pass-through to working directory
        """
        return self.workingDirectory.rename(newName,relativePath)

    def regexFind(self,expression,ignoreCase:bool=False,idx:int=0):
        """
        pass-through to working directory
        """
        return self.workingDirectory.regexFind(expression,ignoreCase,idx)

    @property
    def flat(self)->typing.Iterable[ezFs.EzFsItem]:
        """
        all children, grandchildren, etc as a flattened list
        (same thing as getAll())
        """
        return self.getAll()
    def getAll(self,
        subdir:typing.Optional[str]=None,
        _tape:typing.Optional[typing.Dict[ezFs.EzFsItem,None]]=None
        )->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        retrieves all children, grandchildren, etc

        pass-through to working directory
        """
        d:ezFs.EzFsItem=self.workingDirectory
        if d is None:
            d=self._getFsItem(subdir)
        elif subdir is not None:
            if isinstance(d,ezFs.EzFsDirectory):
                d=d.relative(subdir)
        if not isinstance(d,ezFs.EzFsDirectory):
            yield d
            return
        yield from d.getAll()

    def get(self,
        path:UrlCompatible,
        idx:int=0
        )->ezFs.EzFsItem:
        """
        pass-through to working directory
        """
        return self.workingDirectory.get(path,idx)

    @abstractmethod
    def _getFsItem(self,url:UrlCompatible)->ezFs.EzFsItem:
        """
        derived classes must implement
        """

    def walk(self,
        filesCb:typing.Optional[ezFs.FileWalkerCallback]=None,
        context:typing.Any=None,
        algo:typing.Optional[str]=None,
        tape:typing.Optional[typing.Any]=None
        )->typing.Optional[bool]:
        """
        pass-through to working directory
        """
        return self.workingDirectory.walk(filesCb,context,algo,tape)

    def listdir(self,subdir:typing.Optional[str]=None
        )->typing.Generator[ezFs.EzFsItem,None,None]:
        """
        pass-through to working directory
        """
        yield from self.workingDirectory.listdir(subdir)

    @property
    def root(self)->ezFs.EzFsDirectory:
        """
        the filesystem root directory
        """
        wd=self.workingDirectory
        if self.url==wd.url:
            return self
        return wd.root

    def printTree(self,indent:str='')->None:
        """
        pass-through to working directory
        """
        return self.workingDirectory.printTree(indent)

    def markDirty(self)->None:
        return self.workingDirectory.markDirty()

    @property
    def children(self)->typing.Iterable[ezFs.EzFsItem]:
        """
        pass-through to working directory
        """
        return self.workingDirectory.children

    def delete(self,relativePath:typing.Optional[str]=None)->None:
        if self.workingDirectory is not None:
            self.workingDirectory.delete(relativePath)

    @abstractmethod
    def _delete(self,fsItem:"ezFs.EzFsItem")->None:
        """ delete """

    @abstractmethod
    def _rename(self,
        fsItem:"ezFs.EzFsItem",
        newName:str)->None:
        """ rename """

    def isNative(self)->bool:
        """
        returns True for the native os filesystem
        """
        return False

    def relative(self,subdir:str)->ezFs.EzFsItem:
        """
        get a directory relative to the current working directory
        """
        return self.workingDirectory.relative(subdir)

    @property
    def workingDirectory(self)->ezFs.EzFsDirectory:
        """
        the current working directory

        will always return a EzFsDirectory object

        setter works the same as changeDirectory()
        """
        if not hasattr(self,'_workingDirectory'):
            # this has a habit of getting called before constructor is done
            raise AttributeError("Not ready")
        if self._workingDirectory is None:
            lookup=self._getFsItem(self._url)
            if not isinstance(lookup,ezFs.EzFsDirectory):
                raise FileNotFoundError(
                    '"Working directory" is not a directory!')
            self._workingDirectory=lookup
            if self._workingDirectory is not None \
                and self._workingDirectory.url is not None:
                # in case the url was changed/redirected/whatever
                self._url=self._workingDirectory.url
        return self._workingDirectory
    @workingDirectory.setter
    def workingDirectory(self,path):
        self.changeDirectory(path)
    @property
    def cwd(self)->ezFs.EzFsDirectory:
        """
        same as changeDirectory()
        """
        return self.workingDirectory
    @cwd.setter
    def cwd(self,path:UrlCompatible):
        self.changeDirectory(path)

    def changeDirectory(self,
        path:UrlCompatible
        )->None:
        """
        change directory

        If you want to override changeDirectiory() functionality,
        override this function!  (cd,chadir,cwd,workingDirectory all
        go through this)
        """
        location=self.relative(path)
        if not isinstance(location,ezFs.EzFsDirectory):
            raise FileNotFoundError(f'"{path}" is not a directory')
        self._workingDirectory=location
    cd=changeDirectory
    chadir=changeDirectory

    @property
    def ezFs(self)->"ezFs.EzFs":
        """
        gets the top-level Ez object
        """
        if self._ezFs is None:
            self._ezFs=ezFs.EzFs()
        return self._ezFs


class BaseFilebasedFs(EzFsFilesystem):
    """
    This is a filesystem that comes from a file on a parent
    fileystem.  For instance, a zip file.
    """
    def __init__(self):
        EzFsFilesystem.__init__(self)

    @classmethod
    @abstractmethod
    def canRead(cls,
        filename:typing.Optional[UrlCompatible],
        magicBuf:typing.Union[str,bytes,None],
        mimetype:typing.Optional[MimeTypeCompatible]=None
        )->bool:
        """
        Determine wheter a certain file can be considered
        a filesystem of this type

        :param filename: filename (usually used for getting a file extension)
        :type filename: str
        :param magicBuf: first 128 bytes of the file for
            looking for magic numbers
        :type magicBuf: str
        :param mimetype: the mime type, defaults to None
        :type mimetype: typing.Optional[str], optional
        :return: whether this filesystem can read this file type
        :rtype: bool
        """
