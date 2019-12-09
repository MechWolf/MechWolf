from flask import Flask, request
from scipy.signal import find_peaks, peak_prominences, peak_widths
import numpy as np
from math import isclose

import rrcf
from statistics import stdev, mean

# Set tree parameters
num_trees = 50
shingle_size = 1
tree_size = 256
codisp_threshold = 20
stdev_threshold = 3

# Create a forest of empty trees
forest = []
for _ in range(num_trees):
    tree = rrcf.RCTree()
    forest.append(tree)


# Create a dict to store anomaly score of each point
avg_codisp = {}


app = Flask(__name__)


def smooth(x, window_len=11, window="flat"):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError(
            "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        )

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-2 : -window_len - 1 : -1]]
    # print(len(s))
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")
    return y


data = []
peak_count = 0
width = -1
prominence = -1
index = 0
MAX_POINTS = 250

inserted = []


@app.route("/", methods=["POST"])
def hello_world():
    global data, width, prominence, index
    point = float(request.form["data"])
    if len(data) <= MAX_POINTS:
        data.append(point)
    else:
        print("truncating")
        data.pop(0)
        data.append(point)
    smoothed = smooth(np.array(data))
    peaks, properties = find_peaks(smoothed, prominence=0.1, width=1)
    if len(properties["widths"]) >= 4 and not isclose(width, properties["widths"][-3]):
        width = properties["widths"][-3]
        print(width)
    elif len(properties["prominences"]) >= 4 and not isclose(
        prominence, properties["prominences"][-3]
    ):
        prominence = properties["prominences"][-3]
        print(prominence)
    elif width == -1 or prominence == -1:
        return "Too early!"
    else:
        return "Too early!"

    point = [width, prominence]
    for tree in forest:
        # If tree is above permitted size...
        if len(tree.leaves) > tree_size:
            # Drop the oldest point (FIFO)
            tree.forget_point(index - tree_size)
        # Insert the new point into the tree
        tree.insert_point(point, index=index)
        # Compute codisp on the new point...
        new_codisp = tree.codisp(index)
        # And take the average over all trees
        if index not in avg_codisp:
            avg_codisp[index] = 0
        avg_codisp[index] += new_codisp / num_trees
    if avg_codisp[index] > codisp_threshold:
        print("Anomaly detected!: ", avg_codisp[index], codisp_threshold, point)
        return "Error!"
        exit()
    if (
        index > 2
        and mean(avg_codisp.values()) + stdev(avg_codisp.values()) * stdev_threshold
        < avg_codisp[index]
    ):
        print("Anomaly detected via stdev!:", index, point, avg_codisp)
        return "Error!"
        exit()
    index += 1
    return "Got it!"
