import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import requests
from io import StringIO
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import matplotlib
from matplotlib.cm import ScalarMappable, get_cmap
from matplotlib.colors import hex2color, LinearSegmentedColormap, Normalize
import matplotlib.ticker as ticker
from PIL import Image


def create_custom_colormap(negative_colors_hex, n_bins=10):
    # Convert hex colors to RGB
    negative_colors_rgb = [hex2color(color) for color in negative_colors_hex]

    # Access the RdBu_r colormap in the updated manner
    rd_bu = matplotlib.colormaps['seismic']
    reds_rgb = rd_bu(np.linspace(0.5, 1, int(n_bins/2)))

    # Ensure both color arrays have the same shape, specifically the same number of columns
    # Here, we assume the custom colors don't have an alpha channel and thus reshape the reds_rgb to match
    reds_rgb = reds_rgb[:, :3]

    # Combine your custom colors with the reds
    colors_combined = np.vstack((negative_colors_rgb[::-1], reds_rgb))  # Reversing custom colors

    # Create and return a LinearSegmentedColormap
    custom_cmap = LinearSegmentedColormap.from_list("custom_combined", colors_combined, N=n_bins)
    return custom_cmap
def save_colorbar_only(custom_cmap, vmin, vmax, label):
    """
    Save the colorbar as a separate figure.
    """
    # Create a figure and a single subplot
    fig, ax = plt.subplots(figsize=(.2, 5.3))

    # Create a ScalarMappable with the normalization and colormap
    norm = Normalize(vmin=vmin, vmax=vmax)
    sm = ScalarMappable(norm=norm, cmap=custom_cmap)
    sm.set_array([])

    # Create the colorbar in the subplot
    cbar = plt.colorbar(sm, cax=ax, orientation='vertical')
    cbar.set_label(label)
    # Remove the colorbar's border
    cbar.outline.set_edgecolor('none')
    # Save the colorbar figure
    plt.savefig('colorbar.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

def merge_images(plot_image_path, colorbar_image_path, output_path):
    # Open the plot and colorbar images
    plot_image = Image.open(plot_image_path)
    colorbar_image = Image.open(colorbar_image_path)

    # Calculate the total width and max height
    total_width = plot_image.width + colorbar_image.width
    max_height = max(plot_image.height, colorbar_image.height)

    # Create a new blank image with the correct size
    combined_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))

    # Paste the images into the combined image
    combined_image.paste(plot_image, (0, 0))
    combined_image.paste(colorbar_image, (plot_image.width, 0))

    # Save the combined image
    combined_image.save(output_path)


