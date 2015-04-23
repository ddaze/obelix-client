# -*- coding: utf-8 -*-

# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Invenio Obelix Search Engine """

import json
import time
import logger

def get_logger():
    return logger.getLogger('invenio_obelix')


class Obelix(object):

    def __init__(self, storage, queue, userIdentifer='uid', logger=None):
        self.storage = storage
        self.queue = queue
        self.logger = logger or get_logger()


        self.userIdentifer = userIdentifer
        result = self.storage.getFromJson('settings')
        # TODO: make settings configurable
        # We have to make sure all settings are of correct type
        #self.dataStore_prefix = result.get('dataStore_prefix', 'obelix::')
        self.recommendations_impact = float(result.get('recommendations_impact', 0.5))
        self.score_lower_limit = float(result.get('score_lower_limit', 0.2))
        self.score_upper_limit = float(result.get('score_upper_limit', 1))
        self.score_min_limit = int(result.get('score_min_limit', 10))
        self.score_min_multiply = int(result.get('score_min_multiply', 4))
        self.score_one_result = float(result.get('score_one_result', 1))
        self.method_switch_limit = float(result.get('method_switch_limit', 20))
        self.dataStore_timeout_search_result = int(result.get('redis_timeout_search_result', 300))

    def rank_records(hitset, rg=10, jrec=0):
        """
        Ranks a given search result based on recommendations
        Expects the hitset to be sorted by latest last [1,2,3,4,5] (recids)
        :return:
            A tuple, one list with records and one with scores.
            The list of records are integers while the scores are floats: [1,2,3],[.9,.8,7] etc...
        """
        hitset = list(hitset)
        hitset.reverse()
        jrec = max(jrec - 1, 0)

        # TODO: Maybe cache ranked result, if the next page is loaded
        records_by_order = rank_records_by_order(hitset)

        # Get Recommendations from storage
        # TODO: How to name storage.get Function?
        recommendations = selt.storage.getFromTable('recommendations',
                                                    self.userIdentifer)
        # FIXME: getIntDict enforce data types
        recommendations = getIntDict(recommendations)

        # If the user does not have any recommendations, we can just return
        if len(recommendations) == 0 | self.recommendations_impact == 0:
            finalScores = records_by_order
        else:
            # Calculate scores
            finalScores = calcScores(records_by_order, recommendations)

        records, scores = self._sort_records_by_score(final_scores)

        # TODO: implement error check
        # self.logger("FIXME consider propagating error")
        return records[jrec:jrec + rg], scores[jrec:jrec + rg]



    def log(action, *args, **kwargs):
        return getattr(self, 'log_' + action)(*args, **kwargs)

    def log_search_result_obelix(user_info, original_result_ordered, record_ids,
                                results_final_colls_scores, cols_in_result_ordered,
                                seconds_to_rank_and_print, jrec, rg, rm, cc):
        """
        Public method
        Used to log search_results
        :param user_info:
        :param original_result_ordered:
        :param record_ids:
        :param results_final_colls_scores:
        :param cols_in_result_ordered:
        :param seconds_to_rank_and_print:
        :param jrec:
        :param rg:
        :param rm:
        :param cc:
        :return:
        """
        try:
            self.searchLogger.search_result(user_info, original_result_ordered,
                                                    record_ids, results_final_colls_scores,
                                                    cols_in_result_ordered, seconds_to_rank_and_print,
                                                    jrec, rg, rm, cc)
        except Exception:
            register_exception(alert_admin=True)


    def log_page_view_after_search(user_info, recid):
        """
        Public method
        Log page views
        :param user_info:
        :param recid:
        :return:
        """
        try:
            self.searchLogger.page_view(user_info, recid,
                                                type="events.pageviews", file_format="page_view")
        except Exception:
            register_exception(alert_admin=True)


    def log_download_after_search(user_info, recid):
        """
        Public method
        We want to store downloads of PDFs as views (because users may click directly on download)
        :param user_info:
        :param recid:
        :return:
        """
        try:
            if 'uri' in user_info and '.pdf' in user_info['uri'].lower():
                self.searchLogger.page_view(user_info, recid,
                                                    type="events.downloads", file_format="PDF")
        except Exception:
            register_exception(alert_admin=True)



#Utils

