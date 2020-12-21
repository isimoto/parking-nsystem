#!/bin/sh
fn=$(date +%Y%m%d%H%M%S)
raspistill -o /tmp/${fn}.jpg -rot 180
/home/pi/.local/bin/aws s3 cp /tmp/${fn}.jpg s3://nsystem-ohaio/pi-ibs001
