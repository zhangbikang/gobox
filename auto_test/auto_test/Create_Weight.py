import json
import pymysql
import random

class create_weight():
    def __init__(self,*drift_weight):
        self.drift_weight_org=drift_weight[0]
        self.drift_weight=[]
        for i in range(5):
            sub_drift_weight_value = []
            for j in range(3):
                drift_value=random.choice(self.drift_weight_org)
                sub_drift_weight_value.append(drift_value)
            self.drift_weight.append(sub_drift_weight_value)
        self.sku_weight = [[0 for n in range(3)] for n in range(5)]
    def calc_weight(self):
        for f in range(0, 5):
            count_loop = True
            while count_loop:
                for i in range(0, 3):
                    self.sku_weight[f][i] = random.randint(60, 1500)
                cpa = self.sku_weight[f]
                suk_min = 0
                for x in range(0, 3):
                    for y in range(x + 1, 3):
                        if cpa[x] > cpa[y]:
                            sku_min = cpa[y]
                            cpa[y] = cpa[x]
                            cpa[x] = sku_min
                self.sku_weight[f] = cpa
                count_loop = self.multiple(f)
        return (self.sku_weight,self.drift_weight)

    def multiple(self,list_lindex):
        sku_weigh_list=self.sku_weight[list_lindex]
        sku_drift_list=self.drift_weight[list_lindex]
        A_weight = sku_weigh_list[0]
        B_weight = sku_weigh_list[1]
        C_weight = sku_weigh_list[2]
        A_weight_drift = sku_drift_list[0]
        B_weight_drift = sku_drift_list[1]
        C_weight_drift = sku_drift_list[2]
        for i in range(1, 4):
            for n in range(1, 4):
                for m in range(1, 4):
                    A_rg = range((i * A_weight - i * A_weight_drift), (i * A_weight + i * A_weight_drift))
                    B_rg = range((n * B_weight - n * B_weight_drift), (n * B_weight + n * B_weight_drift))
                    C_rg = range((m * C_weight - m * C_weight_drift), (m * C_weight + m * C_weight_drift))
                    AB_cp = [val for val in A_rg if val in B_rg]
                    AC_cp = [val for val in A_rg if val in C_rg]
                    BC_cp = [val for val in B_rg if val in C_rg]
                    if len(AB_cp) or len(AC_cp) or len(BC_cp):
                        return True
        AB_ad = range((A_weight + B_weight - A_weight_drift - B_weight_drift),
                      (A_weight + B_weight + A_weight_drift + B_weight_drift))
        AC_ad = range((A_weight + C_weight - A_weight_drift - C_weight_drift),
                      (A_weight + C_weight + A_weight_drift + C_weight_drift))
        BC_ad = range((C_weight + B_weight - C_weight_drift - B_weight_drift),
                      (C_weight + B_weight + C_weight_drift + B_weight_drift))
        for j in range(1, 9):
            A_ad_rg = range((j * A_weight - j * A_weight_drift), (j * A_weight + j * A_weight_drift))
            B_ad_rg = range((j * B_weight - j * B_weight_drift), (j * B_weight + j * B_weight_drift))
            C_ad_rg = range((j * C_weight - j * C_weight_drift), (j * C_weight + j * C_weight_drift))
            AB_C_cp = [val for val in AB_ad if val in C_ad_rg]
            AC_B_cp = [val for val in AC_ad if val in B_ad_rg]
            BC_A_cp = [val for val in BC_ad if val in A_ad_rg]
            if len(AB_C_cp) or len(AC_B_cp) or len(BC_A_cp):
                return True
