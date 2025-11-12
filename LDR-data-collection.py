import matplotlib.pyplot as plt
import csv
import numpy as np

ls = []

# Read CSV and extract the first column (skipping the header)
with open('LDR_data\data_med_cover_uden_lys3.csv', 'r') as file:
    my_reader = csv.reader(file, delimiter=',')
    next(my_reader)  # Skip header
    for row in my_reader:
        ls.append(float(row[0]))  # Convert to float

# We let x be an index array(for storing data labels) and y be an array (for storing the actual data)
x = np.arange(len(ls))
y = np.array(ls)

name = "LDR Sensor Data Over Time (with cover u. lys) 3"
# Plot the data
plt.plot(x, y)
plt.xlabel("Sample Index")
plt.ylabel("LDR Value")
plt.title(name)
plt.grid(True)
plt.savefig(f"{name}.png")
plt.show()
