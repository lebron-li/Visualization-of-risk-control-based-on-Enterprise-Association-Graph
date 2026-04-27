import os
import json
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


def getInitGuaranteeG(path):
    """
    读取担保关系的excel表格到DataFrame, 并切分子图
    Params:
        path: 含有担保关系数据的excel表格
    Returns: 
        subG: 根据表格数据切分得到的子图集合, 每个元素都是一副子图
    """
    guarantee = pd.read_csv(path, encoding="gb2312")
    guarantee.columns = ["src", "destn", "time", "guarType", "amount"]
    # 担保金额为0的样本视为无效的担保, 直接删去, 可减少870条边
    guarantee = guarantee[~guarantee["amount"].isin([0])]

    # 构建初始图G
    G = nx.DiGraph()
    for _, row in guarantee.iterrows():
        G.add_node(row["src"], guarType=[], m=0.0, std=0.0)
        G.add_node(row["destn"], guarType=[], m=0.0, std=0.0)
        G.add_edge(
            row["src"],
            row["destn"],
            guarType=row["guarType"],
            amount=row["amount"],
            mij=0,
        )
    # 切分子图
    tmp = nx.to_undirected(G)
    subG = list()
    for c in nx.connected_components(tmp):
        subG.append(G.subgraph(c))
    print("----------初始化子图信息完成----------")
    print("有效担保关系节点总数：", nx.number_of_nodes(G))
    print("有效担保关系边总数：", nx.number_of_edges(G))
    print("切分子图数量：", len(subG))
    return subG


def markRiskOfGuaranteeG(GList):
    """
    标记担保关系图的风险
    Params:
        GList: 担保关系子图列表
    Output:
        GList: 更新担保关系的列表
    """
    for subG in GList:
        # 双节点的子图, 仅可能为普通担保或互保
        if subG.number_of_nodes() == 2:
            # 普通担保判定
            if nx.is_tree(subG):
                for n in subG.nodes():
                    subG.nodes[n]["guarType"].append("Normal")
            # 互保判定
            else:
                for n in subG.nodes():
                    subG.nodes[n]["guarType"].append("Mutual")
        # 多于2个节点的情形, 标记节点所属的担保关系类型
        for u, v in subG.edges:
            # 贪心策略: u为源点，则认为u更有可能为Cross; v为终点，则认为v更有可能成为Focus
            # 原图中标记为Cross的边, 形如u为交通枢纽, 即u的度较大
            # 一保多(星型担保 or 担保公司)
            if subG.out_degree(u) >= 3 and "Cross" not in subG.nodes[u]["guarType"]:
                subG.nodes[u]["guarType"].append("Cross")
            # 原图中标记为Focus的边, 形如多个节点指向一个节点
            # 多保一(联合担保)
            if subG.in_degree(v) >= 3 and "Focus" not in subG.nodes[v]["guarType"]:
                subG.nodes[v]["guarType"].append("Focus")
        # 担保圈, 直接通过边属性检查, 经检验只有两个子图含有Circle标记, 但元数据的标记不准确
        # 分别进行正向和逆向的拓扑排序检查, 可以找到遗漏的担保圈和互保关系
        tmpG = nx.DiGraph(subG)
        flag = True
        while flag:
            flag = False
            l = list()
            for n in tmpG.nodes():
                if tmpG.in_degree(n) == 0:
                    l.append(n)
                    flag = True
            tmpG.remove_nodes_from(l)
        # 将边逆向, 再次拓扑排序
        tmpG = nx.reverse(tmpG)
        flag = True
        while flag:
            flag = False
            l = list()
            for n in tmpG.nodes():
                if tmpG.in_degree(n) == 0:
                    l.append(n)
                    flag = True
            tmpG.remove_nodes_from(l)
        # 拓扑排序后图非空说明含有担保圈或互保关系
        if nx.number_of_nodes(tmpG):
            # 互保判定
            for u, v in tmpG.edges():
                if tmpG.has_edge(v, u):
                    if "Mutual" not in subG.nodes[u]["guarType"]:
                        subG.nodes[u]["guarType"].append("Mutual")
                    if "Mutual" not in subG.nodes[v]["guarType"]:
                        subG.nodes[v]["guarType"].append("Mutual")
            # 担保圈判定
            visited = list()
            trace = list()

            def dfs2FindCircle(node):
                """
                用回溯法找环
                Params:
                    node: 子图的起始搜索节点
                """
                if node in visited:
                    if node in trace:
                        trace_index = trace.index(node)
                        # 双节点的互保不作为担保圈进行标记
                        if len(trace) - trace_index > 2:
                            for i in range(trace_index, len(trace)):
                                if "Circle" not in subG.nodes[trace[i]]["guarType"]:
                                    subG.nodes[trace[i]]["guarType"].append("Circle")
                    return
                visited.append(node)
                trace.append(node)
                for child in list(tmpG.neighbors(node)):
                    dfs2FindCircle(child)
                trace.pop()

            dfs2FindCircle(list(tmpG.nodes())[0])
        # 担保链: 若节点均不属于上述情况则该节点为担保链上的点
        for u, v in subG.edges():
            if not subG.nodes[u]["guarType"] and "Chain" not in subG.nodes[u]["guarType"]:
                subG.nodes[u]["guarType"].append("Chain")
            if not subG.nodes[v]["guarType"] and "Chain" not in subG.nodes[v]["guarType"]:
                    subG.nodes[v]["guarType"].append("Chain")
    print("----------担保关系识别完成----------")
    return GList


