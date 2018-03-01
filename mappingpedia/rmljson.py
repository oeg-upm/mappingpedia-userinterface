import json

t1 = """
{
"name": "abc",
"dict1": {"A": "aa", "B": "bb"},
"list2": [1,2],
"list1": [1,2,3]
}
"""

t2 = """
{
"name": "abc",
"dict1": {"A": "aa", "B": "bb"},
"list2": [1,2],
"list1": [1,2,3],
"dict2": {"list2_1": [1,2,3,4]}
}
"""

t3 = """
{
"name": "abc",
"dict1": {"A": "aa", "B": "bb"},
"list2": [1,2],
"list1": [1,2,3],
"dict2": {"list2_1": [1,2,3,4], "dict3": {"again": [1,2,3,4,5]}}
}
"""

t4 = """
{
"name": "abc",
"dict1": {"A": "aa", "B": "bb"},
"list2": [1,2],
"list1": [1],
"dict2": {"list2_1": [1,2], "dict3": {"again": [{"fname": "a", "lname": 5},{"fname": "bb", "lname": 6},
{"fname": "cc", "lname": 7},{"fname": "ddd", "lname": 8}]}}
}
"""


def get_json_path(j):
    max_no = 0
    json_path = []
    for k in j.keys():
        if isinstance(j[k], list):
            # print "list (%d): " % len(j[k])
            # print j[k]
            if len(j[k]) > max_no:
                # print "max list (%d): " % len(j[k])
                # print j[k]
                max_no = len(j[k])
                json_path = [k]
        elif isinstance(j[k], dict):
            j_dict = get_json_path(j[k])
            if j_dict["max_no"] > max_no:
                max_no = j_dict["max_no"]
                json_path = [k] + j_dict["json_path"]
        # else:
        #     print j[k]
        #     print type(j[k])
    return {"max_no": max_no, "json_path": json_path}


def json_unfold_json_path(j, path):
    # print "j: "
    # print j
    # print "path: "
    # print path
    if len(path) == 0:
        # print "returning j"
        # print j
        return j
    else:
        p1 = path[0]
        return json_unfold_json_path(j[p1], path[1:])


def get_json_as_cols(json_text):
    try:
        j = json.loads(json_text)
        jpath_result = get_json_path(j)
        if jpath_result["max_no"] == 0:
            print "max_no is 0"
            return None, []
        else:
            print "json_path: <%s> with num of elements: %d" % (jpath_result["json_path"], jpath_result["max_no"])
            return jpath_result["json_path"], json_unfold_json_path(j, jpath_result["json_path"])[0].keys()
    except Exception as e:
        print "Error parsing the json text"
        print e
        return None, []


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        f = open(sys.argv[1])
        print get_json_as_cols(f.read())

# j = json.loads(t4)
# result = get_json_path(j)
# print json_unfold_json_path(j, result["json_path"])
# print get_json_as_cols(t4)





