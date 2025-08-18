"""
Find and use plugins registered via the package manager
"""
import typing
from importlib.metadata import entry_points


T=typing.TypeVar('T')
class PluginManager(typing.Generic[T]):
    """
    Find and use plugins registered via the package manager
    """
    def __init__(self,pluginGroup:str):
        self.pluginGroup=pluginGroup
        self._plugins:typing.Optional[typing.Dict[str,T]]=None

    def __getitem__(self,name:str)->T:
        """
        Use this like a dict
        """
        if self._plugins is None:
            self.reload()
        return self._plugins[name] # type: ignore

    def get(self,
        name:str,
        default:typing.Optional[T]=None
        )->typing.Optional[T]:
        """
        Use this like a dict
        """
        if self._plugins is None:
            self.reload()
        return self._plugins.get(name,default) # type: ignore

    def __len__(self)->int:
        """
        Use this like a dict
        """
        if self._plugins is None:
            self.reload()
        return len(self._plugins) # type: ignore

    def __iter__(self)->typing.Iterator[T]:
        """
        Use this like a dict
        """
        if self._plugins is None:
            self.reload()
        return iter(self._plugins.values()) # type: ignore

    def keys(self)->typing.Iterable[str]:
        """
        Use this like a dict
        """
        if self._plugins is None:
            self.reload()
        return self._plugins.values() # type: ignore

    def values(self)->typing.Iterable[T]:
        """
        Use this like a dict
        """
        if self._plugins is None:
            self.reload()
        return self._plugins.values() # type: ignore

    def reload(self):
        """
        Refresh the list of installed plugins

        (usually do not need to call this unless you
        think something has changed)
        """
        self._plugins={}
        for entry in entry_points(group=self.pluginGroup): # noqa: E501 # pylint:disable=unexpected-keyword-arg
            try:
                plugin_cls=entry.load()
                self._plugins[entry.name]=plugin_cls
            except Exception as e:
                print(f"[WARN] Could not load plugin {entry.name}:{e}")
Plugins=PluginManager
