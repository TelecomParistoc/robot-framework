from threading import Thread
import time


class Thread_Easy_Stop(Thread):

    threads = []

    def __init__(self, callback_in_loop, delay = 0.05):
        self.ended = False
        self.is_running = True
        self.delay = delay
        self.callback_in_loop = callback_in_loop
        super(Thread, self).__init__(target=self.run)
        threads.append(self)
        self.start()

    def run(self):
        beg = time.time()
        while self.is_running:
            if not self.callback_in_loop(time.time() - beg):
                self.is_running = False
            time.sleep(self.delay)
        self.ended = True

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

    def stop_all_threads():
        print "[+++] Stopping all remaining threads"
        for t in threads:
            t.stop()
