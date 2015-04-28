from blinker import signal


def connect_redis_queue_signals(api, queue):
    statistics_search_result = signal('obelix_intern_statistics_search_result')
    statistics_page_view = signal('obelix_intern_statistics_page_view')
    save_to_neo_feeder = signal('obelix_intern_save_to_neo_feeder')

    @statistics_search_result.connect
    def obelix_intern_statistics_search_result(sender, **kwargs):
        queue.lpush("statistics-search-result", data)

    @statistics_page_view.connect
    def obelix_intern_statistics_page_view(sender, **kwargs):
        queue.lpush("statistics-page-view", data)

    @save_to_neo_feeder.connect
    def obelix_intern_save_to_neo_feeder(sender, **kwargs):
        queue.lpush("logentries", data)


def connect_obelix_signals(api, storage):
    get_recommendations = signal('obelix_get_recommendations')

    @get_recommendations.connect
    def obelix_get_recommendations(sender, **kwargs):
        uid = kwargs['uid']
        storage_key = "{0}::{1}".format("recommendations", uid)

        return storage.get(storage_key)
