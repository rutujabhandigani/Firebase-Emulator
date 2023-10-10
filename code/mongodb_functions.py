from pymongo import MongoClient
import validators
import json
import uuid
import random

command_list = ["GET", "PUT", "POST", "PATCH", "DELETE"]
filter_conds_list = ["orderBy", "limitToFirst",
                     "limitToLast", "equalTo", "startAt", "endAt"]


def dict_keys_helper(dict_, keys):
    if not isinstance(dict_, dict):
        return dict_
    output = dict_
    for key in keys:
        if key in list(output.keys()):
            temp = output[key]
            output = temp
    return output


def filter_process(content, condition_query):
    orderBy = condition_query["orderBy"]
    limitValue = condition_query["limitValue"]
    startAt = condition_query["startAt"]
    endAt = condition_query["endAt"]
    equalTo = condition_query["equalTo"]
    output = []
    if content is None:
        return content
    elif isinstance(content, dict):
        for item in content.items():
            document = {item[0]: item[1]}
            output.append(document)
    elif not hasattr(content, '__iter__'):
        return content
    else:
        output = content

    if orderBy is None:
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    elif orderBy.lower() == "$key":
        output = sorted(output, key=lambda x: list(x.keys())[0])
        if equalTo is not None:
            temp = [document for document in output if list(document.keys())[
                0] == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if list(document.keys())[
                0] >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if list(document.keys())[
                0] <= endAt]
            output = temp
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    elif orderBy.lower() == "$value":
        can_sort = []
        non_sort = []
        for x in output:
            if isinstance(x[list(x.keys())[0]], dict) or x[list(x.keys())[0]] is None:
                non_sort.append(x)
            else:
                can_sort.append(x)
        can_sort = sorted(can_sort, key=lambda x: x[list(x.keys())[0]])
        output = can_sort
        if equalTo is not None:
            temp = [document for document in output if document[list(document.keys())[
                0]] == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if document[list(document.keys())[
                0]] >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if document[list(document.keys())[
                0]] <= endAt]
            output = temp
        output += non_sort
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    else:

        can_sort = []
        non_sort = []
        paths = orderBy.split("/")
        for x in output:
            if isinstance(x[list(x.keys())[0]], dict):
                existFlag = True
                temp = x[list(x.keys())[0]]
                for p in paths:
                    if not isinstance(temp, dict):
                        existFlag = False
                        break
                    if p in list(temp.keys()):
                        temp = temp[p]
                    else:
                        existFlag = False
                        break
                if isinstance(temp, dict):
                    existFlag = False

                if existFlag:
                    can_sort.append(x)
                else:
                    non_sort.append(x)
            else:
                non_sort.append(x)
        can_sort = sorted(can_sort, key=lambda x: dict_keys_helper(
            x[list(x.keys())[0]], paths))
        output = can_sort
        if equalTo is not None:
            temp = [document for document in output if dict_keys_helper(
                document[list(document.keys())[0]], paths) == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if dict_keys_helper(
                document[list(document.keys())[0]], paths) >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if dict_keys_helper(
                document[list(document.keys())[0]], paths) <= endAt]
            output = temp
        output += non_sort
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    output_dict = dict()
    for document in output:
        output_dict.update(document)

    return output_dict


