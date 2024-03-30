import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry.base import BaseGeometry
from shapely import wkt

def read_shp(file_path):
    """
    The function loads a shapefile into a GeoDataFrame using GeoPandas, then filters the GeoDataFrame
    to include only those entries that belong to Mérida, identified by their 'CVEGEO' field starting
    with '310500001'.
    
    Parameters:
    - file_path (str): The path to the shapefile (.shp) that contains the AGEBs data for 2010.
    
    Returns:
    - GeoDataFrame: A GeoDataFrame containing the filtered AGEBs for Merida. Each row in the GeoDataFrame
      corresponds to a specific AGEB within Merida.
    
    Note:
    - This function is tailored to work with a specific dataset structure, particularly the use of 'CVEGEO'
      for identifying geographical regions. Modifications may be necessary to adapt to other datasets or different
      identifiers.
    """
    gpd_df = gpd.read_file(file_path)
    # Filter the AGEBs of Merida with identifier 310500001
    agebs_merida = gpd_df[gpd_df.CVEGEO.str.startswith('310500001')]
    return agebs_merida

def plot_gdf(gdf):
    """
    Plots a GeoDataFrame containing geometry information.
    
    This function checks if the 'geometry' column of the given GeoDataFrame contains Shapely geometry objects.
    If the geometries are already in the correct format, it plots them directly. If not, it attempts to convert
    them into Shapely geometry objects using WKT (Well-Known Text) before plotting.
    
    Parameters:
    - gdf (GeoDataFrame): A GeoDataFrame containing a 'geometry' column with geographic data.
    
    Returns:
    - None: The function plots the geometries and does not return any value.
    """
    # Check if the 'geometry' column contains Shapely geometry objects
    if isinstance(gdf.geometry.iloc[0], BaseGeometry):
        # Plot directly since it's already Shapely geometry objects
        gdf.plot()
    else:
        # Attempt to convert from WKT to Shapely geometry objects if necessary
        gdf['geometry'] = gdf['geometry'].apply(wkt.loads)
        gdf.plot()

    # Show the plot
    plt.show()

def remain(gdf_2010, gdf_2020):
    """
    Identifies and returns a GeoDataFrame containing AGEBs from 2010 that are still present 
    in 2020 by comparing their 'CVEGEO' identifiers.

    This function compares the 'CVEGEO' identifiers, which are unique to each AGEB, between
    two GeoDataFrames corresponding to the years 2010 and 2020. It then filters the 2010
    GeoDataFrame to include only those AGEBs whose identifiers are found in both years, 
    effectively identifying the AGEBs that have remained over the decade.

    Parameters:
    - gdf_2010 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2010, 
      including a 'CVEGEO' column with unique identifiers for each AGEB.
    - gdf_2020 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2020, 
      including a 'CVEGEO' column with unique identifiers for each AGEB.

    Returns:
    - GeoDataFrame: A GeoDataFrame filtered from the 2010 input, containing only the AGEBs 
      that are still present in 2020 according to their 'CVEGEO' identifiers.

    Note:
    - This function assumes that the 'CVEGEO' column is present and correctly formatted 
      in both GeoDataFrames. It also assumes that the geometries in the input GeoDataFrames
      are valid and that the 'CVEGEO' identifiers are consistent across the datasets.
    """
    # Convert the 'CVEGEO' columns from both GeoDataFrames to sets
    cvegeo_2010 = set(gdf_2010['CVEGEO'])
    cvegeo_2020 = set(gdf_2020['CVEGEO'])

    # Find the intersection of the two sets to get the common AGEBs
    common_agebs = cvegeo_2010.intersection(cvegeo_2020)

    # Filter the 2010 GeoDataFrame to only include the common AGEBs
    common_agebs_gdf = gdf_2010[gdf_2010['CVEGEO'].isin(common_agebs)]
    return common_agebs_gdf

import geopandas as gpd
import matplotlib.pyplot as plt

