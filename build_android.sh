#!/bin/bash
# ============================================================
# Sovereign Engine — Android Build Script
# Builds cdylib (.so) for all common Android ABIs
# ============================================================

set -e

echo "🔨 Building sovereign_engine for Android..."

# Make sure you have the Android NDK installed and rustup targets added:
# rustup target add aarch64-linux-android armv7-linux-androideabi x86_64-linux-android

TARGET_DIR="target"
RELEASE_DIR="release"

# Android ABIs we support
ABIS=("aarch64-linux-android" "armv7-linux-androideabi" "x86_64-linux-android")

for ABI in "${ABIS[@]}"; do
    echo "→ Building for $ABI"
    cargo build --release --target "$ABI"

    # Create jniLibs directory structure if it doesn't exist
    JNI_DIR="../../android/app/src/main/jniLibs"
    mkdir -p "$JNI_DIR/${ABI%%-*}"   # arm64-v8a, armeabi-v7a, x86_64

    # Map Rust target to Android ABI folder name
    case "$ABI" in
        aarch64-linux-android)   OUT_DIR="arm64-v8a" ;;
        armv7-linux-androideabi) OUT_DIR="armeabi-v7a" ;;
        x86_64-linux-android)    OUT_DIR="x86_64" ;;
    esac

    mkdir -p "$JNI_DIR/$OUT_DIR"
    cp "$TARGET_DIR/$ABI/$RELEASE_DIR/libsovereign_engine.so" "$JNI_DIR/$OUT_DIR/"
    echo "   ✓ Copied to $JNI_DIR/$OUT_DIR/libsovereign_engine.so"
done

echo ""
echo "✅ Android build complete!"
echo "   Place the jniLibs folder in your Flutter Android project:"
echo "   android/app/src/main/jniLibs/"
echo ""
echo "   Then run: flutter build apk --release"
