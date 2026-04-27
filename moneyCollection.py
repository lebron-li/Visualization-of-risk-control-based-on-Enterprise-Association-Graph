import re
import json
import csv
import networkx as nx
import matplotlib.pyplot as plt

# 资金归集识别条件
# txn: transaction, recip: reciprocal
txn = {
    "code": ['EK95','8002','8003','7743'],
    "isLoan": 0,
    "txnAmountLimit": 90000.0,
}
loan = {
    "code": ['6101' ,'6102', '6104' , '61' , '6151' , '2202' , '6002' , '6003' ,
            '6005' , '6006' , '7641' , '7799', '7641' ,'7810', 'DK06' , 'DK05'],
    "txnAmountLimit": 100000.0,
    "isLoan": 1,
    "status": 0,
    "abstract": ['贷款还款', '委托贷款收回利息', '委托贷款收回本金',
                '现金管理子账户占用上存金额补足本次扣款', '公积金放款', '贷款并账']
}


def getInitmoneyCollectionG(path):
    """
    读取资金归集的excel表格到DataFrame, 并切分子图
    Params:
        path: 含有资金归集数据的csv表格
    Returns: 
        GList: 根据表格数据切分得到的子图集合, 每个元素都是一副子图
    """
    # 由于可能存在两个节点间重复建立交易关系, 故使用MultiDiGraph
    G = nx.MultiDiGraph()
    codes = [[], []]
    # 由于原csv中存在非utf-8字符, 需过滤掉非uft-8字符
    with open("./backend/res/moneyCollection.csv", encoding='utf-8', errors='ignore') as f:
        # 给定的识别贷款和转账的条件
        originData = csv.reader(f)
        tag = {
            "myId": 0,  # 本人账户
            "recipId": 29,  # 对方账户
            "txnDateTime": 1,  # 交易日期
            "txnCode": 4,  # 交易码
            "txnAmount": 7,  # 交易金额
            "isLoan": 6,  # 借贷标志
            "status": 33,  # 状态码
            "abstract": 21  # 摘要
        }
        i = 0
        for line in originData:
            # 是否读入数据的标志
            canIn = False
            # 忽略标题行和Id为空的行
            if line[tag["myId"]] == '' or line[tag["recipId"]] == '' or i == 0:
                i += 1
                continue
            # 贷款和转账条件筛选            
            # 转账条件筛选
            if (
                int(line[tag["isLoan"]]) == txn["isLoan"] 
                and line[tag["txnCode"]] in txn["code"]
                and float(line[tag["txnAmount"]]) >= txn["txnAmountLimit"]
            ):
                codes[1].append(line[tag["txnCode"]])
                canIn = True
            # 贷款条件筛选
            elif (
                not line[tag["status"]] == "R" 
                and float(line[tag["txnAmount"]]) >= loan["txnAmountLimit"] 
                and line[tag["txnCode"]] in loan["code"] 
                and int(line[tag["isLoan"]]) == loan["isLoan"] 
                and int(line[tag["status"]]) == loan["status"]
            ):
                flag = False
                for item in loan["abstract"]:
                    if re.search(item, line[tag["abstract"]]):
                        flag = True
                        break
                if flag:
                    continue
                codes[0].append(line[tag["txnCode"]])
                canIn = True
            if canIn:
                # 构建初始图G, 将符合条件的节点和边加入G
                if not G.has_node(line[tag["myId"]]):
                    if len(line[tag["myId"]]) >= 15:
                        line[tag["myId"]] = line[tag["myId"]][:-2] + '00'
                    G.add_node(line[tag["myId"]], netIncome=0, std=0)
                if not G.has_node(line[tag["recipId"]]):
                    if len(line[tag["recipId"]]) >= 15:
                        line[tag["recipId"]] = line[tag["recipId"]][:-2] + '00'
                    G.add_node(line[tag["recipId"]], netIncome=0, std=0)
                G.add_edge(
                    line[tag["myId"]],
                    line[tag["recipId"]],
                    txnAmount=float(line[tag["txnAmount"]]),
                    txnDateTime=int(line[tag["txnDateTime"]]),
                    isLoan=int(line[tag["isLoan"]]),
                    txnCode=line[tag["txnCode"]],
                    width=float(line[tag["txnAmount"]])**0.5 / 1800
                )                         
            i += 1
    print("----------资金归集表数据读取完成----------")
    print("符合条件的贷款和转账关系总数：", G.size())
    print("含有贷款和转账的公司数量：", nx.number_of_nodes(G))
    codes = [list(set(codes[i])) for i in range(2)]
    print("符合条件的贷款交易码类型：", codes[0])
    print("符合条件的转账交易码类型：", codes[1])
    # 切分子图
    tmp = nx.to_undirected(G)
    GList = list()
    for c in nx.connected_components(tmp):
        GList.append(G.subgraph(c))
    print("----------资金归集子图切分完成----------")
    return GList


