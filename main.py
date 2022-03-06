"""
Extracts various values from logcat trace during a video call
"""

__author__ = "Lukas Daschinger"
__version__ = "1.0.1"
__maintainer__ = "Lukas Daschinger"
__email__ = "ldaschinger@student.ethz.ch"


import argparse
import re
from ast import literal_eval
import numpy as np
import json



def analyzeWebRTCStats(filepath):
    # print head including sampling interval
    with open(filepath) as myfile:
        head = [next(myfile) for x in range(6)]
    # print(head, "\n")

    bitrateRegex = re.compile(r'ExtendedACodec:   int32_t bitrate = (\d+)') #ExtendedACodec:   int32_t bitrate = 2000000

    bitrateValues = []

    for i, line in enumerate(open(filepath)):
        for match in re.finditer(bitrateRegex, line):
            # print('Found on line %s: %s' % (i + 1, match.group(1)))
            # now append it to the availableOutgoingBitrate list
            bitrateValues.append(match.group(1))

    # array = literal_eval(bitrateValues)
    npArray = np.asarray(bitrateValues)
    npArray = npArray.astype(int)
    print("\nAVERAGE bitrateValues: " + str(npArray.mean()))
    print("STDDEV bitrateValues: " + str(npArray.std()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath",
                        required=True,
                        default=None,
                        help="Path to target CSV file")
    args = parser.parse_args()
    # pass the filepath to the analysis function
    analyzeWebRTCStats(args.filepath)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