def getIntDict(dataDict):
    """ Retrieves the recommendation for the self.uid (current user) from redis

    The cached recommendations may be on the form {'123': 0.2.. but we want {123: 0.2
    Therefore we have to enforce that the keys in the resulting dictionary are integers

    :return
        dict with recommendations if any with the user id as the key {123: 0.3, 321: 0.2}
        empty dict if no recommendations

    :raises
        redis.ConnectionError if redis is unavailable
        TypeError: TypeError: expected string or buffer, if anything else than a str is stored
        ValueError: No JSON object could be decoded (invalid json format)
    """
    result = {}
    for key, value in dataDict:
        result[int(key)] = float(value)

    return result

    def rank_records_by_order(self, hitset):
        """
        Rank the records by the original order they we're provided

        If the SearchEngineObelix([1,2,3]) then this method will return [1.0, 0.933, 0.867]

        Typically called like this:
            records, scores = __build_ranked_by_order()

        :return:
            A tuple, one list with records and one with scores.
            The list of records are integers while the scores are floats: [1,2,3],[.9,.8,7] etc...
        """
        if len(hitset) == 1:
            return hitset, [self.score_one_result]

        upper = 1
        lower = self.score_lower_limit
        size = len(hitset)

        # TODO: Check why
        if size < self.score_min_limit:
            size *= self.score_min_multiply

        step = ((upper - lower) * 1.0 / size)
        scores = [1 - (lower + i * step) for i in range(0, size)]
        scores = scores[0:len(hitset)]

        rankedHitseta = {}
        for idx, score in enumerate(scores):
            result[hitset[idx]] = score

        return rankedHitset

    def sort_records_by_score(self, record_scores):
        """
        :param record_scores: dictionary {1:0.2, 2:0.3 etc...
        :return: a tuple with two lists, the first is a list of records
        and the second of scores
        """
        records = []
        scores = []

        for recid in sorted(record_scores, key=record_scores.get, reverse=True):
            records.append(recid)
            scores.append(record_scores[recid])

        return records, scores

    def calcScores(records_by_order, recommendations, recommendations_impact):
        final_scores = {}

        for recid, recScore in records_by_order:
            recommendationScore = recommendations.get(recid, None)
            # TODO: Check if this fits
            finalScore = order_score = recScore * (1 - recommendations_impact)
            if recommendationScore:
                recommended_score = recomendationScore * recommendations_impact
                finalScore = order_score + recommended_score

            final_scores[recid] = finalScore

        return final_scores



class Recommender(object):
    """ Obelix Recommender """

    def __init__(self, config):

        self.keyObelixSettings = "obelix::settings"
        self.userKey = config.get('userKey', 'uid')
        self.dataStore_prefix = "obelix::"

        result = json.loads(self.dataStore.get(redis_key))

        # We have to make sure all settings are of correct type
        self.dataStore_prefix = result.get('dataStore_prefix', 'obelix::')
        self.recommendations_impact = float(result.get('recommendations_impact', 0.5))
        self.score_lower_limit = float(result.get('score_lower_limit', 0.2))
        self.score_upper_limit = float(result.get('score_upper_limit', 1))
        self.score_min_limit = int(result.get('score_min_limit', 10))
        self.score_min_multiply = int(result.get('score_min_multiply', 4))
        self.score_one_result = float(result.get('score_one_result', 1))
        self.method_switch_limit = float(result.get('method_switch_limit', 20))
        self.dataStore_timeout_search_result = int(result.get('redis_timeout_search_result', 300))


    def redis_key(self, *keys):
        """
        Generate a key for redis, combine multiple arguments into one key with a prefix (from obj)
        :param
            keys: *keys, may be called as _redis_key("key") or _redis_key("key1", "key")
        :return
            str - to use as a key in redis
        :raises
        """
        key = "::".join([str(x) for x in keys])
        return "{0}{1}".format(self.dataStore_prefix, key)

    def fetch_recommendations(self, uid):
        """ Retrieves the recommendation for the self.uid (current user) from redis

        The cached recommendations may be on the form {'123': 0.2.. but we want {123: 0.2
        Therefore we have to enforce that the keys in the resulting dictionary are integers

        :return
            dict with recommendations if any with the user id as the key {123: 0.3, 321: 0.2}
            empty dict if no recommendations

        :raises
            redis.ConnectionError if redis is unavailable
            TypeError: TypeError: expected string or buffer, if anything else than a str is stored
            ValueError: No JSON object could be decoded (invalid json format)
        """
        recommendations = self.dataStore.get(self.redis_key("recommendations", uid))

        result = {}
        if recommendations:
            for key, value in json.loads(recommendations).iteritems():
                result[int(key)] = float(value)

        return result

    def rank(self, hitset, uid):
        """
        hitset = records
        :return: a tuple records, scores - sorted by the ranking based on
        recommendations
        """
        recommendations = self.fetch_recommendations(uid)
        records_by_order = self._rank_records_by_order(hitset)

        # If the recommendations have no impact on the final result, we can just skip this!
        # We don't even need to sort, everything is sorted already (by order)
        if self.recommendations_impact == 0:
            return self._sort_records_by_score(records_by_order)

        # If the user does not have any recommendations, we can just return
        if len(self.recommendations) == 0:
            return self._sort_records_by_score(records_by_order)

        final_scores = {}
        for recid, recScore in records_by_order:
            final_scores[recid] = \
                    self._calc_score(recommendations.get(recid, None), recScore)

        return self._sort_records_by_score(final_scores)


    def _calc_score(self, scoreByRecommendation, scorceByOrder):
        """
        Returns a score for a given recid, the score is combined from the
        order and recommendation
        :param recid: the recid we want to score
        :param recid_index: the position of the given recid in the original hitset
        :return: a float, the final score for the recid
        """
        # TODO: Check if this fits
        order_score = scorceByOrder * (1 - self.recommendations_impact)

        if scoreByRecommendation is not None:
            recommended_score = scoreByRecommendation * self.recommendations_impact
            return order_score + recommended_score

        return order_score


    def _rank_records_by_order(self, hitset):
        """
        Rank the records by the original order they we're provided

        If the SearchEngineObelix([1,2,3]) then this method will return [1.0, 0.933, 0.867]

        Typically called like this:
            records, scores = __build_ranked_by_order()

        :return:
            A tuple, one list with records and one with scores.
            The list of records are integers while the scores are floats: [1,2,3],[.9,.8,7] etc...
        """
        if len(hitset) == 1:
            return hitset, [self.score_one_result]

        upper = 1
        lower = self.score_lower_limit
        size = len(hitset)

        # TODO: Check why
        if size < self.score_min_limit:
            size *= self.score_min_multiply

        step = ((upper - lower) * 1.0 / size)
        scores = [1 - (lower + i * step) for i in range(0, size)]
        scores = scores[0:len(hitset)]

        rankedHitseta = {}
        for idx, score in enumerate(scores):
            result[hitset[idx]] = score

        return rankedHitset

    def _sort_records_by_score(self, record_scores):
        """
        :param record_scores: dictionary {1:0.2, 2:0.3 etc...
        :return: a tuple with two lists, the first is a list of records
        and the second of scores
        """
        records = []
        scores = []

        for recid in sorted(record_scores, key=record_scores.get, reverse=True):
            records.append(recid)
            scores.append(record_scores[recid])

        return records, scores



