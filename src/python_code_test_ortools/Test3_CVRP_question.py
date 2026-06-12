#Exercise: CVRP sample question

import sys
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model(m):
    data = {}
    #依旧是图方便（检验结果）先用例题数据了.JPG
    data["distance_matrix"] = [
    [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
    [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
    [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
    [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
    [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
    [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
    [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
    [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
    [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
    [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
    [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
    [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
    [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
    [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
    [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
    [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
    [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
    ]
    data['demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data["num_vehicles"] = m
    data['vehicle_capacities'] = [15, 15, 15, 15]
    data["depot"] = 0
    return data

def main():
    
    n = 16
    m = int(input("Enter the number of vehicles:\n"))
    data = create_data_model(m)

    manager = pywrapcp.RoutingIndexManager(n+1, m, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(node1, node2):
        point1 = manager.IndexToNode(node1)
        point2 = manager.IndexToNode(node2)
        return data['distance_matrix'][point1][point2]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    
    #容量constraint conditions
    def demand_callback(x):
        node = manager.IndexToNode(x)
        return data['demands'][node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data['vehicle_capacities'],
        True,
        "Capacity"
    )

    print("------------------------\n")

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    #GLS:元启发式算法 - ortools官方推荐
    #（编译时间明显增加了）（但也确实让路径总长6872m->6208m了）
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    search_parameters.time_limit.seconds = 30
    solution = routing.SolveWithParameters(search_parameters)

    def print_solution():
        sum_all = 0
        for i in range(m):
            sum = 0
            print(f"Route for vehicle{i+1}:\n")
            x = routing.Start(i)
            while (not routing.IsEnd(x)):
                node = manager.IndexToNode(x)
                print(f"{node} -> ")
                x0 = x
                x = solution.Value(routing.NextVar(x))
                sum += routing.GetArcCostForVehicle(x0,x,i)
            print(f"{manager.IndexToNode(x)}, End.")
            print(f"Distance of this route = {sum}m\n")
            sum_all += sum
        print(f"Total time of all routes:{sum_all}m\n")


    print_solution()



if __name__ == "__main__":
    main()


"""
测试输入输出:
Enter the number of vehicles:
4
------------------------

Route for vehicle1:

0 -> 
7 -> 
3 -> 
4 -> 
1 -> 
0, End.
Distance of this route = 1552m

Route for vehicle2:

0 -> 
14 -> 
16 -> 
10 -> 
9 -> 
0, End.
Distance of this route = 1552m

Route for vehicle3:

0 -> 
12 -> 
11 -> 
15 -> 
13 -> 
0, End.
Distance of this route = 1552m

Route for vehicle4:

0 -> 
8 -> 
2 -> 
6 -> 
5 -> 
0, End.
Distance of this route = 1552m

Total time of all routes:6208m
"""
