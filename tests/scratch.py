import pandas as pd
import numpy as np
import datetime

from numpy import ndarray

# TESTING FUNCTION RETURNS AND TYPES
def test(
        in1: float,
        in2: str
) -> "ndarray":
    out1=in1+5
    out2=in2+'_x'
    print(f'1: {out1}, 2: {out2}')
    return (out1,out2)

(res1,res2) = test(1,'y')
print(f'Res1: {res1}, Res2: {res2}')


# TESTING INTERPOLATION LOGIC FOR GROUNDWATER DEPTH
# base=pd.to_datetime(f'{1979}/10/01 00:00:00')
# date_list = [base+datetime.timedelta(days=x) for x in range(4)]
# test_dates2=date_list
# test_values2=[0,1,2]

# test_dates1=[f'{1979}/10/01', f'{1979}/10/04']
# test_values1=[0.5,2]

# df = pd.DataFrame([test_dates1, test_values1]).T
# df.columns = ["Date", "Depth(mm)"]

# # get date in correct format
# df.Date = pd.DatetimeIndex(df.Date)

# print(df.Date)
# add_dates=[f'{1979}/10/05', f'{1979}/10/06']
# time_span=date_list + add_dates
# print(time_span)

# if len(df) > 1:

#     z_gw = pd.Series(
#         np.nan * np.ones(len(time_span)), index=time_span
#     )

#     print(z_gw)

#     for row in range(len(df)):
#         date = df.Date.iloc[row]
#         depth = df["Depth(mm)"].iloc[row]
#         z_gw.loc[date] = depth

#     # Interpolate daily groundwater depths
#     print(f"pre-interpolation Z_GW: {z_gw.values}")
#     z_gw = z_gw.interpolate()
#     print(f"post-interpolation Z_GW: {z_gw.values}")