def riskQuantification(subG):
    """
    标记节点的风险值m
    Params:
        G: 子图列表
    Outputs:
        G: 标记各个节点风险值m后的子图列表
    """
    for G in subG:
        de = dict()
        tmpG = nx.Graph(G)
        txnAllSum = sum(nx.get_edge_attributes(tmpG, "amount").values())
        for n in tmpG.nodes():
            neighbors = tmpG.adj[n].keys()
            de[n] = sum(tmpG[n][neighbor]["amount"] / txnAllSum for neighbor in neighbors)
            G.nodes[n]["m"] = de[n]
        maxM, minM = max(de.values()), min(de.values())
        if maxM == minM:
            for n in G.nodes():
                G.nodes[n]["std"] = 15
        else:
            k = 20/(maxM - minM)
            for n in G.nodes():
                G.nodes[n]["std"] = 5 + k * (G.nodes[n]["m"] - minM)
    print("----------m值计算完成----------")



def graphs2json(GList):
    """
    将图数据输出为前端可视化用的json文件
    Params:
        GList: 图数据
    Outputs:
        输出转化后的json文件到filePath1和filepath2下
    """
    circleList = {"links": [], "nodes": []}
    mutualList = {"links": [], "nodes": []}
    crossList = {"links": [], "nodes": []}
    focusList = {"links": [], "nodes": []}
    doubleNormalList = {"links": [], "nodes": []}
    multiNormalList = {"links": [], "nodes": []}
    Gid = 0  # 子图编号
    doubleCount = 0
    i = 0
    c = ["doubleRisk", "tripleRisk", "quadraRisk"]
    offsetDict = {"Chain": 0, "Mutual": 1, "Focus": 2, "Cross": 3,"Circle": 4, "Normal": 5}
    for item in GList:
        # 初始化子图数据, 先后加点和边
        isMutual, isCircle, isCross, isFocus, isUnusual = False, False, False, False, False
        tmp = {"links": [], "nodes": []}
        for n in item.nodes:
            riskCount = len(item.nodes[n]["guarType"]) - 1
            if "Mutual" in item.nodes[n]["guarType"]:
                isMutual, isUnusual = True, True
            if "Focus" in item.nodes[n]["guarType"]:
                isFocus, isUnusual = True, True
            if "Cross" in item.nodes[n]["guarType"]:
                isCross, isUnusual = True, True
            if "Circle" in item.nodes[n]["guarType"]:
                isCircle, isUnusual = True, True
            if riskCount > 0:
                tmp["nodes"].append({
                    "group": riskCount + 5, 
                    "class": c[riskCount-1], 
                    "size": item.nodes[n]["std"], 
                    "ctx": ', '.join(item.nodes[n]["guarType"]), 
                    "Gid": Gid, 
                    "id": n, 
                    "m": item.nodes[n]["m"]
                })
            else:
                tmp["nodes"].append({
                    "group": offsetDict[item.nodes[n]["guarType"][0]], 
                    "class": item.nodes[n]["guarType"][0], 
                    "size": item.nodes[n]["std"], 
                    "ctx": ', '.join(item.nodes[n]["guarType"]), 
                    "Gid": Gid, 
                    "id": n, 
                    "m": item.nodes[n]["m"]
                })
        # 加边
        for u, v in item.edges:
            tmp["links"].append({
                "source": u, 
                "target": v, 
                "amount": item[u][v]["amount"]
            })
        # 存到对应类型的json中
        if isUnusual:
            if isCircle:
                circleList["nodes"] += (tmp["nodes"])
                circleList["links"] += (tmp["links"])
            if isMutual:
                mutualList["nodes"] += (tmp["nodes"])
                mutualList["links"] += (tmp["links"])
            if isCross:
                crossList["nodes"] += (tmp["nodes"])
                crossList["links"] += (tmp["links"])
            if isFocus:
                focusList["nodes"] += (tmp["nodes"])
                focusList["links"] += (tmp["links"])
        else:  # "Chain"
            if nx.number_of_nodes(item) == 2:
                doubleCount += 2
                if doubleCount < 2950:
                    doubleNormalList["nodes"] += (tmp["nodes"])
                    doubleNormalList["links"] += (tmp["links"])
                else:
                    print("doubleNormalList", len(doubleNormalList["nodes"]))
                    with open("./frontend/public/res/json/guarantee/doubleNormal_" + str(i) + ".json", "w") as f:
                        json.dump(doubleNormalList, f)
                    i += 1
                    doubleCount = 2
                    doubleNormalList = {"links": [], "nodes": []}
                    doubleNormalList["nodes"] += (tmp["nodes"])
                    doubleNormalList["links"] += (tmp["links"])
            else:
                multiNormalList["nodes"] += (tmp["nodes"])
                multiNormalList["links"] += (tmp["links"])
        Gid += 1
    # 将剩余的双节点子图存到下一个json中
    if doubleNormalList["nodes"]:
        print("doubleNormalList", len(doubleNormalList["nodes"]))
        with open("./frontend/public/res/json/guarantee/doubleNormal_" + str(i) + ".json", "w") as f:
            json.dump(doubleNormalList, f)
    print("circleList", len(circleList["nodes"]))
    print("mutualList", len(mutualList["nodes"]))
    print("crossList", len(crossList["nodes"]))
    print("focusList", len(focusList["nodes"]))
    print("multiNormalList", len(multiNormalList["nodes"]))
    # 将上述数据写入文件
    with open(r"./frontend/public/res/json/guarantee/circle.json", "w") as f:
        json.dump(circleList, f)
    with open(r"./frontend/public/res/json/guarantee/mutual.json", "w") as f:
        json.dump(mutualList, f)
    with open(r"./frontend/republic/res/jsons/guarantee/cross.json", "w") as f:
        json.dump(crossList, f)
    with open(r"./frontend/public/res/json/guarantee/focus.json", "w") as f:
        json.dump(focusList, f)
    with open(r"./frontend/public/res/json/guarantee/multiNormal.json", "w") as f:
        json.dump(multiNormalList, f)
    print("----------担保关系的json导出完成完成----------")


