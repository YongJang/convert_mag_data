"""
Author : YongJang 2017-09-21
https://www.github.com/YongJang
"""

import numpy as np
import math


def convert_data(file_path, file_name_nearest, file_name_average, location, measurement_tool) :
    data = np.loadtxt(file_path, delimiter=",", dtype=np.float32)

    if location == "engineering" :
        number_of_x_point = 17
        number_of_y_point = 37
        # pdr data divided by sl data --> x = 2.78, y = 2.86
        if measurement_tool == "sl" :
            start_point_x = 600 * 2.78
            end_point_x = 680 * 2.78
            start_point_y = 310 * 2.86
            end_point_y = 500 * 2.86
        elif measurement_tool == "pdr" :
            start_point_x = 1670
            end_point_x = 1890
            start_point_y = 886
            end_point_y = 1430
    elif location == "hanasquare" :
        number_of_x_point = -1 # not measured yet.
        number_of_y_point = -1 # not measured yet.
        # pdr data diveded by sl data --> x, y = 4.5
        if measurement_tool == "sl" :
            start_point_x = 140 * 4.5
            end_point_x = 180 * 4.5
            start_point_y = 170 * 4.5
            end_point_y = 290 * 4.5
        elif measurement_tool == "pdr" :
            start_point_x = 630
            end_point_x = 810
            start_point_y = 800
            end_point_y = 1340

    pos_x = data[:,0]
    pos_y = data[:,1]
    mag_data = data[:,2]
    mag_data_list = []

    # for reuse mag_data.
    for i in range(len(mag_data)) :
        mag_data_list.append(mag_data[i])

    interval_length_x = (end_point_x - start_point_x) / (number_of_x_point - 1)
    interval_length_y = (end_point_y - start_point_y) / (number_of_y_point - 1)

    # change start point to (0, 0)
    offset_x = []
    offset_y = []

    for i in range(len(pos_x)):
        offset_x.append(pos_x[i] - start_point_x)
        offset_y.append(pos_y[i] - start_point_y)

    # offset point divided by the number of x, y points
    divided_x = []
    divided_y = []

    for i in range(len(offset_x)) :
        divided_x.append(offset_x[i] / interval_length_x)
        divided_y.append(offset_y[i] / interval_length_y)

    # round each values
    round_x = []
    round_y = []

    for i in range(len(divided_x)) :
        round_x.append(round(divided_x[i]))
        round_y.append(round(divided_y[i]))

    # for cheking whether any point is not assigned and for Way 2.
    sum_equal_point = [[0 for y in range(number_of_y_point)] for x in range(number_of_x_point)]     # sum values pointing equal point.
    count_equal_point = [[0 for y in range(number_of_y_point)] for x in range(number_of_x_point)]   # count the number of pointing equal point.

    # change round list from float list to integer list for using it as pointing array index.
    round_x = [int(i) for i in round_x]
    round_y = [int(i) for i in round_y]

    for i in range(len(round_x)) :
        sum_equal_point[round_x[i]][round_y[i]] += mag_data[i]
        count_equal_point[round_x[i]][round_y[i]] = count_equal_point[round_x[i]][round_y[i]] + 1


    # if any point is not assigned, fill the point with average value from adjacent points
    """
    It has still problems. Because it fill the blank point from top to bottom and left to right.
    so, the filled values are more affected by top and left values.
    e.g. 1 1 2 3
         2 0 0 5
         4 0 0 7
         6 7 8 9    the 0 values(blank) tend to be assigned small values instead of big values.

    second, the blank data is affected by same row and columm values not nearest values.
    e.g. 0 0 0 0 2
         0 9 8 6 3
         0 8 7 4 4
         0 6 6 5 4
         1 3 4 4 3   the 0 value at (0, 0) is affected by (0, 4) and (4, 0), not the nearest value at (1, 1).
    """

    for i in range(number_of_x_point) :
        for j in range(number_of_y_point) :
            if count_equal_point[i][j] <= 0 :       # if any point is not assigned value
                temp_sum = sum_equal_point[i][j]
                temp_index = count_equal_point[i][j]
                if i == 0 :                         # if point is a edge of left side
                    find_not_zero = i + 1
                    while (count_equal_point[find_not_zero][j] == 0) :
                        find_not_zero += 1
                    temp_sum += sum_equal_point[find_not_zero][j]
                    temp_index += count_equal_point[find_not_zero][j]
                elif i == number_of_x_point - 1 :   # if point is a edge of right side
                    find_not_zero = i - 1
                    while (count_equal_point[find_not_zero][j] == 0) :
                        find_not_zero -= 1
                    temp_sum += sum_equal_point[find_not_zero][j]
                    temp_index += count_equal_point[find_not_zero][j]
                else :
                    temp_sum += sum_equal_point[i + 1][j] + sum_equal_point[i - 1][j]
                    temp_index += count_equal_point[i + 1][j] + count_equal_point[i - 1][j]
                if j == 0 :                         # if point is a edge of top side
                    find_not_zero = j + 1
                    while (count_equal_point[i][find_not_zero] == 0) :
                        find_not_zero += 1
                    temp_sum += sum_equal_point[i][find_not_zero]
                    temp_index += count_equal_point[i][find_not_zero]
                elif j == number_of_y_point - 1 :   # if point is a edge of bottom side
                    find_not_zero = j - 1
                    while (count_equal_point[i][find_not_zero] == 0) :
                        find_not_zero -= 1
                    temp_sum += sum_equal_point[i][find_not_zero]
                    temp_index += count_equal_point[i][find_not_zero]
                else :
                    temp_sum += sum_equal_point[i][j + 1] + sum_equal_point[i][j - 1]
                    temp_index += count_equal_point[i][j + 1] + count_equal_point[i][j - 1]
                sum_equal_point[i][j] = temp_sum
                count_equal_point[i][j] = temp_index
                divided_x.append(i)
                divided_y.append(j)
                round_x.append(i)
                round_y.append(j)
                # print(i)
                # print(j)
                # print("(",i,", ",j,")",(temp_sum / temp_index))
                mag_data_list.append(temp_sum / temp_index)

    # Way 1. nearest point as a reference point
    min_distance_matrix = [[1000 for y in range(number_of_y_point)] for x in range(number_of_x_point)] # 1000 as infinite number
    min_distance_index = [[-1 for y in range(number_of_y_point)] for x in range(number_of_x_point)] # to memorize index

    for i in range(len(round_x)) :
        distance = math.sqrt((divided_x[i] - round_x[i]) * (divided_x[i] - round_x[i]) + (divided_y[i] - round_y[i]) * (divided_y[i] - round_y[i]))

        if min_distance_matrix[round_x[i]][round_y[i]] > distance :
            min_distance_matrix[round_x[i]][round_y[i]] = distance
            min_distance_index[round_x[i]][round_y[i]] = i

    nearest_x = []
    nearest_y = []
    nearest_data = []


    for i in range(number_of_x_point) :
        for j in range(number_of_y_point) :
            nearest_x.append(round_x[min_distance_index[i][j]])
            nearest_y.append(round_y[min_distance_index[i][j]])
            nearest_data.append(mag_data_list[min_distance_index[i][j]])

    # Way 2. averaged by adjacent values
    average_x = []
    average_y = []
    average_data = []

    for i in range(number_of_x_point) :
        for j in range(number_of_y_point) :
            average_x.append(i)
            average_y.append(j)
            average_data.append(sum_equal_point[i][j] / count_equal_point[i][j])

    # output result
    f_nearest = open(file_name_nearest, 'w')
    for i in range(len(nearest_data)) :
        data = str(nearest_x[i]) + "," + str(nearest_y[i]) + "," + str(nearest_data[i]) + "\r"
        f_nearest.write(data)
    f_nearest.close()

    f_average = open(file_name_average, 'w')
    for i in range(len(average_data)) :
        data = str(average_x[i]) + "," + str(average_y[i]) + "," + str(average_data[i]) + "\r"
        f_average.write(data)
    f_average.close()

def main() :
    file_path = "C:\MgData\engineer\engineerPDR2_outofbounds_del_complete.csv"                             # input data
    file_name_nearest = "C:\MgData\engineer\engineerPDR_RESET_2_convert_nearest.csv"     # nearest output data
    file_name_average = "C:\MgData\engineer\engineerPDR_RESET_2_convert_average.csv"     # average output data
    location = "engineering"                                                    # measured location
    measurement_tool = "pdr"                                                     # measurement tool

    convert_data(file_path, file_name_nearest, file_name_average, location, measurement_tool)

if __name__ == "__main__" :
    main()
