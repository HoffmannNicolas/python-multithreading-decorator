


import time
import threading
import math
import queue



def multiThreadFunction(originalFunction, *args, **kwargs):
    # This decorator multi-threads the <originalFunction>.
    # The <originalFunction> needs to receive the tasks to be done as a [list] in its first argument, and return the solution to each tasks as a [list] of results.
    # This constraint imposes to compute all solutions before eventually fusing them (summing them, for example).
    # The multi-threading steps are :
    #     - Split the list in <numberOfWorkers> sublists.
    #     - Start <numberOfWorkers> processes, each computing the <originalFunction> on one sublist each.
    #     - Wait for all workers to be finished.
    #     - Fuse the results of all workers and return the full result.

    maxNumberOfWorkers = 4
    localQueue = queue.Queue()

    def _workerFunction(originalFunction, subList, queue, workerNumber, *args, **kwargs):
        # This worker function executes the original function on a sublist of tasks and return the results
        originalArgs = (subList, *args)
        result = originalFunction(*originalArgs, **kwargs)
        localQueue.put((workerNumber, result)) # The <workerNumber> is used to sort() the results later
        return

    def _multiThreadedFunction(*args, **kwargs):
        fullList = args[0] # The original list of tasks to be splitted
        numberOfWorkers = min(maxNumberOfWorkers, len(fullList)) # At most one worker per task

        workers = []
        for workerNumber in range(numberOfWorkers):
            workerList = fullList[math.floor(workerNumber * len(fullList) / numberOfWorkers) : math.floor((workerNumber + 1) * len(fullList) / numberOfWorkers)]
            if not(isinstance(workerList, list)): workerList = [workerList] # Prevent edge-case where a singleton looses its list nature
            arguments = (originalFunction, workerList, localQueue, workerNumber, *(args[1:]))
            kwarguments = kwargs
            worker = threading.Thread(target=_workerFunction, args=(arguments), kwargs=(kwarguments))
            workers.append(worker)

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join() # Waiting for all workers to be finished

        workerResults = []
        while not localQueue.empty(): # Reading the partial results from all workers
            workerResult = localQueue.get()
            workerResults.append(workerResult)

        results = []
        workerResults.sort(key=lambda x:x[0]) # Sorting the partial results to match the original task list
        for workerResult in workerResults: # Concatenating all partial results
            results.extend(workerResult[1])
        
        return results

    return _multiThreadedFunction


if (__name__ == "__main__"):

    myList = list(range(200))

    # @multiThreadFunction
    def computeSquares(listToSquare, initialValue, endMessage=''):
        results = []
        for elt in listToSquare:
            results.append(elt*elt + initialValue)
            time.sleep(0.5)
        print(endMessage)
        return results

    nbIterations = 10
    before = time.time()
    for _ in range(nbIterations):
        val = computeSquares(list(range(20)), 4, endMessage="I'm done compting")
        print(val)
    after = time.time()
    print(f"{(after - before) / nbIterations}s average over {nbIterations} samples")



