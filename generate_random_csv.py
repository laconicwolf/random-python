import pandas as pd
import numpy as np
import sys


if len(sys.argv) != 4:
	print("\nUsage: python3 generate_random_csv <outfile_name> <number of columns> <number of rows>")
	print("Example: python3 generate_random_csv out.csv 5 10000")
	print("\nThe above example will create a csv files with 5 columns and 10000 rows\n")
	exit()


outfile = sys.argv[1]
cols = int(sys.argv[2])	
rows = int(sys.argv[3])
	
def generate_data(number_of_rows, number_of_columns):
	df = pd.DataFrame(np.random.randint(0,100,size=(number_of_rows, number_of_columns)), columns=range(number_of_columns))
	return df
	
	
def write_to_csv(dataframe, filename):
	dataframe.to_csv(filename, index=False)
	
	
def main():
	df = generate_data(rows, cols)
	write_to_csv(df, outfile)
	print("{} has been created with {} rows and {} columns".format(outfile, rows, cols))
	
	
if __name__ == '__main__':
	main()