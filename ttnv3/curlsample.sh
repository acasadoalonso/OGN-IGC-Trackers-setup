curl --location \
  --header "Authorization: Bearer NNSXS.KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ" \
  --header 'Content-Type: application/json' \
  --request POST \
  --data-raw '{
    "identifiers":[{
        "device_ids":{
            "device_id":"ognc30734",
            "application_ids":{"application_id":"ogn"}
        }
    }]
  }' \
  'https://eu1.cloud.thethings.network/api/v3/events'
echo "==================================================================="
bash checkip
echo "==================================================================="
curl --location  \
     --header "Authorization: Bearer NNSXS.KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ" \
      --header 'Accept: application/json'   \
     --header 'User-Agent: my-integration/my-integration-version' \
     'https://eu1.cloud.thethings.network/api/v3/applications/ogn/devices/ognc30734'