class ObelixLogger(object):
    """ ObelixSearchEngineLogger used to store page views, downloads and search results """

    def get_log_prefix(self, *name):
        """Generates the redis key, the main use case is to ensure we always use the prefix"""
        return self.settings.redis_key(*name)


    def log_search_result(self, user_info, original_result_ordered, record_ids,
                      results_final_colls_scores, cols_in_result_ordered,
                      seconds_to_rank_and_print, jrec, rg, rm, cc):
        """ Logs search result, used for both statistics and to lookup last search """
        if self.user_info_valid(user_info):
            uid = self.get_uid(user_info)
            search_timestamp = time.time()

            # Store the current search to use with page views later
            redis_key = self.get_redis_key("last-search-result", uid)
            data = json.dumps({'search_timestamp': search_timestamp,
                               'record_ids': record_ids,
                               'jrec': jrec,
                               'rm': rm,
                               'rg': rg,
                               'cc': cc})
            self.settings.redis.set(redis_key, data, self.settings.redis_timeout_search_result)

            # Store search result for statistics
            data = {'obelix_redis': CFG_WEBSEARCH_OBELIX_REDIS,
                    'obelix_uid': self.settings.userKey,
                    'result': record_ids,
                    'original_result_ordered': original_result_ordered,
                    'results_final_colls_scores': results_final_colls_scores,
                    'uid': uid,
                    'remote_ip': user_info.get("remote_ip"),
                    'uri': user_info.get('uri'),
                    'timestamp': search_timestamp,
                    'settings': self.settings.dump(),
                    'recommendations': self.settings.fetch_recommendations(uid),
                    'seconds_to_rank_and_print': seconds_to_rank_and_print,
                    'cols_in_result_ordered': cols_in_result_ordered,
                    'jrec': jrec,
                    'rg': rg,
                    'rm': rm,
                    'cc': cc}

            data = json.dumps(data)
            redis_key = self.get_redis_key("statistics-search-result")
            self.settings.redis.lpush(redis_key, data)








