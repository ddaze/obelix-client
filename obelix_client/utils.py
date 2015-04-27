
def getIntDict(dataDict):
    """ Retrieves the recommendation for the self.uid (current user)
    from redis

    The cached recommendations may be on the form
    {'123': 0.2.. but we want {123: 0.2
    Therefore we have to enforce that the keys in the
    resulting dictionary are integers

    :return
        dict with recommendations if any with the user id as the
        key {123: 0.3, 321: 0.2} empty dict if no recommendations

    :raises
        redis.ConnectionError if redis is unavailable
        TypeError: TypeError: expected string or buffer,
        if anything else than a str is stored
        ValueError: No JSON object could be decoded (invalid json format)
    """
    result = {}
    if dataDict:
        for key, value in dataDict.items():
            result[int(key)] = float(value)

    return result


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

    rankedHitset = {}
    for idx, score in enumerate(scores):
        rankedHitset[hitset[idx]] = score

    return rankedHitset


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


def calcScores(conf, records_by_order, recommendations):
    final_scores = {}

    for recid, recScore in records_by_order.items():
        recommendationScore = recommendations.get(recid, None)
        # TODO: Check if this fits
        finalScore = order_score = recScore * (1 - conf['recommendations_impact'])
        if recommendationScore:
            recommendedScore = recommendationScore * conf['recommendations_impact']
            finalScore = order_score + recommendedScore

        final_scores[recid] = finalScore

    return final_scores
