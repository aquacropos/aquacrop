#import os
#os.environ['DEVELOPMENT'] = 'True'
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement, CO2, FieldMngt, GroundWater
from aquacrop.utils import prepare_weather

# function to return the irrigation depth to apply on next day
def get_depth(model, taw):
    t = model._clock_struct.time_step_counter # current timestep
    # print(f'Depletion = {model._init_cond.depletion}, model TAW = {model._init_cond.taw}, target TAW: {taw}')
    # if t>0 and model._init_cond.depletion/model._init_cond.taw > taw:
    if t>0 and model._init_cond.taw < taw:
        depth=15
    else:
        depth=0

    return depth


def run_aquacrop_model(crop_name, planting_date, soil_type, weather_file, output_file, initial_water_content, irrigation_management,
                       co2_file = 'C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/MaunaLoaCO2.txt',
                       wc_type='Num', method='Depth', depth_layer=[0.3, 0.9], 
                       wc_values=[0.3, 0.15], sim_start_date='1979/10/15', sim_end_date='2001/03/31',
                       field_management = None, groundwater = None, initialise = False):
    """
    Run AquaCrop model for specified parameters and save outputs to a CSV file.
    
    Parameters:
        crop_name (str): Name of the crop.
        planting_date (str): Planting date in MM/DD format.
        soil_type (str): Soil type for the model.
        weather_file (str): Path to the weather file.
        co2_file (str): Path to the CO2 concentration file.
        output_file (str): Path to save the final stats CSV file.
        irrigation_method (int): Irrigation management method (default: 0).
        wc_type (str): Type of initial water content (default: 'Num').
        method (str): Method for initial water content (default: 'Depth').
        depth_layer (list): Depth layers for initial water content (default: [0.3, 0.9]).
        wc_values (list): Water content values for the layers (default: [0.3, 0.15]).
        sim_start_date (str): Simulation start date (default: '1979/10/15').
        sim_end_date (str): Simulation end date (default: '2001/03/31').
    """
    # Prepare weather data
    weather_df = prepare_weather(weather_file)
    
    # Define soil, crop, and initial water content
    soil = Soil(soil_type=soil_type)
    crop = Crop(crop_name, planting_date=planting_date)
    
    # Load CO2 data
    co2_data = pd.read_csv(co2_file, header=1, sep='\s+', names=["year", "ppm"])
    co2_concentration = CO2(co2_data=co2_data)
    
    if field_management:
        if groundwater:
            model = AquaCropModel(
                sim_start_time=sim_start_date,
                sim_end_time=sim_end_date,
                weather_df=weather_df,
                soil=soil,
                crop=crop,
                field_management = field_management,
                irrigation_management=irrigation_management,
                groundwater = groundwater,
                initial_water_content=initial_water_content,
                co2_concentration=co2_concentration
            )
        else:
            model = AquaCropModel(
                sim_start_time=sim_start_date,
                sim_end_time=sim_end_date,
                weather_df=weather_df,
                soil=soil,
                crop=crop,
                field_management = field_management,
                irrigation_management=irrigation_management,
                initial_water_content=initial_water_content,
                co2_concentration=co2_concentration
            )
    else:
        if groundwater:
            model = AquaCropModel(
                sim_start_time=sim_start_date,
                sim_end_time=sim_end_date,
                weather_df=weather_df,
                soil=soil,
                crop=crop,
                irrigation_management=irrigation_management,
                initial_water_content=initial_water_content,
                groundwater = groundwater,
                co2_concentration=co2_concentration
            )
        else:
            model = AquaCropModel(
                sim_start_time=sim_start_date,
                sim_end_time=sim_end_date,
                weather_df=weather_df,
                soil=soil,
                crop=crop,
                irrigation_management=irrigation_management,
                initial_water_content=initial_water_content,
                co2_concentration=co2_concentration
            )
            
    if initialise:
        model._initialize()

        while model._clock_struct.model_is_finished is False:
            # get depth to apply, RAW = 36%, p_up2 = 0.6 so TAW = 21.6, inverse is 78.4
            depth=get_depth(model,78.4)
        
            model._param_struct.IrrMngt.depth=depth
        
            model.run_model(initialize_model=False)
            
    else:
         # Run the model
         
         model.run_model(till_termination=True)   
    
    
    # Save final stats
    final_stats = model._outputs.final_stats
    final_stats.to_csv(output_file)
    print(f"Model run complete. Outputs saved to {output_file}.")