def plot_remaining_agebs(gdf_2010, gdf_2020):
    """
    Plots the AGEBs from 2010 that are still present in 2020. The AGEBs from 2010 and 2020
    are displayed as a gray background layer, and the remaining AGEBs common to both
    2010 and 2020 are overlaid in blue.

    Parameters:
    - gdf_2010 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2010.
    - gdf_2020 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2020.

    Returns:
    - None: The function plots the geometries and does not return any value.
    """
    # Ensure both GeoDataFrames are in the same CRS
    if gdf_2010.crs != gdf_2020.crs:
        gdf_2020 = gdf_2020.to_crs(gdf_2010.crs)

    # Combine the two GeoDataFrames to create a layer representing all unique AGEBs
    # Dissolve all geometries into a single geometry for each GeoDataFrame before combining
    combined_gdf = pd.concat([gdf_2010, gdf_2020]).dissolve(by='CVEGEO', as_index=False)

    # Identify the remaining AGEBs from 2010 that are present in 2020
    remaining_agebs = remain(gdf_2010, gdf_2020)

    fig, ax = plt.subplots(figsize=(10, 10))  # Create figure and axes

    # Plot the combined layer of AGEBs from both years in gray
    combined_gdf.plot(ax=ax, color='gray', edgecolor='k', alpha=0.5)

    # Overlay the remaining AGEBs from 2010 in blue
    remaining_agebs.plot(ax=ax, color='purple', edgecolor='k', alpha=1)

    # Create custom legend
    legend_labels = [
        mpatches.Patch(color='gray', label='Combined AGEBs 2010 & 2020'),
        mpatches.Patch(color='purple', label='Remaining AGEBs')
    ]
    ax.legend(handles=legend_labels)

    ax.set_title('Combined AGEBs from 2010 and 2020 with Remaining AGEBs Highlighted')

    plt.show()

def new(gdf_2010, gdf_2020):
    """
    Identifies new AGEBs in 2020 that were not present in the 2010 dataset and returns
    a GeoDataFrame containing these new AGEBs. The identification is based on the comparison
    of 'CVEGEO' identifiers between the two datasets.

    Parameters:
    - gdf_2010 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2010, 
      including a 'CVEGEO' column with unique identifiers for each AGEB.
    - gdf_2020 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2020, 
      including a 'CVEGEO' column with unique identifiers for each AGEB.

    Returns:
    - GeoDataFrame: A GeoDataFrame containing only the new AGEBs introduced in 2020.

    Note:
    - This function assumes that the 'CVEGEO' column is present and correctly formatted 
      in both GeoDataFrames. It also assumes that the geometries in the input GeoDataFrames
      are valid and that the 'CVEGEO' identifiers are consistent across the datasets.
    """
    # Convert the 'CVEGEO' columns to sets for efficient comparison
    cvegeo_2010 = set(gdf_2010['CVEGEO'])
    cvegeo_2020 = set(gdf_2020['CVEGEO'])

    # Find identifiers in 2020 that were not present in 2010
    new_agebs_identifiers = cvegeo_2020 - cvegeo_2010

    # Filter the 2020 GeoDataFrame to include only new AGEBs
    new_agebs_gdf = gdf_2020[gdf_2020['CVEGEO'].isin(new_agebs_identifiers)]

    return new_agebs_gdf

def plot_new_agebs(gdf_2010, gdf_2020):
    """
    Plots the AGEBs from 2020 that are new and not present in 2010. The AGEBs from 
    2010 are displayed as a gray background layer, and the new AGEBs introduced in 
    2020 are overlaid in red.

    Parameters:
    - gdf_2010 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2010.
    - gdf_2020 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2020.

    Returns:
    - None: The function plots the geometries and does not return any value.
    """
    new_agebs = new(gdf_2010, gdf_2020)  # Identify the new AGEBs introduced in 2020

    fig, ax = plt.subplots(figsize=(10, 10))  # Create figure and axes

    # Plot the combined layer of AGEBs from both years in gray
    gdf_2010.plot(ax=ax, color='gray', edgecolor='k', alpha=0.5)

    # Overlay the new AGEBs introduced in 2020 in red
    new_agebs.plot(ax=ax, color='red', edgecolor='k', alpha=1)

    # Create custom legend
    legend_labels = [
        mpatches.Patch(color='gray', label='AGEBs 2010'),
        mpatches.Patch(color='red', label='New AGEBs 2020')
    ]
    ax.legend(handles=legend_labels)

    ax.set_title('AGEBs from 2010 with New AGEBs from 2020 Highlighted')

    plt.show()

