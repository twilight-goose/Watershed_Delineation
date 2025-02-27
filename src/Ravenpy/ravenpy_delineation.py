#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
# Import the necessary libraries to format, send, and parse our returned results
import os
import birdy
import geopandas
import pandas as pd

#-------------------------------------------------------------------------------
# Delineate Watershed
#-------------------------------------------------------------------------------
def delineate(basins='', output=''):
    """
    Description
    -----------
    delineate(basins, output) delineates watersheds

    Input           Format          Description
    -----           ------          -----------
    basins          str             The path the basins/pourpoints csv
    output_dir      str             The path to the output folder

    Output          Format          Description
    ------          ------          -----------
    watersheds      Shapefiles      The watershed shapefiles delineated

    Returns
    -------
    None

    """
    # Create WPS instances# Set environment variable WPS_URL to "http://localhost:9099" to run on the default local server
    pavics_url = "https://pavics.ouranos.ca"
    raven_url = os.environ.get("WPS_URL", f"{pavics_url}/twitcher/ows/proxy/raven/wps")
    raven = birdy.WPSClient(raven_url)

    # Specify pour point
    print("Specify pour point")
    lats = basins['lat'].tolist()
    lons = basins['lon'].tolist()
    ids = basins['id'].tolist()

    # Delineate each pour point
    for index in range(0, len(lats)):
        x = lons[index]
        y = lats[index]
        id = ids[index]
        print("lon: {} lat: {} id: {}".format(x, y, id))
        basin_dir = "{}/{}".format(output, id)
        if not os.path.isdir(basin_dir):
            os.mkdir(basin_dir)

        user_lonlat = [x, y]

        # Get the shape of the watershed contributing to flow at the selected location.
        resp = raven.hydrobasins_select(location=str(user_lonlat),
                                        aggregate_upstream=True)

        # Extract the URL of the resulting GeoJSON feature
        feat = resp.get(asobj=False).feature
        print(
            "This is the geoJSON file that can be used as the watershed contour in other toolboxes:"
        )
        print("")
        print(feat)
        print("")

        # Print the properties from the extracted watershed
        gdf = geopandas.read_file(feat)

        # Converting geojson to shapefile
        if not os.path.isdir("{}}/{}".format(output, id)):
            os.mkdir("{}}/{}".format(output, id))
        gdf.to_file("{}/{}/{}.shp".format(output, id, id))

    print("Delineation complete!")

#-------------------------------------------------------------------------------
# Run Program
#-------------------------------------------------------------------------------
def main():
    input = "data"
    output = "output"
    if not os.path.isdir(output):
        os.mkdir(output)

    basins = pd.read_csv("{}/basins.csv".format(input))  # path to csv of pour points
    delineate(basins, output)

if __name__ == "__main__":
    main()