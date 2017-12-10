
import sys
import pandas as pd
import numpy as np
import json


def generate_prop_json(file_dir):
    df = pd.read_csv(file_dir)
    t = '{'
    num_of_rows = df.shape[0]
    for index, row in df.iterrows():

        key = row[1]
        properties_str = str(row[5])
        if properties_str.strip() == 'nan':
            properties_as_str = ""
        else:
            properties = properties_str.replace('\n', '').split(',')
            properties_clean = ['"'+p.strip()+'"' for p in properties]
            properties_as_str = ",".join(properties_clean)

        single_element = '\n"'+key.strip()+'":['+properties_as_str+']'
        if index != num_of_rows-1:
            single_element += ','
        t += single_element
    t += '}'
    f_output = open("schema-prop.json", 'w')
    f_output.write(t)
    f_output.close()
    try:
        f = open("schema-prop.json")
        json.loads(f.read())
        print "correct json is produced"
    except Exception as e:
        print "produced json is not correct: %s" % str(e)


if __name__ == '__main__':
    #print sys.argv[1]
    schema_csv = sys.argv[1]
    generate_prop_json(schema_csv)

