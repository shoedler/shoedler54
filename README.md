# shoedler54
A 54-key, column-staggered, ortholinear, wireless split keyboard, inspired by ZSA Voyager and silakka54.
Designed for Mx-spacing (19*19mm keycaps) and 1350 Choc v1 or v2 switches.

> [!WARNING]
> This is still in development - DO NOT BUILD THIS YET!

## Why?

This project came to life as I wanted to get up to speed with [ergogen.xyz](ergogen.xyz). The main goal of was to build a keyboard using solely the declarative ergogen paradigm - including making a case. As such, the only thing that was done outside of ergogen was to route the PCB and flip one case half in the slicer. That, as well as configuring the firmware (it'd be a nice extension to ergogen to generate the `.dtsi` file for ZMK automatically, but alas, that's not supported - yet).
Other things I've aimed for:
- Must be cheap, < $100 for a complete keyboard.
- Must be low profile, comparable to the ZSA Voyager.

## Bill of materials

For one complete board - e.g. two halves - you'll need:

- 2 Promicro NRF52840
- 54 1N4148W SOD-123 Diodes
- 54 Kailh Low-profile 1350 Hotswap Sockets
- 54 Keyswitches, Choc v1 or v2
- 54 1u Keycaps, Choc v1 or v2 (I suggest Taihao THTs)
- 2 EVQPUL02K Switches ($\to$ board reset button)
- 2 SSSS811101 Switches ($\to$ power switch)
- 2 701535 3.7v, 350mAh Batteries
- 2 JST PH 2.0 THT Sockets

For the case you'll need:

- Obviously, the printed out case files. The key plate can be printed twice as it is reversible. The case must be mirrored in your slicer of choice for the right half. For convenience, I've added *.3mf files which includes a mirrored version of the plate and the case. The case also has the fuzzy skin applied.
- 10x M2x5 (or 6)mm flathead screws
- 10x M2x3mm Heat set inserts
- Optionally some painters tape.

## Approximate cost

| What | Supplier | Comment | Price |
| --- | --- | --- | --- |
| 2 PCBs | JLCPCB | 5pcs. (min), including a hefty delivery fee to get to my location, $32 | ~$13 |
| 2 MCUs | AliExpress | Promicro NRF52840 | ~$4 |
| 54 Diodes | AliExpress | 1N4148W SOD-123 | ~$1 |
| 54 Kailh Low 1350 Sockets | AliExpress | Hotswap | $4 |
| 54 Keyswitches, Choc v1/v2 | AliExpress | pack of 70 | $25 |
| 54 1u Keycaps, Choc v1/v2 | AliExpress | pack of 60 | $15 |
| 2 Reset Switches | AliExpress | EVQPUL02K | ~$1 |
| 2 Power Switches | AliExpress | SSSS811101 | $1 |
| 2 Batteries | AliExpress | 70153, 350mAh | $8 |
| 2 JST PH 2.0 Sockets | AliExpress | ~$1 |
> Prices as of january, 2026

Should result in ~$75 per completed keyboard. This does not include the case hardware and printed case files, but it's all you need to get a working keyboard. Also, the prices listed are adjusted to the amount of parts required.

> [!NOTE]
> You'd want to buy some parts in "bulk", like a strip of 100 diodes. Since you likely also have a minimum order quantity for the PCBs, it might make sense to buy two more MCUs and maybe some old keyswitches and caps to get another full keyboard out of the rest of the parts and still have one PCB for soldering mistakes left ;)

Another thing, there's a great deal of 3d printable keycaps, which could lower the cost of building even more.

## Build guide

### PCB manufacturing

> PCB related files are located in the `kicad` directory.

Assuming you have ordered the parts and don't want to route the PCB yourself, there's premade gerber archive located at `kicad/gerber.zip` which you can use. I've used JLCPCB, default settings (1.6mm two layer PCB) and with the black solder mask.

### Printing the case

> Case files are located in the `stl` directory.

I used a Babulab A1 mini and default slicer settings (Bambustudio). Everything was printed in their PLA Matte.

