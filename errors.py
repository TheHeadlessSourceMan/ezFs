#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
errors defined

TODO: I want to use FileNotFound exceptions for convenience,
    but not sure if the errno and so on, make it make sense
"""

from paths import UrlCompatible


class EzFsException(Exception):
    """
    All filesystem errors inherit from common base
    """

    def __init__(self,filePath:str,problemMessage:str):
        self.filename:str=filePath
        problemMessage='File error:\n   %s\nWhile attempting to access:\n   %s'%(problemMessage,filePath) # noqa: E501 # pylint: disable=line-too-long
        Exception.__init__(self,problemMessage)


class FileAccessException(EzFsException):
    """
    Thrown when attempting to do something to a file/directory that you do not
    have permission for.
    """

    def __init__(self,filePath:str,mode:str=''):
        err:str='Unable to open with mode "%s"'%mode
        EzFsException.__init__(self,filePath,err)


class UrlProtocolNotSupportedException(EzFsException):
    """
    Thrown when the url's protocol is not associated with anything
    """

    def __init__(self,filePath:UrlCompatible):
        err:str='URL protocol not supported.'
        EzFsException.__init__(self,str(filePath),err)


class NoFileException(EzFsException):
    """
    Thrown when there is no file
    """

    def __init__(self,filePath:str):
        err:str='File not found'
        EzFsException.__init__(self,filePath,err)


class TooManyFilesException(EzFsException):
    """
    Thrown when there are too many files found
    """

    def __init__(self,filePath:str,numFiles:int):
        err:str='Too many files (%d) found for operation'%numFiles
        EzFsException.__init__(self,filePath,err)
