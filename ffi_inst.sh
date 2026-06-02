# Sovereign Engine — FFI Build Instructions (Android + iOS)

This document explains how to build `libsovereign_engine` for Flutter on Android and iOS.

## Prerequisites

- Rust toolchain (`rustup`)
- For Android: Android NDK + `rustup target add` for Android triples
- For iOS: Xcode + `rustup target add aarch64-apple-ios aarch64-apple-ios-sim`

## 1. Update Cargo.toml (already done)

The `[lib]` section now supports both dynamic and static linking:

```toml
[lib]
name = "sovereign_engine"
crate-type = ["cdylib", "staticlib"]
```

## 2. Android

### Build

```bash
cd sovereign_engine
chmod +x build_android.sh
./build_android.sh
```

This will:
- Build for `arm64-v8a`, `armeabi-v7a`, and `x86_64`
- Automatically copy the `.so` files into the correct `jniLibs` structure

### Manual placement (if not using the script)

Create this folder structure in your Flutter project:

```
android/app/src/main/jniLibs/
├── arm64-v8a/
│   └── libsovereign_engine.so
├── armeabi-v7a/
│   └── libsovereign_engine.so
└── x86_64/
    └── libsovereign_engine.so
```

Flutter will automatically package these when you run:

```bash
flutter build apk --release
# or
flutter build appbundle --release
```

## 3. iOS (Recommended: Static Library)

iOS has stricter rules around dynamic libraries. We recommend using the **staticlib** output.

### Build

```bash
cd sovereign_engine
chmod +x build_ios.sh
./build_ios.sh
```

This produces:
- `ios/Libraries/libsovereign_engine-device.a`
- `ios/Libraries/libsovereign_engine-simulator.a`

### Integrate into Xcode (Flutter generated project)

1. Open `ios/Runner.xcodeproj`
2. Drag both `.a` files into your project (or add via "Add Files")
3. Go to **Build Phases → Link Binary With Libraries** and add them
4. In **Build Settings**:
   - Add to **Library Search Paths**:
     ```
     $(SRCROOT)/../Libraries
     ```
   - In **Other Linker Flags** add:
     ```
     -lsovereign_engine
     ```

### Better: Create an XCFramework (recommended)

After running `build_ios.sh`, run:

```bash
xcodebuild -create-xcframework \
  -library ios/Libraries/libsovereign_engine-device.a \
  -library ios/Libraries/libsovereign_engine-simulator.a \
  -output ios/Libraries/sovereign_engine.xcframework
```

Then add the `.xcframework` to your Xcode project and embed it.

## 4. Dart FFI Loading

No changes needed in Dart. The `DynamicLibrary.open('libsovereign_engine.so')` call works on Android.

On iOS, when using static linking, you usually do **not** call `DynamicLibrary.open`. Instead, the symbols are available directly. You can use:

```dart
final _lib = DynamicLibrary.process(); // or DynamicLibrary.executable()
```

Or keep using `DynamicLibrary.open` if you embed a dynamic framework.

## 5. Troubleshooting

- **Android**: Make sure the NDK path is set in `local.properties` or Android Studio.
- **iOS Simulator on Intel Macs**: You may also need `x86_64-apple-ios` target (legacy).
- **Missing symbols**: Ensure all `#[no_mangle] pub unsafe extern "C"` functions are present in the built library.
- **Release optimization**: The aggressive release profile in `Cargo.toml` is already applied.

## Lineage

Flamekeeper Protocol — Two Mile Solutions LLC • Dinjji Zhuu Kwaa
99733-Q Extraction Guard active
