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

import time
import logging
import obelix_client.utils as utils


def get_logger():
    return logging.getLogger('obelix_client')


class Obelix(object):

    def __init__(self, storage, queues, userIdentifer='uid', logger=None):
        self.logger = logger or get_logger()
        self.storage = storage
        self.queues = queues
        self.conf = Settings(storage)
        self.conf['userIdentifer'] = userIdentifer

    def rank_records(self, hitset, userId, rg=10, jrec=0):
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
        records_by_order = utils.rank_records_by_order(self.conf, hitset)

        # Get Recommendations from storage
        # TODO: How to name storage.get Function?
        recommendations = self.storage.getFromTable('recommendations', userId)
        # FIXME: getIntDict enforce data types
        recommendations = utils.getIntDict(recommendations)

        # If the user does not have any recommendations, we can just return
        if len(recommendations) == 0 or self.conf['recommendations_impact'] == 0:
            finalScores = records_by_order
        else:
            # Calculate scores
            finalScores = utils.calcScores(self.conf, records_by_order, recommendations)

        records, scores = utils.sort_records_by_score(finalScores)

        # TODO: implement error check
        # self.logger("FIXME consider propagating error")
        return records[jrec:jrec + rg], scores[jrec:jrec + rg]

    def log(self, action, *args, **kwargs):
        return getattr(self, 'log_' + action)(*args, **kwargs)

    def log_search_result(self, user_info, original_result_ordered,
                          record_ids, results_final_colls_scores,
                          cols_in_result_ordered,
                          seconds_to_rank_and_print, jrec, rg, rm, cc):
        """
        Logs search result, used for both statistics and to lookup last search
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
        # FIXME: make logging for different user identifier work
        uid = user_info.get('uid', None)
        search_timestamp = time.time()

        # Store the current search to use with page views later
        data = {'search_timestamp': search_timestamp,
                'record_ids': record_ids,
                'jrec': jrec,
                'rm': rm,
                'rg': rg,
                'cc': cc}
        self.storage.setToTable("last-search-result", uid, data)

        # Store search result for statistics
        data = {'obelix_redis': "CFG_WEBSEARCH_OBELIX_REDIS",
                'obelix_uid': self.conf['userIdentifer'],
                'result': record_ids,
                'original_result_ordered': original_result_ordered,
                'results_final_colls_scores': results_final_colls_scores,
                'uid': uid,
                'remote_ip': user_info.get("remote_ip"),
                'uri': user_info.get('uri'),
                'timestamp': search_timestamp,
                'settings': self.conf,
                'recommendations': self.storage.getFromTable('recommendations',
                                                             uid),
                'seconds_to_rank_and_print': seconds_to_rank_and_print,
                'cols_in_result_ordered': cols_in_result_ordered,
                'jrec': jrec,
                'rg': rg,
                'rm': rm,
                'cc': cc}
        # TODO: Does it make sense to use more queues?
        queueName = "{0}::{1}".format("statistics-search-result", uid)
        self.queues.lpush(queueName, data)

    def log_page_view_after_search(user_info, recid):
        """
        Log page views
        :param user_info:
        :param recid:
        :return:
        """
        # TODO: Check if needed
        self.log_page_view(user_info, recid,
                           type="events.pageviews",
                           file_format="page_view")

    def log_download_after_search(user_info, recid):
        """
        We want to store downloads of PDFs as views
        (because users may click directly on download)
        :param user_info:
        :param recid:
        :return:
        """
        # TODO: Check if needed
        if 'uri' in user_info and '.pdf' in user_info['uri'].lower():
            self.searchLogger.page_view(user_info, recid,
                                        type="events.downloads",
                                        file_format="PDF")

    def log_page_view(self, user_info, recid, type="events.pageviews", file_format="view"):
        """ Logs a page view """
        # TODO: Maybe check if valid user
        uid = user_info.get('uid', None)
        ip = user_info.get('remote_ip', None)
        uri = user_info.get('uri', None)

        self.log_page_view_for_neo_feeder(uid, recid, ip, type, file_format)
        self.log_page_view_for_analytics(uid, recid, ip, uri, type)

    def log_page_view_for_neo_feeder(self, uid, recid, remote_ip, type, file_format):
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

        # TODO: check r- or l-push
        self.queues.rpush("logentries", data)

    def log_page_view_for_analytics(self, uid, recid, ip, uri, type):
        """ Mainly used to store statistics, may be removed in the future
        :param uid:
        :param recid:
        :param ip:
        :param uri:
        :return:
        """
        # TODO: Check if needed
        last_search_info = self.storage.getFromTable("last-search-result", uid)

        if not last_search_info:
            return

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

                recommendations = self.storage.getFromTable('recommendations',
                                                            uid),
                self.queues.lpush(
                    "statistics-page-view",
                    {'search_timestamp': timestamp,
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
                     'type': type})

            hit_number_global += len(collection_result)


class Settings(dict):
    def __init__(self, storage):
        super(Settings, self).__init__()
        self.storage = storage

        result = self.storage.get('settings', {})
        # TODO: make settings configurable
        # We have to make sure all settings are of correct type
        # self.dataStore_prefix = result.get('dataStore_prefix', 'obelix::')
        self['recommendations_impact'] = float(result.get('recommendations_impact', 0.5))
        self['score_lower_limit'] = float(result.get('score_lower_limit', 0.2))
        self['score_upper_limit'] = float(result.get('score_upper_limit', 1))
        self['score_min_limit'] = int(result.get('score_min_limit', 10))
        self['score_min_multiply'] = int(result.get('score_min_multiply', 4))
        self['score_one_result'] = float(result.get('score_one_result', 1))
        self['method_switch_limit'] = float(result.get('method_switch_limit', 20))
        self['dataStore_timeout_search_result'] = int(result.get('redis_timeout_search_result', 300))
