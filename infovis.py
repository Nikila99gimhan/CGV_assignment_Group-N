import sys
import xml.etree.ElementTree as ElementTree
import os
from matplotlib import pyplot as plt

# Path to the directory containing XML files
xml_files_path = './Outputs/'

# Student ID provided as a command-line argument
student_id = sys.argv[1]

# Create dictionaries to store data from XML files
data_by_file = {}
files_repository = []

# Iterate through files in the specified directory
for filename in os.listdir(xml_files_path):
    # Check if the file is an XML file
    if not filename.endswith('.xml'):
        continue

    # Get the full path to the XML file
    full_path = os.path.join(xml_files_path, filename)
    files_repository.append(full_path)

    # Parse the XML file
    root = ElementTree.parse(full_path)

    # Create a dictionary to store attendance data for this file
    data_by_file[filename] = {}

    # Iterate through the XML elements
    for child in root.iter('students'):
        for student in child:
            index = None
            for data in student:
                # Check if the element represents student index
                if data.tag == 'index':
                    index = data.text
                    data_by_file[filename][index] = {}
                # Check if the element represents student attendance
                if data.tag == 'attendance':
                    data_by_file[filename][index] = True if data.text == 'true' else False

# Create a list to store attendance data for the specified student
student_data = []

# Iterate through data from all XML files and collect attendance data for the student
for file_data in data_by_file.values():
    if student_id in file_data:
        student_data.append(file_data[student_id])

# Count the number of 'True' (Present) and 'False' (Absent) entries
attendance_counts = [student_data.count(True), student_data.count(False)]

# Create a pie chart to visualize attendance data
plt.pie(attendance_counts, labels=['Present', 'Absent'])

# Add text annotations to display the counts on the chart
for i, count in enumerate(attendance_counts):
    plt.text(0.5 * (i - 0.5), -0.15, f'{count}', color='white', fontsize=12,
             bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 5})

# Display the pie chart
plt.show()