# 3Doodle

## Project Overview
3Doodle is a 3D drawing tablet. Two mounted phone cameras capture images of a moving pen; we use [KLT feature tracking](https://en.wikipedia.org/wiki/Kanade%E2%80%93Lucas%E2%80%93Tomasi_feature_tracker) to estimate the pen tip position and then render the computed points in the browser.

## Requirements
Install the [Android NDK](https://developer.android.com/ndk/index.html). One way to do this is to install [Android Studio](https://developer.android.com/studio/index.html), then when you have it installed follow the instructions [here](https://developer.android.com/ndk/guides/index.html). You'll also need to make sure you have `adb` installed in the same process.

You'll also need to install [OpenCV](http://www.mobileway.net/2015/02/14/install-opencv-for-python-on-mac-os-x/).

* Python - 2.7.12
* OpenCV - 2.4.13
* Android NDK - 15.1.4119039 (includes ndk-build)
* Android SDK platform tools - 26.0.0 (includes adb)

## Setup
Run `git submodule init` and `git submodule update` in this folder to set up the minicap submodule. You'll also have to follow the setup instructions in that directory's README.

Run `virtualenv venv` in this folder to set up a Python virtualenv. Then run `source venv/bin/activate`. Then do `pip install -r requirements.txt`.
