import torch

def get_random_problems(batch_size, problem_size, n_stations):

    total_nodes = 1 + n_stations + problem_size

    depot_xy = torch.full(size=(batch_size, 1, 2), fill_value=0.5)
    node_xy = 0.15 + 0.70 * torch.rand(size=(batch_size, problem_size, 2))

    if n_stations > 0:
        station_xy = 0.5 + 0.25 * (torch.rand(size=(batch_size, n_stations, 2)) - 0.5)
        station_xy = station_xy.clamp(0.05, 0.95)
    else:
        station_xy = torch.zeros(batch_size, 0, 2)

    raw_demand = torch.randint(10, 51, size=(batch_size, problem_size)).float()
    node_demand = raw_demand / 200.0

    depot_tw = torch.zeros(batch_size, 1, 2)
    depot_tw[:, :, 1] = 1.0

    station_tw = torch.zeros(batch_size, n_stations, 2)
    station_tw[:, :, 1] = 1.0

    e_cust = torch.rand(batch_size, problem_size) * 0.35
    width = 0.45 + torch.rand(batch_size, problem_size) * 0.35
    l_cust = torch.clamp(e_cust + width, max=1.0)

    customer_tw = torch.stack((e_cust, l_cust), dim=2)
    time_windows = torch.cat([depot_tw, station_tw, customer_tw], dim=1)

    service_time = torch.zeros(batch_size, total_nodes)
    service_time[:, 1 + n_stations:1 + n_stations + problem_size] = 0.045

    return depot_xy, node_xy, node_demand, station_xy, time_windows, service_time

# ========================= 8 倍坐标增强 =========================
def augment_xy_data_by_8_fold(xy_data):
    """对坐标进行 8 种对称变换（假设坐标在 [0,1] 区间）。"""
    x = xy_data[:, :, [0]]
    y = xy_data[:, :, [1]]

    dat1 = torch.cat((x, y), dim=2)
    dat2 = torch.cat((1 - x, y), dim=2)
    dat3 = torch.cat((x, 1 - y), dim=2)
    dat4 = torch.cat((1 - x, 1 - y), dim=2)
    dat5 = torch.cat((y, x), dim=2)
    dat6 = torch.cat((1 - y, x), dim=2)
    dat7 = torch.cat((y, 1 - x), dim=2)
    dat8 = torch.cat((1 - y, 1 - x), dim=2)

    aug_xy_data = torch.cat((dat1, dat2, dat3, dat4, dat5, dat6, dat7, dat8), dim=0)
    return aug_xy_data
