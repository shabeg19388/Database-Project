import json 
def similarity_score(relation1_json, relation2_json, weights=None):
    from collections import defaultdict
    relation1 = json.loads(relation1_json)
    relation2 = json.loads(relation2_json)

    attributes1 = set(relation1[0].keys()) if relation1 else set()
    attributes2 = set(relation2[0].keys()) if relation2 else set()

    common_attributes = attributes1.intersection(attributes2)

    unique_attr_penalty = len(attributes1.symmetric_difference(attributes2))

    normalized_relation1 = [tuple(row[attr] for attr in common_attributes) for row in relation1]
    normalized_relation2 = [tuple(row[attr] for attr in common_attributes) for row in relation2]

    set1, set2 = set(normalized_relation1), set(normalized_relation2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    jaccard_similarity = intersection / union if union else 1.0

    attribute_similarity = defaultdict(float)
    for attr in common_attributes:
        values1 = {row[attr] for row in relation1}
        values2 = {row[attr] for row in relation2}
        attr_intersection = len(values1.intersection(values2))
        attr_union = len(values1.union(values2))
        attribute_similarity[attr] = attr_intersection / attr_union if attr_union else 1.0

    if weights is None:
        weights = {attr: 1.0 for attr in common_attributes} 

    weighted_similarity = sum(attribute_similarity[attr] * weights.get(attr, 1.0) for attr in common_attributes)
    normalized_weight = sum(weights.values())

    composite_score = 0.4 * jaccard_similarity + 0.6 * (weighted_similarity / normalized_weight) - 0.1 * unique_attr_penalty
    return max(0.0, composite_score) 

relation1_json = json.dumps([{"id": 1, "name": "gill", "age": 23},{"id": 2, "name": "Namya", "age": 24}
])
relation2_json = json.dumps([
    {"id": 1, "name": "gill", "age": 23},
    {"id": 3, "name": "Charlie", "age": 35}
])
weights = {"id": 1.0, "name": 2.0, "age": 0.5}
score = similarity_score(relation1_json, relation2_json, weights)
