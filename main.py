from astropy.visualization import time_support
import matplotlib.pyplot as plt
from astropy.time import Time
import numpy as np
import matplotlib.dates as mdates

time_support()


def read_tsv_and_group(filename):
    # Create a dictionary to store lines based on the third column value
    groups = {}

    # Open the TSV file for reading
    with open(filename, 'r') as tsv_file:
        # Skip the first three lines containing column names or comments
        next(tsv_file)
        next(tsv_file)
        next(tsv_file)

        # Iterate over each line in the file
        for line in tsv_file:
            # Split the line by tabs to get individual values
            values = line.strip().split('\t')

            # Check if the line has enough columns
            if len(values) >= 12:
                try:
                    # Extract the number from the third column
                    number = int(values[2])

                    # Attempt to extract and convert the distance from the seventh column
                    distance = float(values[6])

                    # Add the line to the corresponding group if distance is valid
                    if number not in groups:
                        groups[number] = {'x': [], 'y': [], 'distances': []}
                    groups[number]['x'].append(Time(values[4]))  # 5th column as x-axis
                    groups[number]['y'].append(float(values[5]))  # 6th column as y-axis
                    groups[number]['distances'].append(distance)  # 7th column as distance

                except ValueError:
                    # Skip the line if distance is not a valid float
                    print(f"Skipping line: {line.strip()} due to invalid distance value")

            else:
                print(f"Skipping line: {line.strip()} as it does not have enough columns")

    return groups


# Calculate mean distances and plot with color mapping
def plot_grouped_data_with_colormap(filename):
    grouped_data = read_tsv_and_group(filename)

    # Compute mean distances
    mean_distances = {group: np.mean(data['distances']) for group, data in grouped_data.items()}

    # Normalize distances to use in color mapping
    max_distance = max(mean_distances.values())
    min_distance = min(mean_distances.values())

    # Create a colormap and norm
    colormap = plt.cm.gist_rainbow
    norm = plt.Normalize(vmin=min_distance, vmax=max_distance)

    # Plotting
    fig, ax = plt.subplots()
    for number in sorted(grouped_data.keys()):
        data = grouped_data[number]
        datetime_objects = [time_obj.datetime for time_obj in data['x']]

        # Normalize the mean distance to get a color intensity between 0 and 1
        norm_distance = (mean_distances[number] - min_distance) / (max_distance - min_distance)
        color_intensity = 1 - norm_distance  # Darker color for larger distance

        ax.plot(datetime_objects, data['y'], label=f'Feature {number}', color=colormap(color_intensity))

    plt.xlabel('Year of observation')
    plt.ylabel('Flux density at 15 GHz, mJy')
    plt.title('1730-130 features')
    plt.legend()

    # Create a scalar mappable and add a colorbar
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Mean separation from core, mas')
    specific_time = Time('2016-01-28')
    plt.axvline(x=mdates.date2num(specific_time.datetime), color='r', linestyle='--')

    plt.grid()
    plt.show()


# Example usage
filename = 'C:/Users/Admin/PycharmProjects/sthOnScience/asu.tsv'
plot_grouped_data_with_colormap(filename)

