#EVRP_TW_MODEL 顶层封装 调用编码器和解码器
#pre_forward 预处理 编码所有节点
#forward 判断、作出行动
import torch
import torch.nn as nn
import torch.nn.functional as F


class BaselineModel(nn.Module):
    def __init__(self, **model_params):
        super().__init__()
        self.model_params = model_params
        self.encoder = EVRPTW_Encoder(**model_params)
        self.decoder = EVRPTW_Decoder(**model_params)
        self.encoded_nodes = None
        self.n_stations = 0

    def pre_forward(self, reset_state):
        depot_xy = reset_state.depot_xy
        node_xy = reset_state.node_xy
        station_xy = reset_state.station_xy
        node_demand = reset_state.node_demand
        time_windows = reset_state.time_windows

        batch_size = depot_xy.size(0)
        problem_size = node_xy.size(1)
        n_stations = station_xy.size(1)
        total_nodes = 1 + problem_size + n_stations

        all_xy = torch.cat((depot_xy, station_xy, node_xy), dim=1)
        demand = torch.zeros(batch_size, total_nodes, 1, device=depot_xy.device)
        demand[:, 1+n_stations:1+n_stations+problem_size, 0] = node_demand
        tw = time_windows
        node_features = torch.cat((all_xy, demand, tw), dim=2)

        self.encoded_nodes = self.encoder(node_features)
        self.decoder.set_kv(self.encoded_nodes)
        self.n_stations = n_stations

    def forward(self, state):
        batch_size = state.BATCH_IDX.size(0)
        pomo_size = state.BATCH_IDX.size(1)
        device = state.BATCH_IDX.device

        if state.selected_count == 0:
            selected = torch.zeros(size=(batch_size, pomo_size), dtype=torch.long, device=device)
            prob = torch.ones(size=(batch_size, pomo_size), device=device)

        elif state.selected_count == 1:
            start = 1 + self.n_stations
            customer_count = self.encoded_nodes.size(1) - start

            base = torch.arange(pomo_size, device=device) % customer_count
            selected = (start + base)[None, :].expand(batch_size, pomo_size)

            illegal = torch.isneginf(state.ninf_mask.gather(2, selected[:, :, None]).squeeze(2))
            if illegal.any():
                legal = ~torch.isneginf(state.ninf_mask)
                fallback = legal.float().argmax(dim=2)
                selected = torch.where(illegal, fallback, selected)

            prob = torch.ones(size=(batch_size, pomo_size), device=device)

        else:
            encoded_last_node = _get_encoding(self.encoded_nodes, state.current_node)
            probs = self.decoder(
                encoded_last_node,
                state.energy,
                state.current_time,
                ninf_mask=state.ninf_mask
            )

            if self.training or self.model_params['eval_type'] == 'softmax':    #train的时候用softmax
                probs_flat = probs.reshape(batch_size * pomo_size, -1)

                row_sum = probs_flat.sum(dim=1)
                bad_rows = (~torch.isfinite(row_sum)) | (row_sum <= 0)

                if bad_rows.any():
                    # 使用 mask 找合法动作
                    legal = ~torch.isneginf(state.ninf_mask)
                    legal_flat = legal.reshape(batch_size * pomo_size, -1)

                    no_legal = legal_flat.sum(dim=1) == 0
                    if no_legal.any():
                        legal_flat[no_legal, 0] = True

                    fallback_probs = legal_flat.float()
                    fallback_probs = fallback_probs / fallback_probs.sum(dim=1, keepdim=True).clamp_min(1.0)

                    probs_flat[bad_rows] = fallback_probs[bad_rows]

                with torch.no_grad():
                    selected = probs_flat.multinomial(1).squeeze(dim=1).reshape(batch_size, pomo_size)

                prob = probs[state.BATCH_IDX, state.POMO_IDX, selected].reshape(batch_size, pomo_size)

                prob = torch.nan_to_num(prob, nan=0.0, posinf=0.0, neginf=0.0)
                prob = prob.clamp_min(1e-12)

            else:
                probs_flat = probs.reshape(batch_size * pomo_size, -1)
                row_sum = probs_flat.sum(dim=1)
                bad_rows = (~torch.isfinite(row_sum)) | (row_sum <= 0)

                selected = probs.argmax(dim=2)

                if bad_rows.any():
                    legal = ~torch.isneginf(state.ninf_mask)
                    legal_flat = legal.reshape(batch_size * pomo_size, -1)

                    no_legal = legal_flat.sum(dim=1) == 0
                    if no_legal.any():
                        legal_flat[no_legal, 0] = True

                    fallback_selected = legal_flat.float().argmax(dim=1).reshape(batch_size, pomo_size)
                    bad_rows_2d = bad_rows.reshape(batch_size, pomo_size)
                    selected = torch.where(bad_rows_2d, fallback_selected, selected)

                prob = None

        return selected, prob

def _get_encoding(encoded_nodes, node_index_to_pick):
    batch_size = node_index_to_pick.size(0)
    pomo_size = node_index_to_pick.size(1)
    embedding_dim = encoded_nodes.size(2)

    gathering_index = node_index_to_pick[:, :, None].expand(batch_size, pomo_size, embedding_dim)
    picked_nodes = encoded_nodes.gather(dim=1, index=gathering_index)
    return picked_nodes

class EVRPTW_Encoder(nn.Module):
    def __init__(self, **model_params):
        super().__init__()
        self.model_params = model_params
        embedding_dim = self.model_params['embedding_dim']
        encoder_layer_num = self.model_params['encoder_layer_num']

        self.embedding = nn.Linear(5, embedding_dim)
        self.layers = nn.ModuleList([EncoderLayer(**model_params) for _ in range(encoder_layer_num)])

    def forward(self, node_features):

        embedded = self.embedding(node_features)
        out = embedded
        for layer in self.layers:
            out = layer(out)
        return out
        # shape: (batch, total_nodes, embedding)