def dissapear(gdf_2010, gdf_2020):
    """
    Identifies AGEBs that were present in 2010 but disappeared by 2020 by comparing
    the 'CVEGEO' identifiers. It returns a GeoDataFrame of these disappeared AGEBs
    and visualizes them.

    Parameters:
    - gdf_2010 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2010, 
      including a 'CVEGEO' column with unique identifiers for each AGEB.
    - gdf_2020 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2020, 
      including a 'CVEGEO' column with unique identifiers for each AGEB.

    Returns:
    - GeoDataFrame: A GeoDataFrame containing the AGEBs that disappeared by 2020.

    Note:
    - This function assumes that the 'CVEGEO' column is present and correctly formatted 
      in both GeoDataFrames. It also assumes that the geometries in the input GeoDataFrames
      are valid and that the 'CVEGEO' identifiers are consistent across the datasets.
    """
    # Convert the 'CVEGEO' columns from both GeoDataFrames to sets for efficient comparison
    cvegeo_2010 = set(gdf_2010['CVEGEO'])
    cvegeo_2020 = set(gdf_2020['CVEGEO'])

    # Find identifiers in 2010 that are not present in 2020
    disappeared_agebs_identifiers = cvegeo_2010 - cvegeo_2020

    # Filter the 2010 GeoDataFrame to include only the disappeared AGEBs
    disappeared_agebs_gdf = gdf_2010[gdf_2010['CVEGEO'].isin(disappeared_agebs_identifiers)]

    return disappeared_agebs_gdf

def plot_disappeared_agebs(gdf_2010, gdf_2020):
    """
    Plots the AGEBs from 2010 that disappeared by 2020. The AGEBs from 2020 are displayed
    as a gray background layer, and the AGEBs that disappeared by 2020 are overlaid in blue.

    Parameters:
    - gdf_2010 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2010.
    - gdf_2020 (GeoDataFrame): A GeoDataFrame containing the AGEBs for the year 2020.

    Returns:
    - None: The function plots the geometries and does not return any value.
    """
    disappeared_agebs = dissapear(gdf_2010, gdf_2020)  # Identify the AGEBs that disappeared by 2020

    fig, ax = plt.subplots(figsize=(10, 10))  # Create figure and axes

    # Plot the combined layer of AGEBs from both years in gray
    gdf_2020.plot(ax=ax, color='gray', edgecolor='k', alpha=0.5)

    # Overlay the AGEBs that disappeared by 2020 in green
    disappeared_agebs.plot(ax=ax, color='blue', edgecolor='k', alpha=1)

    # Create custom legend
    legend_labels = [
        mpatches.Patch(color='gray', label='AGEBs 2020'),
        mpatches.Patch(color='blue', label='Disappeared AGEBs')
    ]
    ax.legend(handles=legend_labels)

    ax.set_title('AGEBs from 2020 with Disappeared AGEBs Highlighted')

    plt.show()

def comparison_plot(gdf_2010, gdf_2020):
    """
    Plots and compares the AGEBs from 2010 and 2020 GeoDataFrames on the same map for visual comparison.

    The function plots the 2010 AGEBs in blue and the 2020 AGEBs in red. Areas where AGEBs overlap will
    appear in a blended color, indicating no change. Areas in red or blue only indicate AGEBs that are new in 2020
    or were only present in 2010, respectively.
    
    Parameters:
    - gdf_2010 (GeoDataFrame): GeoDataFrame containing AGEBs for the year 2010.
    - gdf_2020 (GeoDataFrame): GeoDataFrame containing AGEBs for the year 2020.

    Returns:
    - None: The function plots the geometries and does not return any value.
    """
    fig, ax = plt.subplots(figsize=(10, 10))  # Create a figure and axes object

    # Plot 2010 AGEBs
    gdf_2010.plot(ax=ax, color='blue', edgecolor='k', alpha=0.5)

    # Overlay 2020 AGEBs
    gdf_2020.plot(ax=ax, color='red', edgecolor='k', alpha=0.5)

    # Create custom legend
    legend_labels = [
        mpatches.Patch(color='blue', label='AGEBs 2010'),
        mpatches.Patch(color='red', label='AGEBs 2020')
    ]
    ax.legend(handles=legend_labels)

    ax.set_title('Comparison of AGEBs between 2010 and 2020')
    
    plt.show()