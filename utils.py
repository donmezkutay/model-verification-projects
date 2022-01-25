import cartopy
import rioxarray
import numpy as np

# define specific constants
g= 9.80665 # m s-2 gravity
basic_crs_info_1 = cartopy.crs.LambertConformal(35.75154, 39.49263, standard_parallels=(20, 60)).proj4_params
basic_crs_info_2 = cartopy.crs.PlateCarree().proj4_params



def get_anomaly(data, climatology, anomaly_type, resample_by='mean'):
    """
    Calculate the anomaly of the data given a climatology
    data: data for which the anomaly values are to be calculated (xarray obj)
    climatology: data which will be used as a reference in anomaly calculation (xarray obj)
    anomaly_type: calculate "anomaly_type" anomaly (e.g., monthly anomaly where anomaly_type='month')
    resample_by: resampling method of the climatology data. Use mean or sum depending on the utilized data variable
    
    Returns data anomaly having the same spatial and temporal dims as 'data'
    """
    
    if resample_by == 'mean':
        data_mean = climatology.groupby(fr"time.{anomaly_type}").mean(dim='time')
    elif resample_by == 'sum':
        data_mean = climatology.groupby(fr"time.{anomaly_type}").sum(dim='time')   
    
    data_anom = data.groupby(fr"time.{anomaly_type}") - data_mean
    
    return data_anom

def check_dim_consistency(data1, data2):
    assert data1.dims == data2.dims, "data dims do not match, consider matching"
    print("data dims match, you can continue")
    
def reproject_match_rio(data, match_data, data_proj, match_data_proj):
    """
    reproject data to match the spatial structure of match data
    """
    data = data.rio.write_crs(data_proj)
    match_data = match_data.rio.write_crs(match_data_proj)
        
    return data.rio.reproject_match(match_data)

def match_latlon_dims(data):
    """
    match y to latitude; x to longitude
    """
    return data.rename({'y': 'latitude',
                        'x': 'longitude'})

def interpolate_xy(data, lon_name, lat_name, interp_size):
    
    # new lon and lat info
    new_lon = np.linspace(data[lon_name][0], data[lon_name][-1], len(data[lon_name]) * interp_size)
    new_lat = np.linspace(data[lat_name][0], data[lat_name][-1], len(data[lat_name]) * interp_size)
    
    # interpolate the data
    new_parameters = {lon_name:new_lon,
                      lat_name:new_lat}
    interp_data = data.interp(new_parameters)
    
    return interp_data