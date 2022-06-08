from Window import Window
import os

URL = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'


class WindowsPool(object):

    def __init__(self) -> None:
        self.windows: list = []
        self.free_windows: list = []
        self.limit = 2  # threads for core

    def __del__(self):
        for window in self.windows:
            window.close()

    def pop_window(self):
        while True:
            if len(self.free_windows):
                key = self.free_windows.pop()
                return self.windows[key]
            if len(self.windows) != self.limit:
                window = Window()
                window.open(URL)
                self.windows.append(window)
                return window

    def put_window(self, window):
        self.free_windows.append(self.windows.index(window))