class EVRPTW_Decoder(nn.Module):
    def __init__(self, **model_params):
        super().__init__()
        self.model_params = model_params
        embedding_dim = self.model_params['embedding_dim']
        head_num = self.model_params['head_num']
        qkv_dim = self.model_params['qkv_dim']

        self.Wq_last = nn.Linear(embedding_dim + 2, head_num * qkv_dim, bias=False)
        self.Wk = nn.Linear(embedding_dim, head_num * qkv_dim, bias=False)
        self.Wv = nn.Linear(embedding_dim, head_num * qkv_dim, bias=False)

        self.multi_head_combine = nn.Linear(head_num * qkv_dim, embedding_dim)

        self.k = None
        self.v = None
        self.single_head_key = None

    def set_kv(self, encoded_nodes):
        head_num = self.model_params['head_num']
        self.k = reshape_by_heads(self.Wk(encoded_nodes), head_num=head_num)
        self.v = reshape_by_heads(self.Wv(encoded_nodes), head_num=head_num)
        self.single_head_key = encoded_nodes.transpose(1, 2)

    def forward(self, encoded_last_node, energy, current_time, ninf_mask):
        head_num = self.model_params['head_num']

        context = torch.cat((encoded_last_node, energy[:, :, None], current_time[:, :, None]), dim=2)
        q_last = reshape_by_heads(self.Wq_last(context), head_num=head_num)

        out_concat = multi_head_attention(q_last, self.k, self.v, rank3_ninf_mask=ninf_mask)
        mh_atten_out = self.multi_head_combine(out_concat)

        score = torch.matmul(mh_atten_out, self.single_head_key)
        score_scaled = score / self.model_params['sqrt_embedding_dim']
        score_clipped = self.model_params['logit_clipping'] * torch.tanh(score_scaled)

        score_masked = score_clipped + ninf_mask
        probs = F.softmax(score_masked, dim=2)
        probs = torch.nan_to_num(probs, nan=0.0, posinf=0.0, neginf=0.0)
        return probs

class EncoderLayer(nn.Module):
    def __init__(self, **model_params):
        super().__init__()
        self.model_params = model_params
        embedding_dim = self.model_params['embedding_dim']
        head_num = self.model_params['head_num']
        qkv_dim = self.model_params['qkv_dim']

        self.Wq = nn.Linear(embedding_dim, head_num * qkv_dim, bias=False)
        self.Wk = nn.Linear(embedding_dim, head_num * qkv_dim, bias=False)
        self.Wv = nn.Linear(embedding_dim, head_num * qkv_dim, bias=False)
        self.multi_head_combine = nn.Linear(head_num * qkv_dim, embedding_dim)

        self.add_n_normalization_1 = AddAndInstanceNormalization(**model_params)
        self.feed_forward = FeedForward(**model_params)
        self.add_n_normalization_2 = AddAndInstanceNormalization(**model_params)

    def forward(self, input1):
        head_num = self.model_params['head_num']
        q = reshape_by_heads(self.Wq(input1), head_num=head_num)
        k = reshape_by_heads(self.Wk(input1), head_num=head_num)
        v = reshape_by_heads(self.Wv(input1), head_num=head_num)

        out_concat = multi_head_attention(q, k, v)
        multi_head_out = self.multi_head_combine(out_concat)

        out1 = self.add_n_normalization_1(input1, multi_head_out)
        out2 = self.feed_forward(out1)
        out3 = self.add_n_normalization_2(out1, out2)
        return out3


def reshape_by_heads(qkv, head_num):
    batch_s = qkv.size(0)
    n = qkv.size(1)
    q_reshaped = qkv.reshape(batch_s, n, head_num, -1)
    q_transposed = q_reshaped.transpose(1, 2)
    return q_transposed


def multi_head_attention(q, k, v, rank2_ninf_mask=None, rank3_ninf_mask=None):
    batch_s = q.size(0)
    head_num = q.size(1)
    n = q.size(2)
    key_dim = q.size(3)
    input_s = k.size(2)

    score = torch.matmul(q, k.transpose(2, 3))
    score_scaled = score / (key_dim ** 0.5)
    if rank2_ninf_mask is not None:
        score_scaled = score_scaled + rank2_ninf_mask[:, None, None, :].expand(batch_s, head_num, n, input_s)
    if rank3_ninf_mask is not None:
        score_scaled = score_scaled + rank3_ninf_mask[:, None, :, :].expand(batch_s, head_num, n, input_s)

    weights = nn.Softmax(dim=3)(score_scaled)
    out = torch.matmul(weights, v)
    out_transposed = out.transpose(1, 2)
    out_concat = out_transposed.reshape(batch_s, n, head_num * key_dim)
    return out_concat


class AddAndInstanceNormalization(nn.Module):
    def __init__(self, **model_params):
        super().__init__()
        embedding_dim = model_params['embedding_dim']
        self.norm = nn.InstanceNorm1d(embedding_dim, affine=True, track_running_stats=False)

    def forward(self, input1, input2):
        added = input1 + input2
        transposed = added.transpose(1, 2)
        normalized = self.norm(transposed)
        back_trans = normalized.transpose(1, 2)
        return back_trans


class FeedForward(nn.Module):
    def __init__(self, **model_params):
        super().__init__()
        embedding_dim = model_params['embedding_dim']
        ff_hidden_dim = model_params['ff_hidden_dim']
        self.W1 = nn.Linear(embedding_dim, ff_hidden_dim)
        self.W2 = nn.Linear(ff_hidden_dim, embedding_dim)

    def forward(self, input1):
        return self.W2(F.relu(self.W1(input1)))