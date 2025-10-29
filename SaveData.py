

def SaveData(Data):
    with open('data_log.csv' , 'w') as f:     
        for item in Data:
            # Append the data to the file
            f.write(str(item) + "\n") #Writes item into csv file
            f.flush() # Ensure data is written to the file
