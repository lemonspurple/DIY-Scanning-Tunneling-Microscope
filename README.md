# Do-It-Yourself Scanning Tunneling Microscope


![Top view of the STM.](/images/header.jpg)

When [John Alexander](https://john-alexander42.github.io/simple-stm-web-page/Disk_Scanner_Exp.htm) shared his idea of using piezo elements from everyday devices like fire alarms and greeting cards as actuators for scanning tunneling microscopes, he demonstrated that nanoscopic measurement techniques can be explored by anyone curious enough.  
This repository exists to consolidate the scattered knowledge, parts and documentation as well as preserve everything needed to build your own. 

> [!NOTE]
> This project needs proofreading and the guide should be considered in-alpha.



<!-- 

######## BOM #######

-->
<details>
  <summary><strong>Bill of Materials (BOM)</strong></summary>

<br>

### **Legend:**
* `*` Cheaper in bulk / sets.
* `𐤲` Often breaks. Consider buying more.
* `▭` SMD Component.

### Controller
* LED 𐤲*
* 2x Red LED (5mm)
* 1x Red LED (3mm)
* 3x Yellow LED (3mm)
* 1x Green LED (3mm)

### Chips
* 2x TL072 by Texas Instruments 𐤲
* 1x ESP32-DevKitC (WROOM-32 by Espressif Systems)
* 3x DAC 2 Click by Mikroe
* 1x ADC 8 Click by Mikroe

### Screw Terminals (2,54mm) *
* 1x 5 Connectors
* 1x 3 Connectors
* 3x 2 Connectors

### Single-row male pin headers 𐤲*
* 1x 4 Pin
* 3x 1 Pin

### Jumper Cables 𐤲*
* 20-30 Female to Male

### Resistors 𐤲*
* 17x 3k3 Ω
* 9x 220 Ω
* 1x 1k6 Ω

### Capacitor 𐤲*
* 6x 4n7F
* 4x 100n

### Diode 𐤲
* 2x N5819

### Various
* 1x USB to TTL Converter (Has to support PL2303, Version TA not PL2303 HXA)
* 1x Micro-USB Cable for ESP32

### Tunneling Amp
* 1x ADA4637-1ARZ-ND 𐤲
* 1x Resistor RC1206JR-07100ML 𐤲 ▭
* 1x Shielding BMI-S-201-F ▭
* 2x Ceramics Capacitor 47nF 𐤲 ▭
* 2x Ceramics Capacitor 1µF 𐤲 ▭
* 2x Condensator (Polarized) 4,7 µF/35V (for example TAJ 6032 4,7/35) 𐤲 ▭

### Mechanics
* 1x KC1-T/M - Kinematic, SM1-Threaded, 30 mm-Cage-Compatible Mount for Ø1" Optic
* 1x ER2-P4 - Cage Assembly Rod, 2" Long, Ø6 mm, 4 Pack
* 1x SP05/M - 30 mm to 16 mm Cage Adapter Plate, Metric
* (You have to order through Thorlabs)

### Scannerhead
* Multiple Piezo-Disks (20mm) 𐤲𐤲
* 5 Gold Pins 𐤲
* Conductive Silver Lacquer
* Silverwire (prone to oxidation) or Platin-Iridium Wire (expensive)
* Insulated enamelled copper wire (Ø 0.1 mm)

### Batteries
* 2x 10x AA Battery Holder
* 1x 1x AA Battery Holder
* 21x AA Batteries

### PCB
* **Controller Board:** https://github.com/PeterDirnhofer/KiCad_RTM_Adapterboard_v3_0
* **Tunnelling Amp Board:** https://github.com/PeterDirnhofer/Tunnelling-Amp-20

### Probes
* Conductive Adhesive Pads
* Microscope Cover Glass Slides
* Brass Stamping Blank Round (Ø10mm, 0,4mm)*
* Blu-Ray Disk and/or
* Gold leaf and/or
* Graphene

### Vibration Insulation
* Sponges
* Rubber Mats
* Washing Machine Insulation Mats
* Bubble Wrap

### Tools
* Multimeter
* Soldering Iron + Flux + Soldering Wick + Soldering Tip Cleaning Wire
* Third Hand (With rubber covered clamps)
* Wirecutter
* Wirestripper
* Precision Screwdriver Set Repair Tool Kit
* Pliers (Probably part of the Repair Tool Kit already)
* Needle-nose pliers
* Scalpel
* Standing drill

### Glues
* Fixogum
* Two-part epoxy adhesive by J-B Weld
* Superglue
* Duct Tape

### Screws
* 4x M5 Tapping Screws
* 4x M5 Nuts
* 8x M5 Washers 𐤲
* 2x Washers to pin the piezo disk inbetween (17x30x3mm / M16)

</details>

<!-- GUIDE -->
## 1. Aquisition of Materials / Preperation
While most parts are commonly available off-the-self solutions, there still are some outliers that are worth ordering first, as their availability might vary.

### Aquisition

- **Mechanics:** Parts such as the KC1-T/M mount from Thorlabs have to be ordered directly from the manufacturer. You'll likely have to reach out to them first (via eMail or phone), as they're working mostly with institutions it seems. Keep in mind that you'll also have to drill holes using a standing drill, followed by cutting threads for the screws. You can find the tools you'd need in maker- and hackerspaces often.

- **PCB:** The board for the controllerboard and transimpedance amplifier have to be printed by a PCB manufacturer. The gerber files for that are available, but the production process usually takes ~10 business days, so it's worth planning ahead. The ones we're using were provided by the Uni Regensburg.

- **Chips:** Parts such as the TL072, DAC 2 Click by Mikroe, ADC 8 Click by Mikroe aren't super common and have to be sourced from the US in some cases. It is worth purchasing as many parts as possible in one go to save on shipping costs.

- **Conductive silver lacquer:** When you're soldering something onto the piezo disk, there is a high chance that you're going to ruin the component through the heat. Instead of soldering the pins to the disk, you can alternatively super glue them on top. To restore conductivity, silver lacquer which is often used among model makers, can be painted over the parts afterwards.

### Preperation

- **SMD Soldering:** Now would be a good time to practice SMD soldering, while you're waiting for the components to arrive. It's not a beginners endavour to undertake and it is worth watching [guides](https://www.youtube.com/watch?v=4GrQNH80oDY) (it's in German, perhaps use AI autotranslate) and probably one of the most fiddly and frustrating things I ever undertook. However, I nailed it on the second attempt, while drunk so I guess it's somewhat doable.

- **Insulation:** I have crafted a sandwich out of bubble wrap and sponges that serves as an insulation from vibration to warrant that the microscope has a chance to get good readings. While this is enough to get a result, it is highly recommended to not cheap out on this aspect. There are a bunch of [approaches](https://dberard.com/home-built-stm/vibration-isolation/) how you can tackle this. A reading can take several minutes so a noisy neighbour or passing car can ruin your result.

- **Operation System:** You need a computer to talk to the ESP32, flash it, and run the software. It's easies to do this on Windows, but also works with a bit of troubleshooting on Ubuntu/Linux. It should work on MacOSX too, but I haven't verified this.

### Things I Wished I Would Have Known Earlier

- **Redundancy:** Components that break often are marked with a 𐤲 in the bill of materials. Especially the piezo disks and transimpendance components are worth considering buying in bigger quantities, be it for the peace of mind that you don't have to nail it on the second attempt.

- **Time management:** It's doable to assemble this in a week, but it's worth taking more time into consideration. Ordering ahead of time will help avoid downtimes, however, this can also be said about the assembly of the piezo disk, as the glue/silver laquer needs to dry. It is also good to configure the ESP32 first. Although it is totally fine to configure it last, this is one of the easiest components to verify and troubleshoot quickly.

- **Multimeter verification:** Speaking about everything piezo disk, controller and transimpendance board, it is worth verifiying if all parts connect properly after soldering. Especially the gluing of the pins to the disk together with the copper wire is prone to errors and has to be checked.

- **Copper Wire:** Use a lighter to quickly melt off the insulation before you're soldering it to the pins. Just soldering it to the pins won't strip it reliably enough of its insulation to warrant connectivity. Do not purchause them in black because it will look cooler; you will barely see them.

- **LED Setup:** The LED's on the controllerboard have wrong positive/negative positionings. Or I did it the other way around. We're currently troubleshooting / verifiying this, but it won't impact the functionality. 

## 2. Piezo Schmiezo
![Top view of Piezo element.](/images/piezo.jpg)
<div align="center"><sup>(Fig 1. The piezo buzzer is being held by the third hand)</sup></div>

With an exacto knife/scalpel you're going to divide the brighter middle part of the piezo disk into quarters. After that, apply some super glue to the gold pins and attach one on each quarter. The super glue will take some time to dry. After that, remove insulation from the copper wires with a lighter and solder them to the top of the pins as seen in the picture. You can then use conductive silver laquer to restore conductivity between pin and the quarter of the piezo disk in case it has been interrupted by the glue.  
After that, solder a fifth copper wire to the outer ring for grounding.

>[!WARNING]
>Verifiy with the multimeter that the quadrants are disconnected from each other before executing any of the other steps mentioned. It is worth double checking the copper wire and silver laquer to piezo disk conductivity as well.

After the construction has dried, flip it around and prepare the Two-part epoxy adhesive. The fifth pin is glued with this to the other side of the piezo disk. **Compared to the other five connections, this pin is not allowed to be connected to the circuit and has to be isolated by the glue. Verify with your multimeter that is is not connected to the piezo disk.**
You can help with this by attaching the pin to a piece of plastic and gluing this to the piezo buzzer to guarantee that there is no electric connection between the last pin and the disk.

## 3. Controller Board
![Backside of controller.](/images/controllerboard_back.jpg)
<div align="center"><sup>(Fig 2. Multiple components are being soldered on before the wires are cut)</sup></div>

> [!IMPORTANT]
> Do not solder components such as the ESP32, ADC Click or DAC Click directly onto the board for christ's sake. Buy some female pin headers, cut them to size and solder those onto the board instead. If any part breaks (be it a chip, resistor or the PCB), you will have to face either desoldering everything or buying some pricey components again.

For reference where to place components, it is most handy to have these two charts below open on a screen nearby.

![Schematics of the controller.](/images/controller_parts.png)
<div align="center"><sup>(Fig 3. The pink plus stands for positive)</sup></div>

There really isn't much you can do wrong when placing these parts as long as you follow the instructions on the left side. For example, R309 stands for resistor number 309. It has to have 220 Ohm. C203 is a capacitor that requires 4nF (that's nanofarad).
The TL072 chips have either a little missing corner or circle to indicate how these want to be placed. It corresponds to the plus sign of U201. While this information should be universal, it is best to check with the manufacturer just in case, as all usually provide documentation.

>[!WARNING]
>You can solder on resistors and capacitors one way or another, once you've decided on an orientation, it is good practice to keep it consistent. This isn't true for diodes (D107, D108) and the chips, as these are polarized components that require a correct positive and negative connection.

> [!NOTE]
> LED's might be missplaced (positive/negative swapped). Solder them on last after verifiying if they are correct. We're working on verficiation / fixes ourselves on that matter.

![Top view of the controller.](/images/controllerboard_top.jpg)
<div align="center"><sup>(Fig 4. After soldering. Mine looks a bit uneven because I didn't add the female pin headers and soldered the components on directly.)</sup></div>


## 4. Transimpedance Amplifier
![Top view of the amplifier.](/images/transimpendance_smd.jpg)
<div align="center"><sup>(Fig 5. Top view of the first amplifier soldering attempt. The components are at the right place.)</sup></div>

If you managed the schematics of the controller you will do with these just fine. It is really worth trainign SMD soldering beforehand.
C1,C2 get a 47nF capacitor and C3,C4 1µF. C5 and C6 require 4,7 µF/35V **and are polarized, hence you have to pay attention to positive/negative.**

![Schematics of the amplifier.](/images/transpimendance_smd_schematics.jpg)
<div align="center"><sup>(Fig 6. Some components are polarized. Mind their orientation.)</sup></div>

You want to test with a multimeter if everything worked out okay before applying the Shielding (BMI-S-201-F). Writing and connector next to Shield can be ignored. One of the corners of the square has to be left exposed as it will serve as a ground connection later. You can achieve this by using by carefully bending the shield. This part is very prone to shorting out elements by accident.

## 5. Mechanics
![Thorlabs lensholder](/images/lenseholder_thorlabs.png)
<div align="center"><sup>(Fig 7. The lenseholder from Thorlabs before further work)</sup></div>

The lenseholder requires you to drill 4 holes and cut threads for the screws. This can be done easiest with a standing drill. I used a center punch tool on the positions to give the drill some extra grip and went all out with oil. The holder is made out of aluminium, which easier to cut through than it sounds, but it's worth going very slowly.
When you're cutting threads it is recommended to turn the tool 180° forwards (cutting) followed by turning it back 90° (to remove the debris from the threads). 

![Holes and disks for holding the piezo element](/images/demo_Marten_Scheuck.png)
<div align="center"><sup>(Fig 8. Progress picture by Marten Scheuck. CC BY-NC-SA 4.0)</sup></div>

>[!WARNING]
>The lenseholder has intricate mechanics inside it's plate. Turn it around (See the first picture) and be very mindful to not accidentally drill through them.

![STM Sideview](/images/stm_sideview.jpg)
<div align="center"><sup>(Fig 9. The piezo element is between both plates.)</sup></div>

You can now add the piezo disk you prepared earlier between the two big disks. The quadrants shouldn't connect with the metal, only the outer rim of the piezo element. 

> [!NOTE]
> As you can see in the image above, the bottom of the measuring element glued to the piezo element is pointing downwards. It is worth considering how you incorporate this construction into the vibration isolation, as you will be soldering new tips to the pin quite frequently.

## 6. Batteries And Cables
![Diagram of how the cables are connected](/images/diagram.jpg)
<div align="center"><sup>(Fig 11. Mockup describing how the cables are connected)</sup></div>

- A) You should have two batterypacks with 10 AA Batteries each. Connect the positive and negative cable to create one large batterypack, that effectively supplies +15V and -15V. This feels incredibly shady (and probably is), but also works.
The connected positive and negative cable splits again and connects to the ground of the controller board as shown above. Verify with a multimeter that you connect + and - to the right port.

- B) The piezo element connects with the controller board as shown above. You do not wire them directly to the piezo element, but rather through the copper wires (Fig. 1, Fig. 9) to make sure they can move easily. Z+X and Z-X have to be neighbours and the same goes for Z+Y and Z-Y.
You can also see in Fig. 9 that I soldered the porangeurple ground cable (in Fig. 11 it is purple) to the plates that hold the piezo. Verify with the multimeter that there is not shorting and that ground connects to the outer rim of the piezo element.
I have fixated the cables using Fixogum (light, nondestructive, easy to remove glue).

- C) This is the bottom side of the piezo element. The tip simply connects to the IN plate of the transimpendance amplifier.

