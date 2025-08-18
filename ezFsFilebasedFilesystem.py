#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A filesystem based upon a file in another filesystem,
for instance, a .zip file or .iso image
"""
import typing
from abc import abstractmethod
from paths import URLCompatible,MimeTypeCompatible
import ezFs


class EzFsFilebasedFilesystem(ezFs.EzFsFilesystem):
    """
    A filesystem based upon a file in another filesystem,
    for instance, a .zip file or .iso image
    """
    def __init__(self):
        ezFs.EzFsFilesystem.__init__(self)

    @classmethod
    @abstractmethod
    def canRead(cls,
        filename:typing.Optional[URLCompatible],
        magicBuf:typing.Union[str,bytes,None],
        mimetype:typing.Optional[MimeTypeCompatible]=None
        )->bool:
        """
        Determine wheter a certain file can be considered
        a filesystem of this type

        :param filename: filename (usually used for getting a file extension)
        :type filename: str
        :param magicBuf: first 128 bytes of the file for looking
            for magic numbers
        :type magicBuf: str
        :param mimetype: the mime type, defaults to None
        :type mimetype: typing.Optional[str], optional
        :return: whether this filesystem can read this file type
        :rtype: bool
        """
        raise NotImplementedError()
