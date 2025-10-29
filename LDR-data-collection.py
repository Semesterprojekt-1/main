import matplotlib.pyplot as plt
import csv
import numpy as np

ls = []

# Read CSV and extract the first column (skipping the header)
with open('data_log.csv', 'r') as file:
    my_reader = csv.reader(file, delimiter=',')
    next(my_reader)  # Skip header
    for row in my_reader:
        ls.append(float(row[0]))  # Convert to float

# We let x be an index array(for storing data labels) and y be an array (for storing the actual data)
x = np.arange(len(ls))
y = np.array(ls)

# Plot the data
plt.plot(x, y)
plt.xlabel("Sample Index")
plt.ylabel("LDR Value")
plt.title("LDR Sensor Data Over Time")
plt.grid(True)
plt.show()