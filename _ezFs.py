#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A system for common access to any given filesystem from python
"""
import typing
from paths import UrlCompatible,asUrl,URL
import ezFs


class EzFs(ezFs.EzFsFilesystem):
    """
    A system for common access to any given filesystem from python

    This is the grandaddy filesystem that incorporates all other filesystems
    """

    # proper filesystems such as file:// ftp:// or even http://
    FILESYSTEMS:typing.Optional[typing.List[
        typing.Type[ezFs.EzFsFilesystem]]]=None

    # filesystems within files, such as .zip or .tar
    # (not necessarily compression formats though)
    FILEBASED_FILESYSTEMS:typing.Optional[typing.List[
        typing.Type[ezFs.BaseFilebasedFs]]]=None

    def __init__(self,url:typing.Optional[UrlCompatible]=None):
        # must instanciate shared class variables first thing
        if self.FILESYSTEMS is None:
            # TODO: search for this stuff
            classes:typing.List[typing.Tuple[str,str]]=[
                ('osFs','OsFs'),
                ('httpFs','HttpFs'),
                #('webdavFs','DavFs'),
                ('ftpFs','Ftp'),
                ('zipFs','ZipFs'),
                ]
            self.FILESYSTEMS=[]
            self.FILEBASED_FILESYSTEMS=[]
            for moduleName,className in classes:
                import importlib
                module=importlib.import_module(moduleName)
                clazz=module.__dict__[className]
                if clazz.URL_PROTOCOLS:
                    # if it has url protocols, it is a filesystem
                    self.FILESYSTEMS.append(clazz)
                else:
                    # if it has no url protocols, it is a file type
                    self.FILEBASED_FILESYSTEMS.append(clazz)
        # base constructor
        ezFs.EzFsFilesystem.__init__(self,url)
        # any local values to init

    def getUrlSupport(self,
        url:UrlCompatible
        )->typing.Type[ezFs.EzFsFilesystem]:
        """
        get filesystem that supports this url
        """
        url=asUrl(url)
        if self.FILESYSTEMS is not None:
            for fs in self.FILESYSTEMS:
                if fs.supportsUrl(url):
                    return fs
        raise ezFs.UrlProtocolNotSupportedException(url)

    def _getFsItem(self,url:UrlCompatible)->ezFs.EzFsItem:
        """
        get a single item from the filesystem
        """
        url=asUrl(url)
        fs=self.getUrlSupport(url)
        return fs().get(url)

    def open(self,
        path:UrlCompatible,
        accessMode:typing.Optional[str]=None
        )->ezFs.EzFsFile:
        """
        open any url, anywhere
        """
        urlObj=asUrl(path)
        fs=self.getUrlSupport(urlObj)
        return fs.open(urlObj,accessMode)

    def getFsForCompressed(self,
        path:typing.Union[str,typing.IO]
        )->typing.Optional[ezFs.EzFsFilesystem]:
        """
        file can be a filename or open file-like object

        returns either a EzFsFilesystem-derived object for the given file,
        or None if that particualr file cannot serve as a filesystem
        """
        fname:typing.Optional[str]=None
        if isinstance(path,str):
            fname=path
            f:typing.IO=open(path,'rb+')
            magicBuf:typing.Union[str,bytes]=f.read(128)
            f.seek(0)
        else:
            f=path
            if hasattr(f,'name'):
                fname=f.name
            loc=f.tell()
            magicBuf:typing.Union[str,bytes]=f.read(128) # type: ignore
            f.seek(loc)
        if self.FILEBASED_FILESYSTEMS is not None:
            for fbfs in self.FILEBASED_FILESYSTEMS:
                if fbfs.canRead(fname,magicBuf): # type: ignore
                    return fbfs(self,fname) # type: ignore
        return None

    def addWatch(self,watchFn:ezFs.WatcherFn,pollingInterval:float=30):
        """
        add a change watcher to this item
        """
        if self.cwd is not None:
            self.cwd.addWatch(watchFn,pollingInterval)

    def removeWatch(self,watchFn:ezFs.WatcherFn):
        """
        remove a change watcher to this item
        """
        if self.cwd is not None:
            self.cwd.removeWatch(watchFn)

    def copy(self,fromPath:UrlCompatible,toPath:UrlCompatible):
        """
        Copy a file
        """
        raise NotImplementedError()

    def move(self,fromPath:str,toPath:str):
        """
        Move a file
        """
        self.copy(fromPath,toPath)
        self.delete(fromPath)

    def _delete(self,fsItem:ezFs.EzFsItem):
        fsItem.filesystem._delete(fsItem) # pylint: disable=protected-access

    def _rename(self,fsItem:ezFs.EzFsItem,newName:str):
        fsItem.filesystem._rename(fsItem,newName) # noqa: E501 # pylint: disable=line-too-long,protected-access

    def mount(self,
        location:UrlCompatible,
        otherFs:typing.Optional[ezFs.EzFsFilesystem]=None
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
            Thus mount('/mnt/mything',None) IS NOT the same thing as
            mount('/mnt/mything',OsFs())

        TODO: implement this.  See also:
            C:\Users\kurt\AppData\Local\Programs\Python\Python37\Lib\site-packages\fs-0.5.5a1-py3.7.egg\fs\mountfs.py
        """ # noqa: E501 # pylint: disable=line-too-long
        raise NotImplementedError()


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        fs=EzFs("c:\\backed_up\\")
        for arg in args:
            if arg.startswith('-'):
                av=arg.split('=',1)
                av[0]=av[0].strip()
                if av[0] in ['-h','--help']:
                    printhelp=True
                elif av[0]=='--tree':
                    fs.printTree()
                elif av[0] in ['--cd','--chadir']:
                    if len(av)>1:
                        fs.cd(av[1])
                    print('\n$ cd %s'%fs.workingDirectory)
                elif av[0] in ['--dir','--ls']:
                    if len(av)>1:
                        print('\n$ ls %s/%s'%(fs.cwd,av[1]))
                        items=[x for x in fs.ls(av[1])]
                    else:
                        print('\n$ ls %s'%fs.cwd)
                        items=[x for x in fs.ls()]
                    print('%d item(s):'%len(items))
                    for item in items:
                        print('   %s'%item)
                elif av[0] in ['--flat']:
                    if len(av)>1:
                        print('\n$ flat %s/%s'%(fs.cwd,av[1]))
                        items=[x for x in fs.getAll(av[1])]
                    else:
                        print('\n$ flat%s'%fs.cwd)
                        items=[x for x in fs.getAll()]
                    print('%d item(s):'%len(items))
                    for item in items:
                        print('   %s'%(item))
                elif av[0] in ['--find']:
                    if len(av)>1:
                        print('\n$ find %s'%av[1])
                        items=list(fs.find(av[1]))
                        print('%d item(s) found:'%len(items))
                        for item in items:
                            print('   %s'%item)
                elif av[0] in ['--regex']:
                    if len(av)>1:
                        print('\n$ regex %s'%fs.workingDirectory)
                        items=fs.regexFind(av[1])
                        print('%d item(s) found:'%len(items))
                        for item in items:
                            print('   %s'%item)
                else:
                    print('ERR: unknown argument "'+av[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  _ezFs.py [options]')
        print('Options:')
        print('   --cd=path .......... change directory')
        print('   --chadir=path ...... change directory')
        print('   --dir[=path] ....... list directory')
        print('   --ls[=path] ........ list directory')
        print('   --tree ............. print file tree')
        print('   --regex[=path] ..... find files by regex')
        print('   --find[=path] ...... find files by glob')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