def getNetIncome(Glist):
    '''
    计算各个企业的净资金流入
    Params:
        GList: 资金归集子图列表
    Outputs:
        GList: 在原图中加入点的权重
    '''
    for subG in Glist:
        for n in subG.nodes():
            children = list(subG.neighbors(n))
            father = list(subG.predecessors(n))
            netIncome = 0
            # 贷款流入
            for f in father:
                for k1 in subG[f][n]:
                    netIncome += subG[f][n][k1]["txnAmount"]
            # 转账流出
            for c in children:
                for k2 in subG[n][c]:
                    netIncome -= subG[n][c][k2]["txnAmount"]
            subG.nodes[n]["netIncome"] = netIncome
        # 标准化净资金流入, 用于可视化时的size, 范围为[5, 14]
        d = [abs(x) 
            for x in nx.get_node_attributes(subG, "netIncome").values()
        ]
        maxNetIncome, minNetIncome = max(d), min(d)
        if maxNetIncome == minNetIncome:
            for n in subG.nodes():
                subG.nodes[n]["std"] = 9
        else:
            k = 9/(maxNetIncome - minNetIncome)
            for n in subG.nodes():
                subG.nodes[n]["std"] = 5 + k * (
                        abs(subG.nodes[n]["netIncome"]) - minNetIncome
                    )
    print("----------净资金流入计算完成----------")


def findShellEnterprise(GList):
    '''
    根据资金归集关系找到空壳企业
    Params:
        GList: 资金归集子图列表
    Returns:
        se: 企业资金归集图
        seNodes: 资金归集企业列表
    '''
    se = nx.MultiDiGraph()
    seNodes = [[] for i in range(3)]
    codes = [[], []]
    for subG in GList:
        for n in subG.nodes():
            children = list(subG.neighbors(n))
            father = list(subG.predecessors(n))
            if not father or not children:
                continue
            # 上游企业
            for f in father:
                for k1 in subG[f][n]:
                    # 若入边非贷款, 直接跳过
                    if subG[f][n][k1]["isLoan"] == txn["isLoan"]:
                        continue
                    # 寻找最匹配的贷款和转账
                    bestMatchF, bestMatchRate, bestMatchC, bestMatchLoan, bestMatchTxn, bestMatchDate = "", 0.9, "", -1, -1, 0
                    # 下游企业
                    for c in children:
                        for k2 in subG[n][c]:
                            # 若出边非转账或三元组上任意两个节点相同, 直接跳过
                            if subG[n][c][k2]["isLoan"] == loan["isLoan"]:
                                continue
                            # 日期相差五天, 且金额变化在0.9-1.0范围内
                            rate = subG[n][c][k2]["txnAmount"] / subG[f][n][k1]["txnAmount"]
                            if (
                                subG[n][c][k2]["txnDateTime"] - subG[f][n][k1]["txnDateTime"] <= 5 
                                and subG[n][c][k2]["txnDateTime"] >= subG[f][n][k1]["txnDateTime"]
                                and rate >= bestMatchRate
                                and rate <= 1
                            ):
                                bestMatchC, bestMatchRate, bestMatchF = c, rate, f
                                bestMatchLoan, bestMatchTxn = subG[f][n][k1]["txnAmount"], subG[n][c][k2]["txnAmount"]
                                bestMatchDate = (subG[f][n][k1]["txnDateTime"], subG[n][c][k2]["txnDateTime"])
                        # 如果找到了匹配到的贷款和转账, 则修改节点属性, 将其记录到se中
                    if bestMatchC:
                        print(
                            "father: ", bestMatchF, 
                            "node: ", n, 
                            "child: ", bestMatchC, "\n"
                            "贷款交易码：", subG[bestMatchF][n][k1]["txnCode"], 
                            "转账交易码：", subG[n][bestMatchC][k2]["txnCode"]
                        )
                        print(
                            "rate: ", bestMatchRate, 
                            "贷款金额: ", bestMatchLoan, 
                            "转账金额: ", bestMatchTxn, 
                            "贷款和转账日期: ", bestMatchDate
                        )
                        codes[0].append(subG[bestMatchF][n][k1]["txnCode"])
                        codes[1].append(subG[n][bestMatchC][k2]["txnCode"])
                        se.add_edge(
                            bestMatchF, 
                            n, 
                            txnAmount=bestMatchLoan, 
                            isLoan=0, 
                            txnDateTime=bestMatchDate[0], 
                            txnCode=subG[bestMatchF][n][k1]["txnCode"], 
                            width=subG[bestMatchF][n][k1]["width"]
                        )
                        se.add_edge(
                            n, 
                            bestMatchC, 
                            txnAmount=bestMatchTxn, 
                            isLoan=1, 
                            txnDateTime=bestMatchDate[1], 
                            txnCode=subG[n][bestMatchC][k2]["txnCode"], 
                            width=subG[n][bestMatchC][k2]["width"]
                        )
                        seNodes[0].append(bestMatchF)
                        seNodes[1].append(n)
                        seNodes[2].append(bestMatchC)
    if (nx.number_of_nodes(se)):
        print("资金归集三元组关系数量：", se.size() / 2)
        print("所有处于资金归集三元组中的企业总数", nx.number_of_nodes(se))
        seNodes = [list(set(seNodes[i])) for i in range(3)]
        codes = [list(set(codes[i])) for i in range(2)]
        print("筛选后贷款的交易码含有：", codes[0])
        print("筛选后转账的交易码含有：", codes[1])
        print("具有资金归集行为的提供贷款企业数量为：", len(seNodes[0]))
        print("具有资金归集行为的中间企业数量为：", len(seNodes[1]))
        print("具有资金归集行为的接收转账企业数量为：", len(seNodes[2]))
        seNodes = [seNodes[i][j] for i in range(3) for j in range(len(seNodes[i]))]
        print("资金归集的企业列表：", seNodes)
    return se, seNodes


