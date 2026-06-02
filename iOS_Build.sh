#!/bin/bash
# ============================================================
# Sovereign Engine — iOS Build Script (Static Library)
# Builds staticlib (.a) for device + simulator
# ============================================================

set -e

echo "🔨 Building sovereign_engine for iOS (static library)..."

# Add targets if missing:
# rustup target add aarch64-apple-ios aarch64-apple-ios-sim

TARGET_DIR="target"
RELEASE_DIR="release"

# iOS device
echo "→ Building for aarch64-apple-ios (device)"
cargo build --release --target aarch64-apple-ios

# iOS simulator (Apple Silicon Macs)
echo "→ Building for aarch64-apple-ios-sim (simulator)"
cargo build --release --target aarch64-apple-ios-sim

# Create output directory for frameworks / libraries
mkdir -p "../ios/Libraries"

# Copy static libraries
cp "$TARGET_DIR/aarch64-apple-ios/$RELEASE_DIR/libsovereign_engine.a" \
   "../ios/Libraries/libsovereign_engine-device.a"

cp "$TARGET_DIR/aarch64-apple-ios-sim/$RELEASE_DIR/libsovereign_engine.a" \
   "../ios/Libraries/libsovereign_engine-simulator.a"

echo ""
echo "✅ iOS static libraries built!"
echo ""
echo "Next steps for Flutter iOS integration:"
echo "1. Open ios/Runner.xcodeproj in Xcode"
echo "2. Add both .a files to your project (Link Binary With Libraries)"
echo "3. In Build Settings → Library Search Paths, add:"
echo "   \$(SRCROOT)/../Libraries"
echo "4. In Build Settings → Other Linker Flags, add:"
echo "   -lsovereign_engine-device   (for device)"
echo "   or use a build phase script to pick the right one"
echo ""
echo "Alternative (recommended for production):"
echo "   Create an XCFramework from the two .a files using:"
echo "   xcodebuild -create-xcframework \\"
echo "     -library Libraries/libsovereign_engine-device.a \\"
echo "     -library Libraries/libsovereign_engine-simulator.a \\"
echo "     -output Libraries/sovereign_engine.xcframework"
echo ""
echo "Then embed the XCFramework in your Xcode project."
