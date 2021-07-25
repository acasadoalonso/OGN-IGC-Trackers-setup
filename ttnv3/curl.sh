curl --location \
  --header 'Accept: application/json' \
  --header "Authorization: Bearer NNSXS.KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ" \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: my-integration/my-integration-version' \
  --request POST \
  --data-raw '{
    "end_device" : {
    "ids": {
    "device_id": "ognfc2710",
    "application_ids": {
      "application_id": "ogn"
    },
    "dev_eui": "0000CC50E3fc2710",
    "join_eui": "70B3D57ED0035895"
  },
  "name": "ognfc2710",
  "description": "TEST_device",
  "attributes": {
  },
  "network_server_address": "eu1.cloud.thethings.network",
  "application_server_address": "eu1.cloud.thethings.network",
  "join_server_address": "eu1.cloud.thethings.network",
  "lorawan_version": "MAC_V1_0_3",
  "lorawan_phy_version": "PHY_V1_0_3_REV_A",
  "frequency_plan_id": "EU_863_870",
  "supports_join": True,
  "field_mask":{
      "paths":[
         "multicast",
         "supports_join",
         "lorawan_version",
         "ids.device_id",
         "ids.dev_eui",
         "ids.join_eui",
         "mac_settings.supports_32_bit_f_cnt",
         "supports_class_c",
         "supports_class_b",
         "lorawan_phy_version",
         "frequency_plan_id"
      ]
   }
}}' \
'https://eu1.cloud.thethings.network/api/v3/applications/ogn/devices/'


