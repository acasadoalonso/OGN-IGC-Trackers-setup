#!/usr/bin/python3

import requests
import json

theApplication = "ogn"
TTN_auth       = "Bearer NNSXS.KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ"

# Note the path you have to specify. Double note that it has be prefixed with up.
theFields = "up.uplink_message.decoded_payload,up.uplink_message.frm_payload"

theNumberOfRecords = 10

theURL = "https://eu1.cloud.thethings.network/api/v3/as/applications/" + theApplication + "/packages/storage/uplink_message?order=-received_at&limit=" + str(theNumberOfRecords) + "&field_mask=" + theFields

# These are the headers required in the documentation. The Accept header needs
# further investigation as you can ask for other formats but it is ignored.
theHeaders = { 'Accept': 'text/event-stream', 'Authorization': TTN_auth }

print("\n\nFetching from data storage  ...\n")

r = requests.get(theURL, headers=theHeaders)

print("URL: " + r.url)
print()

print("Status: " + str(r.status_code))
print()

print("Response: ")
print(r.text)
print()


# Due to some design choices by TTI, the text returned is not proper JSON.
# Event Stream (see headers above) is a connection type that sends well 
# formed blocks of JSON as a chunk or a message becomes available. We can't 
# subscribe to this stream due to CORS restrictions and if we ask for more 
# than one record, we are sent the chunks with a blank line between them and
# no [] to turn it in to an array. So we have to here, as at 17th March 2021

theJSON = "{\"data\": [" + r.text.replace("\n\n", ",")[:-1] + "]}";


print("JSON: ")
parsedJSON = json.loads(theJSON)
print(json.dumps(parsedJSON, indent=4))
print()
