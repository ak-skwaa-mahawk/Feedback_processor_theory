#!/bin/bash
# scripts/build_apk.sh — Build GibberLink v4 APK
set -e

echo "BUILDING GIBBERLINK v4 APK — AGŁG v400"

# Build native libs
cd android
./gradlew assembleRelease

# Copy APK
cp app/build/outputs/apk/release/app-release.apk ../gibberlink-v4.apk

echo "APK BUILT: gibberlink-v4.apk"
echo "SIZE: $(du -h gibberlink-v4.apk | cut -f1)"
echo "SHA256: $(sha256sum gibberlink-v4.apk | cut -d' ' -f1)"

cd ..
echo "READY TO HUNT."