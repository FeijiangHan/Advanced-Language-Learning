# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 13:34:47 2020

@author: kanwa
"""
7

# 以下有5个字典数据类型，除了学生的基本信息学号和信息还有
#  每次作业成绩、测验成绩、实验成绩以及分数
# 作业成绩有4项、测验成绩有2项、实验成绩有2项，以上任何缺失都标记为0
# 每个学生的总分公式如下 分数 = 作业的平均成绩 * 30% + 测验的平均成绩 * 30% + 实验的平均成绩 * 40%
# 程序要求如下：
    # 1 计算每个学生的作业平均成绩、测验平均成绩、实验平均成绩
    # 2 依据总分公式计算学生的分数以及在班级的排名
    # 3 添加学生信息:还有剩余35位同学的成绩需要输入，
    #   每个学生的作业应该输入4次成绩，测验应该输入2次成绩以及实验输入2次成绩，
    #   任何缺失成绩都是0
    # 4 修改学生信息:依据用户输入的学号修改该生的信息
    # 5 删除学生信息:依据用户输入的学号删除该生的信息
    # 6 查找学生信息:依据用户输入的学号输出该生的信息，要包括在班级的名次
    # 7 打印全体学生信息
    # 8 本课程统计信息，包括最高分、最低分、平均分和中位数

  
# 1. score1
score1 = { "姓名":"张三丰", 
         "学号":"U19990001", 
         "作业" : [80, 64, 67, 20], 
         "测验" : [75, 75], 
         "实验" : [78, 57] ,
         "分数" : 0
       } 
         
# 2. score2 
score2 = { "姓名":"李四光", 
         "学号":"U19990002", 
         "作业" : [78, 89, 40, 70], 
         "测验" : [73, 87], 
         "实验" : [78, 67], 
         "分数" : 0
       } 
  
# 3. score3 
score3 = { "姓名":"刘备", 
         "学号":"U19990003", 
         "作业" : [58, 79, 65, 90], 
         "测验" : [65, 61], 
         "实验" : [76, 89], 
         "分数" : 0
       } 
          
# 4. score4 
score4 = { "姓名":"牛顿", 
         "学号":"U19990004", 
         "作业" : [80, 89, 67, 72], 
         "测验" : [75, 75], 
         "实验" : [82, 45], 
         "分数" : 0
       } 
         
# 5. score5 
score5 = { "姓名":"贝佐夫", 
         "学号":"U19990005", 
         "作业" : [80, 0, 65, 89], 
         "测验" : [75, 75], 
         "实验" : [67, 79], 
         "分数" : 0
       } 

# 导入相关的库 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
import os

INF = 2147483647


def show_menu():
    print("    +－－－－－－－－－－－－－－－－－－－－－+")
    print("    |      学生成绩信息管理系统             |")
    print("    |          版本: V1.0                 |")
    print("    +－－－－－－－－－－－－－－－－－－－－－+")
    print("    |          用户操作说明                |")
    print("    +－－－－－－－－－－－－－－－－－－－－－+")
    print("    |        1 添加学生信息                |")
    print("    |        2 修改学生信息                |")
    print("    |        3 删除学生信息                |")
    print("    |        4 查找学生信息                |")
    print("    |        5 打印全体学生成绩信息         |")
    print("    |        6 课程成绩统计                |")
    print("    |        7 保存学生信息到文件中         |")
    print("    |        8 从文件中读取学生信息         |")
    print("    |        9 退出                       |")
    print("    +－－－－－－－－－－－－－－－－－－－－－+")
    print("    |          输出颜色说明                |")
    print("    +－－－－－－－－－－－－－－－－－－－－－+")
    print("\033[34m",end='')
    print("    |        蓝色表示待输入的信息           |")
    print("\033[0m",end='')
    print('\033[1;31m',end='')
    print("    |        红色表示操作执行结果           |")
    print("\033[0m",end='')
    print("    |        黑色表示查询返回信息           |")
    print("    +－－－－－－－－－－－－－－－－－－－－－+")


# 直接导入程序定义的学生信息
def init_data():
    score1["分数"] = calc_score(score1["作业"], score1["测验"], score1["实验"])
    score2["分数"] = calc_score(score2["作业"], score2["测验"], score2["实验"])
    score3["分数"] = calc_score(score3["作业"], score3["测验"], score3["实验"])
    score4["分数"] = calc_score(score4["作业"], score4["测验"], score4["实验"])
    score5["分数"] = calc_score(score5["作业"], score5["测验"], score5["实验"])
    stu_list = [score1, score2, score3, score4, score5]
    # 排序按照：[分数、作业平均、测验平均、实验平均]的顺序排名
    stu_list.sort(key=lambda d:(d["分数"],np.mean(d["作业"]),np.mean(d["测验"]),np.mean(d["实验"])), reverse = True) # 排好序
    return stu_list

# 从文件导入学生的信息 TODO 
def init_data_from_file():
    return []

# 输入一个数字
def input_number(information):
    while True:
        try:
            print("\033[34m",end='')
            number = input(information)
            print("\033[0m",end='')
            if type(eval(number)) == float or type(eval(number)) == int:
                return float(number)
            else:
                raise Exception # 手动抛出异常
        except Exception as e: 
            print("\033[1;31m",end='')
            print('输入的不是数字，请重新输入！')
            print(e)
            print("\033[0m",end='')

     
        
# 计算总分数
def calc_score(assignments, tests, experiments):
    #分数 = 作业的平均成绩 * 30% + 测验的平均成绩 * 30% + 实验的平均成绩 * 40%
    return round(np.mean(assignments)*0.3 + np.mean(tests)*0.3 + 
                 np.mean(experiments)*0.4, 3) # 取3位小数



# 根据优先级[分数、作业平均、测验平均、实验平均]比较s1是否优于s2
def cmp_student(s1, s2):
    if s1["分数"] != s2["分数"]:
        return s1["分数"] > s2["分数"]
    else:
        if np.mean(s1["作业"]) != np.mean(s2["作业"]):
            return np.mean(s1["作业"]) > np.mean(s2["作业"])
        else:
            if np.mean(s1["测验"]) != np.mean(s2["测验"]):
                return np.mean(s1["测验"]) > np.mean(s2["测验"])
            else:
                return np.mean(s1["实验"]) > np.mean(s2["实验"])



# 根据分数大小，将学生信息插入到列表中，插入排序
# def add_to_list(stu, stu_list):
#     if len(stu_list):
#         if cmp_student(stu, stu_list[0]): # 插入到0(往-1插入)
#             stu_list.insert(0, stu)
#         elif cmp_student(stu, stu_list[-1]): # 插入到n+1（往size处插入）
#             stu_list.append(stu)
#         for index,student in enumerate(stu_list): # 插入到1-n之间
#             if not cmp_student(stu, student) and (cmp_student(stu, stu_list[index+1])):
#                 stu_list.insert(index+1, stu)
#                 return
#     else:
#         stu_list.append(stu)

# 优化版本：二分插入排序
def add_to_list(stu, stu_list):
    if len(stu_list) == 0:
        stu_list.append(stu)
        return
    low = 0
    high = len(stu_list)

    while low < high:
        mid = (low + high) // 2
        if cmp_student(stu, stu_list[mid]):
            high = mid
        else:
            low = mid + 1
    stu_list.insert(low, stu)
    
    
    
    
#添加学生信息
def add_student_info(stu_list):
    print("\033[34m",end='')
    u_id         = input("请输入学号 >> ")
    while find_student_uid(u_id, stu_list) != -INF:
        u_id  = input("该学号已经存在，请重新输入 >> ")
    name         = input("请输入姓名 >> ")
    assignments  = []
    tests        = []
    experiments  = []
    assignments.append(input_number("请输入作业1成绩 >> "))
    assignments.append(input_number("请输入作业2成绩 >> "))
    assignments.append(input_number("请输入作业3成绩 >> "))
    assignments.append(input_number("请输入作业4成绩 >> "))
    tests.append(input_number("请输入测试1成绩 >> "))
    tests.append(input_number("请输入测试2成绩 >> "))
    experiments.append(input_number("请输入实验1成绩 >> "))
    experiments.append(input_number("请输入实验2成绩 >> "))
    score = calc_score(assignments, tests, experiments)
    stu_info = {'姓名':name, '学号':u_id, '作业':assignments,
                    '测验':tests, '实验': experiments, '分数':score} 
    add_to_list(stu_info,stu_list)   #将字典数据添加到列表中，插入排序。
    print('\033[0m',end='')
    print('\033[1;31m')  
    print("\n该生信息已经添加！")
    print('\033[0m')  
    return stu_list



# 从文件添加学生信息
# 需要遵循格式：['序号','姓名','学号','分数','排名','作业1','作业2','作业3','作业4', '测验1', '测验2', '实验1', '实验2']
def add_from_file(stu_list):
    print("\033[34m",end='')
    fn = input("请输入文件路径(例如: C:/a.csv, 直接回车则默认为[./data_file/学生成绩信息.csv]) >> ")
    print("\033[0m",end='')
    file_path = './data_file/'+'学生成绩信息.csv' if fn == '' else fn # 默认选项

    all = 0
    sameId = 0
    cover = 0
    choice = 'n'
    print("\033[1;31m")
    choice = input("若遇到相同学号的学生是否覆盖信息？(y/n) >> ")
    print("\033[0m",end='')
    
    with open(file_path) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        next(csv_reader)  # 跳过文件头
        for row in csv_reader:  # 读取数据
            # 改进：选择是否覆盖
            if find_student_uid(row[2], stu_list) != -INF: # 如果存在学号相同，则不添加
                print("1")
                if(choice == 'n'):
                    sameId += 1
                    continue
                elif(choice == 'y'):
                    cover += 1
                    stu_list.remove(stu_list[find_student_uid(row[2], stu_list)])
            work       = [float(x) for x in row[5:9]] #转化作业成绩
            test       = [float(x) for x in row[9:11]] #转化测验成绩
            experiment = [float(x) for x in row[11:]] #转化实验成绩
            score =  calc_score(work, test, experiment) if row[3] == '' else float(row[3])
            add_to_list({'姓名':row[1], '学号':row[2], '作业':work,'测验':test, '实验': experiment, '分数':score},stu_list) 
            all += 1
    print('\033[1;31m')  
    print(f"从文件[{file_path}]添加信息成功！共添加 {all} 条信息，覆盖 {cover}条重复信息，跳过 {sameId} 条重复信息！")
    print('\033[0m')  

    return stu_list




bar1_colors = ['#7199cf','#4fc4aa','#e1a7a2']
labels = np.array(['作业1','作业2','作业3','作业4','测验1','测验2','实验1','实验2'])
name=['作业','测验','实验']
# 统计学生成绩等信息
def statistics_student(stu):
    #=======自己设置开始============
    #标签
    #数据个数
    dataLenth = len(stu["作业"])+len(stu["测验"])+len(stu["实验"])
    #数据
    all_scores = stu["作业"] + stu["测验"] + stu["实验"]
    data = np.array(all_scores)
    average_score=[np.mean(stu["作业"]),np.mean(stu["测验"]),np.mean(stu["实验"])]
    
    #========自己设置结束============
    
    angles = np.linspace(0, 2*np.pi, dataLenth, endpoint=False)
    data = np.concatenate((data, [data[0]])) # 闭合 # #将数据结合起来
    angles = np.concatenate((angles, [angles[0]])) # 闭合
    
    fig = plt.figure(figsize=(8, 4.2), dpi=80)
    ax = fig.add_subplot(121, polar=True)# polar参数！！121代表总行数总列数位置
    ax.plot(angles, data, 'bo-', linewidth=1)# 画线四个参数为x,y,标记和颜色，闲的宽度
    ax.fill(angles, data, facecolor='r', alpha=0.1)# 填充颜色和透明度
    ax.set_thetagrids(angles * 180/np.pi, labels, fontproperties='SimHei')
    ax.set_title("{} 详细成绩雷达图".format(stu["姓名"]),fontproperties='SimHei',weight='bold', size='medium', position=(0.5, 1.11),
                     horizontalalignment='center', verticalalignment='center')
    ax.set_rlim(0,100)
    ax.grid(True)
    xticks = np.arange(len(average_score))  #生成x轴每个元素的位置
    ax=fig.add_subplot(133)
    ax.set_xticklabels(name, fontproperties='SimHei')
    ax.set_xticks(xticks)  #设置x轴上每个标签的具体位置
    ax.set_ylim([0, 100]) # 设置y轴范围
    ax.bar(xticks,average_score,color=bar1_colors)
    ax.set_title("{} 平均成绩柱状图".format(stu["姓名"]),fontproperties='SimHei')
    plt.show()


# 打印学生信息
def print_student_info(index, stu_info):
    print("姓名: "+stu_info["姓名"].ljust(8)+"学号: "+stu_info["学号"])
    print("分数: "+str(stu_info["分数"]).ljust(10)+"排名: "+str(index))
    print("四次作业成绩: "+str(stu_info["作业"]))
    print("两次测验成绩: "+str(stu_info["测验"]))
    print("两次实验成绩: "+str(stu_info["实验"]))
    print("作业平均分: "+str(np.mean(stu_info["作业"])).ljust(6)+
          "测验平均分: "+str(np.mean(stu_info["测验"])).ljust(6)+
          "实验平均分: "+str(np.mean(stu_info["实验"])))
    
    
# 打印所有学生信息
def print_all_infos(stu_list):
    print('\033[1;31m')
    print("所有学生信息如下: ")
    print('\033[0m',end='')
    print("+================================================+")
    for index,student in enumerate(stu_list,1):
        print_student_info(index, student)
        print("+------------------------------------------------+")
    print("+=================================================+")
    print('\033[1;31m',end='')
    print("打印完成，总人数: "+str(len(stu_list))+"\n")
    print('\033[0m',end='')


# 根据学号查找学生
def find_student_uid(uid, stu_list):
    for index, stu in enumerate(stu_list): #寻找该学号下的学生
        if stu["学号"] == uid:
            return index
    return -INF


def PrintIdNotFound():
    print('\033[1;31m',end='')
    print("找不到该学生，请检查学号是否输入正确！\n")
    print('\033[0m',end='')



# 修改学生信息
def modify_student_info(stu_list):
    print("\033[34m",end='')
    u_id = input("请输入您要修改学生信息的学号 >> ")
    print('\033[0m',end='')
    
    modify_index = find_student_uid(u_id,stu_list)
    if modify_index != -INF:
        print('\033[1;31m',end='')
        #print("找到学生，学号: "+u_id+" 姓名: "+ stu_list[modify_index]["姓名"])
        print(f"找到学生，学号: {u_id} 姓名: {stu_list[modify_index].get('姓名')}")
        print('\033[0m',end='')
        print("\033[34m",end='')
    else:
        PrintIdNotFound()
        return
        
    while True:
        ch = input("请输入1-5的修改项序号：1学号、2姓名、3作业、4测验、5实验  输入0退出 >> ")
        if ch == '1':
            
            stu_list[modify_index]["学号"] = input("请输入新的学号 >> ")
            print('\033[0m',end='')
            print('\033[1;31m')  
            print("该生学号已经修改为 "+stu_list[modify_index]["学号"])
            print('\033[0m')  
        elif ch == '2':
            
            stu_list[modify_index]["姓名"] = input("请输入新的姓名 >> ")
            print('\033[0m',end='')
            print('\033[1;31m')  
            print("该生姓名已经修改为 "+stu_list[modify_index]["姓名"])
            print('\033[0m')  
        elif ch == '3':
            
            for i,student in enumerate(stu_list):
                student["作业"] = input_number(f"请输入新作业{i+1}的新成绩 >> ")
            stu_list[modify_index]["分数"]= calc_score(stu_list[modify_index]["作业"], stu_list[modify_index]["测验"], stu_list[modify_index]["实验"])
            sorted(stu_list,key=lambda x:(x["分数"],np.mean(x['作业'],np.mean('测试'),np.mean('实验'))),reverse=True)
            print('\033[0m',end='')
            print('\033[1;31m')  
            print("该生作业成绩已经修改为 "+str(stu_list[modify_index]["作业"]))
            print('\033[0m')  
        elif ch == '4':
            
            for i,student in enumerate(stu_list):
                student["测验"] = input_number(f"请输入新测验{i+1}的新成绩 >> ") 
            stu_list[modify_index]["分数"]= calc_score(stu_list[modify_index]["作业"], stu_list[modify_index]["测验"], stu_list[modify_index]["实验"])
            sorted(stu_list,key=lambda x:(x["分数"],np.mean(x['作业'],np.mean('测试'),np.mean('实验'))),reverse=True)
            print('\033[0m',end='')
            print('\033[1;31m')  
            print("该生测验成绩已经修改为 "+str(stu_list[modify_index]["测验"]))
            print('\033[0m')  
        elif ch == '5':
            
            for i,student in enumerate(stu_list):
                student["实验"] = input_number(f"请输入新实验{i+1}的新成绩 >> ")
            stu_list[modify_index]["分数"]= calc_score(stu_list[modify_index]["作业"], stu_list[modify_index]["测验"], stu_list[modify_index]["实验"])
            sorted(stu_list,key=lambda x:(x["分数"],np.mean(x['作业'],np.mean('测试'),np.mean('实验'))),reverse=True)
            print('\033[0m',end='')
            print('\033[1;31m')  
            print("该生测验成绩已经修改为 "+str(stu_list[modify_index]["测验"]))
            print('\033[0m')  
        elif ch == '0':
            return
        else:
            print('\033[1;31m',end='')  
            print("输入有误，请检查输入！")
            print('\033[0m',end='') 



# 删除学生信息
def delete_student_info(stu_list):
    print("\033[34m",end='')
    u_id = input("请输入您要删除学生信息的学号 >> ")
    print('\033[0m',end='')
    
    delete_index = find_student_uid(u_id,stu_list)
    if delete_index != -INF:
        print('\033[1;31m',end='')
        print(f"确认删除学号为 {u_id} ，姓名为 {stu_list[delete_index]['姓名']} 的信息吗？")
        print('\033[0m',end='')
        print("\033[34m",end='')
        ch = input("是否确认删除?(输入Y/y确认，其它取消) >> ")
        print('\033[0m',end='')
        if ch == 'Y' or ch == 'y':
            stu_list.pop(delete_index) #删除该学生
            print('\033[1;31m')  
            print("该生信息已经删除！")
            print('\033[0m')  
            
    PrintIdNotFound()# 打印学号不存在
            
            
# 查找学生信息
def find_student(stu_list):
    print("\033[34m",end='')
    u_id = input("请输入您要查找学生的学号 >> ")
    print('\033[0m',end='')
    find_index = find_student_uid(u_id,stu_list)
    if find_index != -INF:
        print('\033[1;31m')
        print("找到该学生的信息如下: ")
        print('\033[0m',end='')
        print('+------------------------------------------------+')
        print_student_info(find_index+1, stu_list[find_index])
        statistics_student(stu_list[find_index])
        print('+------------------------------------------------+\n')
    else:
        PrintIdNotFound()# 打印学号不存在


# 获取中位数
def get_median(listNum):
    return listNum[(len(listNum)-1) / 2] if not len(listNum)%2 else (listNum[len(listNum) // 2]+listNum[len(listNum)//2-1])/2 
    

# 计算及格\不及格\缺考人数
def count_type(stu, number_list):
    if stu["分数"] >= 60:
        number_list[0] = number_list[0] + 1
    else:
        number_list[1] = number_list[1] + 1

# 计算各分数段人数
def count_range(stu, number_list):
    if stu["分数"] < 60:
        number_list[0] = number_list[0] + 1
    elif stu["分数"] < 70:
        number_list[1] = number_list[1] + 1
    elif stu["分数"] < 80:
        number_list[2] = number_list[2] + 1
    elif stu["分数"] < 90:
        number_list[3] = number_list[3] + 1
    else:
        number_list[4] = number_list[4] + 1


## 显示分数统计信息和及格\不及格\缺考人数信息
def print_statistics_view(stu_list):
    ##### 数据设置
    range_number = [0,0,0,0,0]  #各分数段人数
    type_number = [0,0]          # 各类型人数[及格,不及格,缺考]
    
    for stu in stu_list:
        count_type(stu, type_number)
        count_range(stu, range_number)
    #### 开始绘图
    fig = plt.figure(figsize=(8, 4), dpi=85)  #整体图的标题
    colors = ['#7199cf', '#4fc4aa', '#00BFFF', '#FF7F50', '#BDB76B']
    #①在121位置上添加柱图，通过fig.add_subplot()加入子图
    ax = fig.add_subplot(121)  
    ax.set_title('各分数段人数统计', fontproperties='SimHei')  #子图标题
    xticks = np.arange(len(range_number))  #生成x轴每个元素的位置
    bar_width = 0.5  #定义柱状图每个柱的宽度
    
    #设置x轴标签
    score_range = ['[0,60)','[60,70)','[70,80)','[80,90)','[90,100]']
    ax.set_xticklabels(score_range) 
    ax.set_xticks(xticks)  #设置x轴上每个标签的具体位置
    #设置y轴的标签
    ax.set_ylabel('人数', fontproperties='SimHei')  
    ax.bar(xticks, range_number, width=bar_width, color=colors, edgecolor='none')  #设置柱的边缘为透明
    #②在122位置加入饼图
    ax = fig.add_subplot(122)
    ax.set_title('及格\不及格占比')
    # 生成同时包含名称和速度的标签
    type_labels = ['及格','不及格']
    pie_labels = ['{}:{}人'.format(type_name, number) for type_name, number in zip(type_labels, type_number)]
    # 画饼状图，并指定标签和对应颜色
    #解决汉字乱码问题
    matplotlib.rcParams['font.sans-serif']=['SimHei']  #使用指定的汉字字体类型（此处为黑体）
    
    ax.pie(type_number, labels=pie_labels, colors=colors, autopct='%1.2f%%')
    ax.axis('equal')   #保证饼图不变形
    plt.show()



# 成绩统计
def score_statistics(stu_list):
    if len(stu_list):
        # 把每个学生对象的分数放入列表中
        scores = []
        for stu in stu_list:
            scores.append(stu["分数"])
        
        print('\033[1;31m')
        print("课程成绩信息统计如下: ")
        print('\033[0m',end='')
        print('+--------------------------------------------------------+')
        print_statistics_view(stu_list)
        print(f"最高分: {scores[0]} 最低分: {scores[len(scores)-1]} 平均分: {round(np.mean(scores),3)} 中位数: {get_median(scores)}")
        print('+--------------------------------------------------------+\n')
    else:
        print("Nothing to 统计！")
  
      

# 文件头
STUDENT_LABEL = ['序号','姓名','学号','分数','排名','作业1','作业2','作业3','作业4', '测验1', '测验2', '实验1', '实验2']
FILE_DIR = './data_file/' #保存文件的目录，默认为当前文件下的data_file目录

# save to file保存到文件
def save_to_file(stu_list):
    print("\033[34m",end='')
    fn = input("请输入文件名(例如: a.csv, 直接回车则默认为[学生成绩信息.csv]) >> ")
    print('\033[0m',end='')
    
    if fn == '': # 默认选项
        fn = '学生成绩信息.csv'
    elif fn[-4:] != '.csv': # 该用户没有输入后缀名
        if fn[-4: ] == '.txt' or fn[-4: ] == '.pdf' or fn[-4: ] == '.doc' or fn[-4: ] == 'docx':
            choice = input("仅支持csv文件格式保存！输入[Y/y]默认在结尾添加'.csv'后缀 >> ")
            if(choice == 'Y' or choice == 'y'):
                fn += '.csv'
            else:
                print("创建文件失败，请指定正确的文件格式！")
                return
        else:
            choice = input("文件没有指定格式，是否保存为csv文件[Y/y] >> ")
            if(choice == 'Y' or choice == 'y'):
                fn += '.csv'
            else:
                print("创建文件失败，请指定正确的文件格式！")
                return
            
    all_values = []
    for index, stu in enumerate(stu_list):
        '''
        把每一个学生信息做成一个list，添加为csv文件的一列
        '''
       # stu_value = [index, stu['姓名'], stu['学号'], stu['分数'], index+1].extend(stu['作业'] + stu['测验'] + stu['实验'])
        stu_value = [index, stu['姓名'], stu['学号'], stu['分数'], index+1] + stu['作业'] + stu['测验'] + stu['实验']
        all_values.append(stu_value)
    with open(FILE_DIR+fn,'w+',newline='') as f:
        writer = csv.writer(f)#创建一个csv的写入器
        writer.writerow(STUDENT_LABEL)#写入标签
        writer.writerows(all_values) #写入样本数据
        f.close()
    print('\033[1;31m')  
    print("保存信息到["+FILE_DIR+fn+"]成功！")
    print('\033[0m')  

# def save_to_file(stu_list):
#     print("\033[34m",end='')
#     fn = input("请输入文件名(例如: a.csv, 直接回车则默认为[学生成绩信息.csv]) >> ")
#     print('\033[0m',end='')
#     if fn == '': # 默认选项
#         fn = '学生成绩信息.csv'
#     elif len(fn) < 5: # 该用户没有输入后缀名
#         fn = fn + '.csv'
#     elif fn[-4:] != '.csv': # 该用户没有输入后缀名
#         fn = fn + '.csv'
#     all_values = []
#     for index, stu in enumerate(stu_list):
#         '''
#         一个stu字典实体序列化成我们想要的格式，便于保存到文件
#         index为保存到文件后该实体的序号，与list的序号对应
#         '''
#         stu_value = [index, stu['姓名'], stu['学号'], stu['分数'], index+1]
#         stu_value = stu_value + stu['作业'] + stu['测验'] + stu['实验']
#         all_values.append(stu_value)
#     with open(FILE_DIR+fn,'w+',newline='') as f:
#         writer = csv.writer(f)#创建一个csv的写入器
#         writer.writerow(STUDENT_LABEL)#写入标签
#         writer.writerows(all_values) #写入样本数据
#         f.close()
#     print('\033[1;31m')  
#     print("保存信息到["+FILE_DIR+fn+"]成功！")
#     print('\033[0m')  


# 从文件导入信息
# 需要遵循格式：['序号','姓名','学号','分数','排名','作业1','作业2','作业3','作业4', '测验1', '测验2', '实验1', '实验2']
def load_from_file():
    print("\033[34m",end='')
    fn = input("请输入文件路径(例如: C:/a.csv, 直接回车则默认为[./data_file/学生成绩信息.csv]) >> ")
    print('\033[0m',end='')
    
    file_path = FILE_DIR+'学生成绩信息.csv' # 默认选项
    if fn != '':
        file_path = fn
        
    stu_list = []
    count = 0
    with open(file_path) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        next(csv_reader)  # 跳过文件头
        for row in csv_reader:  # 读取数据
            work       = [float(x) for x in row[5:9]] #转化作业成绩
            test       = [float(x) for x in row[9:11]] #转化测验成绩
            experiment = [float(x) for x in row[11:]] #转化实验成绩
            score = float(row[3]) if row[3] != '' else calc_score(work, test, experiment) # 分数
             # 添加学生信息
            stu_list.append({'姓名':row[1],'学号':row[2],'分数':score,'作业':work,'测验':test,'实验':experiment, '分数':score})
            count += 1
    # 如果读取的是本程序输出的，按理说不用排序
    # 但也可能是从其他文件读入的数据，所以还是得做一下排序。
    stu_list.sort(key=lambda d:(d["分数"],np.mean(d["作业"]),np.mean(d["测验"]),np.mean(d["实验"])), reverse = True) # 排好序
    
    print('\033[1;31m')  
    print("从文件["+file_path+"]导入成功！共 "+str(count)+" 条信息！")
    print('\033[0m')  

    return stu_list



def main():
    #创建数据文件目录
    if not os.path.exists('./data_file'):
        os.mkdir('./data_file')
    students_list = init_data()
    #print_all_infos(students_list)
    #statistics_student(students_list[0])
    while  True:
        show_menu()
        print("\033[34m",end='')
        s=input("请选择您需要执行的操作(Q/q退出) >> ")
        print("\033[0m",end='')
        if s=='q' or s == '9':
            print("\033[34m",end='')
            s = input('需要保存学生信息到文件中吗？(Y/y确定，其他退出) >> ')
            print("\033[0m",end='')
            if s == 'Y' or s == 'y':
                save_to_file(students_list)
            return #退出
        elif s == '1':
            print("\033[34m",end='')
            ch = input("请选择添加的方式(1.手动输入 2.从文件批量导入) >> ")
            print("\033[0m",end='')
            if ch == '1':
                add_student_info(students_list)
            elif ch == '2':
                add_from_file(students_list)
            else:
                print('\033[1;31m') 
                print("输入错误！")
                print('\033[0m') 
            #print_all_infos(students_list)
        elif s == '2':
            modify_student_info(students_list)
        elif s == '3':
            delete_student_info(students_list)
        elif s=='4':
            find_student(students_list)
        elif s=='5':
            print_all_infos(students_list)
        elif s=='6':
            score_statistics(students_list)
        elif s=='7':
            save_to_file(students_list)
        elif s == '8':
            students_list = load_from_file()
        else:
            print('\033[1;31m') 
            print("输入有误，请重新输入！")
            print('\033[0m') 
            
#测试
if __name__=='__main__':
    main() #从主函数开始


