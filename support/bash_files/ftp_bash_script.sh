#!/bin/bash

HOST='sunnyside-times.com'
USER='sstweb'
PASSWD='sDl7Wsvqdk&rXm42'
FILE='foo.zip'

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
binary
put $FILE
quit
END_SCRIPT
exit 0
done