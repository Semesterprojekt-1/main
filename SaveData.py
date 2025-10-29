from machine import ADC

def SaveData():
    adc = ADC(28)
    with open('data_log.csv' , 'w') as f:
            digital_value = adc.read_u16()
            volt=3.3*(digital_value/65535)
            #print("Voltage: {}V ".format(volt))
            
            # Append the data to the file
            f.write(f'{volt}\n')
            f.flush() # Ensure data is written to the file
