import threading

printPool = threading.Semaphore()  # Make only one thread able to use the pool at a time
writePool = threading.Semaphore()


def cprint(text):
    """Ensures there is only one thread printing at a time"""
    printPool.acquire()
    print(text)
    printPool.release()


def cwrite(file, text):
    """Ensures there is only one thread writing at a time"""
    writePool.acquire()
    file.write(text + '\n')
    writePool.release()
