
      6.1       : AquaCrop Version (May 2018)
  27515         : First day of simulation period - 1 May 1976       
  27598         : Last day of simulation period - 23 July 1976     
  27515         : First day of cropping period - 1 May 1976       
  27598         : Last day of cropping period - 23 July 1976     
      4         : Evaporation decline factor for stage II
      1.10      : Ke(x) Soil evaporation coefficient for fully wet and non-shaded soil surface
      5         : Threshold for green CC below which HI can no longer increase (% cover)
     70         : Starting depth of root zone expansion curve (% of Zmin)
      5.00      : Maximum allowable root zone expansion (fixed at 5 cm/day)
     -6         : Shape factor for effect water stress on root zone expansion
     20         : Required soil water content in top soil for germination (% TAW)
      1.0       : Adjustment factor for FAO-adjustment soil water depletion (p) by ETo
      3         : Number of days after which deficient aeration is fully effective
      1.00      : Exponent of senescence factor adjusting drop in photosynthetic activity of dying crop
     12         : Decrease of p(sen) once early canopy senescence is triggered (% of p(sen))
     10         : Thickness top soil (cm) in which soil water depletion has to be determined
     30         : Depth [cm] of soil profile affected by water extraction by soil evaporation
      0.30      : Considered depth (m) of soil profile for calculation of mean soil water content for CN adjustment
      1         : CN is adjusted to Antecedent Moisture Class
     20         : salt diffusion factor (capacity for salt diffusion in micro pores) [%]
    100         : salt solubility [g/liter]
     16         : shape factor for effect of soil water content gradient on capillary rise
     12.0       : Default minimum temperature (°C) if no temperature file is specified
     28.0       : Default maximum temperature (°C) if no temperature file is specified
      3         : Default method for the calculation of growing degree days
-- 1. Climate (CLI) file
   Bru76-05.CLI
   M:\AquaCropV61Nr02052018\DATA\
   1.1 Temperature (Tnx or TMP) file
   Bru76-05.TMP
   M:\AquaCropV61Nr02052018\DATA\
   1.2 Reference ET (ETo) file
   Bru76-05.ETo
   M:\AquaCropV61Nr02052018\DATA\
   1.3 Rain (PLU) file
   Bru76-05.PLU
   M:\AquaCropV61Nr02052018\DATA\
   1.4 Atmospheric CO2 concentration (CO2) file
   MaunaLoa.CO2
   M:\AquaCropV61Nr02052018\SIMUL\
-- 2. Crop (CRO) file
   PotatoGDD_test.CRO
   M:\AquaCropV61Nr02052018\DATA\
-- 3. Irrigation management (IRR) file
   Inet.IRR
   M:\AquaCropV61Nr02052018\DATA\
-- 4. Field management (MAN) file
   (None)
   (None)
-- 5. Soil profile (SOL) file
   SandyLoam.SOL
   M:\AquaCropV61Nr02052018\DATA\
-- 6. Groundwater table (GWT) file
   (None)
   (None)
-- 7. Initial conditions (SW0) file
   (None)
   (None)
-- 8. Off-season conditions (OFF) file
   (None)
   (None)
