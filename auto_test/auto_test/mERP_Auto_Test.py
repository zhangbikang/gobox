# -*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
import urllib
from http import cookiejar
import json
import time
import pymysql
import random
from auto_test.Create_Weight import create_weight
from auto_test.write_job_suite import operator_suite_log
from auto_test.mERP_Operation import mERP_operation

class merp_auto_test():
    def __init__(self,url,login_name,login_pw,env,db_name, job_name):
        self.mERP=mERP_operation(str(url), str(login_name), str(login_pw),int(env))
        self.save_log=operator_suite_log(str(db_name), str(job_name))
        drift_weight = [5, 10, 15, 20, 25, 30]
        clac_sku_weight = create_weight(drift_weight)
        sku_weight_drift_group = clac_sku_weight.calc_weight()
        self.sku_weight_list = sku_weight_drift_group[0]
        self.sku_drift_list  = sku_weight_drift_group[1]
    def goods_operation(self,barcode_list):
        # 创建商品到ERP
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print("11111111111")
        layer_count = 0
        weight_count = 0
        add_goods_control = True
        for i in range(len(barcode_list)):
            if i > 1:
                if i % 3 == 0:
                    layer_count += 1
            barcode = barcode_list[i]
            base_weight = self.sku_weight_list[layer_count][weight_count]
            weight_drift = self.sku_drift_list [layer_count][weight_count]
            add_sku_result = self.mERP.add_goods(barcode, base_weight, weight_drift)
            print(add_sku_result)
            if add_sku_result[0] != "Pass":
                add_goods_control = False
                break
            weight_count += 1
            if weight_count % 3 == 0:
                weight_count = 0
            time.sleep(5)
        if add_goods_control:
            self.save_log.write_case("0", "add_goods", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "add_goods", "Fail", add_sku_result[1], case_tm)
        time.sleep(20)
        # 商品库里查询商品，更新商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sku_result_org = self.mERP.query_goods()
        query_sku_result_status = query_sku_result_org[0]
        if query_sku_result_status == "Pass":
            self.save_log.write_case("0", "query_goods", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "query_goods", "Fail", query_sku_result_org[1], case_tm)
        time.sleep(20)
        # 更新商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if query_sku_result_status == "Pass":
            query_sku_result_date = query_sku_result_org[1]
            for i in range(len(query_sku_result_date)):
                goods_info = query_sku_result_date[i]
                if goods_info["barcode"] == barcode_list[0]:
                    update_goods_date = goods_info
                    break
            update_goods_date["brand"] = "update_ustar"
            update_goods_result = self.mERP.update_goods(**update_goods_date)
            if update_goods_result[0] == "Pass":
                self.save_log.write_case("0", "update_goods", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "update_goods", "Fail", update_goods_result[1], case_tm)
        time.sleep(20)
        # 商品入库
        update_stock_control = True
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        for i in range(len(barcode_list)):
            add_stock_reslut = self.mERP.update_stock(str(barcode_list[i]), "1", "1000")
            if add_stock_reslut[0] != "Pass":
                update_stock_control = False
                break
            time.sleep(5)
        if update_stock_control:
            self.save_log.write_case("0", "add_goods_stock", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "add_goods_stock", "Fail", add_stock_reslut[1], case_tm)
        time.sleep(20)
        # 商品出库
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_stock_reslut = self.mERP.update_stock(barcode_list[0], 2, 100)
        if update_goods_result[0] == "Pass":
            self.save_log.write_case("0", "update_goods_stock", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_goods_stock", "Fail", update_stock_reslut[1], case_tm)
        time.sleep(20)
        # 删除商品
        sub_barcode = []
        sub_barcode.append(barcode_list[0])
        delete_goods_result = self.mERP.delete_goods(*sub_barcode)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if delete_goods_result[0] == "Pass":
            self.save_log.write_case("0", "delete_goods_stock", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "delete_goods_stock", "Fail", delete_goods_result[1], case_tm)

        time.sleep(20)
        # 恢复添加删除的商品，入库
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        add_goods_reslut = self.mERP.add_goods(barcode_list[0], self.sku_weight_list[0][0], self.sku_drift_list [0][0])
        if add_goods_reslut[0] == "Pass":
            add_stock_again_reslut = self.mERP.update_stock(barcode_list[0], 1, 100)
            if add_stock_again_reslut[0] == "Pass":
                self.save_log.write_case("0", "add_goods_stock_again", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "add_goods_stock_again", "Fail", add_goods_reslut[1], case_tm)
        else:
            self.save_log.write_case("0", "add_goods_again", "Fail", add_goods_reslut[1], case_tm)
        time.sleep(20)
    def template_operation(self,template_date, barcode_list, dev_date):
        # 添加模板
        add_template_date = {}
        del_template_date = {}
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        add_template_date["command"] = "add_dev_profile"
        add_template_date["profile_dev_type"] = template_date["profile_dev_type"]
        add_template_date["box_model"] = template_date["box_model"]
        add_template_date["profile_name"] = "auto_test"
        add_template_date["weigh_type"] = template_date["weigh_type"]
        add_template_result = self.mERP.add_delete_template(**add_template_date)
        if add_template_result[0] == "Pass":
            self.save_log.write_case("0", "add_template", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "add_template", "Fail", add_template_result, case_tm)
        time.sleep(20)
        # 查询模板
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_template_result_org = self.mERP.query_templates_all()
        if query_template_result_org[0] == "Pass":
            query_template_result_name = query_template_result_org[1]
            find_init = False
            for i in range(len(query_template_result_name)):
                if query_template_result_name[i]["profile_name"] == "auto_test" and int(
                        query_template_result_name[i]["box_model"]) == int(template_date["box_model"]) \
                        and int(query_template_result_name[i]["profile_dev_type"]) == int(
                    template_date["profile_dev_type"]) and int(query_template_result_name[i]["weigh_type"]) == int(
                    template_date["weigh_type"]):
                    find_init = True
                    break
            if find_init:
                self.save_log.write_case("0", "query_template", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_template", "Fail", query_template_result_name[i], case_tm)
        else:
            self.save_log.write_case("0", "query_template", "Fail", query_template_result_org, case_tm)
        # 删除模板
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        del_template_date["command"] = "del_dev_profile"
        del_template_date["profile_name"] = "auto_test"
        del_template_result = self.mERP.add_delete_template(**del_template_date)
        if del_template_result[0] == "Pass":
            self.save_log.write_case("0", "del_template", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "del_template", "Fail", del_template_result[1], case_tm)
        time.sleep(20)
        # 模板添加商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        add_template_result = self.mERP.add_delete_template(**add_template_date)
        template_add_sku_contorl = False
        if add_template_result[0] == "Pass":
            box_mode = dev_date["box_model"]
            if int(box_mode) == 3:
                layer_count = 4
                pos_id_list = ["010101", "010201", "010301", "010401"]
            elif int(box_mode) == 1 or int(box_mode) == 2:
                layer_count = 5
                pos_id_list = ["010101", "010201", "010301", "010401", "010501"]
            goods_count = 0
            for i in range(layer_count):
                for j in range(3):
                    add_template_sku_result = self.mERP.add_delete_sku_template("add_dev_sku", pos_id_list[i],
                                                                           barcode_list[goods_count], 0, "auto_test")
                    if add_template_sku_result[0] != "Pass":
                        template_add_sku_contorl = True
                        break
                    goods_count += 1
                    time.sleep(5)
            if template_add_sku_contorl:
                self.save_log.write_case("0", "add_template_sku", "Fail", add_template_sku_result[1], case_tm)
            else:
                self.save_log.write_case("0", "add_template_sku", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "add_template_sku", "Fail", add_template_result[1], case_tm)
            time.sleep(20)
        # 查询模板配置商品：
        query_template_sku_result = self.mERP.query_template_detail("auto_test")
        if query_template_sku_result[0] == "Pass":
            if len(query_template_sku_result[1]) == (layer_count * 3):
                self.save_log.write_case("0", "query_template_sku", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_template_sku", "Fail", query_template_sku_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_template_sku", "Fail", query_template_sku_result[1], case_tm)
        # 删除模板商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        del_template_sku_result = self.mERP.add_delete_sku_template("update_dev_sku", pos_id_list[0], barcode_list[0], 1,"auto_test")
        if del_template_sku_result[0] == "Pass":
            self.save_log.write_case("0", "del_template_sku", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "del_template_sku", "Fail", del_template_sku_result[1], case_tm)
        # 恢复模板配置
        self.mERP.add_delete_sku_template("add_dev_sku", pos_id_list[0], barcode_list[0], 0, "auto_test")
        time.sleep(20)
    def box_goods_operation(self,template_date, barcode_list):
        # 同步模板
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dev_id = template_date["dev_id"]
        union_id = template_date["union_id"]
        sku_list = []
        query_template_sku_result = self.mERP.query_template_detail("auto_test")
        if query_template_sku_result[0] == "Pass":
            for i in range(len(query_template_sku_result[1])):
                sub_sku_date = {}
                sub_sku_date["pos"] = query_template_sku_result[1][i]["pos"]
                sub_sku_date["barcode"] = query_template_sku_result[1][i]["barcode"]
                sku_list.append(sub_sku_date)
            apply_template_result = self.mERP.apply_template_to_box(dev_id, union_id, *sku_list)
            if apply_template_result[0] == "Pass":
                self.save_log.write_case("0", "apply_template_sku", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "del_template_sku", "Fail", apply_template_result[1], case_tm)
            time.sleep(20)

        # 查询商品信息
        query_box_sku_result = self.mERP.query_dev_sku(dev_id, union_id)
        if query_box_sku_result[0] == "Pass":
            if len(query_box_sku_result[1]) ==16 or len(query_box_sku_result[1]) ==13:
                self.save_log.write_case("0", "query_box_sku", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_box_sku", "Fail", query_box_sku_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_box_sku", "Fail", query_box_sku_result[1], case_tm)
        time.sleep(20)
        # 检查商品同步
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        check_impack_result = self.mERP.check_sku_impact(dev_id)
        if check_impack_result[0] == "Pass":
            self.save_log.write_case("0", "check_sku_impact", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "check_sku_impact", "Fail", check_impack_result, case_tm)
        time.sleep(20)
        # 商品配置同步
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sync_goods_result = self.mERP.sync_config_box(dev_id)
        if sync_goods_result[0] == "Pass":
            self.save_log.write_case("0", "sync_config_box", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "sync_config_box", "Fail", sync_goods_result, case_tm)
        time.sleep(20)
        # 清除商品配置
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        clear_goods_config_result = self.mERP.clear_config_box(dev_id, union_id)
        if clear_goods_config_result[0] == "Pass":
            self.save_log.write_case("0", "clear_config_box", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "clear_config_box", "Fail", clear_goods_config_result[1], case_tm)
        time.sleep(20)
        # 删除模板
        # 删除模板
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        del_template_date = {"command": "del_dev_profile", "profile_name": "auto_test"}
        del_template_result = self.mERP.add_delete_template(**del_template_date)
        if del_template_result[0] == "Pass":
            self.save_log.write_case("0", "del_template", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "del_template", "Fail", del_template_result[1], case_tm)
        time.sleep(20)

        # 货柜增加商品
        add_sku_control = True
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        box_mode = template_date["box_model"]
        if int(box_mode) == 3:
            layer_count = 4
            pos_id_list = ["010101", "010201", "010301", "010401"]
        elif int(box_mode) == 1 or int(box_mode) == 2:
            layer_count = 5
            pos_id_list = ["010101", "010201", "010301", "010401", "010501"]
        goods_count = 0
        for i in range(layer_count):
            for j in range(3):
                add_box_sku_result = self.mERP.operation_sku_box("add", dev_id, union_id, barcode_list[goods_count],
                                                            pos_id_list[i], 0)
                if add_box_sku_result[0] != "Pass":
                    add_sku_control = False
                    break
                goods_count += 1
        time.sleep(20)
        if add_sku_control:
            self.save_log.write_case("0", "add_box_sku", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "add_box_sku", "Fail", add_box_sku_result[1], case_tm)
        time.sleep(20)
        # 上货
        update_add_sku_control = True
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        goods_count = 0
        for i in range(layer_count):
            for j in range(3):
                add_goods_num_result = self.mERP.update_sku_count(union_id, barcode_list[goods_count], pos_id_list[i], 0, 3)
                if add_goods_num_result[0] != "Pass":
                    update_add_sku_control = False
                    break
                goods_count += 1
        time.sleep(5)
        if update_add_sku_control:
            self.save_log.write_case("0", "update_sku_count", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_sku_count_add", "Fail", add_goods_num_result[1], case_tm)

        time.sleep(20)
        # 下货
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        del_goods_num_result = self.mERP.update_sku_count(union_id, barcode_list[0], pos_id_list[0], 1, 3)
        if del_goods_num_result[0] == "Pass":
            self.save_log.write_case("0", "update_sku_count_del", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_sku_count_del", "Fail", del_goods_num_result[1], case_tm)
        # 商品下架
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_goods_result = self.mERP.operation_sku_box("update", dev_id, union_id, barcode_list[0], pos_id_list[0], 2)
        if update_goods_result[0] == "Pass":
            self.save_log.write_case("0", "update_sku_count_update", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_sku_count_update", "Fail", update_goods_result[1], case_tm)
        time.sleep(20)
        # 删除商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        del_goods_result = self.mERP.operation_sku_box("delete", dev_id, union_id, barcode_list[0], pos_id_list[0], 1)
        if del_goods_result[0] == "Pass":
            self.save_log.write_case("0", "update_sku_count_delete", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_sku_count_delete", "Fail", del_goods_result[1], case_tm)
        time.sleep(20)
        # 添加删除的商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        add_box_sku_again_result = self.mERP.operation_sku_box("add", dev_id, union_id, barcode_list[0], pos_id_list[0], 0)
        if add_box_sku_again_result[0] == "Pass":
            self.save_log.write_case("0", "add_box_sku_again", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "add_box_sku_again", "Fail", add_box_sku_again_result[1], case_tm)
        time.sleep(20)
        # 上货
        update_goods_again_result = self.mERP.update_sku_count(union_id, barcode_list[0], pos_id_list[0], 0, 5)
        if update_goods_again_result[0] == "Pass":
            self.save_log.write_case("0", "update_sku_count_again", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_sku_count_again", "Fail", update_goods_again_result[1], case_tm)
        time.sleep(20)
        # 更新商品价格
        update_price_result = self.mERP.update_price_box(dev_id, union_id, barcode_list[0], pos_id_list[0], "2")
        price_check = False
        if update_price_result[0] == "Pass":
            query_actual_price = self.mERP.query_dev_sku(dev_id, union_id)
            if query_actual_price[0] == "Pass":
                for i in range(len(query_actual_price[1])):
                    if query_actual_price[1][i]["barcode"] == barcode_list[0]:
                        if query_actual_price[1][i]["price"] == "2.00":
                            price_check = True
                            break
                time.sleep(5)
            else:
                self.save_log.write_case("0", "query_actual_price", "Fail", query_actual_price[1], case_tm)
            if price_check:
                self.save_log.write_case("0", "update_sku_price", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "update_sku_price", "Fail", query_actual_price[1], case_tm)
        else:
            self.save_log.write_case("0", "update_sku_price", "Fail", update_price_result[1], case_tm)
        time.sleep(20)
        # 价格配置恢复
        update_price_result = self.mERP.update_price_box(dev_id, union_id, barcode_list[0], pos_id_list[0], "0")
        price_check = False
        if update_price_result[0] == "Pass":
            query_actual_price = self.mERP.query_dev_sku(dev_id, union_id)
            if query_actual_price[0] == "Pass":
                for i in range(len(query_actual_price[1])):
                    if query_actual_price[1][i]["barcode"] == barcode_list[0]:
                        if query_actual_price[1][i]["price"] == "0.01":
                            price_check = True
                            break
                    time.sleep(5)
            else:
                self.save_log.write_case("0", "resume_sku_price", "Fail", query_actual_price[1], case_tm)
            if price_check:
                self.save_log.write_case("0", "resume_sku_price", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "resume_sku_price", "Fail", query_actual_price[1], case_tm)

        else:
            self.save_log.write_case("0", "resume_sku_price", "Fail", update_price_result[1], case_tm)
        time.sleep(20)
        # 配置阀值
        config_threshold_result = self.mERP.config_store_threshold(dev_id, union_id, barcode_list[0], pos_id_list[0], 4)
        threshold_check = False
        if config_threshold_result[0] == "Pass":
            query_actual_threshold = self.mERP.query_dev_sku(dev_id, union_id)
            if query_actual_threshold[0] == "Pass":
                for i in range(len(query_actual_threshold[1])):
                    if query_actual_threshold[1][i]["barcode"] == barcode_list[0]:
                        if int(query_actual_threshold[1][i]["reserve_thr"]) == 4:
                            threshold_check = True
                            break
                    time.sleep(5)
            else:
                self.save_log.write_case("0", "config_store_threshold", "Fail", query_actual_threshold[1], case_tm)
            if threshold_check:
                self.save_log.write_case("0", "config_store_threshold", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "config_store_threshold", "Fail", query_actual_threshold[1], case_tm)
        else:
            self.save_log.write_case("0", "config_store_threshold", "Fail", config_threshold_result[1], case_tm)
        time.sleep(20)
        # 门限配置恢复
        resume_threshold_result = self.mERP.config_store_threshold(dev_id, union_id, barcode_list[0], pos_id_list[0], 0)
        threshold_check = False
        if resume_threshold_result[0] == "Pass":
            query_actual_threshold = self.mERP.query_dev_sku(dev_id, union_id)
            if query_actual_threshold[0] == "Pass":
                for i in range(len(query_actual_threshold[1])):
                    if query_actual_threshold[1][i]["barcode"] == barcode_list[0]:
                        if int(query_actual_threshold[1][i]["reserve_thr"]) == 0:
                            threshold_check = True
                            break
                    time.sleep(5)
            else:
                self.save_log.write_case("0", "resume_store_threshold", "Fail", query_actual_threshold[1], case_tm)
            if threshold_check:
                self.save_log.write_case("0", "resume_store_threshold", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "resume_store_threshold", "Fail", query_actual_threshold[1], case_tm)
        else:
            self.save_log.write_case("0", "resume_store_threshold", "Fail", resume_threshold_result[1], case_tm)
        time.sleep(20)

        # 商品语音更新
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_goods_mp3_result = self.mERP.update_goods_mp3(union_id, barcode_list[0])
        if update_goods_mp3_result[0] == "Pass":
            self.save_log.write_case("0", "update_goods_mp3", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_goods_mp3", "Fail", update_goods_mp3_result[1], case_tm)
        time.sleep(20)
    def stoke_management(self,barcode_list, dev_id, query_start_time, query_end_time):
        # 仓库库存
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_stoke_store_all = self.mERP.query_goods_store()
        if query_stoke_store_all[0] == "Pass":
            if len(query_stoke_store_all[1]) > 1:
                self.save_log.write_case("0", "query_goods_store", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store", "Fail", query_stoke_store_all[1], case_tm)
        time.sleep(20)
        # 按照barcode查询库存
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_list = {}
        stoke_query_status = True
        for i in range(len(barcode_list)):
            query_list["barcode_contain"] = barcode_list[i]
            query_stoke_store_by_barcode = self.mERP.query_goods_store(**query_list)
            if len(query_stoke_store_by_barcode[1]) != 1:
                stoke_query_status = False
                break
            time.sleep(5)
        if stoke_query_status:
            self.save_log.write_case("0", "query_stoke_store_by_barcode", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "query_stoke_store_by_barcode", "Fail", query_stoke_store_by_barcode[1], case_tm)
        time.sleep(20)
        # 查询库存按照名字
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_name_list = {"name": "测试商品"}
        query_stoke_name = self.mERP.query_goods_store(**query_name_list)
        if query_stoke_name[0] == "Pass":
            if len(query_stoke_name[1]) > 1:
                self.save_log.write_case("0", "query_stoke_store_by_name", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_stoke_store_by_name", "Fail", query_stoke_name[1], case_tm)
        else:
            self.save_log.write_case("0", "query_stoke_store_by_barcode", "Fail", query_stoke_name[1], case_tm)
        time.sleep(20)
        # 查询库存按照名字和barcode
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_list_name_barcode = {}
        query_list_name_barcode["name"] = "测试商品"
        query_list_name_barcode["barcode_contain"] = "1234567890123"
        stoke_query_status = True
        for i in range(len(barcode_list)):
            query_list_name_barcode["barcode_contain"] = barcode_list[i]
            query_stoke_name_barcode = self.mERP.query_goods_store(**query_list_name_barcode)
            if len(query_stoke_name_barcode[1]) != 1:
                stoke_query_status = False
                break
            time.sleep(5)
        if stoke_query_status:
            self.save_log.write_case("0", "query_stoke_store_by_name_barcode", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "query_stoke_store_by_name", "Fail", query_stoke_name_barcode[1], case_tm)
        time.sleep(20)
        # 查询仓库流水
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_stock_inventory_result = self.mERP.query_goods_store_inventory(query_start_time, query_end_time)
        if query_stock_inventory_result[0] == "Pass":
            if len(query_stock_inventory_result[1]) > 1:
                self.save_log.write_case("0", "query_stock_inventory", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_stock_inventory", "Pass", query_stock_inventory_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_stock_inventory", "Fail", query_stock_inventory_result[1], case_tm)
        time.sleep(20)
        # 查询仓库按照设备ID
        dev_dict = {"dev_list": [dev_id]}
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_stock_inventory_by_dev_id_result = self.mERP.query_goods_store_inventory(query_start_time, query_end_time,
                                                                                  **dev_dict)
        if query_stock_inventory_by_dev_id_result[0] == "Pass":
            if len(query_stock_inventory_by_dev_id_result[1]) > 1:
                self.save_log.write_case("0", "query_stock_by_id_inventory", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_stock_by_id_inventory", "Pass",
                                    query_stock_inventory_by_dev_id_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_stock_by_id_inventory", "Fail", query_stock_inventory_by_dev_id_result[1],
                                case_tm)
        time.sleep(20)
        # 查询货柜库存
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_result = self.mERP.query_goods_store_box()
        if query_goods_store_box_result[0] == "Pass":
            if len(query_goods_store_box_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box", "Pass", query_goods_store_box_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box", "Fail", query_goods_store_box_result[1], case_tm)
        time.sleep(20)
        # 查询货柜库存按照设备ID
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_by_dev_result = self.mERP.query_goods_store_box(**dev_dict)
        if query_goods_store_box_by_dev_result[0] == "Pass":
            if len(query_goods_store_box_by_dev_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box_by_dev", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_by_dev", "Pass", query_goods_store_box_by_dev_result[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_by_dev", "Fail", query_goods_store_box_by_dev_result[1],
                                case_tm)
        time.sleep(20)
        # 查询货柜库存按照域名
        domain_name = {"domain_name": "auto_test"}
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_by_domain_result = self.mERP.query_goods_store_box(**domain_name)
        if query_goods_store_box_by_domain_result[0] == "Pass":
            if len(query_goods_store_box_by_domain_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_by_domain", "Pass",
                                    query_goods_store_box_by_domain_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_by_domain", "Fail", query_goods_store_box_by_domain_result[1],
                                case_tm)
        time.sleep(20)
        # 查询货柜库存按照id和domain
        dev_domain = {"dev_list": [int(dev_id)], "domain_name": "auto_test"}
        query_goods_store_box_by_id_domain_result = self.mERP.query_goods_store_box(**dev_domain)
        if query_goods_store_box_by_id_domain_result[0] == "Pass":
            if len(query_goods_store_box_by_id_domain_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box_by_id_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_by_id_domain", "Pass",
                                    query_goods_store_box_by_id_domain_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_by_id_domain", "Fail",
                                query_goods_store_box_by_id_domain_result[1], case_tm)
        time.sleep(20)
        # 查询货柜库存流水
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_inventory_result = self.mERP.query_goods_box_inventory(query_start_time, query_end_time)
        if query_goods_store_box_inventory_result[0] == "Pass":
            if len(query_goods_store_box_inventory_result[1]) >= 16:
                self.save_log.write_case("0", "query_goods_store_box_inventory", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_inventory", "Pass",
                                    query_goods_store_box_inventory_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_inventory", "Fail", query_goods_store_box_inventory_result[1],
                                case_tm)
        time.sleep(20)
        # 查询货柜流水按照设备号
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_by_id_inventory_result = self.mERP.query_goods_box_inventory(query_start_time, query_end_time,
                                                                                      **dev_dict)
        if query_goods_store_box_by_id_inventory_result[0] == "Pass":
            if len(query_goods_store_box_by_id_inventory_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box_by_id_inventory", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_by_id_inventory", "Pass",
                                    query_goods_store_box_by_id_inventory_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_by_id_inventory", "Fail",
                                query_goods_store_box_by_id_inventory_result[1], case_tm)
        time.sleep(20)
        # 查询货柜流水按照domain
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_by_domain_inventory_result = self.mERP.query_goods_box_inventory(query_start_time,
                                                                                          query_end_time, **domain_name)
        if query_goods_store_box_by_domain_inventory_result[0] == "Pass":
            if len(query_goods_store_box_by_domain_inventory_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box_by_domain_inventory", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_by_domain_inventory", "Pass",
                                    query_goods_store_box_by_domain_inventory_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_by_domain_inventory", "Fail",
                                query_goods_store_box_by_domain_inventory_result[1], case_tm)
        time.sleep(20)
        # 查询货柜流水按照domain和id

        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_store_box_by_id_domain_inventory_result = self.mERP.query_goods_box_inventory(query_start_time,
                                                                                             query_end_time,
                                                                                             **dev_domain)
        if query_goods_store_box_by_id_domain_inventory_result[0] == "Pass":
            if len(query_goods_store_box_by_id_domain_inventory_result[1]) >= 12:
                self.save_log.write_case("0", "query_goods_store_box_by_id_domain_inventory", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_store_box_by_id_domain_inventory", "Pass",
                                    query_goods_store_box_by_id_domain_inventory_result[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_store_box_by_id_domain_inventory", "Fail",
                                query_goods_store_box_by_id_domain_inventory_result[1], case_tm)
        time.sleep(20)
    def deal_order_count(self,query_start_time, query_end_time, dev_id):
        # 查询交易订单，默认值
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_trans_id = {}
        query_date_trans_status = {}
        query_date_paymode = {}
        query_date_domain = {}
        query_parameter = {}
        query_deal_order_count = self.mERP.query_trade_pack(query_start_time, query_end_time)
        if query_deal_order_count[0] == "Pass":
            if len(query_deal_order_count[1]) > 0:
                self.save_log.write_case("0", "query_deal_order_count", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_deal_order_count[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_deal_order_count[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_deal_order_count[1][0]["dev_name"]
                query_date_trans_id["trans_id"] = query_deal_order_count[1][0]["trans_id"]
                query_date_paymode["paymode"] = [query_deal_order_count[1][0]["paymode"]]
                query_date_trans_status["trans_status"] = [query_deal_order_count[1][0]["status"]]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_deal_order_count", "Pass", query_deal_order_count[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_trans_id["trans_id"] = "1234567890"
                query_date_paymode["paymode"] = [7]
                query_date_trans_status["trans_status"] = [100]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"

        else:
            self.save_log.write_case("0", "query_deal_order_count", "Fail", query_deal_order_count[1], case_tm)
        time.sleep(20)
        # 交易订单按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_deal_order_count_by_city = self.mERP.query_trade_pack(query_start_time, query_end_time, **query_date_postion)
        if query_deal_order_count_by_city[0] == "Pass":
            if len(query_deal_order_count_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_city", "Fail", query_deal_order_count_by_city[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_city", "Fail", query_deal_order_count_by_city[1],
                                case_tm)
        time.sleep(20)
        # 交易订单查询按照id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_order_count_by_devid = self.mERP.query_trade_pack(query_start_time, query_end_time, **query_date_dev_id)
        if query_deal_order_count_by_devid[0] == "Pass":
            if len(query_deal_order_count_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_devid", "Pass", query_deal_order_count_by_devid[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_devid", "Fail", query_deal_order_count_by_devid[1],
                                case_tm)
        time.sleep(20)
        # 交易订单查询按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_order_count_by_devname = self.mERP.query_trade_pack(query_start_time, query_end_time,
                                                                  **query_date_dev_name)
        if query_deal_order_count_by_devname[0] == "Pass":
            if len(query_deal_order_count_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_devname", "Pass",
                                    query_deal_order_count_by_devname[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_devname", "Fail", query_deal_order_count_by_devname[1],
                                case_tm)
        time.sleep(20)
        # 查询交易订单按照交易id
        query_parameter.update(query_date_trans_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_order_count_by_transid = self.mERP.query_trade_pack(query_start_time, query_end_time,
                                                                  **query_date_trans_id)
        if query_deal_order_count_by_transid[0] == "Pass":
            if len(query_deal_order_count_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_transid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_transid", "Pass",
                                    query_deal_order_count_by_transid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_transid", "Fail", query_deal_order_count_by_transid[1],
                                case_tm)
        time.sleep(20)
        # 查询交易订单按照交易状态
        query_parameter.update(query_date_trans_status)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_order_count_by_transstatus = self.mERP.query_trade_pack(query_start_time, query_end_time,
                                                                      **query_date_trans_status)
        if query_deal_order_count_by_transstatus[0] == "Pass":
            if len(query_deal_order_count_by_transstatus[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_transstatus", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_transstatus", "Pass",
                                    query_deal_order_count_by_transstatus[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_transstatus", "Fail",
                                query_deal_order_count_by_transstatus[1], case_tm)
        time.sleep(5)
        add_trans_status_list_org = [0, 100, 101, 102, 103, 104, 105, 107, 109, 110, 111, 112]
        config_trans_status_list = []
        trans_status_result = False
        for i in range(len(add_trans_status_list_org)):
            all_trans_status = {}
            config_trans_status_list.append(add_trans_status_list_org[i])
            all_trans_status["trans_status"] = config_trans_status_list
            query_deal_order_count_by_transstatus_all = self.mERP.query_trade_pack(query_start_time, query_end_time,
                                                                              **all_trans_status)
            if query_deal_order_count_by_transstatus_all[0] != "Pass":
                trans_status_result = True
                break
            time.sleep(5)
        if trans_status_result:
            self.save_log.write_case("0", "query_deal_order_count_by_transstatus_all", "Fail", all_trans_status, case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_transstatus_all", "Pass", "Pass", case_tm)
        time.sleep(20)
        # 查询交易订单按照支付方式
        query_parameter.update(query_date_paymode)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_order_count_by_pamode = self.mERP.query_trade_pack(query_start_time, query_end_time, **query_date_paymode)
        if query_deal_order_count_by_pamode[0] == "Pass":
            if len(query_deal_order_count_by_pamode[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_paymode", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_paymode", "Pass",
                                    query_deal_order_count_by_pamode[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_transstatus", "Fail",
                                query_deal_order_count_by_pamode[1], case_tm)

        add_paymode_list_org = [7, 8, 9, 10, 11, 12, 13, 14]
        config_paymode_list = []
        paymode_result = False
        for i in range(len(add_paymode_list_org)):
            all_paymode = {}
            config_paymode_list.append(add_paymode_list_org[i])
            all_paymode["pay_mode"] = config_paymode_list
            query_deal_order_count_by_paymode_all = self.mERP.query_trade_pack(query_start_time, query_end_time,
                                                                          **all_trans_status)
            if query_deal_order_count_by_paymode_all[0] != "Pass":
                paymode_result = True
                break
            time.sleep(5)
        if paymode_result:
            self.save_log.write_case("0", "query_deal_order_count_by_paymode_all", "Fail", all_paymode, case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_paymode_all", "Pass", "Pass", case_tm)
        time.sleep(20)
        # 查询订单按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_order_count_by_domain = self.mERP.query_trade_pack(query_start_time, query_end_time, **query_date_domain)
        if query_deal_order_count_by_domain[0] == "Pass":
            if len(query_deal_order_count_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_order_count_by_domain", "Pass",
                                    query_deal_order_count_by_domain[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_order_count_by_domain", "Fail", query_deal_order_count_by_domain[1],
                                case_tm)

        time.sleep(20)
        # 查询订单条件组合
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_deal_order_count_by_Random = self.mERP.query_trade_pack(query_start_time, query_end_time,
                                                                     **query_parameter)
            if query_deal_order_count_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_deal_order_count_by_random", "Fail", query_parameter, case_tm)
        time.sleep(20)
    def deal_goods_count(self,query_start_time, query_end_time, dev_id):
        # 查询交易订单，默认值
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_trans_id = {}
        query_date_goods_name = {}
        query_date_domain = {}
        query_parameter = {}
        query_deal_goods_count = self.mERP.query_trade_goods(query_start_time, query_end_time)
        if query_deal_goods_count[0] == "Pass":
            if len(query_deal_goods_count[1]) > 0:
                self.save_log.write_case("0", "query_deal_goods_count", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_deal_goods_count[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_deal_goods_count[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_deal_goods_count[1][0]["dev_name"]
                query_date_trans_id["trans_id"] = query_deal_goods_count[1][0]["trans_id"]
                query_date_goods_name["prod_name"] = query_deal_goods_count[1][0]["name"]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_deal_goods_count", "Pass", query_deal_goods_count[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_trans_id["trans_id"] = "1234567890"
                query_date_goods_name["prod_name"] = "测试商品"
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
        else:
            self.save_log.write_case("0", "query_deal_order_count", "Fail", query_deal_goods_count[1], case_tm)
        time.sleep(20)
        # 交易商品按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_deal_goods_count_by_city = self.mERP.query_trade_goods(query_start_time, query_end_time, **query_date_postion)
        if query_deal_goods_count_by_city[0] == "Pass":
            if len(query_deal_goods_count_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_deal_goods_count_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_goods_count_by_city", "Pass", query_deal_goods_count_by_city[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_city", "Fail", query_deal_goods_count_by_city[1],
                                case_tm)
        time.sleep(20)
        # 交易商品查询按照设备id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_goods_count_by_devid = self.mERP.query_trade_goods(query_start_time, query_end_time, **query_date_dev_id)
        if query_deal_goods_count_by_devid[0] == "Pass":
            if len(query_deal_goods_count_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_deal_goods_count_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_goods_count_by_devid", "Pass", query_deal_goods_count_by_devid[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_devid", "Fail", query_deal_goods_count_by_devid[1],
                                case_tm)
        time.sleep(20)
        # 交易商品查询按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_goods_count_by_devname = self.mERP.query_trade_goods(query_start_time, query_end_time,
                                                                   **query_date_dev_name)
        if query_deal_goods_count_by_devname[0] == "Pass":
            if len(query_deal_goods_count_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_deal_order_count_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_goods_count_by_devname", "Pass",
                                    query_deal_goods_count_by_devname[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_devname", "Fail", query_deal_goods_count_by_devname[1],
                                case_tm)
        time.sleep(20)
        # 查询交易订单按照交易id
        query_parameter.update(query_date_trans_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_goods_count_by_transid = self.mERP.query_trade_goods(query_start_time, query_end_time,
                                                                   **query_date_trans_id)
        if query_deal_goods_count_by_transid[0] == "Pass":
            if len(query_deal_goods_count_by_transid[1]) >= 1:
                self.save_log.write_case("0", "query_deal_goods_count_by_transid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_goods_count_by_transid", "Pass",
                                    query_deal_goods_count_by_transid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_transid", "Fail", query_deal_goods_count_by_transid[1],
                                case_tm)
        time.sleep(20)
        # 查询商品按照商品名字
        query_parameter.update(query_date_goods_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_goods_count_by_goods_name = self.mERP.query_trade_goods(query_start_time, query_end_time,
                                                                      **query_date_goods_name)
        if query_deal_goods_count_by_goods_name[0] == "Pass":
            if len(query_deal_goods_count_by_goods_name[1]) >= 1:
                self.save_log.write_case("0", "query_deal_goods_count_by_goods_name", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_goods_count_by_goods_name", "Pass",
                                    query_deal_goods_count_by_goods_name[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_goods_name", "Fail",
                                query_deal_goods_count_by_goods_name[1], case_tm)
        time.sleep(20)
        # 查询商品按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_deal_goods_count_by_domain = self.mERP.query_trade_goods(query_start_time, query_end_time, **query_date_domain)
        if query_deal_goods_count_by_domain[0] == "Pass":
            if len(query_deal_goods_count_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_deal_goods_count_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_deal_goods_count_by_domain", "Pass",
                                    query_deal_goods_count_by_domain[1], case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_domain", "Fail", query_deal_goods_count_by_domain[1],
                                case_tm)
        time.sleep(20)
        # 查询商品条件组合
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_deal_goods_count_by_Random = self.mERP.query_trade_goods(query_start_time, query_end_time,
                                                                      **query_parameter)
            if query_deal_goods_count_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_deal_goods_count_by_Random", "Fail", query_parameter, case_tm)
        else:
            self.save_log.write_case("0", "query_deal_goods_count_by_Random", "Pass", "Pass", case_tm)
        time.sleep(20)
    def income_count(self,query_start_time, query_end_time, dev_id):
        # 查询入账信息，默认值
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_trans_id = {}
        query_date_out_trade_no = {}
        query_date_domain = {}
        query_parameter = {}
        query_income_count = self.mERP.query_trade_income(query_start_time, query_end_time)
        if query_income_count[0] == "Pass":
            if len(query_income_count[1]) > 0:
                self.save_log.write_case("0", "query_income_count", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_income_count[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_income_count[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_income_count[1][0]["dev_name"]
                query_date_trans_id["trans_id"] = query_income_count[1][0]["trans_id"]
                query_date_out_trade_no["out_trade_no"] = query_income_count[1][0]["out_trade_no"]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_income_count", "Pass", query_income_count[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_trans_id["trans_id"] = "1234567890"
                query_date_out_trade_no["out_trade_no"] = "‌2019051710173703810080100018524"
                query_date_domain["domain_name"] = "USTAR_Test_Domain"

        else:
            self.save_log.write_case("0", "query_income_count", "Fail", query_income_count[1], case_tm)
        time.sleep(20)
        # 交易入账信息按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_income_count_by_city = self.mERP.query_trade_income(query_start_time, query_end_time, **query_date_postion)
        if query_income_count_by_city[0] == "Pass":
            if len(query_income_count_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_income_count_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_income_count_by_city", "Fail", query_income_count_by_city[1], case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_city", "Fail", query_income_count_by_city[1], case_tm)
        time.sleep(20)
        # 交易商品查询按照设备id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_income_count_by_devid = self.mERP.query_trade_income(query_start_time, query_end_time, **query_date_dev_id)
        if query_income_count_by_devid[0] == "Pass":
            if len(query_income_count_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_income_count_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_income_count_by_devid", "Pass", query_income_count_by_devid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_devid", "Fail", query_income_count_by_devid[1], case_tm)
        time.sleep(20)
        # 交易入账查询按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_income_count_by_devname = self.mERP.query_trade_income(query_start_time, query_end_time, **query_date_dev_name)
        if query_income_count_by_devname[0] == "Pass":
            if len(query_income_count_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_income_count_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_income_count_by_devname", "Fail", query_income_count_by_devname[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_devname", "Fail", query_income_count_by_devname[1], case_tm)
        time.sleep(20)
        # 查询交易订单按照交易id
        query_parameter.update(query_date_trans_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_income_count_by_transid = self.mERP.query_trade_income(query_start_time, query_end_time, **query_date_trans_id)
        if query_income_count_by_transid[0] == "Pass":
            if len(query_income_count_by_transid[1]) >= 1:
                self.save_log.write_case("0", "query_income_count_by_transid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_income_count_by_transid", "Fail", query_income_count_by_transid[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_transid", "Fail", query_income_count_by_transid[1], case_tm)
        time.sleep(20)
        # 查询入账按照商户订单号
        query_parameter.update(query_date_out_trade_no)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_income_count_by_out_trade = self.mERP.query_trade_income(query_start_time, query_end_time,
                                                                  **query_date_out_trade_no)
        if query_income_count_by_out_trade[0] == "Pass":
            if len(query_income_count_by_out_trade[1]) >= 1:
                self.save_log.write_case("0", "query_income_count_by_out_trade", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_income_count_by_out_trade", "Pass", query_income_count_by_out_trade[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_out_trade", "Fail", query_income_count_by_out_trade[1],
                                case_tm)
        time.sleep(20)
        # 查询商品按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_income_count_by_domain = self.mERP.query_trade_income(query_start_time, query_end_time, **query_date_domain)
        if query_income_count_by_domain[0] == "Pass":
            if len(query_income_count_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_income_count_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_income_count_by_domain", "Pass", query_income_count_by_domain[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_domain", "Fail", query_income_count_by_domain[1], case_tm)
        time.sleep(20)
        # 查询商品条件组合
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_income_count_by_Random = self.mERP.query_trade_income(query_start_time, query_end_time, **query_parameter)
            if query_income_count_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_income_count_by_Random", "Fail", query_parameter, case_tm)
        else:
            self.save_log.write_case("0", "query_income_count_by_Random", "Pass", "Pass", case_tm)
        time.sleep(20)
    def resume_count(self,query_start_time, query_end_time, dev_id):
        # 查询入账信息，默认值
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_trans_id = {}
        query_date_resume_status = {}
        query_date_domain = {}
        query_parameter = {}
        query_resume_count = self.mERP.query_trade_refund(query_start_time, query_end_time)
        if query_resume_count[0] == "Pass":
            if len(query_resume_count[1]) > 0:
                self.save_log.write_case("0", "query_income_count", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_resume_count[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_resume_count[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_resume_count[1][0]["dev_name"]
                query_date_trans_id["trans_id"] = query_resume_count[1][0]["trans_id"]
                query_date_resume_status["ref_stat"] = [int(query_resume_count[1][0]["status"])]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_income_count", "Pass", query_resume_count[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_trans_id["trans_id"] = "1234567890"
                query_date_resume_status["ref_stat"] = [103]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
        else:
            self.save_log.write_case("0", "query_income_count", "Fail", query_resume_count[1], case_tm)
        time.sleep(20)
        # 退款信息按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_resume_count_by_city = self.mERP.query_trade_refund(query_start_time, query_end_time, **query_date_postion)
        if query_resume_count_by_city[0] == "Pass":
            if len(query_resume_count_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_resume_count_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_count_by_city", "Fail", query_resume_count_by_city[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_city", "Fail", query_resume_count_by_city[1], case_tm)
        time.sleep(20)
        # 退款查询按照设备id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_count_by_devid = self.mERP.query_trade_refund(query_start_time, query_end_time, **query_date_dev_id)
        if query_resume_count_by_devid[0] == "Pass":
            if len(query_resume_count_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_resume_count_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_count_by_devid", "Pass", query_resume_count_by_devid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_devid", "Fail", query_resume_count_by_devid[1], case_tm)
        time.sleep(20)
        # 交易入账查询按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_count_by_devname = self.mERP.query_trade_refund(query_start_time, query_end_time, **query_date_dev_name)
        if query_resume_count_by_devname[0] == "Pass":
            if len(query_resume_count_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_resume_count_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_count_by_devname", "Fail", query_resume_count_by_devname[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_devname", "Fail", query_resume_count_by_devname[1], case_tm)
        time.sleep(20)
        # 查询退款按照交易id
        query_parameter.update(query_date_trans_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_count_by_transid = self.mERP.query_trade_refund(query_start_time, query_end_time, **query_date_trans_id)
        if query_resume_count_by_transid[0] == "Pass":
            if len(query_resume_count_by_transid[1]) >= 1:
                self.save_log.write_case("0", "query_resume_count_by_transid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_count_by_transid", "Fail", query_resume_count_by_transid[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_transid", "Fail", query_resume_count_by_transid[1], case_tm)
        time.sleep(20)
        # 查询退款订单按照交易状态
        query_parameter.update(query_date_resume_status)
        print(query_date_resume_status)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_count_by_transstatus = self.mERP.query_trade_refund(query_start_time, query_end_time,
                                                                    **query_date_resume_status)
        if query_resume_count_by_transstatus[0] == "Pass":
            if len(query_resume_count_by_transstatus[1]) >= 1:
                self.save_log.write_case("0", "query_resume_count_by_transstatus", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_count_by_transstatus", "Pass",
                                    query_resume_count_by_transstatus[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_transstatus", "Fail", query_resume_count_by_transstatus[1],
                                case_tm)
        time.sleep(5)
        add_trans_status_list_org = [0, 100, 101, 102, 103, 104, 105, 107, 109, 110, 111, 112]
        config_trans_status_list = []
        trans_status_result = False
        for i in range(len(add_trans_status_list_org)):
            all_trans_status = {}
            config_trans_status_list.append(add_trans_status_list_org[i])
            all_trans_status["ref_stat"] = config_trans_status_list
            query_resume_count_by_transstatus_all = self.mERP.query_trade_refund(query_start_time, query_end_time,
                                                                            **all_trans_status)
            if query_resume_count_by_transstatus_all[0] != "Pass":
                trans_status_result = True
                break
            time.sleep(5)
        if trans_status_result:
            self.save_log.write_case("0", "query_resume_count_by_transstatus_all", "Fail", all_trans_status, case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_transstatus_all", "Pass", "Pass", case_tm)
        time.sleep(20)

        # 查询商品按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_count_by_domain = self.mERP.query_trade_refund(query_start_time, query_end_time, **query_date_domain)
        if query_resume_count_by_domain[0] == "Pass":
            if len(query_resume_count_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_resume_count_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_count_by_domain", "Pass", query_resume_count_by_domain[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_domain", "Fail", query_resume_count_by_domain[1], case_tm)
        time.sleep(20)
        # 查询商品条件组合
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_resume_count_by_Random = self.mERP.query_trade_refund(query_start_time, query_end_time, **query_parameter)
            if query_resume_count_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_resume_count_by_Random", "Fail", query_parameter, case_tm)
        else:
            self.save_log.write_case("0", "query_resume_count_by_Random", "Pass", "Pass", case_tm)
        time.sleep(20)
    def resume_count_requerst(self,query_start_time, query_end_time, dev_id):
        # 查询退款申请，默认值
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_trans_id = {}
        query_date_trans_status = {}
        query_date_domain = {}
        query_parameter = {}
        query_resume_request_count = self.mERP.query_trade_refund_request(query_start_time, query_end_time)
        if query_resume_request_count[0] == "Pass":
            if len(query_resume_request_count[1]) > 0:
                self.save_log.write_case("0", "query_resume_request_count", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_resume_request_count[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_resume_request_count[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_resume_request_count[1][0]["dev_name"]
                query_date_trans_id["trans_id"] = query_resume_request_count[1][0]["trans_id"]
                query_date_trans_status["trans_status"] = [int(query_resume_request_count[1][0]["status"])]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_resume_request_count", "Pass", query_resume_request_count[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_trans_id["trans_id"] = "1234567890"
                query_date_trans_status["trans_status"] = [103]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
        else:
            self.save_log.write_case("0", "query_resume_request_count", "Fail", query_resume_request_count[1], case_tm)
        time.sleep(20)
        # 退款请求信息按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_resume_request_count_by_city = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                             **query_date_postion)
        if query_resume_request_count_by_city[0] == "Pass":
            if len(query_resume_request_count_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_resume_request_count_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_request_count_by_city", "Fail",
                                    query_resume_request_count_by_city[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_city", "Fail",
                                query_resume_request_count_by_city[1], case_tm)
        time.sleep(20)
        # 退款请求查询按照设备id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_request_count_by_devid = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                              **query_date_dev_id)
        if query_resume_request_count_by_devid[0] == "Pass":
            if len(query_resume_request_count_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_resume_request_count_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_request_count_by_devid", "Pass",
                                    query_resume_request_count_by_devid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_devid", "Fail",
                                query_resume_request_count_by_devid[1], case_tm)
        time.sleep(20)
        # 交易入账查询按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_request_count_by_devname = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                                **query_date_dev_name)
        if query_resume_request_count_by_devname[0] == "Pass":
            if len(query_resume_request_count_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_resume_request_count_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_request_count_by_devname", "Fail",
                                    query_resume_request_count_by_devname[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_devname", "Fail",
                                query_resume_request_count_by_devname[1], case_tm)
        time.sleep(20)
        # 查询退款按照交易id
        query_parameter.update(query_date_trans_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_request_count_by_transid = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                                **query_date_trans_id)
        if query_resume_request_count_by_transid[0] == "Pass":
            if len(query_resume_request_count_by_transid[1]) >= 1:
                self.save_log.write_case("0", "query_resume_request_count_by_transid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_request_count_by_transid", "Fail",
                                    query_resume_request_count_by_transid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_transid", "Fail",
                                query_resume_request_count_by_transid[1], case_tm)
        time.sleep(20)
        # 查询退款订单按照交易状态
        query_parameter.update(query_date_trans_status)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_request_count_by_transstatus = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                                    **query_date_trans_status)
        if query_resume_request_count_by_transstatus[0] == "Pass":
            if len(query_resume_request_count_by_transstatus[1]) >= 1:
                self.save_log.write_case("0", "query_resume_request_count_by_transstatus", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_request_count_by_transstatus", "Pass",
                                    query_resume_request_count_by_transstatus[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_transstatus", "Fail",
                                query_resume_request_count_by_transstatus[1], case_tm)
        time.sleep(5)
        add_trans_status_list_org = [0, 100, 101, 102, 103, 104, 105, 107, 109, 110, 111, 112]
        config_trans_status_list = []
        trans_status_result = False
        for i in range(len(add_trans_status_list_org)):
            all_trans_status = {}
            config_trans_status_list.append(add_trans_status_list_org[i])
            all_trans_status["ref_stat"] = config_trans_status_list
            query_resume_request_count_by_transstatus_all = self.mERP.query_trade_refund_request(query_start_time,
                                                                                            query_end_time,
                                                                                            **all_trans_status)
            if query_resume_request_count_by_transstatus_all[0] != "Pass":
                trans_status_result = True
                break
            time.sleep(5)
        if trans_status_result:
            self.save_log.write_case("0", "query_resume_request_count_by_transstatus_all", "Fail", all_trans_status, case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_transstatus_all", "Pass", "Pass", case_tm)
        time.sleep(20)

        # 查询商品按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_resume_request_count_by_domain = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                               **query_date_domain)
        if query_resume_request_count_by_domain[0] == "Pass":
            if len(query_resume_request_count_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_resume_request_count_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_resume_request_count_by_domain", "Pass",
                                    query_resume_request_count_by_domain[1], case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_domain", "Fail",
                                query_resume_request_count_by_domain[1], case_tm)
        time.sleep(20)
        # 查询商品条件组合
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_resume_request_count_by_Random = self.mERP.query_trade_refund_request(query_start_time, query_end_time,
                                                                                   **query_parameter)
            if query_resume_request_count_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_resume_request_count_by_Random", "Fail", query_parameter, case_tm)
        else:
            self.save_log.write_case("0", "query_resume_request_count_by_Random", "Pass", "Pass", case_tm)
        time.sleep(20)
    def date_count(self,query_start_time, query_end_time, dev_id):
        # 商品销售统计
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_goods_sales = self.mERP.query_goods_sales_count(query_start_time, query_end_time)
        if query_goods_sales[0] == "Pass":
            if len(query_goods_sales[1]) > 0:
                self.save_log.write_case("0", "query_goods_sales", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_goods_sales", "Pass", query_goods_sales[1], case_tm)
        else:
            self.save_log.write_case("0", "query_goods_sales", "Fail", query_goods_sales[1], case_tm)
        time.sleep(20)
        # 新增用户统计
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_user_add = self.mERP.query_user_add(query_start_time, query_end_time)
        if query_user_add[0] == "Pass":
            if len(query_user_add[1]) > 0:
                self.save_log.write_case("0", "query_user_add", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_user_add", "Pass", query_user_add[1], case_tm)
        else:
            self.save_log.write_case("0", "query_user_add", "Fail", query_user_add[1], case_tm)
        time.sleep(20)
        # 新增用户统计按照设备ID
        dev_list = dict.fromkeys(["dev_list"], [dev_id])
        print(dev_list)
        query_user_add_by_id = self.mERP.query_user_add(query_start_time, query_end_time, **dev_list)
        if query_user_add_by_id[0] == "Pass":
            if len(query_user_add_by_id[1]) > 0:
                self.save_log.write_case("0", "query_user_add_by_id", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_user_add_by_id", "Pass", query_user_add_by_id[1], case_tm)
        else:
            self.save_log.write_case("0", "query_user_add_by_id", "Fail", query_user_add_by_id[1], case_tm)
        time.sleep(20)
    def sales_goods_box(self,query_start_time, query_end_time, dev_id):
        # 货柜商品销售统计
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_prod_code = {}
        query_date_goods_name = {}
        query_date_domain = {}
        query_parameter = {}
        query_sales_goods_count_box = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time)
        if query_sales_goods_count_box[0] == "Pass":
            if len(query_sales_goods_count_box[1]) > 0:
                self.save_log.write_case("0", "query_deal_goods_count", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_sales_goods_count_box[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_sales_goods_count_box[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_sales_goods_count_box[1][0]["dev_name"]
                query_date_prod_code["prod_code"] = query_sales_goods_count_box[1][0]["barcode"]
                query_date_goods_name["prod_name"] = query_sales_goods_count_box[1][0]["name"]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box", "Pass", query_sales_goods_count_box[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_prod_code["prod_code"] = "1234567890123"
                query_date_goods_name["prod_name"] = "测试商品"
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box", "Fail", query_sales_goods_count_box[1], case_tm)
        time.sleep(20)
        # 货柜商品销售统计按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_sales_goods_count_box_by_city = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time,
                                                                               **query_date_postion)
        if query_sales_goods_count_box_by_city[0] == "Pass":
            if len(query_sales_goods_count_box_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_city", "Pass",
                                    query_sales_goods_count_box_by_city[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_city", "Fail",
                                query_sales_goods_count_box_by_city[1], case_tm)
        time.sleep(20)
        # 货柜商品销售统计按照设备id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_goods_count_box_by_devid = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time,
                                                                                **query_date_dev_id)
        if query_sales_goods_count_box_by_devid[0] == "Pass":
            if len(query_sales_goods_count_box_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_devid", "Pass",
                                    query_sales_goods_count_box_by_devid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_devid", "Fail",
                                query_sales_goods_count_box_by_devid[1], case_tm)
        time.sleep(20)
        # 货柜商品销售统计按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_goods_count_box_by_devname = self.mERP.query_trade_goods(query_start_time, query_end_time,
                                                                        **query_date_dev_name)
        if query_sales_goods_count_box_by_devname[0] == "Pass":
            if len(query_sales_goods_count_box_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_devname", "Pass",
                                    query_sales_goods_count_box_by_devname[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_devname", "Fail",
                                query_sales_goods_count_box_by_devname[1], case_tm)
        time.sleep(20)
        # 货柜商品销售统计商品名字
        query_parameter.update(query_date_goods_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_goods_count_box_by_goods_name = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time,
                                                                                     **query_date_goods_name)
        if query_sales_goods_count_box_by_goods_name[0] == "Pass":
            if len(query_sales_goods_count_box_by_goods_name[1]) >= 1:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_goods_name", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_goods_name", "Pass",
                                    query_sales_goods_count_box_by_goods_name[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_goods_name", "Fail",
                                query_sales_goods_count_box_by_goods_name[1], case_tm)
        time.sleep(20)
        # 货柜商品销售统计商品条码
        query_parameter.update(query_date_prod_code)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_goods_count_box_by_goods_code = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time,
                                                                                     **query_date_prod_code)
        if query_sales_goods_count_box_by_goods_code[0] == "Pass":
            if len(query_sales_goods_count_box_by_goods_code[1]) >= 1:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_goods_code", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_goods_code", "Pass",
                                    query_sales_goods_count_box_by_goods_code[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_goods_code", "Fail",
                                query_sales_goods_count_box_by_goods_code[1], case_tm)
        time.sleep(20)
        # 货柜商品销售按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_goods_count_box_by_domain = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time,
                                                                                 **query_date_domain)
        if query_sales_goods_count_box_by_domain[0] == "Pass":
            if len(query_sales_goods_count_box_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_goods_count_box_by_domain", "Pass",
                                    query_sales_goods_count_box_by_domain[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_domain", "Fail",
                                query_sales_goods_count_box_by_domain[1],
                                case_tm)
        time.sleep(20)
        # 查询商品条件组合
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_sales_goods_count_box_by_Random = self.mERP.query_goods_sales_count_box(query_start_time, query_end_time,
                                                                                     **query_parameter)
            if query_sales_goods_count_box_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_Random", "Fail", query_parameter, case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_Random", "Pass", "Pass", case_tm)
        time.sleep(20)
    def sales_service_box(self,query_start_time, query_end_time, dev_id):
        # 货柜销售业务统计
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_date_postion = {}
        query_date_dev_id = {}
        query_date_dev_name = {}
        query_date_domain = {}
        query_parameter = {}
        query_sales_service_box = self.mERP.query_sales_service_box(query_start_time, query_end_time)
        if query_sales_service_box[0] == "Pass":
            if len(query_sales_service_box[1]) > 0:
                self.save_log.write_case("0", "query_sales_service_box", "Pass", "Pass", case_tm)
                query_date_postion["city"] = query_sales_service_box[1][0]["city"]
                query_date_dev_id["dev_list"] = [query_sales_service_box[1][0]["dev_id"]]
                query_date_dev_name["dev_name"] = query_sales_service_box[1][0]["dev_name"]
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
            else:
                self.save_log.write_case("0", "query_sales_service_box", "Pass", query_sales_service_box[1], case_tm)
                query_date_postion["city"] = "杭州"
                query_date_dev_id["dev_list"] = [dev_id]
                query_date_dev_name["dev_name"] = "auto_test"
                query_date_domain["domain_name"] = "USTAR_Test_Domain"
        else:
            self.save_log.write_case("0", "query_sales_service_box", "Fail", query_sales_service_box[1], case_tm)
        time.sleep(20)
        # 货柜销售业务统计按照区域查询
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_parameter.update(query_date_postion)
        query_sales_service_box_by_city = self.mERP.query_sales_service_box(query_start_time, query_end_time,
                                                                       **query_date_postion)
        if query_sales_service_box_by_city[0] == "Pass":
            if len(query_sales_service_box_by_city[1]) >= 1:
                self.save_log.write_case("0", "query_sales_service_box_by_city", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_service_box_by_city", "Pass", query_sales_service_box_by_city[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_sales_service_box_by_city", "Fail", query_sales_service_box_by_city[1],
                                case_tm)
        time.sleep(20)
        # 货柜销售业务统计按照设备id
        query_parameter.update(query_date_dev_id)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_service_box_by_devid = self.mERP.query_sales_service_box(query_start_time, query_end_time,
                                                                        **query_date_dev_id)
        if query_sales_service_box_by_devid[0] == "Pass":
            if len(query_sales_service_box_by_devid[1]) >= 1:
                self.save_log.write_case("0", "query_sales_service_box_by_devid", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_service_box_by_devid", "Pass",
                                    query_sales_service_box_by_devid[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_goods_count_box_by_devid", "Fail",
                                query_sales_service_box_by_devid[1], case_tm)
        time.sleep(20)
        # 货柜销售业务统计按照设备名字
        query_parameter.update(query_date_dev_name)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_service_box_by_devname = self.mERP.query_trade_goods(query_start_time, query_end_time,
                                                                    **query_date_dev_name)
        if query_sales_service_box_by_devname[0] == "Pass":
            if len(query_sales_service_box_by_devname[1]) >= 1:
                self.save_log.write_case("0", "query_sales_service_box_by_devname", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_service_box_by_devname", "Pass",
                                    query_sales_service_box_by_devname[1], case_tm)
        else:
            self.save_log.write_case("0", "query_sales_service_box_by_devname", "Fail",
                                query_sales_service_box_by_devname[1], case_tm)
        time.sleep(20)
        # 货柜商品销售按照域
        query_parameter.update(query_date_domain)
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_sales_service_box_by_domain = self.mERP.query_sales_service_box(query_start_time, query_end_time,
                                                                         **query_date_domain)
        if query_sales_service_box_by_domain[0] == "Pass":
            if len(query_sales_service_box_by_domain[1]) >= 1:
                self.save_log.write_case("0", "query_sales_service_box_by_domain", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_sales_service_box_by_domain", "Pass",
                                    query_sales_service_box_by_domain[1],
                                    case_tm)
        else:
            self.save_log.write_case("0", "query_sales_service_box_by_domain", "Fail", query_sales_service_box_by_domain[1],
                                case_tm)
        time.sleep(20)
        #  货柜商品销售按条件组合
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_key_list = query_parameter.keys()
        query_count_control = False
        for i in range(len(query_key_list)):
            query_sales_service_box_by_Random = self.mERP.query_sales_service_box(query_start_time, query_end_time,
                                                                             **query_parameter)
            if query_sales_service_box_by_Random[0] != "Pass":
                query_count_control = True
                break
            time.sleep(5)
            query_parameter.popitem()
        if query_count_control:
            self.save_log.write_case("0", "query_sales_service_box_by_Random", "Fail", query_parameter, case_tm)
        else:
            self.save_log.write_case("0", "query_sales_service_box_by_Random", "Pass", "Pass", case_tm)
        time.sleep(20)
    def devid_attr_operation(self,dev_id):
        # 配置货柜名字
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dev_name_info = {"dev_id": dev_id, "dev_name": "auto_test"}
        update_dev_name = self.mERP.update_dev_detailinfo(**dev_name_info)
        if update_dev_name[0] == "Pass":
            self.save_log.write_case("0", "update_dev_name", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_dev_name", "Fail", update_dev_name, case_tm)
        time.sleep(20)
        # 配置货柜区域
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dev_position_info = {"dev_id": dev_id, "province": "浙江省", "city": "杭州市", "district": "滨江区", "location": "六合路"}
        update_dev_position = self.mERP.update_dev_detailinfo(**dev_position_info)
        if update_dev_position[0] == "Pass":
            self.save_log.write_case("0", "update_dev_postion", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_dev_postion", "Fail", update_dev_position, case_tm)
        time.sleep(20)
        # 配置货柜SN
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dev_sn_info = {"dev_id": dev_id, "user_define_sn": "1234567890"}
        update_dev_SN = self.mERP.update_dev_detailinfo(**dev_sn_info)
        if update_dev_SN[0] == "Pass":
            self.save_log.write_case("0", "update_dev_SN", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "update_dev_SN", "Fail", update_dev_SN, case_tm)
        time.sleep(20)
        # 查询货柜信息
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_dev_detail_info = self.mERP.query_dev_detailinfo(dev_id)
        if query_dev_detail_info[0] == "Pass":
            province = query_dev_detail_info[1]["dev_loc"]["province"]
            city = query_dev_detail_info[1]["dev_loc"]["city"]
            district = query_dev_detail_info[1]["dev_loc"]["district"]
            location = query_dev_detail_info[1]["info"]["location"]
            dev_sn = query_dev_detail_info[1]["user_define_sn"]
            dev_name = query_dev_detail_info[1]["info"]["name"]
            if dev_position_info["province"] == province and dev_position_info["city"] == city and dev_position_info[
                "district"] == district and dev_position_info["location"] == location:
                self.save_log.write_case("0", "query_dev_detail_info_position", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_dev_detail_info_position", "Fail", query_dev_detail_info, case_tm)
            if dev_sn_info["user_define_sn"] == dev_sn:
                self.save_log.write_case("0", "query_dev_detail_info_sn", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_dev_detail_info_sn", "Fail", query_dev_detail_info, case_tm)
            if dev_name_info["dev_name"] == dev_name:
                self.save_log.write_case("0", "query_dev_detail_info_name", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "query_dev_detail_info_name", "Fail", query_dev_detail_info, case_tm)
        else:
            self.save_log.write_case("0", "query_dev_detail_info", "Fail", query_dev_detail_info, case_tm)
        time.sleep(20)
    def devid_audio_config(self,dev_id):
        # 配置语音播报全部不播报
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_all_disable = self.mERP.set_dev_AudioConfig(dev_id, 0)
        time.sleep(30)
        if config_audio_all_disable[0] == "Pass":
            query_audio_all_disable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_all_disable[0] == "Pass":
                if not (query_audio_all_disable[1]["door"] and query_audio_all_disable[1]["abnormal_op"] and
                        query_audio_all_disable[1]["normal_op"] and query_audio_all_disable[1]["others"]):
                    self.save_log.write_case("0", "config_audio_all_disable", "Pass", "Pass", case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_all_disable", "Fail", query_audio_all_disable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_all_disable", "Fail", query_audio_all_disable, case_tm)
        else:
            self.save_log.write_case("0", "config_audio_all_disable", "Fail", config_audio_all_disable, case_tm)
        time.sleep(20)
        # 配置开门提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_door_enable = self.mERP.set_dev_AudioConfig(dev_id, 1)
        time.sleep(10)
        if config_audio_door_enable[0] == "Pass":
            query_audio_door_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_door_enable[0] == "Pass":
                if query_audio_door_enable[1]["door"]:
                    if not (query_audio_door_enable[1]["abnormal_op"] and query_audio_door_enable[1]["normal_op"] and
                            query_audio_door_enable[1]["others"]):
                        self.save_log.write_case("0", "config_audio_door_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "query_audio_door_enable", "Fail", query_audio_door_enable, case_tm)
                else:
                    self.save_log.write_case("0", "query_audio_door_enable", "Fail", query_audio_door_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_door_enable", "Fail", query_audio_door_enable, case_tm)
        else:
            self.save_log.write_case("0", "config_audio_door_enable", "Fail", config_audio_door_enable, case_tm)
        time.sleep(20)
        # 配置语音使能正常购物提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_normal_op_enable = self.mERP.set_dev_AudioConfig(dev_id, 2)
        time.sleep(5)
        if config_audio_normal_op_enable[0] == "Pass":
            query_audio_normal_op_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_normal_op_enable[0] == "Pass":
                if query_audio_normal_op_enable[1]["normal_op"]:
                    if not (query_audio_normal_op_enable[1]["door"] and query_audio_normal_op_enable[1]["normal_op"] and
                            query_audio_normal_op_enable[1]["others"]):
                        self.save_log.write_case("0", "config_audio_normal_op_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_normal_op_enable", "Fail", config_audio_normal_op_enable,
                                            case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_normal_op_enable", "Fail", config_audio_normal_op_enable,
                                        case_tm)
            else:
                self.save_log.write_case("0", "config_audio_normal_op_enable", "Fail", config_audio_normal_op_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_door_enable", "Fail", config_audio_normal_op_enable, case_tm)
        time.sleep(20)
        # 配置开门和正常购物提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_normal_door_enable = self.mERP.set_dev_AudioConfig(dev_id, 3)
        time.sleep(5)
        if config_audio_normal_door_enable[0] == "Pass":
            query_audio_normal_door_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_normal_door_enable[0] == "Pass":
                if query_audio_normal_door_enable[1]["normal_op"] and query_audio_normal_door_enable[1]["door"]:
                    if not (query_audio_normal_door_enable[1]["abnormal_op"] and query_audio_normal_door_enable[1][
                        "others"]):
                        self.save_log.write_case("0", "config_audio_normal_door_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_normal_door_enable", "Fail",
                                            config_audio_normal_door_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_normal_door_enable", "Fail", config_audio_normal_door_enable,
                                        case_tm)
            else:
                self.save_log.write_case("0", "query_audio_normal_door_enable", "Fail", query_audio_normal_door_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_normal_door_enable", "Fail", config_audio_normal_door_enable,
                                case_tm)
        time.sleep(20)
        # 配置异常操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_abnormal_enable = self.mERP.set_dev_AudioConfig(dev_id, 4)
        time.sleep(5)
        if config_audio_abnormal_enable[0] == "Pass":
            query_audio_abnormal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_abnormal_enable[0] == "Pass":
                if query_audio_abnormal_enable[1]["abnormal_op"]:
                    if not (query_audio_abnormal_enable[1]["normal_op"] and query_audio_abnormal_enable[1]["others"] and
                            query_audio_abnormal_enable[1]["door"]):
                        self.save_log.write_case("0", "config_audio_abnormal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_abnormal_enable", "Fail", query_audio_abnormal_enable,
                                            case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_abnormal_enable", "Fail", query_audio_abnormal_enable,
                                        case_tm)
            else:
                self.save_log.write_case("0", "query_audio_abnormal_enable", "Fail", query_audio_abnormal_enable, case_tm)
        else:
            self.save_log.write_case("0", "config_audio_abnormal_enable", "Fail", config_audio_abnormal_enable, case_tm)
        time.sleep(20)
        # 配置异常和开门操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_door_abnormal_enable = self.mERP.set_dev_AudioConfig(dev_id, 5)
        time.sleep(5)
        if config_audio_door_abnormal_enable[0] == "Pass":
            query_audio_door_abnormal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_door_abnormal_enable[0] == "Pass":
                if query_audio_door_abnormal_enable[1]["abnormal_op"] and query_audio_door_abnormal_enable[1]["door"]:
                    if not (query_audio_door_abnormal_enable[1]["normal_op"] and query_audio_door_abnormal_enable[1][
                        "others"]):
                        self.save_log.write_case("0", "config_audio_door_abnormal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_door_abnormal_enable", "Fail",
                                            query_audio_door_abnormal_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_door_abnormal_enable", "Fail",
                                        query_audio_door_abnormal_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_door_abnormal_enable", "Fail", query_audio_door_abnormal_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_door_abnormal_enable", "Fail", config_audio_door_abnormal_enable,
                                case_tm)
        time.sleep(20)
        # 配置异常和正常操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_normal_abnormal_enable = self.mERP.set_dev_AudioConfig(dev_id, 6)
        if config_audio_normal_abnormal_enable[0] == "Pass":
            query_audio_normal_abnormal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_normal_abnormal_enable[0] == "Pass":
                if query_audio_normal_abnormal_enable[1]["abnormal_op"] and query_audio_normal_abnormal_enable[1][
                    "normal_op"]:
                    if not (query_audio_normal_abnormal_enable[1]["door"] and query_audio_normal_abnormal_enable[1][
                        "others"]):
                        self.save_log.write_case("0", "config_audio_normal_abnormal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_normal_abnormal_enable", "Fail",
                                            query_audio_door_abnormal_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_normal_abnormal_enable", "Fail",
                                        query_audio_door_abnormal_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_normal_abnormal_enable", "Fail",
                                    query_audio_normal_abnormal_enable, case_tm)
        else:
            self.save_log.write_case("0", "config_audio_normal_abnormal_enable", "Fail", config_audio_normal_abnormal_enable,
                                case_tm)
        time.sleep(20)
        # 配置异常、正常操作和开门提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_door_normal_abnormal_enable = self.mERP.set_dev_AudioConfig(dev_id, 7)
        if config_audio_door_normal_abnormal_enable[0] == "Pass":
            query_audio_door_normal_abnormal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_door_normal_abnormal_enable[0] == "Pass":
                if query_audio_door_normal_abnormal_enable[1]["abnormal_op"] and \
                        query_audio_door_normal_abnormal_enable[1][
                            "normal_op"] and query_audio_door_normal_abnormal_enable[1]["door"]:
                    if not query_audio_door_normal_abnormal_enable[1]["others"]:
                        self.save_log.write_case("0", "config_audio_door_normal_abnormal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_door_normal_abnormal_enable", "Fail",
                                            query_audio_door_normal_abnormal_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_door_normal_abnormal_enable", "Fail",
                                        query_audio_door_normal_abnormal_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_door_normal_abnormal_enable", "Fail",
                                    query_audio_door_normal_abnormal_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_door_normal_abnormal_enable", "Fail",
                                config_audio_door_normal_abnormal_enable,
                                case_tm)
        time.sleep(20)
        # 配置其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_enable = self.mERP.set_dev_AudioConfig(dev_id, 8)
        if config_audio_other_enable[0] == "Pass":
            query_audio_other_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_enable[0] == "Pass":
                if query_audio_other_enable[1]["others"]:
                    if not (query_audio_other_enable[1]["door"] and query_audio_other_enable[1]["abnormal_op"] and
                            query_audio_other_enable[1]["normal_op"]):
                        self.save_log.write_case("0", "config_audio_other_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_enable", "Fail", query_audio_other_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_other_enable", "Fail", query_audio_other_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_enable", "Fail", query_audio_other_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_enable", "Fail", config_audio_other_enable, case_tm)
        time.sleep(20)
        # 配置开门和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_door_enable = self.mERP.set_dev_AudioConfig(dev_id, 9)
        if config_audio_other_door_enable[0] == "Pass":
            query_audio_other_door_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_door_enable[0] == "Pass":
                if query_audio_other_door_enable[1]["others"] and query_audio_other_door_enable[1]["door"]:
                    if not (query_audio_other_door_enable[1]["abnormal_op"] and query_audio_other_door_enable[1][
                        "normal_op"]):
                        self.save_log.write_case("0", "config_audio_other_door_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_door_enable", "Fail",
                                            query_audio_other_door_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_other_door_enable", "Fail", query_audio_other_door_enable,
                                        case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_door_enable", "Fail", query_audio_other_door_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_door_enable", "Fail", config_audio_other_door_enable, case_tm)
        time.sleep(20)
        # 配置开门和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_normal_enable = self.mERP.set_dev_AudioConfig(dev_id, 10)
        if config_audio_other_normal_enable[0] == "Pass":
            query_audio_other_normal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_normal_enable[0] == "Pass":
                if query_audio_other_normal_enable[1]["others"] and query_audio_other_normal_enable[1]["normal_op"]:
                    if not (query_audio_other_normal_enable[1]["abnormal_op"] and query_audio_other_normal_enable[1][
                        "door"]):
                        self.save_log.write_case("0", "config_audio_other_normal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_normal_enable", "Fail",
                                            query_audio_other_normal_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_other_normal_enable", "Fail",
                                        query_audio_other_normal_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_normal_enable", "Fail", query_audio_other_normal_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_normal_enable", "Fail", config_audio_other_normal_enable,
                                case_tm)
        time.sleep(20)
        # 配置开门、正常和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_normal_door_enable = self.mERP.set_dev_AudioConfig(dev_id, 11)
        if config_audio_other_normal_door_enable[0] == "Pass":
            query_audio_other_normal_door_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_normal_door_enable[0] == "Pass":
                if query_audio_other_normal_door_enable[1]["others"] and query_audio_other_normal_door_enable[1][
                    "normal_op"] and query_audio_other_normal_door_enable[1]["door"]:
                    if not query_audio_other_normal_door_enable[1]["abnormal_op"]:
                        self.save_log.write_case("0", "config_audio_other_normal_door_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_normal_door_enable", "Fail",
                                            query_audio_other_normal_door_enable, case_tm)
                else:
                    self.save_log.write_case("0", "query_audio_other_normal_door_enable", "Fail",
                                        query_audio_other_normal_door_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_normal_door_enable", "Fail",
                                    query_audio_other_normal_door_enable, case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_normal_door_enable", "Fail",
                                config_audio_other_normal_door_enable, case_tm)
        time.sleep(20)
        # 配置异常和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_abnormal_enable = self.mERP.set_dev_AudioConfig(dev_id, 12)
        if config_audio_other_abnormal_enable[0] == "Pass":
            query_audio_other_abnormal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_abnormal_enable[0] == "Pass":
                if query_audio_other_abnormal_enable[1]["others"] and query_audio_other_abnormal_enable[1][
                    "abnormal_op"]:
                    if not (query_audio_other_abnormal_enable[1]["normal_op"] and query_audio_other_abnormal_enable[1][
                        "door"]):
                        self.save_log.write_case("0", "config_audio_other_abnormal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_abnormal_enable", "Fail",
                                            query_audio_other_abnormal_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_other_abnormal_enable", "Fail",
                                        query_audio_other_abnormal_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_abnormal_enable", "Fail", query_audio_other_abnormal_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_abnormal_enable", "Fail", config_audio_other_abnormal_enable,
                                case_tm)
        time.sleep(20)
        # 配置开门、异常和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_abnormal_door_enable = self.mERP.set_dev_AudioConfig(dev_id, 13)
        if config_audio_other_abnormal_door_enable[0] == "Pass":
            query_audio_other_abnormal_door_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_abnormal_door_enable[0] == "Pass":
                if query_audio_other_abnormal_door_enable[1]["others"] and query_audio_other_abnormal_door_enable[1][
                    "abnormal_op"] and query_audio_other_abnormal_door_enable[1][
                    "door"]:
                    if not query_audio_other_abnormal_door_enable[1]["normal_op"]:
                        self.save_log.write_case("0", "config_audio_other_abnormal_door_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_abnormal_door_enable", "Fail",
                                            query_audio_other_abnormal_door_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_other_abnormal_door_enable", "Fail",
                                        query_audio_other_abnormal_door_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_abnormal_door_enable", "Fail",
                                    query_audio_other_abnormal_door_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_abnormal_door_enable", "Fail",
                                config_audio_other_abnormal_door_enable,
                                case_tm)
        time.sleep(20)

        # 配置开门、异常和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_other_abnormal_normal_enable = self.mERP.set_dev_AudioConfig(dev_id, 14)
        if config_audio_other_abnormal_normal_enable[0] == "Pass":
            query_audio_other_abnormal_normal_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_other_abnormal_normal_enable[0] == "Pass":
                if query_audio_other_abnormal_normal_enable[1]["others"] and \
                        query_audio_other_abnormal_normal_enable[1]["abnormal_op"] and \
                        query_audio_other_abnormal_normal_enable[1][
                            "normal_op"]:
                    if not query_audio_other_abnormal_normal_enable[1]["door"]:
                        self.save_log.write_case("0", "config_audio_other_abnormal_normal_enable", "Pass", "Pass", case_tm)
                    else:
                        self.save_log.write_case("0", "config_audio_other_abnormal_normal_enable", "Fail",
                                            query_audio_other_abnormal_normal_enable, case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_other_abnormal_normal_enable", "Fail",
                                        query_audio_other_abnormal_normal_enable, case_tm)
            else:
                self.save_log.write_case("0", "query_audio_other_abnormal_normal_enable", "Fail",
                                    query_audio_other_abnormal_normal_enable,
                                    case_tm)
        else:
            self.save_log.write_case("0", "config_audio_other_abnormal_normal_enable", "Fail",
                                config_audio_other_abnormal_normal_enable,
                                case_tm)
        time.sleep(20)
        # 配置开门、开门、异常和其他操作提示
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_audio_all_enable = self.mERP.set_dev_AudioConfig(dev_id, 12)
        if config_audio_all_enable[0] == "Pass":
            query_audio_all_enable = self.mERP.query_dev_AudioConfig(dev_id)
            if query_audio_all_enable[0] == "Pass":
                if query_audio_all_enable[1]["others"] and query_audio_all_enable[1]["abnormal_op"] and \
                        query_audio_all_enable[1]["normal_op"] and query_audio_all_enable[1]["door"]:
                    self.save_log.write_case("0", "config_audio_all_enable", "Pass", "Pass", case_tm)
                else:
                    self.save_log.write_case("0", "config_audio_all_enable", "Fail", query_audio_all_enable[1], case_tm)
            else:
                self.save_log.write_case("0", "query_audio_all_enable", "Fail", query_audio_all_enable[1], case_tm)
        else:
            self.save_log.write_case("0", "config_audio_all_enable", "Fail", config_audio_all_enable[1], case_tm)
        time.sleep(20)

        audio_control_list = [1, 2, 3, 4, 5, 6, 7, ]
        # 查询语音播报配置
        query_audio_status = self.mERP.query_dev_AudioConfig(dev_id)
    def init_box_config(self,dev_info_date):
        # 设备下货
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dev_id = dev_info_date["dev_id"]
        union_id = dev_info_date["union_id"]
        query_dev_sku_list = self.mERP.query_dev_sku(dev_id, union_id)
        init_box_sku_control = True
        if query_dev_sku_list[0] == "Pass":
            for i in range(len(query_dev_sku_list[1])):
                for key, value in query_dev_sku_list[1][i].items():
                    num = query_dev_sku_list[1][i]["actual_num"]
                    barcode = query_dev_sku_list[1][i]["barcode"]
                    pos_id = query_dev_sku_list[1][i]["pos"]
                if barcode != "AABBCCDDUSTAR":
                    if int(num) > 0:
                        update_box_sku_count = self.mERP.update_sku_count(union_id, barcode, pos_id, 1, num)
                        if update_box_sku_count[0] == "Pass":
                            update_box_sku_status = self.mERP.operation_sku_box("update", dev_id, union_id, barcode, pos_id,2)
                            time.sleep(5)
                            if update_box_sku_status[0] == "Pass":
                                del_box_sku_status = self.mERP.operation_sku_box("delete", dev_id, union_id, barcode, pos_id,
                                                                            1)
                                if del_box_sku_status[0] != "Pass":
                                    init_box_sku_control = False
                                    fail_index = del_box_sku_status
                                    break
                            else:
                                init_box_sku_control = False
                                fail_index = update_box_sku_status
                                break
                        else:
                            init_box_sku_control = False
                            fail_index = update_box_sku_count
                            break
                    else:
                        update_box_sku_status = self.mERP.operation_sku_box("update", dev_id, union_id, barcode, pos_id, 2)
                        if update_box_sku_status[0] == "Pass":
                            del_box_sku_status = self.mERP.operation_sku_box("delete", dev_id, union_id, barcode, pos_id, 1)
                            if del_box_sku_status[0] != "Pass":
                                init_box_sku_control = False
                                fail_index = del_box_sku_status
                                break
                        else:
                            init_box_sku_control = False
                            fail_index = update_box_sku_status
                            break
                time.sleep(5)
            if init_box_sku_control:
                self.save_log.write_case("0", "init_box_sku", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "init_box_sku", "Fail", fail_index, case_tm)
        time.sleep(20)
    def del_test_goods(self,barcode_list):
        # 商品库删除商品
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        delete_goods_control = True
        for i in range(len(barcode_list)):
            barcode = [barcode_list[i]]
            delete_goods_result = self.mERP.delete_goods(*barcode)
            if delete_goods_result[0] != "Pass":
                delete_goods_control = False
                break
            time.sleep(5)
        if delete_goods_control:
            self.save_log.write_case("0", "delete_goods", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "delete_goods", "Fail", delete_goods_result, case_tm)
        time.sleep(20)
    def weigh_type(self,dev_id):
        # 配置货柜类型非克重20kg
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_weigh_type = self.mERP.config_weigh_tryp(dev_id, 0)
        config_weigh_type_control = False
        if config_weigh_type[0] == "Pass":
            query_weigh_type = self.mERP.query_box()
            if query_weigh_type[0] == "Pass":
                for i in range(len(query_weigh_type[1])):
                    if query_weigh_type[1][i]["dev_id"] == dev_id and query_weigh_type[1][i]["weigh_type"] == 0:
                        config_weigh_type_control = True
                        break
            else:
                config_weigh_type_control = False
                weigh_index = query_weigh_type

        else:
            config_weigh_type_control = False
            weigh_index = config_weigh_type
        if config_weigh_type_control:
            self.save_log.write_case("0", "config_weigh_type_0", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "config_weigh_type_0", "Fail", weigh_index, case_tm)
        time.sleep(20)
        # 配置货柜类型为20kg克重
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_weigh_type = self.mERP.config_weigh_tryp(dev_id, 1)
        config_weigh_type_control = False
        if config_weigh_type[0] == "Pass":
            query_weigh_type = self.mERP.query_box()
            if query_weigh_type[0] == "Pass":
                for i in range(len(query_weigh_type[1])):
                    if query_weigh_type[1][i]["dev_id"] == dev_id and query_weigh_type[1][i]["weigh_type"] == 1:
                        config_weigh_type_control = True
                        break
            else:
                config_weigh_type_control = False
                weigh_index = query_weigh_type

        else:
            config_weigh_type_control = False
            weigh_index = config_weigh_type
        if config_weigh_type_control:
            self.save_log.write_case("0", "config_weigh_type_1", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "config_weigh_type_1", "Fail", weigh_index, case_tm)
        time.sleep(20)
        # 配置40kg非克重模式
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_weigh_type = self.mERP.config_weigh_tryp(dev_id, 2)
        config_weigh_type_control = False
        if config_weigh_type[0] == "Pass":
            query_weigh_type = self.mERP.query_box()
            if query_weigh_type[0] == "Pass":
                for i in range(len(query_weigh_type[1])):
                    if query_weigh_type[1][i]["dev_id"] == dev_id and query_weigh_type[1][i]["weigh_type"] == 2:
                        config_weigh_type_control = True
                        break
            else:
                config_weigh_type_control = False
                weigh_index = query_weigh_type

        else:
            config_weigh_type_control = False
            weigh_index = config_weigh_type
        if config_weigh_type_control:
            self.save_log.write_case("0", "config_weigh_type_2", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "config_weigh_type_2", "Fail", weigh_index, case_tm)
        time.sleep(20)
        # 配置40kg克重模式
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_weigh_type = self.mERP.config_weigh_tryp(dev_id, 3)
        config_weigh_type_control = False
        if config_weigh_type[0] == "Pass":
            query_weigh_type = self.mERP.query_box()
            if query_weigh_type[0] == "Pass":
                for i in range(len(query_weigh_type[1])):
                    if query_weigh_type[1][i]["dev_id"] == dev_id and query_weigh_type[1][i]["weigh_type"] == 3:
                        config_weigh_type_control = True
                        break
            else:
                config_weigh_type_control = False
                weigh_index = query_weigh_type

        else:
            config_weigh_type_control = False
            weigh_index = config_weigh_type
        if config_weigh_type_control:
            self.save_log.write_case("0", "config_weigh_type_3", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "config_weigh_type_3", "Fail", weigh_index, case_tm)
        time.sleep(20)
        # 恢复配置
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_weigh_type = self.mERP.config_weigh_tryp(dev_id, 0)
        config_weigh_type_control = False
        if config_weigh_type[0] == "Pass":
            query_weigh_type = self.mERP.query_box()
            if query_weigh_type[0] == "Pass":
                for i in range(len(query_weigh_type[1])):
                    if query_weigh_type[1][i]["dev_id"] == dev_id and query_weigh_type[1][i]["weigh_type"] == 0:
                        config_weigh_type_control = True
                        break
            else:
                config_weigh_type_control = False
                weigh_index = query_weigh_type

        else:
            config_weigh_type_control = False
            weigh_index = config_weigh_type
        if config_weigh_type_control:
            self.save_log.write_case("0", "config_weigh_type_0", "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", "config_weigh_type_0", "Fail", weigh_index, case_tm)
        time.sleep(20)
    def config_project_info(self,dev_id):
        # 配置项目信息
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_project_result = self.mERP.config_project_info(dev_id)
        if config_project_result[0] == "Pass":
            query_project_result = self.mERP.query_project_info(dev_id)
            print(query_project_result[1]["project_name"])
            if query_project_result[0] == "Pass":
                if query_project_result[1]["project_name"] == "auto_test" and query_project_result[1][
                    "company_name"] == "ustar" and query_project_result[1]["city_name"] == "杭州" and \
                        query_project_result[1]["latitude"] == 100:
                    self.save_log.write_case("0", "config_project", "Pass", "Pass", case_tm)
                else:
                    self.save_log.write_case("0", "config_project", "Fail", query_project_result[1], case_tm)
            else:
                self.save_log.write_case("0", "config_project", "Fail", query_project_result[1], case_tm)
        else:
            self.save_log.write_case("0", "config_project", "Fail", config_project_result[1], case_tm)
        time.sleep(20)
    def query_box_info(self,dev_id):
        dev_info_date_all = self.mERP.query_box()
        if dev_info_date_all[0] == "Pass":
            for i in range(len(dev_info_date_all[1])):
                if dev_info_date_all[1][i]["dev_id"] == dev_id:
                    dev_info_date = dev_info_date_all[1][i]
                    return dev_info_date
    def alarm_mode_base(self,query_start_time,query_end_time,query_mode):
        # 告警查询测试
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        rel, dev_list_org = self.mERP.query_dev_info()
        dev_list = []
        if rel == "Pass":
            for i in range(len(dev_list_org)):
                dev_list.append(dev_list_org[i]["dev_id"])
        else:
            self.save_log.write_case("0", "query_all_cur_alarm", "Fail", dev_list_org, case_tm)
            return
        # 查询全部告警信息
        time.sleep(5)
        if query_mode == "CurAlarm":
            query_all_alm_dict = {"alm_level_list": [0, 1, 2, 3], "command": "QueryCurAlm", "dev_list": dev_list,
                                  "begin_time": query_start_time, "end_time": query_end_time}
            log_flag = "query_cur_arm"
        elif query_mode == "HisAlarm":
            query_all_alm_dict = {"alm_level_list": [0, 1, 2, 3], "command": "QueryHisAlm", "dev_list": dev_list,"report_begin_time": query_start_time, "report_end_time": query_end_time,"clear_begin_time": query_start_time, "clear_end_time": query_end_time}
            log_flag = "query_his_arm"
        rel,query_alarm_all = self.mERP.query_alarm(**query_all_alm_dict)
        log_case_flag = log_flag + "All"
        if rel == "Pass":
            self.save_log.write_case("0", log_case_flag, "Pass", "Pass", case_tm)
            if len(query_alarm_all) < 1:
                self.save_log.write_case("0", log_case_flag, "Fail", "没有告警信息查询", case_tm)
                return
        else:
            self.save_log.write_case("0", log_case_flag, "Fail", query_alarm_all, case_tm)
            return
        time.sleep(5)
        # 按照设备ID
        query_alm_by_dev_id_dict = query_all_alm_dict.copy()
        query_alm_by_dev_id_dict["dev_list"] = [query_alarm_all[0]["dev_id"]]
        rel, query_alarm_by_dev = self.mERP.query_alarm(**query_alm_by_dev_id_dict)
        log_case_flag = log_flag + "by_dev"
        if rel == "Pass":
            if len(query_alarm_by_dev) > 0:
                self.save_log.write_case("0", log_case_flag, "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", log_case_flag, "Fail", "没有查询到告警信息", case_tm)
                return
        else:
            self.save_log.write_case("0", log_case_flag, "Fail", query_alarm_by_dev, case_tm)
            return
        time.sleep(5)
        # 按照告警ID查询
        rel, alarm_id_org = self.mERP.query_alarm_info()
        alarm_id = []
        if rel == "Pass":
            for i in range(len(alarm_id_org)):
                alarm_id.append(alarm_id_org[i]["alm_id"])
        else:
            self.save_log.write_case("0", "query_alarm_id", "Fail", alarm_id_org, case_tm)
            return
        query_alm_by_alm_id_dict = query_all_alm_dict.copy()
        query_alm_by_alm_id_dict["alm_list"] = alarm_id
        rel, query_alarm_by_alarm_id = self.mERP.query_alarm(**query_alm_by_alm_id_dict)
        log_case_flag = log_flag + "by_alm_id"
        if rel == "Pass":
            if len(query_alarm_by_alarm_id) > 0:
                self.save_log.write_case("0", log_case_flag, "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", log_case_flag, "Fail", "没有查询到告警信息", case_tm)
        else:
            self.save_log.write_case("0", log_case_flag, "Fail", query_alarm_by_alarm_id, case_tm)
        time.sleep(5)
        # 按照告警等级查询
        query_alm_by_alm_level_dict = query_all_alm_dict.copy()
        alarm_flag = True
        log_case_flag = log_flag + "by_alm_level"
        for i in range(1, 5):
            level_list = [j for j in range(i)]
            query_alm_by_alm_level_dict["alm_level_list"] = level_list
            rel, query_alarm_by_alarm_level = self.mERP.query_alarm(**query_alm_by_alm_level_dict)
            if rel != "Pass":
                alarm_flag = False
                break
            level_list.clear()
        if alarm_flag:
            self.save_log.write_case("0", log_case_flag, "Pass", "Pass", case_tm)
        else:
            self.save_log.write_case("0", log_case_flag, "Fail", level_list, case_tm)
        time.sleep(5)
    def alarm_sub_test(self,dev_list):
        # 订阅告警
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_data = {"dev_list": dev_list}
        rel, query_alarm_sub_info = self.mERP.query_alarm_sub(**query_data)
        alarm_sub_init = False
        if rel == "Pass":
            if query_alarm_sub_info:
                for i in range(len(query_alarm_sub_info)):
                    query_alarm_sub_info[i].pop("notify_way")
                rel, sub_alarm_del = self.mERP.del_alarm_sub(*query_alarm_sub_info)
                if rel == "Pass":
                    alarm_sub_init = True
                else:
                    tip = "初始化删除告警订阅失败" + str(sub_alarm_del)
                    self.save_log.write_case("0", "alarm_sub", "Fail", tip, case_tm)
                    return
            else:
                alarm_sub_init = True
        else:
            tip = "初始查询订阅信息失败" + str(query_alarm_sub_info)
            self.save_log.write_case("0", "alarm_sub", "Fail", tip, case_tm)
            return
        if alarm_sub_init:
            add_alarm_type = [107, 108, 113, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 302, 101, 102, 103, 104,
                              105, 106, 109, 110, 111, 112, 100]
            rel, add_alarm_sub_info = self.mERP.add_alarm_sub(dev_list, add_alarm_type)
            if rel == "Pass":
                self.save_log.write_case("0", "alarm_sub", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "alarm_sub", "Fail", add_alarm_sub_info, case_tm)
                return
        time.sleep(5)
        # 查询告警订阅
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_data = {"dev_list": dev_list}
        rel, query_alarm_sub_status = self.mERP.query_alarm_sub(**query_data)
        if rel == "Pass":
            if query_alarm_sub_status:
                if len(query_alarm_sub_status) == len(add_alarm_type):
                    add_alarm_type.sort()
                    query_alarm_sub_type = []
                    for i in range(len(query_alarm_sub_status)):
                        query_alarm_sub_type.append(query_alarm_sub_status[i]["alm_evt_id"])
                    query_alarm_sub_type.sort()
                    if add_alarm_type == query_alarm_sub_type:
                        self.save_log.write_case("0", "add_larm_sub", "Pass", "Pass", case_tm)
                    else:
                        tip = "查询和订阅不一致" + str(query_alarm_sub_status)
                        self.save_log.write_case("0", "add_alarm_sub", "Fail", tip, case_tm)
                else:
                    tip = "查询和订阅不个数一致" + str(query_alarm_sub_status)
                    self.save_log.write_case("0", "add_alarm_sub", "Fail", tip, case_tm)
            else:
                self.save_log.write_case("0", "add_alarm_sub", "Fail", query_alarm_sub_status, case_tm)
        else:
            self.save_log.write_case("0", "add_alarm_sub", "Fail", query_alarm_sub_status, case_tm)


