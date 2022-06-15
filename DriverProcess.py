from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process
from Window import Window


class CustomProcess(Process):
    def __init__(self):
        super().__init__()
        self._window = None

    def run(self):
        '''
        Method to be run in sub-process; can be overridden in sub-class
        '''
        self._window = Window() if not self._window else self._window
        if self._target:
            self._target(self._window, *self._args, **self._kwargs)

    def join(self):
        super().join()
        self._popen = None

    
    def set_task(self, target, args=(), kwargs={}):
        # self._window = Window()
        self._target = target
        self._args = tuple(args)
        # kwargs['window'] = self._window
        self._kwargs = dict(kwargs)


def func(window, x):
    window.open('https://www.google.com')
    x = x+5
    print(x**2)

def func1(x):
    x = x+5
    print(x**2)

if __name__ == '__main__':
    # freeze_support()    
    c = CustomProcess()
    c.set_task(func, args=(11,))
    c.start()
    c.join()
    c.set_task(func, args=(12,))
    c.start()
    c.join()
    print('asdasdasds')


    # with ProcessPoolExecutor(1) as executor:
    #     gen_product_availabilities = executor.map(func1, list(range(10)))