def run_all_exercises(file_prefix):
        
    # DEFINE INITIAL WATER CONTENTS
    wet_dry = InitialWaterContent(wc_type='Num',
                                  method='Depth',
                                  depth_layer=[0.3,0.9],
                                  value=[0.3,0.15])
    wet_top = InitialWaterContent('Prop','Depth',[0.5,2],['FC','WP'])
    field_capacity = InitialWaterContent(value=['FC'])
    iwc30taw = InitialWaterContent('Pct','Layer',[1],[30])
    iwc30taw_2 = InitialWaterContent('Pct','Layer',[1,2],[30,30])
    iwc75taw = InitialWaterContent('Pct','Layer',[1],[75])
    iwc75taw_2 = InitialWaterContent('Pct','Layer',[1,2],[75,75])
    iwc_wp = InitialWaterContent('Prop','Layer',[1],['WP'])
    wp = InitialWaterContent(value=['WP'])
    
    # DEFINE IRRIGATION MANAGEMENT
    rainfed = IrrigationManagement(irrigation_method=0)
    net_irr_7 = IrrigationManagement(irrigation_method=4,NetIrrSMT=80.5, MaxIrr=50)
    net_irr_8 = IrrigationManagement(irrigation_method=4, NetIrrSMT=90.5)
    net_irr_9 = IrrigationManagement(irrigation_method=4,NetIrrSMT=79, MaxIrr=40)
    
    # deficit irri scheduling
    all_1_decs=pd.date_range('1979/12/01', '2001/12/01',freq='12MS')
    dates=[]
    for each_start in all_1_decs:
        app1=each_start
        app2=each_start+pd.Timedelta(31,'d')
        app3=each_start+pd.Timedelta(61,'d')
        dates.extend([app1,app2,app3])
    n_years=len(all_1_decs)
    depths=[30,40,40]*n_years
    schedule=pd.DataFrame([dates,depths]).T # create pandas DataFrame
    schedule.columns=['Date','Depth'] # name columns    
    deficit_irr = IrrigationManagement(irrigation_method=3, Schedule=schedule, MaxIrr = 50)
    
    schedule=IrrigationManagement(irrigation_method=5,)
    
    
    # DEFINE FIELD MANAGEMENT
    bunds20 = FieldMngt(bunds=True, z_bund=0.20)
    
    # DEFINE GROUNDWATER
    groundwater_1m = GroundWater('Y','Constant',dates=[f'{2000}/09/01'], values=[1])
    groundwater_2m = GroundWater('Y','Constant',dates=[f'{2000}/09/01'], values=[2])
    
    # EXERCISE 7.1 - WheatGDD with Tunis Local Soil
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='10/15',
        soil_type='ac_TunisLocal',
        initial_water_content = wet_dry,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_1_localSoil.csv'
    )
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='10/15',
        soil_type='SandyLoam',
        initial_water_content = wet_dry,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_1_sandyLoam.csv'
    )
    
    # EXERCISE 7.3 - field capacity
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='10/15',
        soil_type='SandyLoam',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_3_fc.csv'
    )
    
    # EXERCISE 7.3 - 30% TAW
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='10/15',
        soil_type='SandyLoam',
        initial_water_content = iwc30taw,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_3_taw30.csv'
    )
    
    # EXERCISE 7.3 - 75% TAW
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='10/15',
        soil_type='SandyLoam',
        initial_water_content = iwc75taw,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_3_taw75.csv'
    )
    
    # EXERCISE 7.3 - wilting point
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='10/15',
        soil_type='SandyLoam',
        initial_water_content = iwc_wp,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_3_wp.csv'
    )
    
    # EXERCISE 7.6 - net irri
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='12/01',
        sim_start_date = '1979/12/01',
        sim_end_date = '2002/05/31',
        soil_type='SandyLoam',
        initial_water_content = wp,
        irrigation_management = net_irr_7,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_6.csv'
    )
    
    # EXERCISE 7.7 - deficit irri
    run_aquacrop_model(
        crop_name='WheatGDD',
        planting_date='12/01',
        sim_start_date = '1979/12/01',
        sim_end_date = '2002/05/25',
        soil_type='SandyLoam',
        initial_water_content = wp,
        irrigation_management = deficit_irr,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_7_7.csv'
    )


    # EXERCISE 8.2 - nobunds
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='08/01',
        sim_start_date = '2000/08/01',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_2_nobunds.csv'
    )
    
    # EXERCISE 8.2 - bunds
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='08/01',
        sim_start_date = '2000/08/01',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        field_management = bunds20,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_2_bunds.csv'
    )
    
    # EXERCISE 8.2 - earlyplant
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='07/15',
        sim_start_date = '2000/07/15',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        field_management = bunds20,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_2_earlyplant.csv'
    )


    # EXERCISE 8.3 - fc
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='08/01',
        sim_start_date = '2000/08/01',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        field_management = bunds20,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_3_fc.csv'
    )
    
    # EXERCISE 8.3 - 30%taw
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='08/01',
        sim_start_date = '2000/08/01',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = iwc30taw_2,
        irrigation_management = rainfed,
        field_management = bunds20,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_3_30taw.csv'
    )
    
    # EXERCISE 8.3 - 75%taw
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='08/01',
        sim_start_date = '2000/08/01',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = iwc75taw_2,
        irrigation_management = rainfed,
        field_management = bunds20,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_3_75taw.csv'
    )
    
    # EXERCISE 8.3 - wet_top
    run_aquacrop_model(
        crop_name='localpaddy',
        planting_date='08/01',
        sim_start_date = '2000/08/01',
        sim_end_date = '2010/12/31',
        soil_type='Paddy',
        initial_water_content = wet_top,
        irrigation_management = rainfed,
        field_management = bunds20,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_3_wetTop.csv'
    )
    
    # EXERCISE 8.7 - 1m gw
    run_aquacrop_model(
        crop_name='HydWheatGDD',
        planting_date='11/01',
        sim_start_date = '2000/09/01',
        sim_end_date = '2010/12/31',
        soil_type='ClayLoam',
        initial_water_content = field_capacity,
        irrigation_management = net_irr_8,
        groundwater=groundwater_1m,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_4_1m.csv'
    )
    
    # EXERCISE 8.7 - 2m gw
    run_aquacrop_model(
        crop_name='HydWheatGDD',
        planting_date='11/01',
        sim_start_date = '2000/09/01',
        sim_end_date = '2010/12/31',
        soil_type='ClayLoam',
        initial_water_content = field_capacity,
        irrigation_management = net_irr_8,
        groundwater=groundwater_2m,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/hyderabad_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_8_4_2m.csv'
    )
    
    # EXERCISE 9.1 - potato in brussels
    run_aquacrop_model(
        crop_name='PotatoLocalGDD',
        planting_date='04/25',
        sim_start_date = '1976/04/25',
        sim_end_date = '2005/12/31',
        soil_type='Loam',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/brussels_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_9_1.csv'
    )
    
    # EXERCISE 9.4 - net irri
    run_aquacrop_model(
        crop_name='PotatoLocalGDD',
        planting_date='04/25',
        sim_start_date = '1976/04/25',
        sim_end_date = '2005/12/31',
        soil_type='Loam',
        initial_water_content = field_capacity,
        irrigation_management = net_irr_9,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/brussels_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_9_4.csv'
    )
    
    
    # EXERCISE 9.5 - irri schedules
    run_aquacrop_model(
        crop_name='PotatoLocalGDD',
        planting_date='04/25',
        sim_start_date = '1976/04/25',
        sim_end_date = '2005/12/31',
        soil_type='LoamySand',
        initial_water_content = field_capacity,
        irrigation_management = schedule,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/brussels_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_9_5.csv',
        initialise = True
    )
    
        
    # EXERCISE 9.6 - CC impact historical
    run_aquacrop_model(
        crop_name='PotatoLocalGDD',
        planting_date='04/25',
        sim_start_date = '1976/04/25',
        sim_end_date = '2005/12/31',
        soil_type='Loam',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/brussels_climate.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_9_6_hist.csv',
        initialise = True
    )
    
    # EXERCISE 9.6 - CC impact future
    run_aquacrop_model(
        crop_name='PotatoLocalGDD',
        planting_date='04/25',
        sim_start_date = '2041/04/25',
        sim_end_date = '2070/12/31',
        soil_type='Loam',
        initial_water_content = field_capacity,
        irrigation_management = rainfed,
        weather_file='C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/brussels_future.txt',
        output_file=f'../AquaCrop docs/AOT Compilation Removal/{file_prefix}_9_6_future.csv',
        initialise = True
    )
    

run_all_exercises('rm_numba')

#sns.set_theme(style="whitegrid")  # Set a clean theme for the plots

# List of columns to plot
#columns = ['canopy_cover', 'biomass', 'harvest_index', 'z_root']

# Create separate plots for each column
# for col in columns:
#     plt.figure(figsize=(6, 4))  # Create a new figure
#     sns.lineplot(data=crop_growth, x='dap', y=col, color='blue')
#     plt.xlabel('Days After Planting (dap)')
#     plt.ylabel(col.replace('_', ' ').title())  # Format column name for the label
#     plt.title(f'{col.replace("_", " ").title()} vs. DAP')
#     plt.tight_layout()
#     plt.show()  # Show the plot

