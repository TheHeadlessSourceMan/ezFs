#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A utility that causes a derived poll() function
to be called as often as needed for the registered
callbacks
"""
import typing
from abc import abstractmethod
import time


WatcherFn=typing.Callable[[typing.Any],None]


class PollingItem:
    """
    A utility that causes a derived poll() function
    to be called as often as needed for the registered
    callbacks
    """

    def __init__(self)->None:
        """ """
        self._watches:typing.List[
            typing.Tuple[WatcherFn,float]]=[] # (watchFn,interval)
        self._leastPollingInterval:typing.Optional[float]=None
        self._lastPoll:typing.Optional[float]=None

    @abstractmethod
    def poll(self)->bool:
        """
        derived classes implement this

        returns True if watchers should be notified
        """

    def _test_poll(self)->None:
        """
        poll if the interval has elapsed
        and call any watchers
        """
        now=time.time()
        doPoll=False
        if self._lastPoll is None or self._leastPollingInterval is None:
            doPoll=True
        elif now-self._lastPoll>self._leastPollingInterval:
            doPoll=True
        if doPoll:
            self._lastPoll=now
            if self.poll():
                for fn,_ in self._watches:
                    fn(self)

    def addWatch(self,watchFn:WatcherFn,pollingInterval:float=1)->None:
        """
        add a change watcher to this item

        :param watchFn: will call watchFn(pollingItem) upon change
        """
        self._leastPollingInterval=pollingInterval
        for _,interval in self._watches:
            if interval<self._leastPollingInterval:
                self._leastPollingInterval=interval
        self._watches.append((watchFn,pollingInterval))
        self._test_poll()

    def removeWatch(self,watchFn:WatcherFn)->None:
        """
        remove a change watcher to this item
        """
        for i,item in enumerate(self._watches):
            if item[0]==watchFn:
                del self._watches[i]
