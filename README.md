# WAVConverter

Pioneer XDJ-700s have occasional problems with reading Waveform files
downloaded from BandCamp etc.

This tool leverages ffmpeg to make them accessible on said players.

## Installation
1. Install ffmpeg `brew install ffmpeg`.

### For MAC
Install the latest dmg file.

### For other operating systems
- pip install tkinter
- execute the script on the command line: `python3 clean_wav.py` 

## How the application was created
Feel free to inspect the code and compile it yourself
```
# In the root of the git repo
rm -rf build dist WAVConverter.spec

pyinstaller --name "WAVConverter" --icon icon.png --windowed clean_wav.py

mkdir -p dist/dmg
cp -r dist/WAVConverter.app dist/dmg

create-dmg \
	--volname "WAVConverter" \
	--volicon icon.png \
	--window-pos 200 120 \
	--window-size 600 300 \
	--icon-size 100 \
	--icon "WAVConverter.app" 175 120 \
	--hide-extension "WAVConverter.app" \
	--app-drop-link 425 120 \
	"dist/WAVConverter.dmg" \
	"dist/dmg/"
```

## Credits
The icon is from [Jeremiah Foster](https://www.jeremiahfoster.com/).<br>
It is licensed under CC v4.0 and can be found [here](https://icon-icons.com/de/symbol/sound-Wandler/104656).
