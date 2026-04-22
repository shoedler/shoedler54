# py-zmk-keymap-gen

A CLI tool that generates a visual image of a ZMK keyboard keymap.
It parses `.keymap` files, resolves key-code includes, reads the physical layout from the board's `.dtsi` files, and renders all layers stacked vertically into a single PNG.

This tool aims to work for different ZMK setups, but is very much opinionated for the current codebase - the shoedler54 split keyboard with Swiss German keycodes. Adapting it to other boards may require tweaking the key-code label maps or the DTS parsing regexes.

## Requirements

- Python 3.10+
- [Pillow](https://pypi.org/project/Pillow/) (`pip install Pillow`)
- A monospace/nerd font installed on the system (defaults to Agave Nerd Font Mono)

## Usage

```bash
python py-zmk-keymap-gen.py --shield <name> --keymap <path/to/file.keymap> [options]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--shield` | Yes | Shield name (e.g. `shoedler54`). Used to locate layout files and as the image title. |
| `--keymap` | Yes | Path to the `.keymap` file. |
| `--font` | No | Font name or path. Default: `Agave Nerd Font Mono`. |
| `-o`, `--output` | No | Output image path. Default: `<script_dir>/<shield>_keymap.png`. |
| `--printable` | No | Renders on a white background, reduces vertical padding, and scales to A4 (210×297 mm) at 300 DPI. |
| `--boards-dir` | No | Path to the `boards/` directory. Auto-detected by walking up from the keymap file. |

### Quick start (this repo)

```bash
./gen-keymap.sh
```

For a print-ready version:

```bash
./gen-keymap.sh --printable
```

## Limitations

- Key-code resolution is based on static label maps for Swiss German (`DE_*`) and standard ZMK codes. Other locale headers aren't parsed dynamically - you'd need to extend `DE_LABELS` / `ZMK_LABELS`.
- The physical layout parser expects the `key_physical_attrs` format from ZMK's `physical_layouts.dtsi`. Non-standard layout definitions won't be picked up.
- Split detection relies on finding the largest horizontal gap in key positions. Unusual layouts (e.g. unibody with a large gap elsewhere) might confuse it.
- Rotated keys (thumb clusters) are composited via temporary image rotation, which can produce minor aliasing at extreme angles.
- Only behaviors that appear in the keymap file's `behaviors {}` block or as top-level `&name { ... };` overrides are listed. Behaviors defined elsewhere in the Zephyr module tree are not resolved.
- The `#include` directives in `.keymap` files are not actually preprocessed - the tool relies on its built-in label dictionaries instead.
