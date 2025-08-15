#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A filesystem item representing a file.

It also doubles as a file-like object
"""
import typing
from abc import abstractmethod
from typing_extensions import Buffer
from paths import UrlCompatible
import ezFs


class EzFsFile(ezFs.EzFsItem,typing.IO):
    """
    A filesystem item representing a file.

    It also doubles as a file-like object
    """
    def __init__(self,
        url:UrlCompatible,
        filesystem:"ezFs.EzFsFilesystem"):
        """ """
        ezFs.EzFsItem.__init__(self,url,filesystem)
        self._isOpen:bool=False
        self._fileAccessMode:str='rw'

    @property
    def isDir(self)->bool:
        """ is this a directory? """
        return False

    @property
    def fileAccessMode(self)->str:
        """
        file access mode

        setter may require re-open in the correct mode
        (this will always reset file read location to 0)
        """
        return self._fileAccessMode
    @fileAccessMode.setter
    def fileAccessMode(self,fileAccessMode:str):
        if self._fileAccessMode!=fileAccessMode:
            if self.isOpen:
                self.close()
            # will use that mode when next we open
            self._fileAccessMode=fileAccessMode

    @property
    def isOpen(self)->bool:
        """
        wheter or not we are open

        setter calls open() or close()
        """
        return self._isOpen
    @isOpen.setter
    def isOpen(self,isOpen:bool):
        if isOpen:
            self.open()
        else:
            self.close()

    @property
    def closed(self)->bool:
        """
        For compatability with IO
        """
        return not self.isOpen
    @closed.setter
    def closed(self,closed:bool)->None:
        self.isOpen=not closed

    def isatty(self) -> bool:
        """
        For compatability with IO
        """
        return False

    def fileno(self)->int:
        """
        For compatability with IO
        """
        raise AttributeError('No fileno for abstract filesystems')

    def truncate(self,__size:typing.Union[int,None]=None)->int:
        """
        For compatability with IO
        """
        raise AttributeError('No truncate for abstract filesystems')

    @abstractmethod
    def read(self, # pylint: disable=arguments-differ
        numBytes:typing.Optional[int]=None,
        encoding:typing.Optional[str]=None
        )->str:
        """
        read n# of bytes, or the whole thing
        """

    def readline(self,__limit:typing.Optional[int]=None)->str:
        """
        For compatability with IO
        """
        buf:typing.List[str]=[]
        i=0
        while True:
            c=self.read(1)
            if c=='\n':
                break
            if __limit is not None:
                i+=1
                if i>=__limit:
                    break
        return ''.join(buf)

    def readlines(self,__hint:int=0)->list[str]:
        """
        For compatability with IO
        """
        ret=[]
        i=0
        while True:
            ret.append(self.readline())
            if __hint is not None:
                i+=1
                if i>=__hint:
                    break
        return ret

    @abstractmethod
    def write(self,
        s:typing.Any,
        encoding:str='utf-8'
        )->int:
        """
        Write the data to the file
        """

    def writelines(self,
        __lines:typing.Union[
            typing.Iterable[str],
            typing.Iterable[Buffer],
            typing.Iterable[typing.Any]
        ]
        )->None:
        """
        For compatability with IO
        """
        for line in __lines:
            self.write(line)
            self.write('\n')

    def seekable(self) -> bool:
        """
        For compatability with IO
        """
        return True

    def readable(self) -> bool:
        """
        For compatability with IO
        """
        return 'r' in self._fileAccessMode

    def writable(self) -> bool:
        """
        For compatability with IO
        """
        return 'w' in self._fileAccessMode

    @property
    def mode(self)->str:
        """
        For compatability with IO
        """
        return self._fileAccessMode

    def __enter__(self)->"EzFsFile":
        """
        Handle "with" statement
        """
        self.isOpen=True
        return self
    def __exit__(self,
        __t:typing.Type[BaseException]|None,
        __value:BaseException|None,
        __traceback:typing.Any
        #__traceback:TracebackType|None
        )->None:
        """
        Handle "with" statement
        """
        self.isOpen=False

    #@abstractmethod
    def open(self,fileAccessMode:typing.Optional[str]=None)->"EzFsFile":
        """
        Open this file and return a file-like object

        If not specified, file access mode will be self.accessMode
        """
        raise NotImplementedError()

    def __del__(self):
        """
        auto-close on exit
        """
        self.close()

    @abstractmethod
    def seek(self,offset:int,whence:int=0):
        """
        jump to file location
        """

    @abstractmethod
    def tell(self)->int:
        """
        return current file location
        """

    @abstractmethod
    def close(self)->None:
        """
        close open file handles
        """

    @abstractmethod
    def flush(self)->None:
        """
        Complete all i/o operations now.
        """
