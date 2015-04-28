from blinker import signal


class QueueSignals(object):
    def __init__(self, queue):
        self.queue = queue
        self.signals = [('obelix_intern_statistics_search_result',
                         self.obelix_intern_statistics_search_result),
                        ('obelix_intern_statistics_page_view',
                         self.obelix_intern_statistics_page_view),
                        ('obelix_intern_save_to_neo_feeder',
                         self.obelix_intern_save_to_neo_feeder),
                        ]

    def connect(self):
        for sig, sig_func in self.signals:
            signal(sig).connect(sig_func)

    def disconnect(self):
        for sig, sig_func in self.signals:
            signal(sig).disconnect(sig_func)

    def obelix_intern_statistics_search_result(sender, **kwargs):
        print(kwargs)
        #self.queue.lpush("statistics-search-result", data)

    def obelix_intern_statistics_page_view(self, data):
        self.queue.lpush("statistics-page-view", data)

    def obelix_intern_save_to_neo_feeder(self, data):
        self.queue.lpush("logentries", data)


class RestApiSignals(object):
    pass

def obelix_intern_statistics_search_result(sender, **kwargs):
    print(kwargs)
    iself.queue.lpush("statistics-search-result", data)
