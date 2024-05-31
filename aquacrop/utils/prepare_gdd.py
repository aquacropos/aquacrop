import numpy as np
import pandas as pd

def prepare_gdd(weather_df, sim_start, sim_end, gdd, crop, sum_fun):
    """
    function to read in GDD and crop data to return
    mean or median GDD crop growth stages based on all seasons
    in the simulation period
    Arguments:
        weather_df(DataFrame): weather data across entire simulation timespan
        
        sim_start (str): simulation start date 
        
        sim_end (str): simulation end date
        
        gdd (numeric vector): daily gdd values across entire simulation time
        
        crop (Crop object):  Crop object containing crop parameters
            
        sum_fun (str): 'mean' or 'median', select method of summarising
                        multiple years of GDD growth stages calculations
    Returns:
        crop (Crop object): updated crop object with new GDD growth stages
                            calculated based on entire simulation period
    """
    # convert str to datetime 
    sim_start_date=pd.to_datetime(sim_start)
    sim_end_date=pd.to_datetime(sim_end)

    # add gdd as column
    assert len(gdd) == len(weather_df), "The length of 'gdd' does not match the number of rows in 'weather_df', check planting date is on or after simulation start date in first year."
    weather_df['gdd']=gdd

    # Convert mm/dd formatted dates to datetime objects
    def parse_mmdd_to_datetime(mmdd_date, year):
        mm, dd = map(int, mmdd_date.split('/'))
        return pd.to_datetime(f'{year}-{mm:02d}-{dd:02d}')

    # Initialize the season counter
    season_counter = 1

    current_year = sim_start_date.year
    planting_date=crop.planting_date

    # Determine the first planting date
    first_planting_date = parse_mmdd_to_datetime(planting_date, current_year)
    if first_planting_date < sim_start_date:
        current_year += 1
        first_planting_date = parse_mmdd_to_datetime(planting_date, current_year)

    # Loop through each year to assign seasons
    while first_planting_date <= sim_end_date:
        # Determine the end date of the season (a day before the next planting date)
        next_planting_date = parse_mmdd_to_datetime(planting_date, current_year + 1)
        season_end_date = next_planting_date - pd.Timedelta(days=1)

        # If the season end date is beyond the simulation end date, truncate it
        if season_end_date > sim_end_date:
            season_end_date = sim_end_date

        # Update the 'season' column for the current season
        weather_df.loc[(weather_df['Date'] >= first_planting_date) & (weather_df['Date'] <= season_end_date), 'season'] = season_counter

        # Increment the season counter
        season_counter += 1

        # Move to the next year
        current_year += 1
        first_planting_date = next_planting_date

    # List of growth stages
    growth_stages = [
        'Emergence', 'Canopy10Pct', 'MaxRooting', 'MaxCanopy', 'CanopyDevEnd',
        'Senescence', 'Maturity', 'HIstart', 'HIend', 'YieldFormation'
    ]
    if crop.CropType == 3:
        growth_stages.extend(['FloweringEnd', 'FloweringDuration'])

    # Create dictionary of lists to store yearly GDD values for each growth stage
    # i.e. create as many lists as there are elements in 'growth_stages',
    # named with the values in 'growth_stages' in a dictionary
    gdd_lists = {f'{stage}': [] for stage in growth_stages}

    # get list of season numbers to iterate across
    seasons=weather_df['season'].unique()

    # iterate across seasons, calculating GDD to each CD growth stage
    # per season and storing in the gdd_lists lists
    for season in seasons:
        # filter to current season
        season_data = weather_df[weather_df['season']==season]

        # get cumulative GDD for current season
        gdd_cum=np.cumsum(season_data['gdd'])

        # Find GDD equivalent for each crop calendar day growth stage
        gdd_lists['Emergence'].append(gdd_cum.iloc[int(crop.EmergenceCD)])
        gdd_lists['Canopy10Pct'].append(gdd_cum.iloc[int(crop.Canopy10PctCD)])
        gdd_lists['MaxRooting'].append(gdd_cum.iloc[int(crop.MaxRootingCD)])
        gdd_lists['MaxCanopy'].append(gdd_cum.iloc[int(crop.MaxCanopyCD)])
        gdd_lists['CanopyDevEnd'].append(gdd_cum.iloc[int(crop.CanopyDevEndCD)])
        gdd_lists['Senescence'].append(gdd_cum.iloc[int(crop.SenescenceCD)])
        gdd_lists['Maturity'].append(gdd_cum.iloc[int(crop.MaturityCD)])
        gdd_lists['HIstart'].append(gdd_cum.iloc[int(crop.HIstartCD)])
        gdd_lists['HIend'].append(gdd_cum.iloc[int(crop.HIendCD)])
        gdd_lists['YieldFormation'].append(crop.HIend - crop.HIstart)

        # Duration of flowering (gdd's) - (fruit/grain crops only)
        if crop.CropType == 3:
            flowering_end=gdd_cum.iloc[int(crop.FloweringEndCD)]
            # gdd's from sowing to end of flowering
            gdd_lists['FloweringEnd'].append(flowering_end)
            # Duration of flowering (gdd's)
            gdd_lists['FloweringDuration'].append(flowering_end - crop.HIstart)

    # calculate mean/median of GDD growth stages using dictionary logic,
    # set the attribute to update the crop object
    if sum_fun == 'mean':
        for stage, values in gdd_lists.items():
            setattr(crop, stage, np.mean(values))
    elif sum_fun == 'median':
        for stage, values in gdd_lists.items():
            setattr(crop, stage, np.median(values))

    return crop