class _SearchEngineLogger(object):
    """ ObelixSearchEngineLogger used to store page views, downloads and search results """

    def __init__(self, config, redis=None):
        """
        Construct the Logger, fetching settings
        :param redis:
        :return:
        """
        self.settings = config
        self.dataStore = self.settings.dataStore

    def user_info_valid(self, user_info):
        """
        Validates user_info object (checks if user is logged in)
        :param user_info:
        :return:
        """
        keys = ('uid', 'remote_ip', "uri")
        return all(key in user_info for key in keys) and user_info['uid'] != 0

    def get_uid(self, user_info):
        """
        Let you choose what should be defined as the user key, may be uid or remote_id
        Uses CFG_WEBSEARCH_OBELIX_USER_KEY to decide what to use
        :param user_info:
        :return:
        """
        #if CFG_WEBSEARCH_OBELIX_USER_KEY:
        if self.settings.userKey:
            return str(user_info[self.settings.userKey])

        # fallback to use the uid as the uid
        return str(user_info['uid'])

    def get_redis_key(self, *name):
        """Generates the redis key, the main use case is to ensure we always use the prefix"""
        return self.settings.redis_key(*name)

    def _log_page_view_for_neo_feeder(self, uid, recid, remote_ip, type, file_format):
        """
        Feed the Obelix NeoFeeder with new page views, used to construct the graph
        :param uid:
        :param recid:
        :return: None
        """

        data = {
            'item': recid,
            'ip': remote_ip,
            "type": type,
            'user': uid,
            'file_format': file_format,
            "timestamp": time.time()
        }

        redis_key = self.get_redis_key("logentries")
        self.dataStore.rpush(redis_key, json.dumps(data))

    def _log_page_view_for_analytics(self, uid, recid, ip, uri, type):
        """ Mainly used to store statistics, may be removed in the future
        :param uid:
        :param recid:
        :param ip:
        :param uri:
        :return:
        """
        redis_key = self.get_redis_key("last-search-result", uid)
        last_search_info = self.dataStore.get(redis_key)

        if not last_search_info:
            return

        last_search_info = json.loads(last_search_info)

        hit_number_global = 0
        for collection_result in last_search_info['record_ids']:
            if recid in collection_result:
                hit_number_local = collection_result.index(recid)
                hit_number_global += hit_number_local

                timestamp = last_search_info['search_timestamp']
                jrec = last_search_info['jrec']
                rg = last_search_info['rg']
                rm = last_search_info['rm']
                cc = last_search_info['cc']

                redis_key = self.get_redis_key("statistics-page-view")

                recommendations = self.settings.fetch_recommendations(uid)

                self.dataStore.lpush(
                    redis_key,
                    json.dumps({'search_timestamp': timestamp,
                                'recid': recid,
                                'timestamp': time.time(),
                                'uid': uid,
                                'remote_ip': ip,
                                'uri': uri,
                                'jrec': jrec,
                                'rg': rg,
                                'rm': rm,
                                'cc': cc,
                                'hit_number_local': jrec + hit_number_local,
                                'hit_number_global': jrec + hit_number_global,
                                'recommendations': recommendations,
                                'recid_in_recommendations': recid in recommendations,
                                'type': type}))

            hit_number_global += len(collection_result)

    def page_view(self, user_info, recid, type="events.pageviews", file_format="view"):
        """ Logs a page view """
        if self.user_info_valid(user_info):
            uid = self.get_uid(user_info)
            ip = user_info['remote_ip']
            uri = user_info['uri']

            self._log_page_view_for_neo_feeder(uid, recid, ip, type, file_format)
            self._log_page_view_for_analytics(uid, recid, ip, uri, type)

    def search_result(self, user_info, original_result_ordered, record_ids,
                      results_final_colls_scores, cols_in_result_ordered,
                      seconds_to_rank_and_print, jrec, rg, rm, cc):
        """ Logs search result, used for both statistics and to lookup last search """
        if self.user_info_valid(user_info):
            uid = self.get_uid(user_info)
            search_timestamp = time.time()

            # Store the current search to use with page views later
            redis_key = self.get_redis_key("last-search-result", uid)
            data = json.dumps({'search_timestamp': search_timestamp,
                               'record_ids': record_ids,
                               'jrec': jrec,
                               'rm': rm,
                               'rg': rg,
                               'cc': cc})
            self.settings.redis.set(redis_key, data, self.settings.redis_timeout_search_result)

            # Store search result for statistics
            data = {'obelix_redis': CFG_WEBSEARCH_OBELIX_REDIS,
                    'obelix_uid': self.settings.userKey,
                    'result': record_ids,
                    'original_result_ordered': original_result_ordered,
                    'results_final_colls_scores': results_final_colls_scores,
                    'uid': uid,
                    'remote_ip': user_info.get("remote_ip"),
                    'uri': user_info.get('uri'),
                    'timestamp': search_timestamp,
                    'settings': self.settings.dump(),
                    'recommendations': self.settings.fetch_recommendations(uid),
                    'seconds_to_rank_and_print': seconds_to_rank_and_print,
                    'cols_in_result_ordered': cols_in_result_ordered,
                    'jrec': jrec,
                    'rg': rg,
                    'rm': rm,
                    'cc': cc}

            data = json.dumps(data)
            redis_key = self.get_redis_key("statistics-search-result")
            self.settings.redis.lpush(redis_key, data)


