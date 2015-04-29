

class ConnectQueueSignals(object):
    def __init__(self, api, queue):
        self.queue = queue
        self.api = api

    def connect(self):
        self.api.signal_statistics_search_result.connect(self.on_statistics_search_result, sender=self.api)
        self.api.signal_statistics_page_view.connect(self.on_statistics_page_view, sender=self.api)
        self.api.signal_save_to_neo_feeder.connect(self.on_save_to_neo_feeder, sender=self.api)

    def on_statistics_search_result(self, sender, **kwargs):
        self.queue.lpush("statistics-search-result", kwargs['data'])

    def on_statistics_page_view(self, sender, **kwargs):
        self.queue.lpush("statistics-page-view", kwargs['data'])

    def on_save_to_neo_feeder(self, sender, **kwargs):
        self.queue.lpush("logentries", kwargs['data'])
