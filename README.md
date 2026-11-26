# CS2InGame

Converts GTA Vice City **cutscene** player models (`csplayN.dff`) into **in-game** ped models (`playN.dff`).

Useful for outfit mods: build the cutscene model once and get the matching in-game model automatically.

## What it does

- Removes the cutscene-only bones: face (brow, lid, jaw, lip, eye, cheek, corner), `HeadNub`, `Finger01`, `ToeNub`
- Moves the skin weights of every removed bone onto its nearest kept parent bone (max 4 weights per vertex, renormalised)
- Renumbers the toe bones to the in-game IDs (2000 / 2001)
- Rebuilds the HAnim hierarchy and the frame list

Geometry, materials and textures are left untouched.

## Requirements

Python 3 (standard library only, nothing to install with pip).

## Usage

### Windows

1. Put your `csplayN.dff` files into `Import` (subfolders are fine).
2. Run `run.bat`.
3. Take the `playN.dff` files from `Export` (same folder structure as `Import`).

### Android

Works with **Pydroid 3** or **Termux**.

- **Pydroid 3**: copy this folder to your phone storage, put the files into `Import`, open `run.py` in Pydroid 3 and press Run.
- **Termux**:
  ```
  pkg install python
  termux-setup-storage
  cd ~/storage/downloads/CS2InGame
  python run.py
  ```

### Command line

```
python cs2ingame.py csplay13.dff play13.dff
python cs2ingame.py <folder>        # converts every cs*.dff in <folder> into <folder>/Out
```

Output names: `csplay13.dff` becomes `play13.dff`. Files that do not start with `cs` get the prefix `ingame_`.

## Notes

- Test the converted models in game before you release them.
- No game files are included. Use models you made yourself or have the rights to.

## Disclaimer

This is a fan-made modding tool. It is not affiliated with or endorsed by Rockstar Games or Take-Two Interactive.
Grand Theft Auto and Vice City are trademarks of Take-Two Interactive.

## License

MIT, see [LICENSE](LICENSE).
