# shoedler54
A 54-key, column-staggered, wireless split keyboard, inspired by ZSA Voyager and silakka54

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

## Changing the ergogen config

This will force you to retrace the PCB manually again.

1. Run `ergogen` either locally or at [ergogen.xyz](ergogen.xyz) on the `config.yml` file in `/ergogen`
2. `mv ./ergogen/output/pcbs/shoedler54.kicad_pcb ./kicad`
3. Open KiCad, and route the traces.
