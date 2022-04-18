# from aquacrop.classes import    *
# from aquacrop.core import       *
# path = get_filepath('tunis_climate.txt')
# wdf = prepare_weather(path)
# from aquacrop.crops.crop_params import crop_params

# def run_model(year1,year2,crop_config):
#     """
#     funciton to run model and return results for given set of soil moisture targets
#     """

#     maize = CropClass('custom',PlantingDate='05/01',**crop_config) # define crop
#     # maize = CropClass('Potato',PlantingDate='05/01',) # define crop
#     loam = SoilClass('SiltClayLoam') # define soil
#     init_wc = InitWCClass() # define initial soil water conditions

#     irrmngt = IrrMngtClass(IrrMethod=1,SMT=[70]*4,) # define irrigation management

#     # create and run model
#     model = AquaCropModel(f'{year1}/05/01',f'{year2}/12/31',wdf,loam,maize,
#                           IrrMngt=irrmngt,InitWC=init_wc,)
#     model.initialize()
#     model.step(till_termination=True)
#     return model.Outputs

# out = run_model(1980,1990,crop_params['PotatoLocal'])

# print(out.Final)