"""
Extracts various values from logcat trace during a video call
"""

__author__ = "Lukas Daschinger"
__version__ = "1.0.1"
__maintainer__ = "Lukas Daschinger"
__email__ = "ldaschinger@student.ethz.ch"


import argparse
import math
import re
import matplotlib.pyplot as plt
import numpy as np


def analyzeWebRTCStats(filepath):
    # print head including sampling interval
    with open(filepath) as myfile:
        head = [next(myfile) for x in range(6)]
    # print(head, "\n")

    # define regex expressions for required values of codec bitrate and timestamp
    # group 3 = hour
    # group 4 = minute
    # group 5 = second
    # group 6 = millisecond
    # group 9 = bitrate
    bitrateRegex = re.compile(r'(\d+)-(\d+)\s+(\d+):(\d+):(\d+).(\d+)\s+(\d+)\s+(\d+)\s+I\s+ExtendedACodec:\s+int32_t bitrate\s+=\s+(\d+)') #ExtendedACodec:   int32_t bitrate = 2000000
    timestampRegex = re.compile(r'(\d+)-(\d+)\s+(\d+):(\d+):(\d+).(\d+)')

    # ---1...2...3...4...end
    # difference in ms = match.group(3)*3600000 + match.group(4)*60000 + match.group(5)*1000 + match.group(6)
    timestamps_ms = []
    bitrateValues = []

    # get the last timestamp
    with open(filepath) as f:
        lines = f.readlines()
        last = lines[-1]
        #detect last line and get its timestamp
        for match in re.finditer(timestampRegex, last):
            lastTimestamp = (int(match.group(3)) * 3600000) + int(match.group(4)) * 60000 + int(match.group(5)) * 1000 + int(match.group(6))

    for i, line in enumerate(open(filepath)):
        for match in re.finditer(bitrateRegex, line):
            # print('Found on line %s: %s' % (i + 1, match.group(1)))
            # now append it to the availableOutgoingBitrate list
            bitrateValues.append(match.group(9))
            timestamp = (int(match.group(3)) * 3600000) + int(match.group(4)) * 60000 + int(match.group(5)) * 1000 + int(match.group(6))
            timestamps_ms.append(timestamp)

    # append last timestamp to list
    timestamps_ms.append(lastTimestamp)

    """
    Average calculation
    durations = [ts2-ts1, ts3-ts2, ts4-ts3, last-ts4]
    bitrates = [1,2,3,4]

    total = durations*bitrates
    average = total/(timestamps[-1]-timestamps[0])
    """

    durations = []
    for x in range(len(timestamps_ms)-1):
        # print(timestamps_ms[0])
        durations.append(timestamps_ms[x+1] - timestamps_ms[x])
        # print(durations[x])

    npArray = np.asarray(bitrateValues)
    npArrayBitrates = npArray.astype(int)
    npArray = np.asarray(durations)
    npArrayDurations = npArray.astype(int)

    print(npArrayDurations)
    fromSampleN = 0

    # during ramp up of the test, bitrate increases in short intervals. We only want to consider the stable parts:
    npArrayConstantTimestamps = npArrayDurations[npArrayDurations > 4500]
    print(npArrayConstantTimestamps)
    npArrayConstantBitrates = npArrayBitrates[npArrayDurations > 4500]
    print(npArrayConstantBitrates)

    # calculate a weighted avarage using the duration of a bitrate being used as the weights
    print('\naverage and stddev of bitrate found: ')
    # weightedAverage = np.average(npArrayBitrates[fromSampleN:], weights=npArrayDurations[fromSampleN:])
    weightedAverage = np.average(npArrayBitrates, weights=npArrayDurations)
    print(weightedAverage)

    plt.plot(npArrayBitrates)
    plt.plot(npArrayDurations)
    plt.show()

    # weighted avg by hand:
    # total = sum(npArrayDurations*npArrayBitrates)
    # average = total/(timestamps_ms[-1]-timestamps_ms[0])

    # calculate stddev weighted
    variance = np.average((npArrayBitrates - weightedAverage) ** 2, weights=npArrayDurations)
    print(math.sqrt(variance))

    # print(weighted_stddev(bitrateValues, durations))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath",
                        required=True,
                        default=None,
                        help="Path to target CSV file")
    args = parser.parse_args()
    # pass the filepath to the analysis function
    analyzeWebRTCStats(args.filepath)


