# shoedler54
A 54-key, column-staggered, wireless split keyboard, inspired by ZSA Voyager and silakka54

Designed for Mx-spacing (19*19mm keycaps) and 1350 Choc v1 or v2 switches.

## Bill of materials

- 2 Promicro NRF52840
- 54 1N4148W SOD-123 Diodes
- 54 Kailh Low-profile 1350 Hotswap Sockets
- 54 Keyswitches, Choc v1 or v2
- 54 1u Keycaps, Choc v1 or v2
- 2 EVQPUL02K Switches ($\to$ board reset button)
- 2 SSSS811101 Switches ($\to$ power switch)
- 2 501646 3.7v, 380mAh Batteries
- 2 JST PH 2.0 THT Sockets

## Approximate cost

| What | Supplier | Comment | Price |
| --- | --- | --- | --- |
| 2 PCBs | JLCPCB | 5pcs. (min), including a hefty delivery fee to get to my location | $32 |
| 2 MCUs | AliExpress | Promicro NRF52840, 2pcs. | $8
| 54 Diodes | AliExpress | 1N4148W SOD-123, strip of 100 | ~$2 |
| 54 Kailh Low 1350 Sockets | AliExpress | pack of 100 | $8 |
| 54 Keyswitches, Choc v1/v2 | AliExpress | pack of 70 | $25 |
| 54 1u Keycaps, Choc v1/v2 | AliExpress | pack of 60 | $25 |
| 2 Reset Switches | AliExpress | EVQPUL02K, pack of 10 | $5 |
| 2 Power Switches | AliExpress | SSSS811101, pack of 20 | $3 |
| 2 Batteries | AliExpress | 501646, 380mAh | $9 |
| 2 JST PH 2.0 Sockets | AliExpress | Assortment Box | $3 |

Should result in ~ $100 per completed keyboard.

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