def graphs2json(GList, se, seNodes):
    '''
    将资金归集的识别结果导出为json
    Params:
        se: 按中心企业切分的资金归集识别列表
        seNodes: 中心企业列表
    '''
    collectionList = {"nodes": [], "links": []}
    allList = {"nodes": [], "links": []}
    tmp = {"nodes": [], "links": []}
    i = 0
    Gid = 0  # 子图编号
    allCount = 0
    for item in GList:
        tmp["nodes"], tmp["links"] = [], []
        # 初始化子图数据, 先后加点和边
        for n in item.nodes():
            if item.nodes[n]["netIncome"] >= 0:
                group, c = 3, "pos"
            else:
                group, c = 4, "neg"
            tmp["nodes"].append(
                {"group": group, "class": c, "size": item.nodes[n]["std"], "Gid": Gid, "id": n}
            )
        for u in item.nodes():
            for v in list(item.neighbors(u)):
                for k in item[u][v]:
                    dateTmp = '2020-09-' + str(item[u][v][k]["txnDateTime"])[-2:] 
                    tmp["links"].append(
                        {"source": u, "target": v, "date": dateTmp, "width": item[u][v][k]["width"]}
                    )
        allCount += len(tmp["nodes"])
        # 每个json存储的点不超过1500个
        if allCount >= 1500:
            print("第", i, "个json的节点数量：", len(allList["nodes"]))
            path = "./frontend/public/res/json/moneyCollection/" + "all_" + str(i) + ".json"
            with open(path, "w") as f:
                json.dump(allList, f)
            i += 1
            allCount = 0
            allList["nodes"], allList["links"] = [], []
            allList["nodes"] += tmp["nodes"]
            allList["links"] += tmp["links"]
        else:
            allList["nodes"] += tmp["nodes"]
            allList["links"] += tmp["links"]
        Gid += 1
    # 清空还未存储的点
    if allList["nodes"]:
        print("第", i, "个json的节点数量：", len(allList["nodes"]))
        path = "./frontend/public/res/json/moneyCollection/" + "all_" + str(i) + ".json"
        with open(path, "w") as f:
            json.dump(allList, f)
    # 存储具有资金归集行为的点
    for n in se.nodes():
        group, c = 2, "end"
        if n in seNodes[1]:
            group, c = 1, "mid"
        elif n in seNodes[0]:
            group, c = 0, "start"
        collectionList["nodes"].append({"group": group, "class": c, "size": 9, "Gid": Gid, "id": n})
        Gid += 1
    for u in se.nodes():
        for v in list(se.neighbors(u)):
            for k in se[u][v]:
                collectionList["links"].append(
                    {"source": u, "target": v, "width": se[u][v][k]["width"]}
                )
    print("存储具有资金归集行为企业信息的json的节点数量：", len(collectionList["nodes"]))
    with open(r"./frontend/public/res/json/moneyCollection/moneyCollection.json", "w") as f:
        json.dump(collectionList, f)
    print("----------资金归集json数据导出完成----------")


def ansJson(seNodes):
    '''
    将资金归集的识别结果导出为json
    Params:
        se: 按中心企业切分的资金归集识别列表
        seNodes: 中心企业列表
    '''
    with open(r"./answers/moneyCollection/moneyCollection.json", "w") as f:
        json.dump({"list": seNodes}, f)