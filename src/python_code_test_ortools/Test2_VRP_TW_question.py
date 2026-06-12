#Basic VRP-TW Question


import sys
#import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def create_data_model(m):
    data = {}
    #这边图省事就直接用样例数据了。
    data["time_matrix"] = [
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ]
    data["time_windows"] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]
    data["num_vehicles"] = m
    data["depot"] = 0
    return data


def main():
    #input number of vechicles & model creation
    n = 16
    m = int(input("Enter the number of vehicles:"))
    data = create_data_model(m)

    #manager setting
    manager = pywrapcp.RoutingIndexManager(n+1, m, 0)
    routing = pywrapcp.RoutingModel(manager)

    #time_callback builder
    def time_callback(node1, node2):
        point1 = manager.IndexToNode(node1)
        point2 = manager.IndexToNode(node2)
        return data['time_matrix'][point1][point2]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    #同test1

    print("-----------------\n")

    #[Different Part] Add the time constraint conditions
    #create time dimension
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        30,
        30,
        False,
        time
    )
    time_dimension = routing.GetDimensionOrDie(time)

    #conditions for different nodes
    for location_index, time_window in enumerate(data['time_windows']):
        if location_index == data['depot']:
            continue
        x = manager.NodeToIndex(location_index)
        time_dimension.CumulVar(x).SetRange(time_window[0],time_window[1])

    #conditions for vehicles starting period
    depot_index = data['depot']
    for i in range(m):
        x = routing.Start(i)
        time_dimension.CumulVar(x).SetRange(data['time_windows'][depot_index][0],data['time_windows'][depot_index][1])
    #Set searching method for solver
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 30
    #minimize the time when vehicle starting/returning
    for i in range(m):
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))       

    #Set solver
    solution = routing.SolveWithParameters(search_parameters)

    #printf(solution)
    def print_solution():
        sum_time = 0
        for i in range(m):
            print(f"Route for vehicle{i+1}:\n")
            x = routing.Start(i)
            while (not routing.IsEnd(x)):
                tim = time_dimension.CumulVar(x)
                print(f"{manager.IndexToNode(x)} (time:{solution.Min(tim)}-{solution.Max(tim)}) -> ")
                x = solution.Value(routing.NextVar(x))
            tim_end = time_dimension.CumulVar(x)
            print(f"{manager.IndexToNode(x)} (time:{solution.Min(tim_end)}-{solution.Max(tim_end)}), End.")
            print(f"Time of this route = {solution.Min(tim_end)}\n")
            sum_time += solution.Min(tim_end)
        print(f"Total time of all routes:{sum_time}\n")

    print_solution()


#主程序约束
if __name__ == "__main__":
    main()


"""
测试输入输出:
Enter the number of vehicles:4

-----------------

Route for vehicle1:

0 (time:0-0) -> 
9 (time:2-3) -> 
14 (time:7-8) -> 
16 (time:11-11) -> 
0 (time:18-18), End.
Time of this route = 18

Route for vehicle2:

0 (time:0-0) -> 
7 (time:2-4) -> 
1 (time:7-11) -> 
4 (time:10-13) -> 
3 (time:16-16) -> 
0 (time:24-24), End.
Time of this route = 24

Route for vehicle3:

0 (time:0-0) -> 
12 (time:4-4) -> 
13 (time:6-6) -> 
15 (time:11-11) -> 
11 (time:14-14) -> 
0 (time:20-20), End.
Time of this route = 20

Route for vehicle4:

0 (time:0-0) -> 
5 (time:3-3) -> 
8 (time:5-5) -> 
6 (time:7-7) -> 
2 (time:10-10) -> 
10 (time:14-14) -> 
0 (time:20-20), End.
Time of this route = 20

Total time of all routes:82
"""
