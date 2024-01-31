import threading

printPool = threading.Semaphore()  # Make only one thread able to use the pool at a time
writePool = threading.Semaphore()
togglePool = threading.Semaphore()


def poolUse(pool, action, variable):
    pool.acquire()
    action(variable)
    pool.release()


def pPrint(text):
    """Ensures there is only one thread printing at a time"""
    poolUse(printPool, print, text)


def pWrite(file, text):
    """Ensures there is only one thread writing at a time"""
    poolUse(writePool, file.write, text + '\n')


def pToggle(on):
    """Ensures there is only one thread using the toggle at a time"""
    if on:
        togglePool.acquire()
    else:
        togglePool.release()
