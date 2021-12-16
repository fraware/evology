import multiprocessing as mp
from main import *
import time
from main import main as evology

def job(iteration):
	df,pop = evology("static", 'scholl', 'newton', False, 1000, 0, 10, 0, [1/3, 1/3, 1/3], True, False)
	return df['WShare_NT'], df['WShare_VI'], df['WShare_TF']

''' 
reps = 30

def main():
	start = time.perf_counter()
	p = mp.Pool()
	data = p.map(job, [i for i in range(reps)])
	p.close()
	print(data)
	print(len(data))
	finish = time.perf_counter()
	print(f'Multiprocessing () Finished in {round(finish-start, 2)} second(s)')

	start = time.perf_counter()
	data2 = []
	for i in range(reps):
		data2.append(job([]))
	finish = time.perf_counter()
	print(data2)
	print(len(data2))
	print(f'For loop Finished in {round(finish-start, 2)} second(s)')

if __name__ == '__main__':
	main()
	'''
reps = 3
def main():
	start = time.perf_counter()
	p = mp.Pool()
	data = p.map(job, [i for i in range(reps)])
	p.close()
	print(data)
	print(len(data))
	data = np.array(list(data))
	finish = time.perf_counter()
	print(f'Multiprocessing () Finished in {round(finish-start, 2)} second(s)')
	return data

if __name__ == '__main__':
	dataRun = main()

	print('----')
	print(type(dataRun))
	print(dataRun)
	print(dataRun.shape)
	''' 3 2 937
	Hence 3 rows, 3 columns and each of the items is a list of 937 elements 
	Because ATM the job outputs only 3 variables (columns): NT ([0]), VI ([1]), TF ([2]) 
	And does 3 repetitions. Repetitions are rows.
	Example: data from the first run is data[0,0] for the NT series, data[0,1] for VI series, data[0,2] for TF series. '''
	plt.plot(dataRun[0,0], label = 'NT')
	plt.plot(dataRun[0,1], label = 'VI')
	plt.plot(dataRun[0,2], label = 'TF')
	plt.legend()
	plt.show()
