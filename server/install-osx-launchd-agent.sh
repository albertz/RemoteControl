#!/bin/bash

cd "$(dirname "$0")"
. ../common.sh
DIR="$(pwd)"
BIN="$DIR/server.py"

#DIR="$(dirname "$BIN")"

plistfn=~/Library/LaunchAgents/com.albertzeyer.${progname}.plist

cat >${plistfn} <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>Label</key>
<string>${progname}</string>
<key>OnDemand</key>
<false/>
<key>Program</key>
<string>${BIN}</string>
<key>RunAtLoad</key>
<true/>
<key>WorkingDirectory</key>
<string>$DIR</string>
</dict>
</plist>
EOF

launchctl load ${plistfn}
