from threading import Thread
import time


class Thread_Easy_Stop(Thread):

    threads = []

    def __init__(self, callback_in_loop, delay = 0.05):
        self.ended = False
        self.is_running = True
        self.delay = delay
        self.callback_in_loop = callback_in_loop
        Thread.__init__(self)
        Thread_Easy_Stop.threads.append(self)

    def run(self):
        beg = time.time()
        print "Is running ?"
        print self.is_running
        while self.is_running:
            if not self.callback_in_loop(time.time() - beg):
                self.is_running = False
            time.sleep(self.delay)
        self.ended = True
        print "ENDED"

    def stop(self):
        self.is_running = False

    def join(self):
        while not self.ended:
            time.sleep(self.delay)

    def restart(self):
        if not self.is_running:
            self.ended = False
            self.is_running = True
            self.start()

    @classmethod
    def stop_all_threads(cls):
        print "[+++] Stopping all remaining threads"
        for t in Thread_Easy_Stop.threads:
            t.stop()