def plot_country_temperature_anomalies(country_name):
    # Define URL
    url_pattern = "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/{country}-TAVG-Trend.txt"
    url = url_pattern.format(country=country_name.lower().replace(" ", "-"))

    # Download data
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to download data")
        return

    # Convert to StringIO to behave like a file object
    data_string = StringIO(response.text)

    # Read the data, including the columns for year, month, and monthly anomalies
    data = pd.read_csv(data_string, comment='%',
                       delim_whitespace=True,
                       names=['Year', 'Month', 'Monthly Anomaly', 'Monthly Uncertainty',
                              'Annual Anomaly', 'Annual Uncertainty',
                              'Five-year Anomaly', 'Five-year Uncertainty',
                              'Ten-year Anomaly', 'Ten-year Uncertainty',
                              'Twenty-year Anomaly', 'Twenty-year Uncertainty'],
                       na_values=['NaN'])

    # Filter out rows where 'Monthly Anomaly' is NaN to ensure only valid monthly anomalies are processed
    # But finaly I got Annual Anomaly which is more useful because monthly has lots of nans
    # Annual is also moving average of 12 months
    monthly_data = data[pd.notnull(data['Annual Anomaly'])]

    # Group by year and calculate mean of 'Monthly Anomaly' for each year
    yearly_means = monthly_data.groupby('Year')['Annual Anomaly'].mean().reset_index()




    # Calculate mean anomalies for the two periods
    period1 = yearly_means[(yearly_means['Year'] >= 1871) & (yearly_means['Year'] <= 1900)]
    period2 = yearly_means[(yearly_means['Year'] >= 1994) & (yearly_means['Year'] <= 2023)]

    mean_anomaly_period1 = period1['Annual Anomaly'].mean()
    mean_anomaly_period2 = period2['Annual Anomaly'].mean()

    # Compute the anomaly difference
    anomaly_difference = mean_anomaly_period2 - mean_anomaly_period1






    # Define custom colors for negative values
    negative_colors_hex = ['#cce9f1', '#86cbda', '#45a2b4', '#137c8f', '#013f54']

    # Create the custom colormap
    custom_cmap = create_custom_colormap(negative_colors_hex)
	# Normalize the yearly mean anomalies for color mapping
    norm = Normalize(vmin=-2.5, vmax=2.5)

    # Set the figure size and create two subplots
    fig, (ax_pos, ax_neg) = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                                         gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.0})

    # Plot positive values on the top axis
    pos_data = yearly_means[yearly_means['Annual Anomaly'] > 0]
    ax_pos.bar(pos_data['Year'], pos_data['Annual Anomaly'], color=custom_cmap(norm(pos_data['Annual Anomaly'])), width=1)

    # Plot negative values on the bottom axis
    neg_data = yearly_means[yearly_means['Annual Anomaly'] <= 0]
    ax_neg.bar(neg_data['Year'], neg_data['Annual Anomaly'], color=custom_cmap(norm(neg_data['Annual Anomaly'])), width=1)
	# Adjust the position of the colorbar
    # Add the anomaly difference as text to the plot
    fig.text(0.2, 0.8, f'1994-2023 vs. 1871-1900 : ', fontsize=13)
    fig.text(0.41, 0.796, f'+{anomaly_difference:.2f}°C', fontsize=25)
    sm = ScalarMappable(cmap=custom_cmap, norm=norm)
    plt.subplots_adjust(right=0.85)
    # Normalize the data for color mapping and create the colorbar
    norm = Normalize(vmin=-2.5, vmax=2.5)
    sm = ScalarMappable(cmap=custom_cmap, norm=norm)
    sm.set_array([])  # Necessary for ScalarMappable
    #cbar = fig.colorbar(sm, ax=[ax_neg, ax_pos], orientation='vertical',
    #                    label='Monthly Temperature Anomaly (°C)', pad=0.01)
    #cbar.ax.yaxis.set_label_position('left')


    # Set x-ticks and x-tick labels
    ax_neg.xaxis.set_major_locator(ticker.MaxNLocator(integer=True,nbins=10))
    ax_neg.set_xticks([year for year in range(yearly_means['Year'].min()+0, yearly_means['Year'].max() + 1, 20)])
    ax_neg.set_xticklabels([str(year) for year in range(yearly_means['Year'].min()+0, yearly_means['Year'].max() + 1, 20)], rotation=0)

    ## Customize the appearance of the spines to hide the box
    for ax in [ax_pos, ax_neg]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)


    # Set y-axis labels and ticks
    ax_pos.set_ylim(0, 2.5)
    ax_neg.set_ylim(-2.5, 0)
    ax_pos.set_yticks([2.5, 1.25, 0])
    ax_neg.set_yticks([-2.5, -1.25, 0])
    ax_pos.set_yticklabels(["2.5", "1.25", "0"], alpha=0.3)
    ax_neg.set_yticklabels(["-2.5", "-1.25", ""], alpha=0.3)
    #ax_pos.set_yticklabels(["", "", ""])
    #ax_neg.set_yticklabels(["", "", ""])
    plt.subplots_adjust(bottom=0.2,left=0.15, right=0.85)
    plt.xlim(1870, 2023)
    # Save the figure
    plt.savefig('temperature_anomalies_' + country_name + '.png', dpi=300, bbox_inches='tight')
    plt.close()
    # Now save the colorbar in a separate figure
    save_colorbar_only(custom_cmap, vmin=-2.5, vmax=2.5, label='Temperature Anomaly (°C)')

    merge_images('temperature_anomalies_' + country_name + '.png', 'colorbar.png', 'combined_figure_' + country_name + '.png')
# how to run it :

plot_country_temperature_anomalies('Kazakhstan')
#plot_country_temperature_anomalies('Turkmenistan')
#plot_country_temperature_anomalies('Uzbekistan')
#plot_country_temperature_anomalies('Tajikistan')
#plot_country_temperature_anomalies('Kyrgyzstan')
#plot_country_temperature_anomalies('Germany')
# Path: plot_Berkley.py
