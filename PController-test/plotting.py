import matplotlib.pyplot as plt

# Hent data fr git og sæt ind her
data = [
    
]
dt = 0.005
time = [i * dt for i in range(len(data))]

fig, ax = plt.subplots(figsize=(10,5))
ax.plot(time, data, marker='o', linestyle='-')

ax.spines['bottom'].set_position('zero')   
ax.spines['top'].set_color('none')         
ax.spines['right'].set_color('none')       
ax.spines['left'].set_position(('outward', 0))  

y_max = max(data) + 0.05
y_min = min(data) - 0.05
ax.set_ylim(y_min, y_max)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Error")
ax.grid(True)
plt.title("Sensor Error over Time")
plt.show()
