
def rank_records_by_order(conf, hitset):
    """
    Rank the records by the original order they we're provided

    If the SearchEngineObelix([1,2,3]) then this method will
    return [1.0, 0.933, 0.867]

    Typically called like this:
        records, scores = __build_ranked_by_order()

    :return:
        A tuple, one list with records and one with scores.
        The list of records are integers while the scores
        are floats: [1,2,3],[.9,.8,7] etc...
    """
    if len(hitset) == 1:
        return hitset, [conf['score_one_result']]

    upper = 1
    lower = conf['score_lower_limit']
    size = len(hitset)

    # TODO: Check why
    if size < conf['score_min_limit']:
        size *= conf['score_min_multiply']

    step = ((upper - lower) * 1.0 / size)
    scores = [1 - (lower + i * step) for i in range(0, size)]
    scores = scores[0:len(hitset)]

    ranked_hitset = {}
    for idx, score in enumerate(scores):
        ranked_hitset[hitset[idx]] = score

    return ranked_hitset


def sort_records_by_score(rec_scores):
    """
    :param record_scores: dictionary {1:0.2, 2:0.3 etc...
    :return: a tuple with two lists, the first is a list of records
    and the second of scores
    """
    records = []
    scores = []

    for recid in sorted(rec_scores, key=rec_scores.get, reverse=True):
        records.append(recid)
        scores.append(rec_scores[recid])

    return records, scores


def calcScores(config, records_by_order, recommendations):
    final_scores = {}

    for recid, rec_score in records_by_order.items():
        recommendation_score = recommendations.get(recid, None)
        # TODO: Check if this fits
        final_score = order_score = rec_score * (1 - config['recommendations_impact'])
        if recommendation_score:
            recommended_score = recommendation_score * config['recommendations_impact']
            final_score = order_score + recommended_score

        final_scores[recid] = final_score

    return final_scores
