#!/bin/bash

cd "$(dirname "$0")"
. ../common.sh
launchctl remove ${progname}
launchctl load ~/Library/LaunchAgents/com.albertzeyer.${progname}.plist
