import http.client
import json
import feedparser
import datetime

def debug(s):
    global debug_flag
    if debug_flag:
        print(s)

def get_json_string(datasource_id, params):
    request_location = "/resource/" + datasource_id

    if len(params) > 0:
        queries = []
        for k, v in params.items():
            queries.append(k+"="+v)
        request_location += "?" + "&".join(queries)
    #debug(request_location)
    conn = http.client.HTTPSConnection('greengov.data.ca.gov')
    conn.request("GET",request_location)
    return conn.getresponse().read().decode("utf-8")

def get_parsed_json(datasource_id, params):
    json_string = get_json_string(datasource_id, params)
    #debug(json_string)
    return json.loads(json_string)

def build_schema(datasource_id, sample_size):
    debug("begin get json")
    json_list = get_parsed_json(datasource_id, { "$limit": str(sample_size), })

    debug("begin build schemas")
    schemas = []
    for json_dict in json_list:
        schemas.append(build_schema_sample(json_dict))

    return combine_schemas(schemas)

def build_schema_sample(json_dict):
    return {k: get_type(v) for k, v in json_dict.items() }

def get_type(value):
    # get best type match from most to least specific
    try:
        a = dict(value)
        return (-1, build_schema_sample(value))
    except:
        pass

    try:
        a = int(value)
        if a in [0, 1]:
            return (0, "bool")
        else:
            return (1,"int")
    except:
        pass

    try:
        a = float(value)
        return (2, "float")
    except:
        pass

    try:
        a = datetime.datetime.strptime( value, "%Y-%m-%dT%H:%M:%S" )
        return (3, "datetime")
    except:
        pass

    return (4, "string")

def combine_schemas(schemas):
    inverted_dictionary = invert_to_dictionary(schemas)

    return {key: extract_best_type(list) for key, list in inverted_dictionary.items()}

def invert_to_dictionary(list):
    d = {}
    for single_dict in list:
        for k, v in single_dict.items():
            if k not in d:
                d[k] = [v]
            else:
                d[k].append(v)
    return d

def extract_best_type(list):
    if list[0][0] == -1: # nested objects
        return combine_schemas([dict_tuple[1] for dict_tuple in list])
    else:
        return max(list, key=lambda x: x[0])[1]

def get_all_datasources():
    catalog = "https://greengov.data.ca.gov/catalog.rss"
    feed = feedparser.parse( catalog )
    links = [parse_link(x['link']) for x in feed['items']]
    return links

def parse_link(link):
    return link.split("/")[-1]

def test_get_schema():
    global debug_flag
    debug_flag = True
    print(build_schema("cnqf-6t8e", 10))

def test_get_datasources():
    print(get_all_datasources())