export TTNV2_APP_ID="ogn"
export TTNV2_APP_ACCESS_KEY="ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"
export FREQUENCY_PLAN_ID="EU_863_870_TTN"
export TTNV2_DISCOVERY_SERVER_ADDRESS="discovery.thethingsnetwork.org:1900"
echo $TTNV2_APP_ACCESS_KEY
#ttn-lw-migrate device --source ttnv2 "avionix-ognc30a0c" --ttnv2.with-session=false > devices.json
echo "====================================== Migrate from TTN V2  ========================================================"
#ttn-lw-migrate application --source ttnv2 "ogn" --ttnv2.with-session=false --verbose > devices.json
ttn-lw-migrate device --source ttnv2 "ognc30734" --ttnv2.with-session=false > devices1.json
ttn-lw-migrate device --source ttnv2 "ognc30824" --ttnv2.with-session=false >> devices1.json
ttn-lw-migrate device --source ttnv2 "ognc30840" --ttnv2.with-session=false >> devices1.json
ttn-lw-migrate device --source ttnv2 "ognc30854" --ttnv2.with-session=false >> devices1.json
ttn-lw-migrate device --source ttnv2 "ognc30864" --ttnv2.with-session=false >> devices1.json
ttn-lw-migrate device --source ttnv2 "ognc30898" --ttnv2.with-session=false >> devices1.json
echo "====================================== create devices on V3 ========================================================"
ttn-lw-cli end-devices create --application-id "ogn" -c /home/angel/snap/ttn-lw-stack/common/.ttn-lw-cli.yml --session.dev-addr=FC0069C1  --session.keys.app-s-key.key=9F264F712940CA819A4D19EA91B762EB --session.keys.f-nwk-s-int-key.key=E8E2B56D2114E8A0DA0C4338A008DB70 < devices1.json


