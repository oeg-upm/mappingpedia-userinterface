
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
        #properties_str = row[5]
        #if np.isnan(properties_str):
        if properties_str.strip() == 'nan':
            properties_as_str = ""
        else:
            # print key
            # print type(properties_str)
            # print properties_str
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


# def generate_prop_json(file_dir):
#     t = '{'
#     f = open(file_dir)
#     pd.read_csv(file_dir)
#     for line in f.readlines()[0:2]:
#         cells = line.split(',')

#         # print 'cells:'
#         print cells
#         key = cells[1]
#         vals = cells[7]
#         print '5: '+cells[5]
#         print '6: '+cells[6]
#         print '7: '+cells[7]
#         print '8: '+cells[8]
#         print 'vals: '
#         print vals
#         vals_list = [('"' + p.strip() + '"') for p in vals]
#         vals_list_as_str = ",".join(vals_list)
#         print "vals_list_as_str: "
#         print vals_list_as_str
#         t += '"'+key+'":[' +vals_list_as_str+'],'
#     f_output = open("schema-prop.json", 'w')
#     f_output.write(t)
#     f_output.close()

if __name__ == '__main__':
    #print sys.argv[1]
    schema_csv = sys.argv[1]
    generate_prop_json(schema_csv)

