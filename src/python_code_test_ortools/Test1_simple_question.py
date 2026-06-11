#Basic VRP Question (only needs to minimize the total distance)(-> almost TSP)
#With help from website(https://developers.google.com/optimization/routing/tsp?hl=zh-cn)
#But written by myself.

#Step 0: OR-Tools Setting
import sys
import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

#Step 1: Create the data.
"""def dis0(i, j, position_matrix):
    x1=position_matrix[i][0]
    y1=position_matrix[i][1]
    x2=position_matrix[j][0]
    y2=position_matrix[j][1]
    return int(math.hypot(x1-x2,y1-y2))"""

def create_data_model(n, m):
    data = {}
    data['distance_matrix']=[[0 for i in range(n+1)] for j in range(n+1)]
    """    for i in range(0,n+1):
        for j in range(i,n+1):
            if i==j:
                data['distance_matrix'][i][j] = 0
            else:
                data['distance_matrix'][i][j] = dis0(i, j, position_matrix)
                data['distance_matrix'][j][i] = data['distance_matrix'][i][j]
    """
    #本来先入为主想在这里预计算各点距离，后面发现可以直接全部交给回调函数动态计算（复杂问题里还能降低时间复杂度蒽）
    data['num_vehicles'] = m
    data['depot'] = 0
    return data

#def distance_evaluator(from_node, to_node, position_matrix):
#    x1=position_matrix[from_node][0]
#    y1=position_matrix[from_node][1]
#    x2=position_matrix[to_node][0]
#    y2=position_matrix[to_node][1]
#    return math.sqrt((x1-x2)**2+(y1-y2)**2)

#def distance_callback(node1, node2, position_matrix):
#    return distance_evaluator(node1, node2, position_matrix)
    


def main():
    #input data & model creation
    n,m= int(input("Enter the number of nodes & vehicles:")), int(input())
    position_matrix = [[0,0] for _ in range(n+1)]

    print("\nPlease input the position of nodes (nodes 0 = depot)\n")
    for i in range(0,n+1):
        position_matrix[i][0] = int(input(f"Enter the x-coordinate of node {i}:\n"))
        position_matrix[i][1] = int(input(f"Enter the y-coordinate of node {i}:\n"))
    data = create_data_model(n, m)

    print("Distance Matrix:")
    for i in range(0,n+1):
        for j in range(0,n+1):
            print(f"{data['distance_matrix'][i][j]:.2f}", end=' ')
        print('\n')
    
#    print("CHECK Point 0-------------------------------------------------\n")
    

    #create the manager & model with ORTools

    manager = pywrapcp.RoutingIndexManager(n+1, data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)


#    print("CHECK Point 1-------------------------------------------------\n")

    #封装动态回调函数-定义约束条件
    def distance_callback(note1,note2):
        point1 = manager.IndexToNode(note1)
        point2 = manager.IndexToNode(note2)
        x1,y1 = position_matrix[point1]
        x2,y2 = position_matrix[point2]

        #print(f"Calculating{point1}->{point2},position:({x1},{y1})->({x2},{y2}),distance:{math.hypot(x1-x2,y1-y2):.2f} m")
        #记录一则悲伤故事：前面没有注意到ortools里弧成本必须是int型，导致距离输出全是0，debug了好久。

        return int(math.hypot(x1-x2,y1-y2))

#    print("CHECK Point 2-------------------------------------------------\n")

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    #notes:RegisterTransitCallback 是 OR-Tools 提供的 py->C++的翻译器；
    #SetArcCostEvaluatorOfAllVehicles则用于：指定车辆具体使用哪个函数来测算距离——即弧成本。
    #(ps:若有多种不同车辆，可用SetArcCostEvaluatorOfVehicle(vehicle_id, different_callback_index)来指定不同测算方法。)

    #create the solver path
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    solution = routing.SolveWithParameters(search_parameters)
    #notes:此处将PATH_ChEAPEST_ARC（一种贪心算法）设置成了用来求初始解的策略。
    
    #solving & store the results
    def print_solution():
        sum_distance = 0
        x0=0
        for i in range(m):
            x = routing.Start(i)
            print(f"Route for vehicle {i+1}:\n")
            while (not routing.IsEnd(x)):
                print(f"{manager.IndexToNode(x)} -> ")
                x0 = x
                x = solution.Value(routing.NextVar(x))
                #以动态链表的方式提供车辆在下一个节点的去向
                sum_distance += routing.GetArcCostForVehicle(x0, x, i)
                #print(f"[{routing.GetArcCostForVehicle(x0, x, i)} m]")
            print(f"{manager.IndexToNode(x)}\n")
        print(f"Total distance of the route: {sum_distance} m\n")
    

    if solution:
        print("Solution is founded:\n")
        print_solution()

    #print the results

#约束程序
if __name__ == "__main__":
    main()


"""
输入样例
3
1
0 0
4 0
0 3
4 3
-------
理想输出

0->1[4m]->3[3m]->2[4m]->0[3m]
(==0->2[3m]->3[4m]->1[3m]->0[4m])

Total distance of the route:14m
"""
#输入输出格式上总有点不习惯python的写法 后面自己找个时间专门系统化地纠一下吧