def process_GET(url, conditions):

    orderByIndex = None
    startValue = None
    endValue = None
    equalValue = None
    limitOrder = 0
    limitToNumber = None
    current_cond_key = []
    condition_query = dict({"orderBy": orderByIndex, "limitValue": limitToNumber, "startAt": startValue,
                            "endAt": endValue, "equalTo": equalValue})
    if conditions is not None:
        for cond in conditions.split("&"):
            if len(cond.split("=")) < 2:
                return "Invalid Command: inproper filter condition format"
            filter_key = cond.split("=")[0]
            filter_value = cond.split("=")[1]
            if filter_key not in filter_conds_list:
                return "Invalid Command: invalid filter condition"
            if filter_key in current_cond_key:
                return "Invalid Command: duplicated filter condition"
            else:
                current_cond_key.append(filter_key)

            if (filter_value[0] == "\'" and filter_value[-1] == "\'") or (filter_value[0] == "\"" and filter_value[-1] == "\""):
                filter_value = filter_value[1:-1]
            elif filter_value.lower() == "true":
                filter_value = True
            elif filter_value.lower() == "false":
                filter_value = False
            elif "." in filter_value:
                filter_value = float(filter_value)
            else:
                filter_value = int(filter_value)

            if filter_key == "orderBy":
                orderByIndex = filter_value
                condition_query.update({"orderBy": orderByIndex})
            elif filter_key == "limitToFirst":
                if limitOrder < 0:
                    return "Invalid Command: cannot enter limitToFirst and limitToLast together"
                elif not isinstance(filter_value, int):
                    return "Invalid Command: limitToFirst only accepts integer"
                else:
                    limitOrder = 1
                    limitToNumber = filter_value
                    condition_query.update(
                        {"limitValue": limitOrder * limitToNumber})
            elif filter_key == "limitToLast":
                if limitOrder > 0:
                    return "Invalid Command: cannot enter limitToFirst and limitToFirst together"
                elif not isinstance(filter_value, int):
                    return "Invalid Command: limitToLast only accepts integer"
                else:
                    limitOrder = -1
                    limitToNumber = filter_value
                    condition_query.update(
                        {"limitValue": limitOrder * limitToNumber})
            elif filter_key == "startAt":
                startValue = filter_value
                condition_query.update({"startAt": startValue})
            elif filter_key == "endAt":
                endValue = filter_value
                condition_query.update({"endAt": endValue})
            elif filter_key == "equalTo":
                equalValue = filter_value
                condition_query.update({"equalTo": equalValue})
            else:
                return "Invalid Command: invalid filter condition"

    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    
    client = MongoClient(address, int(port))
    ifIndexed = True
    if orderByIndex is not None and orderByIndex.lower() != "$key" and orderByIndex.lower() != "$value": 
        ifIndexed = False
        if "config" not in client.list_database_names():
            return "Invalid Command: Unable to find Rules document"
        if "rules" not in client["config"].list_collection_names():
            return "Invalid Command: Unable to find Rules document"
        rules_col = client["config"]["rules"]
        rules = {}
        for d in rules_col.find({}, {"_id": 0}):
            rules.update(d)
        order_Path = parsed_url[1:]
        indexOn = None
        temp = rules["rules"]
        for o in order_Path:
            if o in list(temp.keys()):
                temp = temp[o]
            else:
                temp = None
                break
        if temp is not None:
            if ".indexOn" in list(temp.keys()):
                indexOn = temp[".indexOn"]
        if indexOn is not None:
            if orderByIndex == indexOn:
                ifIndexed = True
    
    if not ifIndexed:
        return "Invalid Command: " + orderByIndex + " is not Indexed On"
            

        

    if len(parsed_url) == 1:
        output = dict()
        for db_name in client.list_database_names():
            db_content = dict()
            db = client[db_name]
            for col_name in db.list_collection_names():
                col_content = dict()
                for document in db[col_name].find({}, {"_id": 0}):
                    col_content.update(document)
                db_content.update({col_name: col_content})
            output.update({db_name: db_content})
        return output

    elif len(parsed_url) == 2:
        if parsed_url[1] == "":
            output = dict()
            for db_name in client.list_database_names():
                db_content = dict()
                db = client[db_name]
                for col_name in db.list_collection_names():
                    col_content = dict()

                    for document in db[col_name].find({}, {"_id": 0}):
                        col_content.update(document)
                    db_content.update({col_name: col_content})
                output.update({db_name: db_content})
            return filter_process(output, condition_query)

        else:
            db_content = dict()
            db = client[parsed_url[1]]
            for col_name in db.list_collection_names():
                col_content = dict()
                for document in db[col_name].find({}, {"_id": 0}):
                    col_content.update(document)
                db_content.update({col_name: col_content})
            output = dict({parsed_url[1]: db_content})
            return filter_process(output, condition_query)
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        content = []
        for document in db[parsed_url[2]].find({}, {"_id": 0}):
            content.append(document)
        return filter_process(content, condition_query)
    else:
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        content = None
        documents = dict()
        for document in db[parsed_url[2]].find({}, {"_id": 0}):
            documents.update(document)
        item = documents
        for key in json_keys:
            if type(item) == dict:
                if key in list(item.keys()):
                    temp = item[key]
                    item = temp
                else:
                    item = None
                    break
            else:
                item = None
                break
        if item is not None:
            content = item
        
        return filter_process(content, condition_query)


def process_DELETE(url):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017


    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))

    if len(parsed_url) == 3:
        db = client[parsed_url[1]]
        db.drop_collection(parsed_url[2])
    elif len(parsed_url) == 4:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        primary_key = parsed_url[3]
        collection.delete_one({primary_key: {'$exists': True}})
    else:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        primary_key = parsed_url[3]
        to_remove = primary_key
        for k in parsed_url[4:]:
            to_remove = to_remove + "." + k
        collection.update_one({primary_key: {'$exists': True}}, {
                              '$unset': {f'{to_remove}': 1}})
    return "DELETE http://" + url + ".json"