def ansJson(GList):
    """
    将图数据输出为答案的json文件
    Params:
        GList: 图数据
    Outputs:
        输出转化后的json文件到filePath1和filepath2下
    """
    circleList = {"links": [], "nodes": []}
    mutualList = {"links": [], "nodes": []}
    crossList = {"links": [], "nodes": []}
    focusList = {"links": [], "nodes": []}
    doubleNormalList = {"links": [], "nodes": []}
    multiNormalList = {"links": [], "nodes": []}
    Gid = 0  # 子图编号
    c = ["doubleRisk", "tripleRisk", "quadraRisk"]
    for item in GList:
        # 初始化子图数据, 先后加点和边
        isMutual, isCircle, isCross, isFocus, isUnusual = False, False, False, False, False
        tmp = {"links": [], "nodes": []}
        for n in item.nodes:
            riskCount = len(item.nodes[n]["guarType"]) - 1
            # Chain补入
            if nx.number_of_nodes(item) > 2 and "Chain" not in item.nodes[n]["guarType"]:
                ctx = ', '.join(item.nodes[n]["guarType"]) + ', Chain'
            else:
                ctx = ', '.join(item.nodes[n]["guarType"])
            if "Mutual" in item.nodes[n]["guarType"]:
                isMutual, isUnusual = True, True
            if "Focus" in item.nodes[n]["guarType"]:
                isFocus, isUnusual = True, True
            if "Cross" in item.nodes[n]["guarType"]:
                isCross, isUnusual = True, True
            if "Circle" in item.nodes[n]["guarType"]:
                isCircle, isUnusual = True, True
            if riskCount > 0:
                tmp["nodes"].append({
                    "class": c[riskCount-1], 
                    "ctx": ctx, 
                    "Gid": Gid, 
                    "id": n, 
                    "m": item.nodes[n]["m"]
                })
            else:
                tmp["nodes"].append({
                    "class": item.nodes[n]["guarType"][0], 
                    "ctx": ctx, 
                    "Gid": Gid, 
                    "id": n, 
                    "m": item.nodes[n]["m"]
                })
        # 加边
        for u, v in item.edges:
            tmp["links"].append({
                "source": u, 
                "target": v, 
                "amount": item[u][v]["amount"]
            })
        # 存到对应类型的json中
        if isUnusual:
            if isCircle:
                circleList["nodes"] += (tmp["nodes"])
                circleList["links"] += (tmp["links"])
            if isMutual:
                mutualList["nodes"] += (tmp["nodes"])
                mutualList["links"] += (tmp["links"])
            if isCross:
                crossList["nodes"] += (tmp["nodes"])
                crossList["links"] += (tmp["links"])
            if isFocus:
                focusList["nodes"] += (tmp["nodes"])
                focusList["links"] += (tmp["links"])
        else:  # "Chain"
            if nx.number_of_nodes(item) == 2:
                doubleNormalList["nodes"] += (tmp["nodes"])
                doubleNormalList["links"] += (tmp["links"])
            else:
                multiNormalList["nodes"] += (tmp["nodes"])
                multiNormalList["links"] += (tmp["links"])
        Gid += 1
    print("circleList", len(circleList["nodes"]))
    print("mutualList", len(mutualList["nodes"]))
    print("crossList", len(crossList["nodes"]))
    print("focusList", len(focusList["nodes"]))
    print("multiNormalList", len(multiNormalList["nodes"]))
    # 将上述数据写入文件
    with open(r"./answers/guarantee/circle.json", "w") as f:
        json.dump(circleList, f)
    with open(r"./answers/guarantee/mutual.json", "w") as f:
        json.dump(mutualList, f)
    with open(r"./answers/guarantee/cross.json", "w") as f:
        json.dump(crossList, f)
    with open(r"./answers/guarantee/focus.json", "w") as f:
        json.dump(focusList, f)
    with open(r"./answers/guarantee/doubleNormal.json", "w") as f:
        json.dump(doubleNormalList, f)
    with open(r"./answers/guarantee/multiNormal.json", "w") as f:
        json.dump(multiNormalList, f)
    print("----------担保关系的json导出完成完成----------")