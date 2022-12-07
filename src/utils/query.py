import json

def get_single_result(result_list):
    for result in result_list:
        if len(result) > 0:
            return result[0]
    return None


def get_results(query_result):
    results = []
    for r in query_result:
        if len(r) == 1: r = r[0]
        results.append(r)
    return results


def debug_urls(result, debug_url):
    original_url = "https://journalobservatory.org"
    if type(result) == dict:
        string = json.dumps(result)
        string = string.replace(original_url, debug_url)
        return json.loads(string)
    return(result.replace(original_url, debug_url))