def process_PUT(url, data):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))

    js = dict()
    if data[0] != "\'" or data[-1]!="\'":
        return "Invalid Command: Please enter data in single quotation marks"
    else:
        js = json.loads(data[1:-1])

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))
    if len(parsed_url) < 3:
        return "Invalid Command: invalid POST on database or Collection"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)
        if len(list(js.keys())) != 1:
            id = str(generate_random_number(documents.keys()))
            js = {id: js}
        else:
            id = str(list(documents.keys())[0])
            js = {id: js}
        if id in list(documents.keys()):
            collection.update_one({id: {"$exists": True}}, {"$set": js})
        
        else:
            collection.insert_one(js)
    else:
        document_id = parsed_url[3]
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)
        if document_id in list(documents.keys()):
            # get existing document 
            dataToUpdate = dict({document_id: documents[document_id]})
            if len(json_keys)>1:
                dataToUpdate = recursive_helper(dataToUpdate, json_keys, js, True)
            else:
                dataToUpdate[document_id].update(js)
            newValue = {"$set": dataToUpdate}
            filter = {document_id: {"$exists": True}}
            # print(newValue)
            collection.update_one(filter, newValue)
        else:
            item = js
            for key in reversed(json_keys):
                temp = dict()
                temp.update({key:item})
                item = temp
            # print(item)
            collection.insert_one(item)

    
    return 'PUT ' + str(js) + " into http://" + url + ".json"

def recursive_helper(data, keys, js, flag):
    if len(keys) == 0:
        return js
    elif flag:
        if keys[0] in list(data.keys()):
            if type(data[keys[0]]) is not dict:
                data.update({keys[0]:recursive_helper(data, keys[1:], js, False)})
            else:
                data[keys[0]].update(recursive_helper(data[keys[0]], keys[1:], js, flag))
            return data
        else:
            temp = {keys[0]:recursive_helper(data, keys[1:], js, False)}
            return temp
    else:
        temp = {keys[0]:recursive_helper(data, keys[1:], js, flag)}
        return temp
        


def process_POST(url, data):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017
    js = dict()

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))

    db = client[parsed_url[1]]
    collection = db[parsed_url[2]]
    documents = dict()
    for document in collection.find({}, {"_id": 0}):
        documents.update(document)

    # check if data is valid
    if data[0] != "\'" or data[-1]!="\'":
        return "Invalid Command: Please enter data in single quotation marks"
    else:
        js = json.loads(data[1:-1])
        my_new_id = str(generate_random_number(documents.keys()))
        js = dict({my_new_id: js})

    if len(parsed_url) < 3:
        return "Invalid Command: invalid POST on database or Collection"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        collection.insert_one(js)
    else:
        document_id = parsed_url[3]
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)

        if document_id in list(documents.keys()):
            dataToUpdate = dict({document_id: documents[document_id]})
            if len(json_keys)>1:
                dataToUpdate = recursive_helper(dataToUpdate, json_keys, js, True)
            else:
                dataToUpdate[document_id].update(js)
            newValue = {"$set": dataToUpdate}
            filter = {document_id: {"$exists": True}}
            collection.update_one(filter, newValue)
        else:
            item = js
            for key in reversed(json_keys):
                temp = dict()
                temp.update({key:item})
                item = temp
            collection.insert_one(item)

    return "POST " + str(dict({my_new_id:js[my_new_id]})) + " to http://" + url + ".json"
        

def generate_random_number(existing_keys):
    while True:
        existing_keys_set = set(existing_keys)
        new_key = random.randint(10**9, 10**10-1)
        if new_key not in existing_keys_set:
            return int(new_key)

def process_PATCH(url, data):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    if data[0] != "\'" or data[-1] != "\'":
        return "Invalid Command: Please enter data in single quotation marks"
    else:
        formatted_data = json.loads(data[1:-1])

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"

    # Establish a connection to MongoDB using the provided URL
    client = MongoClient(address, int(port))

    if len(parsed_url) < 3:
        return "Invalid Command: invalid POST on database or Collection"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)

        if len(list(formatted_data.keys())) != 1:
            id = str(generate_random_number(documents.keys()))
            formatted_data = {id: formatted_data}
        else:
            id = str(list(documents.keys())[0])
            formatted_data = {id: formatted_data}
        # if document id exist already: do update_one
        if id in list(documents.keys()):
            collection.update_one({id: {"$exists": True}}, {"$set": formatted_data})
        # else: do insert_ones
        else:
            collection.insert_one(formatted_data)
    else:
        document_id = parsed_url[3]
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        # Find a document with the primary_key field present
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)
        if document_id in list(documents.keys()):
            # get existing document
            dataToUpdate = dict({document_id: documents[document_id]})
            if len(json_keys) > 1:
                dataToUpdate = recursive_helper(dataToUpdate, json_keys, formatted_data, True)
            else:
                dataToUpdate[document_id].update(formatted_data)
            newValue = {"$set": dataToUpdate}
            filter = {document_id: {"$exists": True}}
            collection.update_one(filter, newValue)
        else:
            item = formatted_data
            for key in reversed(json_keys):
                temp = dict()
                temp.update({key: item})
                item = temp
            collection.insert_one(item)

    return "PATCH " + str(formatted_data) + " to http://" + url + ".json"


