# ezFs
Common plugin-based interface for accessing data on all filesystems, ever.

The idea is you can do advanced things like:
```python
ezFs.copy('https://foo.com/bar','mailto:bob@foo.com')
```
```python
ezFs.read('sftp://guest@ftp.foo.com/bar/baz.json')
```
```python
ezFs.addWatch('https://foo.com/bar.html',onChangeFn,timedelta(minutes=15))
```

And, of course as soon as any new plugin is added, capabilities automatically expand
```python
ezFs.read('googledrive://myAccount/foo.md')
```

For file-based (pseudo)filesystems there are also experimental chaining options possible like
```python
ezFs.read('file://c:/users/me/desktop/iso://myfile.iso/home/bob/zip://logs.zip/log_1.csv')
```

## Implementing a plugin
Plugins are found via the python packages index so you'll need to register your plugin by using.

    TODO: need to add this

### You must implement:

An ``EzFsItem`` object that implements
```python
    @property
    def isDir(self)->bool:
        """
        Determine if this is a directory
        """
    @property
    def exists(self)->bool:
        """
        Determine if this file/directory exists
        """
    def addWatch(self,
        watchFn:ezFs.WatcherFn,
        pollingInterval:float=30
        )->None:
        """
        Add a watcher for this file/directory
        """
    def removeWatch(self,
        watchFn:ezFs.WatcherFn
        )->None:
        """
        Remove a watcher for this file/directory
        """
```

An ``EzFsFile`` that derives from your ``EzFsItem`` and implements
```python
    def read(self, # pylint: disable=arguments-differ
        numBytes:typing.Optional[int]=None,
        encoding:typing.Optional[str]=None,
        errors:str='ignore',
        mimeType:typing.Optional[MimeTypeCompatible]=None,
        )->str:
        """
        Read from the file
        """
    def write(self, # type: ignore # pylint: disable=arguments-renamed
        data:typing.Union[bytes,str],
        encoding:str='utf-8',
        errors:str='ignore',
        mimeType:typing.Optional[MimeTypeCompatible]=None,
        append:bool=False
        )->int:
        """
        Write to the file
        """
    def open(self,fileAccessMode:typing.Optional[str]=None)->"EzFsFile":
        """
        Open the file
        """
    def seek(self,offset:int,whence:int=0)->int:
        """
        Go to a specific location in the file
        """
    def tell(self)->int:
        """
        Get current location in the file
        """
    def close(self)->None:
        """
        Flush and close the file if it is open
        """
    def flush(self)->None:
        """
        Flush all pending writes
        """
```

An ``EzFsDir`` that that derives from your ``EzFsItem`` and implements
```python
    def mount(self,
        location:UrlCompatible,
        otherFs:typing.Optional["ezFs.EzFsFilesystem"]=None
        )->URL:
        """
        Mount another filesystem at this point.
        EXPERIMENTAL!
        """
    @property
    def children(self)->typing.Iterable[ezFs.EzFsItem]:
        """
        Iterate over all child items (directories and files)
        """
    def markDirty(self)->None:
        """
        Mark this as having changed
        """
    def _mkdir(self,
        newDirectoryName:UrlCompatible
        )->None:
        """
        Create a new subdirectory
        """
```

An ``EzFsFilesystem`` that derives from your ``EzFsDir`` and implements
```python
    def _getFsItem(self,url:UrlCompatible)->ezFs.EzFsItem:
        """
        get a file on the filesystem.
        """
    def _delete(self,fsItem:"ezFs.EzFsItem")->None:
        """
        delete a file on the filesystem.
        """
    def _rename(self,
        fsItem:"ezFs.EzFsItem",
        newName:UrlCompatible)->None:
        """
        Rename a file on the filesystem.
        """
    def _copy(self,
        fsItem:"ezFs.EzFsItem",
        newLocation:UrlCompatible)->None:
        """
        Copy a file from one location to another on the same filesystem.
        """
    def _move(self,
        fsItem:"ezFs.EzFsItem",
        newLocation:UrlCompatible)->None:
        """
        Move a file from one location to another on the same filesystem.
        (OPTIONAL) If this is missing it will simply do copy followed by delete
        """
    @classmethod
    def canRead(cls,
        filename:typing.Optional[UrlCompatible],
        magicBuf:typing.Union[str,bytes,None],
        mimetype:typing.Optional[MimeTypeCompatible]=None
        )->bool:
        """
        Determine if this filename/url can be interpreted as this kind of filesystem
        """
```

In addition, if it is a file based filesystem (eg, a .zip or .iso) your ``EzFsFilesystem`` also needs to derive from ``EzFsFilebasedFilesystem`` and implement
```python
    @classmethod
    def canRead(cls,
        filename:typing.Optional[URLCompatible],
        magicBuf:typing.Union[str,bytes,None],
        mimetype:typing.Optional[MimeTypeCompatible]=None
        )->bool:
        """
        Determine if this file can be interpreted as this kind of filesystem
        """
```