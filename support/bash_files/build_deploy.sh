#!/bin/bash
export TargetHost=sscgurus

cd /home/manage_sst/sst_static/sst
workon sst_venv
nikola build_photo_usage
nikola multi_pages
nikola build -a

zip -r output.zip output

curl --netrc -T output.zip ftp://sunnyside-times.com/httpdocs/output.zip