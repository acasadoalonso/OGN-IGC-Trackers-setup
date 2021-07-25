export TTNV2_APP_ID="ogn"
export TTNV2_APP_ACCESS_KEY="ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"
export FREQUENCY_PLAN_ID="EU_863_870_TTN"
export TTNV2_DISCOVERY_SERVER_ADDRESS="discovery.thethingsnetwork.org:1900"
echo $TTNV2_APP_ACCESS_KEY
echo "====================================== Migrate from TTN V2  ========================================================"
ttn-lw-migrate devices --verbose --source ttnv2 --ttnv2.with-session=false <  devicesTTN.V2.txt > devicesV2.json


