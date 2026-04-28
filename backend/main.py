"""企业关联图谱风险控制——数据处理入口。

使用方法: 在项目根目录执行
    python -m backend.main
"""
from . import control, guarantee, moneyCollection

if __name__ == "__main__":
    # 控制人表
    controlG = control.getInitControlG("backend/res/control.csv")
    controlRootG = control.getRootOfControlG(controlG)
    control.graphs2json(controlRootG)
    control.ansJson(controlRootG)

    # 担保关系表
    guaranteeG = guarantee.getInitGuaranteeG("backend/res/guarantee.csv")
    guaranteeRiskG = guarantee.markRiskOfGuaranteeG(guaranteeG)
    guarantee.riskQuantification(guaranteeRiskG)
    guarantee.graphs2json(guaranteeRiskG)
    guarantee.ansJson(guaranteeRiskG)

    # 资金归集表
    moneyCollectionCut = moneyCollection.getInitmoneyCollectionG("backend/res/moneyCollection.csv")
    se, seNodes = moneyCollection.findShellEnterprise(moneyCollectionCut)
    moneyCollection.getNetIncome(moneyCollectionCut)
    moneyCollection.graphs2json(moneyCollectionCut, se, seNodes)
    moneyCollection.ansJson(seNodes)
