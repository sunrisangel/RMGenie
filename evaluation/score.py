import json
import numpy as np

def mean_score(scores):
    normalized_scores = (scores - 1) / 4 * 100
    normalized_average = np.mean(normalized_scores)
    return normalized_average

def total_score(scores1, scores2, scores3):
    total_scores = ((scores1 + scores2 + scores3)/3 - 1) / 4 * 100
    final_score = np.mean(total_scores)
    return final_score