- D) A single 1.5V battery connects to the sample and provides a negative charge. It is grounded by one exposed plate on the amplifier.

- E) USB Connector is connected to the respective ports. If the COM port shows up but you can't connect, it is very likely because you confused RX and TX. This USB cable is a requirement because it supports a baud rate for 40k+, which is needed for the monitoring of the data. The micro USB port of the ESP32 caps at around 10k and wont work.

![The brass plate holds the sample](/images/pad_connected_to_battery.jpg)
<div align="center"><sup>(Fig 12. The pad holds the sample and is glued using Fixogum to a microscope glass for added support)</sup></div>
  
  

- F) The brass plate holds the sample you're going to measure. You apply a conductive adhesive pads to it that holds the sample. You glue that also on the microscope glass plates using Fixogum for better stability. Fixogum is a super light glue that can be easily removed.

- G) The Controllerboard needs only to connect with the ADC and DAC. Only the VOUT of the ADC is connected. Lastly, connect the wires to the amplifier as described in Fig. 11.

![Measuring tips (silver) under an optical microscope](/images/stm_topview.jpg)
<div align="center"><sup>(Fig 14. By now your STM should look a bit like this. The RX/TX of the USB are wrongly connected, the single 1.5V battery is the wrong direction and the orange cable doesn't ground properly. However, this should give you a rough overview. Consult Fig 11. for proper cable connection)</sup></div>

## 7. Tips
![Measuring tips (silver) under an optical microscope](/images/tips.png)
<div align="center"><sup>(Fig 14. tips cut from silver wire under a microscope. The round results were created by creating break points with a lighter)</sup></div>
Silver wire is sufficient to produce tips (the slimmer the better), however, you have to produce a tip that is so sharp that it's only a single atom sharp at best. This is not as hard as it sounds, but also not as easy. You can try holding it under a lighter to create a breakpoint that can be easy pulled appart. Personally, I achieved the best result by practicing to cut it at a 30° angle and inspecting it under an optical microscope to warrant that it's a good result.

You don't have to hurry, but you also don't have all the time in the word, as silver, especially if there are only a single or only few atoms, will corrode very fast. You can circumvent this by using platin iridium wire, however, it's very expensive and I burned through some meters before I produced good results.

## 8. Software

### Flashing the ESP32
Download this respository. You can do that by either going to the top, clicking code and downloading and unpacking the zip, or simply by using the terminal.
```
git clone git@github.com:lemonspurple/DIY-Scanning-Tunneling-Microscope.git
```

Next download the [Flash Download Tools from Espressif](https://www.espressif.com/en/support/download/other-tools) or any other flashing tool of your preference.

Connect the ESP32 to your PC and check the device manager under Windows to see which COM port your ESP32 is using.

Under Linux the ESP32 rarely shows up as COM but rather ttyUSB or ttyACM. You can detect this by scanning for USB devices via terminal.
```
lsusb
```

If you're using the Espressif Flashing Tool you want to open the .exe and select **ESP32 as ChipType** and **WorkMode Develop**.

![Measuring tips (silver) under an optical microscope](/images/firmware.png)
<div align="center"><sup>(Fig 16. You should be greeted by a menu that looks similar to this.)</sup></div>

Select the firmware that you downloaded along with the repository, which you can find in Software > ESP32 Firmware > firmware.bin. Add a checkmark and add the 10000 to the row next to it.

>[!WARNING]
>Verifiy that you're using the correct COM port at the bottom right.

If you followed these steps correctly, you have succesfully programmed your ESP32 and can disconnect it from your computer.

### STM Software
>[!NOTE]
>You will be using an older snapshot of the software that is used to extract the data out of the microscope. we're actively working on improving it under my [fork](https://github.com/lemonspurple/STM-USB-App), or the [original repo](https://github.com/PeterDirnhofer/tkinter-usb-app). If you want to try out the newest, feel free to get the latest from there. The one included in the project is the most stable.

1. Open your terminal inside the tkinter-usb-app folder by right-clicking into the folder structure and selecting "Open terminal here" or alike.

2. Create a new virtual environment and activate it.

Windows
```
python -m venv .venv
.venv\Scripts\activate
```

Debian/Ubuntu
```
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
```

macOS
```
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the required dependencies (The virtual environment has to be activated through step 2 for this to work)

```
pip install -r requirements.txt
```

On Debian/Ubuntu
```
sudo apt install python3-pip
pip install -r requirements.txt
```

4. Run the project through Visual Studio Code
Install VSCode.
You can use any IDE you want, but this one is tested.

On Debian/Ubuntu  
If you run into the following error:
```
COM port None is not available
Try to connect /dev/ttyUSB0...
Serial connection error on port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
Could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
COM port /dev/ttyUSB0 cannot connect
```
You likely haven't added the required user permissions.

Which can be fixed by using
```
sudo usermod -aG dialout $USER
```

Open the project by typing the following line into your open terminal.
```
code .
```

It can happen that VSCode prompts you to install Python extensions for it to run properly.

5. Run the main.py
Select the main.py in the src folder and click the run button (Right pointing arrow in the top right area of the screen).

6. It can take a try or two before it opens depending on if a lock file already exists.

7. A GUI should now be open. You can try Tools > Sinus to start a quick test. If you connected everything properly, you should hear your microscope make a subtle sound. You can use the other simulations to check, if you get basic readings or errors to verify if you set up everything properly.

8. You can now add your sample to the brass plate and solder on a tip to start your first measurements. You can use the tunnel tool with the standard parameters to get a feeling for what is basic interference and when you used turned the screws of the lenseholder too much and potentially made contact with your sample.

![First measurements](/images/reading.png)
<div align="center"><sup>(Fig 17. First measurement of rough graphene.)</sup></div>

## 8. Samples and Various Notes
For samples you can use gold leafes, the conductive layer of blue rays or graphene. Graphene is a perfect first target, as you can clearly identify terraces through hexagonal patterns. You can try to get your hands on highly oriented pyrolitic graphene (HOPG), but it's tricky to aquire and expensive.
In 2010 Andre Geim and Konstantin Novoselov found out, that you can create graphene by using sticky tape on a graphe rich object (very soft graphit pencil i.E.) and by removing the flexible layer, effectively cleave of a slab of graphene. This can then be used as a target to image with your microscope. My first successful measurement took two days to achieve and utilized graphene pads that were sold as thermal paste substitute.

![First measurements](/images/reading2.png)
<div align="center"><sup>(Fig 18. Although pixelated and unsharp due to insufficient isolation from vibration, the image shows hexagonal repeating patterns that are associated with graphene.)</sup></div>

<!-- 

######## CREDITS #######

-->

<details>
<summary><strong>
9. Credits / Sources / Thanks
</strong></summary>

### Credits / Sources
* Piezo based STM design derived from John Alexander and Dan Berard
* Tunneling-Amp based on Jost Herkenhoff design
* Gerber files for Tunneling-Amp Controller-Board, Software by Peter Dirnhofer

### Additional Thanks
* Chaos Computer Club Cologne for lending me their standing drill.
* Kadse from CCCC for instructions on how to thread screws.
* Lennart Grawe for additional knowledge transfer.

</details>