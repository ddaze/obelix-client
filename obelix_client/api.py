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
from blinker import signal
from obelix_client.recivers import QueueSignals


def get_logger():
    return logging.getLogger('obelix_client')


class Obelix(object):

    def __init__(self, storage, queues, userIdentifer='uid', logger=None):
        self.logger = logger or get_logger()
        self.storage = storage
        # self.storage_last_search_result =
        self.queues = queues
        self.signals = QueueSignals(queues)
        self.signals.connect()
        self.config = {'recommendations_impact': 0.5,
                       'score_lower_limit': 0.2,
                       'score_upper_limit': 10,
                       'score_min_limit': 10,
                       'score_min_multiply': 4,
                       'score_one_result': 1,
                       'method_switch_limit': 20}
        self.config['userIdentifer'] = userIdentifer

        # Save config to DB if not exist
        config_db = self.storage.get("settings", None)
        if config_db is None:
            self.storage.set("settings", self.config)

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
        records_by_order = utils.rank_records_by_order(self.config, hitset)

        # Get Recommendations from storage
        # TODO: How to name storage.get Function?
        recommendations = self.storage.getFromTable('recommendations', userId)
        # FIXME: getIntDict enforce data types
        recommendations = utils.getIntDict(recommendations)

        # If the user does not have any recommendations, we can just return
        if len(recommendations) == 0 or self.config['recommendations_impact'] == 0:
            finalScores = records_by_order
        else:
            # Calculate scores
            finalScores = utils.calcScores(self.config, records_by_order, recommendations)

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
                'obelix_uid': self.config['userIdentifer'],
                'result': record_ids,
                'original_result_ordered': original_result_ordered,
                'results_final_colls_scores': results_final_colls_scores,
                'uid': uid,
                'remote_ip': user_info.get("remote_ip"),
                'uri': user_info.get('uri'),
                'timestamp': search_timestamp,
                'settings': self.config,
                'recommendations': self.storage.getFromTable('recommendations',
                                                             uid),
                'seconds_to_rank_and_print': seconds_to_rank_and_print,
                'cols_in_result_ordered': cols_in_result_ordered,
                'jrec': jrec,
                'rg': rg,
                'rm': rm,
                'cc': cc}
        # queueName = "{0}::{1}".format("statistics-search-result", uid)
        signal('obelix_intern_statistics_search_result').send(self, data=data)
        # self.queues.lpush(queueName, data)

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
            self.log_page_view(user_info, recid,
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
        # self.queues.rpush("logentries", data)
        signal('obelix_intern_save_to_neo_feeder').send(self, data)

    def log_page_view_for_analytics(self, uid, recid, ip, uri, type):
        """ Mainly used to store statistics, may be removed in the future
        :param uid:
        :param recid:
        :param ip:
        :param uri:
        :return:
        """
        last_search_info = self.storage.getFromTable("last-search-result", uid)

        if not last_search_info:
            return
        # TODO: Check optimization
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
                                                            uid)
                data = {'search_timestamp': timestamp,
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
                        'type': type}
                # self.queues.lpush("statistics-page-view", data)
                signal('obelix_intern_statistics_page_view').send(self, data)

            hit_number_global += len(collection_result)
