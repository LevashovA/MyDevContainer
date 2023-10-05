import os

# Adjust input_directory_path to change directory
global_input_directory_path = 'C:/NIH-Cogen/WINCC-tool/To Process'

# Create output directory within global_input_directory_path
OutputDirectory = global_input_directory_path + "/Output"

#Global Varibales
global_as2_value = ""
global_page_PUP = ""

# Function- Read .trs file in input directory
def Read_TRS_PressField(Input_file_path, Output_file_path):
    lines = []
    pressfield_data = []
    inside_pressfield = False

    with open(Input_file_path, 'r') as file:
        for line in file:
            if '[pressfield]' in line:
                inside_pressfield = True
                pressfield_data.append(line) 
        
            elif line.startswith("["): # Found new block
                inside_pressfield = False 
                if len(pressfield_data) != 0: # Add the current pressfield data to lines and clear pressfield data 
                    for var in pressfield_data:
                        lines.append(var)
                    pressfield_data.clear()
            
                lines.append(line)  # Add new Block header to lines
            
            elif inside_pressfield:
                modify_PressField(line, pressfield_data)
            
            else:
                lines.append(line)

    
    with open(Output_file_path, 'w') as file:
        for line in lines:
            file.write(str(line))

# Logic to modify the PressField Block
def modify_PressField(pressfield_Line, pressfield_data):
    
    if pressfield_Line.startswith('Page=PUP-'):
        global global_page_PUP 
        global_page_PUP = pressfield_Line

    elif pressfield_Line.startswith('Substitute='): #Extract AS_DB value from Substitute
        try:
            global global_as2_value
            global_as2_value = pressfield_Line.strip().split('Substitute="')[1].split('"')[1].strip()

            # Update Page=PUP-DIGMON now since it's comes before Substitute
            pressfield_data.append(global_page_PUP.replace("\n", ":-" + global_as2_value + "\n"))
            pressfield_data.append(pressfield_Line)
        except( IndexError ): 
            print("Error in line :" +  pressfield_Line)
            pressfield_data.append(pressfield_Line)

    elif pressfield_Line.startswith('PageName=PUP-'):
        if (global_as2_value != ""):
            pressfield_Line = pressfield_Line.replace("\n", ":-" + global_as2_value + "\n")
        pressfield_data.append(pressfield_Line)
    elif pressfield_Line.startswith("Max"):
        pressfield_data.append(pressfield_Line)
        if (global_as2_value != ""):
            pressfield_data.append("Color=0xFFFF00\n")
            pressfield_data.append("Thickness=3\n")            
            pressfield_data.append("Border=1\n")
    elif pressfield_Line.startswith("OpenAsChild"): # Reached the end of Pressfield block
        pressfield_data.append(pressfield_Line)        
        if (global_as2_value != ""): # Add new line to pressfield parameters
            pressfield_data.append("Highlightcondition=" + global_as2_value + ".hmiPopupOpen\n")
    elif (global_as2_value == ""): # Add new line to pressfield parameters
        pressfield_data.append(pressfield_Line)
    elif not pressfield_Line.startswith("Color") \
     and not pressfield_Line.startswith("Thickness") \
     and not pressfield_Line.startswith("Border"):        
        pressfield_data.append(pressfield_Line)        

def main():
    if not os.path.exists(OutputDirectory):
        os.makedirs(OutputDirectory)

    # Loop through all .trs files in the directory
    for filename in os.listdir(global_input_directory_path):
        if filename.endswith('.trs'):
            Input_file_path = os.path.join(global_input_directory_path, filename)
            Output_file_path = os.path.join(OutputDirectory, filename)
            Read_TRS_PressField(Input_file_path , Output_file_path)

    print("Modification complete.")


if __name__ == "__main__": main()