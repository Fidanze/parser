from Window import Window
import os


class WindowsPool():

    def __init__(self) -> None:
        self.windows: list = []
        self.free_windows: list = []
        self.limit = int(os.environ['NUMBER_OF_PROCESSORS']) + 2

    def __del__(self):
        for window in self.windows:
            window.close()

    def pop_window(self):
        if len(self.free_windows):
            key = self.free_windows.pop()
            return self.windows[key]

        while len(self.windows) == self.limit:
            pass

        window = Window()
        window.set_city(self.city)
        self.windows.append(window)
        return window

    def put_window(self, window):
        self.free_windows.append(self.windows.index(window))

    def set_city(self, city: str):
        self.city = city
        while len(self.free_windows) != len(self.windows):
            pass

        for window in self.windows:
            window.set_city(self.city)
