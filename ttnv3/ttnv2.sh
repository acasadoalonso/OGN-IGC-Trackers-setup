export TTNV2_APP_ID="ogn"
export TTNV2_APP_ACCESS_KEY="ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"
export FREQUENCY_PLAN_ID="EU_863_870_TTN"
export TTNV2_DISCOVERY_SERVER_ADDRESS="discovery.thethingsnetwork.org:1900"
echo $TTNV2_APP_ACCESS_KEY
#ttn-lw-migrate device --source ttnv2 "avionix-ognc30a0c" --ttnv2.with-session=false > devices.json
echo "====================================== Migrate from TTN V2  ========================================================"
ttn-lw-migrate application --source ttnv2 "ogn" --ttnv2.with-session=false --verbose > devices.json
echo "====================================== create devices on V3 ========================================================"
sudo ttn-lw-cli end-devices create --application-id "ogn" -c /home/angel/snap/ttn-lw-stack/common/.ttn-lw-cli.yml < devices.json