def extract_url(user_input):
    # Split the user input string into parts using spaces as delimiters
    input_parts = user_input.split(" ")
    url = None
    for part in input_parts:
        # Check if the current part starts with "http://" or "https://"
        if part.startswith("\"http://") or part.startswith("\"https://"):
            url = part
            break

    return url

def extract_user_data(command):
    user_data = None

    # Iterate through the command string
    for i in range(len(command)):
        # Check if the current character is '-' and the next character is 'd'
        if command[i] == "-" and command[i + 1] == "d":
            # Extract the user_data following the "-d" flag
            data_end_index = [x for x in range(len(command)) if command[x] == "}"]
            user_data = command[i + 3: data_end_index[0]+2]
            # Break the loop once the user data is found
            break

    # Return the extracted user data in JSON format, or None if not found
    return user_data


# High-level function for command processing
def command_process(command):
    try:
        parsed_command = command.split(" ")
        print(parsed_command)
        # check if the command starts with "curl"
        if parsed_command[0].lower() != "curl":
            return "Invalid Command: only accept curl command"

        # check if the second element is "-X"
        if parsed_command[1].lower() != "-x":
            return "Invalid Command: invalid option, please enter \"-X\" option"

        # check if the command is in [GET, , PUT, POST, PATCH, DELETE]
        if parsed_command[2].upper() not in command_list:
            return "Invalid Command: only accept GET, , PUT, POST, PATCH, DELETE command"

        # check if the url is entered in single or double quotes and is a valid url format
        if not ((parsed_command[3][0] == "\'" and parsed_command[3][-1] == "\'")
                or (parsed_command[3][0] == "\"" and parsed_command[3][-1] == "\"")
                or (parsed_command[3][0] == "-" and parsed_command[3][-1] == "d")
                or (parsed_command[5][0] == "\'" and parsed_command[5][-1] == "\'")
                or (parsed_command[5][0] == "\"" and parsed_command[5][-1] == "\"")):
            return "Invalid Command: please enter url with single/double quotes"
        if parsed_command[3] == "-d":
            # Extract user data and insert it to parsed_command[4]
            current_user_data = extract_user_data(command)
            parsed_command[4] = current_user_data
            parsed_command[5] = extract_url(command)
            url = parsed_command[5][1:-1]
            if validators.url(parsed_command[5][0:-1]):
                return "Invalid Command: " + parsed_command[5] + " is invalid url"
        else:
            # url is parsed_command[3] if user inserts data "-d" last
            url = parsed_command[3][1:-1]
            # check if URL is valid
            if validators.url(parsed_command[3][0:-1]):
                return "Invalid Command: " + parsed_command[3] + " is invalid url"

        # further parse the command and identify the filter conditions in the url
        db_url = url.split("?")[0]
        filter_conditions = None
        if len(url.split("?")) == 2:
            filter_conditions = url.split("?")[1]
        elif len(url.split("?")) > 2:
            return "Invalid Command: Improper format of filter conditions"

        # check if the db url starts with http:// and ends with .json
        if db_url[0:7] != "http://" or db_url[-5:] != ".json":
            return "Invalid Command: enter url starts with \'http://\' and ends with \'.json\'"

        # Start real processing and connect to Mongodb
        # process GET with conditions
        if parsed_command[2].upper() == "GET":
            return process_GET(db_url[7:-5], filter_conditions)

        # process POST
        elif parsed_command[2].upper() == "POST":
            # use extract_user_data() function to take in user data
            if parsed_command[3] == '-d':
                process_POST(db_url[7:-5], extract_user_data(command))
            elif parsed_command[4] == '-d':
                return process_POST(db_url[7:-5], extract_user_data(command))
            else:
                return "invalid command please enter a url with -d"
        elif parsed_command[2].upper() == "PUT":
            # use extract_user_data() function to take in user data
            if parsed_command[3] == '-d':
                process_PUT(db_url[7:-5], extract_user_data(command))
            elif parsed_command[4] == '-d':
                return process_PUT(db_url[7:-5], extract_user_data(command))
            else:
                return "invalid command please enter a url with -d"
        elif parsed_command[2].upper() == "PATCH":
            if parsed_command[3] == '-d':
                # insert the url and extracted data
                return process_PATCH(db_url[7:-5], extract_user_data(command))
            elif parsed_command[4] == '-d':
                # insert the url and extracted data
                return process_PATCH(db_url[7:-5], extract_user_data(command))
            else:
                return "invalid command please enter a url with -d"
        elif parsed_command[2].upper() == "DELETE":
            return process_DELETE(db_url[7:-5])
        return parsed_command
    except Exception as e:
        print("Invalid Command:", str(e))
        return "Invalid Command: " + str(e)
