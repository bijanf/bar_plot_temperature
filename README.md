# Country Temperature Anomaly Visualizer

This Python script visualizes the temperature anomalies of various countries over time, comparing historical data with recent trends. It uses data from the Berkeley Earth temperature dataset, plotting both positive and negative temperature anomalies to highlight changes in the climate.

## Features

- Downloads temperature data directly from Berkeley Earth.
- Calculates annual temperature anomalies for each country.
- Generates a custom color map to visually distinguish between positive and negative anomalies.
- Creates a dual-axis bar plot to separately visualize positive and negative temperature anomalies.
- Calculates and displays the temperature anomaly difference between the periods 1995-2024 and 1871-1900.
- Saves the plots and a separate colorbar as images, then merges them for a comprehensive visualization.

## Prerequisites

Before running this script, ensure you have the following Python packages installed:

- pandas
- matplotlib
- numpy
- Pillow
- requests

You can install these packages using pip:

```bash
pip install pandas matplotlib numpy Pillow requests
```
## Usage

To visualize the temperature anomalies for a specific country, run the script with the desired country name as shown below:

```python
plot_country_temperature_anomalies('Country Name')
```
Replace 'Country Name' with the name of the country you want to analyze. For example:
```python
plot_country_temperature_anomalies('Germany')
```