- You'll want to print the keyplate twice - don't forget to flip it once to get the same finish on both sides (I like the side that sits on the buildplate to face outwards for a nice contrast).
- As for the case, you'll see that there is only the `_left` half stl file available - you'll need to mirror it in your slicer to print the right side. I suggest using the fuzzy skin setting (`Others > Special mode > Fuzzy skin`, use "Contour").

### Soldering

Since the PCB is reversible it can get confusing quick. All of the components **except the ProMicro and the JST connector** are soldered to the backside of each half.

1. Solder diodes, hotswap sockets, reset- and powerswitches on the backside of each half.
2. Direct-solder the ProMicro to the frontside of the PCB, along with the JST connector. (Pin Sockets are also an option for the mcu, if you want - it just makes the keyboard a bit thicker)

> [!WARNING]
> Before you continue it's a good idea to verify that there's no short between the JSTs +/- terminal as well as the ProMicros VCC and GND.

I suggest to load the firmware and check that everything works before assembly.

### Loading the ZMK firmware

> Firmware related files consist of: config/, boards/, zephyr/ directories, as well as the build.yml file and the GitHub Actions workflow in .github/workflows.build.yml

Get the latest firmware from https://github.com/shoelder/shoedler54/actions, select the latest run and scroll down to Artifacts - you'll be able to download the zip archive from there.

For each half:

1. Plug in the half to your device using a USB cable.
2. Press the reset button twice within 500ms - on my versions of the ProMicro, their red LED breaths gently once you've entered bootloader mode.
3. You'll see a `NICENANO` appear in your device tree. Simply drag and drop the **correct** firmware for the half your working on onto the mcu - it should eject itself automatically once the firmware is flashed.

### Assembly

1. Prep the cases by installing the heat set inserts and your optional sheets of foam.
2. At this point you might want to [tape-mod](https://typingdonewell.com/blog/keyboard-pcb-tape-mod-what-is-it-and-is-it-worth-it/) the PCB backsides.
3. Assemble both halves.

## Modifying the ergogen config

The whole point of using ergogen, is to easily adapt the PCB to your liking. So give it a go!
Modifying the config will force you to reroute the PCB again. Though fear not - using [Freerouting](www.freerouting.app) this literally takes a minute to do (including adding freerouting to KiCad), provided you have KiCad >=8 and JRE >= 17 for Freerouting already installed.

> [!NOTE]
> To add the Freerouting KiCad integration, just follow [this](https://github.com/freerouting/freerouting/blob/master/docs/integrations.md) official guide.

1. Paste `config.yml` located in `/ergogen` into [ergogen.xyz](ergogen.xyz) and download the `shoedler54.kicad_pcb` file.
2. Copy (and overwrite) `shoedler54.kicad_pcb` to the `kicad` directory of this repository *(this part is only required if you intend to keep the source of this repository up to date - e.g. if you forked this)*
3. Open the PCB in KiCad (Standalone PCB editor suffices) and click on `Tools > External Plugins > Freerouting`
4. Let it rip. In my experience, the defaults of Freerouting suffice.

> [!IMPORTANT]
> Back in KiCad, run the DRC in `Inspect > Design Rule Checker`. I usually right click `> Ignore all 'Footprint not found in libraries' violations` to ignore missing ceoloide footprint warnings. This might leave you with some warnings which you need to manually resolve. For example, i usually get "Track has unconnected end", which is easily resolved by deleting the stub.

5. `File > Plot... > Generate Drill Files`, name the folder "gerber", then press `Generate` and close that popup. Press `Plot` back in the plot dialog. Done!

## References

- Flatfootfox' detailed design guide: https://flatfootfox.com/ergogen-part1-units-points/
- nickcoutsos Keymap-editor: https://nickcoutsos.github.io/keymap-editor/
- nickcoutsos Keymap-layout-tools: https://nickcoutsos.github.io/keymap-layout-tools/
- Joel Spadins zmk-locale-generator for the de-swiss keycode header: https://github.com/joelspadin/zmk-locale-generator
- ZMK guide on how to add a new shield: https://zmk.dev/docs/development/hardware-integration/new-shield
