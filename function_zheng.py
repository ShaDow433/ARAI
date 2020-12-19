import numpy as np 
import math

#输入矩阵,线段起始点和终点,管线的方向direction_flag,线段横截面的长length_pixel,宽width_pixel(包括Newsize,不包括安装空间space)
#在重力流水管中length=width
#在矩阵中管线的路径所占据的矩阵块中沿着管线的方向找到第一个指定的像素值value的点,返回这个点的坐标
def find_fist_point(value,StructWorkArea3D_With_GraFlow,start_point,final_point,length_pixel,width_pixel,direction_flag):
    #表示
    Matrix_Block_List=[]
    #direction_flag表示这个线段平行于y轴
    if  direction_flag:
        #如果线段是朝着y轴的箭头方向走
        if start_point[1]<final_point[1]:
            #得到管线所占据的矩阵块中所有值为value的点的坐标,找到坐标中y最小的一个
            #在矩阵中管线的路径所占据的矩阵块提取出来
            Matrix_Block_List=StructWorkArea3D_With_GraFlow[[start_point[0]-length_pixel/2]:[start_point[0]+length_pixel/2],start_point[1]:final_point[1],[start_point[2]-length_pixel/2]:[start_point[2]+length_pixel/2]].argwhere(StructWorkArea3D_With_GraFlow == value)[:,1].min()
    return first_flag,fist_point



# 把所有重力流管线的z轴都调到最高,需要考虑层高,包裹材料,安装空间。

def up_graflow(GraFlow):
    for graflow in GraFlow:
        for index in range(len(graflow['Route'])):
            graflow['Route'][index][2]=0
    return GraFlow


# 输入线段的群起始点和终点,确定这条线段是跟x轴平行就返回False，跟y轴平行就返回True
def Direction_Segment(Start_Point,Final_Point):
    #首尾的坐标x的差,和坐标y的差
    diff_X = Start_Point[0] - Final_Point[0]
    diff_Y = Start_Point[1] - Final_Point[1]
    #线段是跟y轴平行
    if abs(diff_X) < abs(diff_Y):
        return True
    else:
        return False

# 每条管线的每条线段进行遍历,把管线分成几个线段,每个线段是一个数组,里面包括线段的起始点和终点,后续会插入一下转折点
# Segment=[[[x1,y1],[x2,y2]],[[x2,y2],[x3,y3]]...]
def Create_Segment(graflow):
    Segment=[]
    for i in range(len(graflow['Route'])-1):
        Segment.append([graflow['Route'][i],graflow['Route'][i+1]])
    return Segment


def Compare_corridor(Tmp_Start_Point, Tmp_Final_Point,Temporary_StructWorkArea3D_With_GraFlow):

    #判断线段的方向沿x轴还是沿y轴
    flag_direction = Direction_Segment(Tmp_Start_Point, Tmp_Final_Point)
    #沿着y轴方向
    if flag_direction:
        # 矩阵元素值为0,说明是走廊结构,也就是线段与走廊原本产生冲突坐在
        # 本函数只考虑与走廊结构的冲突,不考虑与其他管线的冲突
        # 把管线走过的地方上非255的坐标都找出来
        Conflict_Collection_y = Temporary_StructWorkArea3D_With_GraFlow[Tmp_Start_Point[0],
                              min(Tmp_Start_Point[1],Tmp_Final_Point[1] + 1):max(Tmp_Start_Point[1],Tmp_Final_Point[1] + 1),
                              Tmp_Start_Point[2]].argwhere(Temporary_StructWorkArea3D_With_GraFlow == 0)
        #如果这条线段与走廊结构没有冲突,输出first_flag=False,first_conflict_point为空
        if len(Conflict_Collection_y)==0:
            return False,[]
        else:
            #沿着y轴从下往上
            if Tmp_Start_Point[1]<Tmp_Final_Point[1]:
                #选出冲突点集合Conflict_Collection中的所有y坐标值最小是多少
                Conflict_Collection_Min_y=Conflict_Collection_y[:,1].min()
                first_conflict_point=Tmp_Start_Point
                #把最小的y值赋值给first_conflict_point[1],first_conflict_point也就是第一个冲突点了
                first_conflict_point[1]=Conflict_Collection_Min_y
            #沿着y轴从上到下
            else:
                # 选出冲突点集合Conflict_Collection中的所有y坐标值最小是多少
                Conflict_Collection_Max_y=Conflict_Collection_y[:,1].max()
                first_conflict_point=Tmp_Start_Point
                # 把最小的y值赋值给first_conflict_point[1],first_conflict_point也就是第一个冲突点了
                first_conflict_point[1] = Conflict_Collection_Max_y
    #沿着x轴方向
    else:
        # 只有像素值是255的点才不是冲突点,非255的点就是冲突点
        # 把管线走过的地方上非255的坐标都找出来
        Conflict_Collection_x = Temporary_StructWorkArea3D_With_GraFlow[Tmp_Start_Point[0],
                              min(Tmp_Start_Point[1],Tmp_Final_Point[1] + 1):max(Tmp_Start_Point[1],Tmp_Final_Point[1] + 1),
                                Tmp_Start_Point[2]].argwhere(Temporary_StructWorkArea3D_With_GraFlow == 0)
        # 如果这条线段与走廊结构没有冲突,输出first_flag=False,first_conflict_point为空
        if len(Conflict_Collection_y) == 0:
            return False, []

        #沿着x轴从下往上
        if  Tmp_Start_Point[0]<Tmp_Final_Point[0]:
            # 选出冲突点集合Conflict_Collection中的所有x坐标值最小是多少
            Conflict_Collection_Min_x = Conflict_Collection_x[:, 1].min()
            first_conflict_point = Tmp_Start_Point
            # 把最小的x值赋值给first_conflict_point[0],first_conflict_point也就是第一个冲突点了
            first_conflict_point[0] = Conflict_Collection_Min_x
        #沿着x轴从上到下
        else:
            # 选出冲突点集合Conflict_Collection中的所有y坐标值最小是多少
            Conflict_Collection_Max_x = Conflict_Collection_x[:, 1].max()
            first_conflict_point = Tmp_Start_Point
            # 把最小的y值赋值给first_conflict_point[1],first_conflict_point也就是第一个冲突点了
            first_conflict_point[0] = Conflict_Collection_Max_x

    return True,first_conflict_point


def Against_wall(GraFlow, Point_Number, graflow, StructWorkArea3D_With_GraFlow):
    print('\n===Enter  in Against_wall_GraFlow--->Against_wall()')

    Start_point,Final_point=graflow['Route'][Point_Number],graflow['Route'][Point_Number+1]
    #判断这个线段的方向
    Direction_Flat=Direction_Segment(Start_point, Final_point)
    # 因为管线两边都需要安装空间,所以space剩以2
    Graflow_Pixel = graflow['NewSizePixelLen'][Point_Number][0] + graflow['SpacePixelLen'] * 2
    graflow_255list = [255] * Graflow_Pixel
    ''''''
    LEN,down,top = calculate_corridor_topdown(Start_point, Final_point, StructWorkArea3D_With_GraFlow)
    print('down in Against wll():',down)
    print('top in Against_wall()',top)
    #当前线段是沿着Y轴方向
    if Direction_Flat:
        print('当前线段是沿着Y轴方向')
        # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
        #判断下一个线段是沿着X轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
        if graflow['Route'][Point_Number+1][0] < graflow['Route'][Point_Number+2][0]:
            while 1:
                print('a')
                if down[2] == StructWorkArea3D_With_GraFlow.shape[2]:
                    raise Exception('In Against_wall():遍历完了所有层，没有找到合适的位置')
                else:
                    for route in graflow['Route']:
                        route[2] = down[2]

                find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0], down[1], down[2]]
                print('aeiou,down,top:', down, top)

                while 1:
                    if 255 in find_255list and len(find_255list)>=Graflow_Pixel:
                        Start_Index = int(np.argwhere(find_255list == 255)[-1])
                        if Start_Index - Graflow_Pixel>=0:
                            if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255*Graflow_Pixel:
                                Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                Move_Point = down.copy()
                                Move_Point[0] += Move_Point_y



                                #改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][0] = Move_Point[0]
                                graflow['Route'][Point_Number+1][0] = Move_Point[0]
                                return graflow
                            else:
                                find_255list=find_255list[0:Start_Index]
                        else:
                            # 挪到下一层查找
                            down[2] += 1
                            top[2] += 1
                            break
                    else:
                        # 挪到下一层查找
                        down[2] += 1
                        top[2] += 1
                        break

        #判断下一个线段是沿着X轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
        elif graflow['Route'][Point_Number + 1][0] > graflow['Route'][Point_Number + 2][0]:

            while 1:
                print('bnn')
                if down[2] == StructWorkArea3D_With_GraFlow.shape[2] :
                    raise Exception('In Against_wall():遍历完了所有层，没有找到合适的位置')
                else:
                    print('test0426-1')
                    print('down[2]',down[2])
                    for route in graflow['Route']:
                        route[2] = down[2]

                find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0], down[1], down[2]]

                while 1:

                    if 255 in find_255list and len(find_255list) >= Graflow_Pixel:
                        Start_Index = int(np.argwhere(find_255list == 255)[0])
                        if Start_Index + Graflow_Pixel < len(find_255list):
                            if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255*Graflow_Pixel:

                                New_X = top[0] - (len(find_255list) - (Start_Index + math.ceil(Graflow_Pixel/2)) )
                                print('New_X',New_X)

                                #改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][0] = New_X
                                graflow['Route'][Point_Number+1][0] = New_X
                                return graflow
                            else:
                                find_255list=find_255list[Start_Index + 1:]
                        else:
                            # 挪到下一层查找
                            down[2] += 1
                            top[2] += 1
                            break
                    else:
                        # 挪到下一层查找
                        down[2] += 1
                        top[2] += 1
                        break

        else:
            raise Exception('Eoor2 in Against_wall()')


    # 当前线段是沿着x轴方向
    else:

        # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
        # 判断下一个线段是沿着Y轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
        if graflow['Route'][Point_Number + 1][1] < graflow['Route'][Point_Number + 2][1]:
            while 1:
                print('c')
                if down[2] > StructWorkArea3D_With_GraFlow.shape[2]:
                    raise Exception('In Against_wall():遍历完了所有层，没有找到合适的位置')

                else:
                    for route in graflow['Route']:
                        route[2] = down[2]

                find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]

                while 1:
                    if 255 in find_255list and len(find_255list) >= Graflow_Pixel:
                        Start_Index = int(np.argwhere(find_255list == 255)[-1])
                        if Start_Index - Graflow_Pixel >= 0:
                            if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255 * Graflow_Pixel:
                                Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                Move_Point = down.copy()
                                Move_Point[1] += Move_Point_y
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][1] = Move_Point[1]
                                graflow['Route'][Point_Number + 1][1] = Move_Point[1]
                                return graflow
                            else:
                                find_255list = find_255list[0:Start_Index]
                        else:
                            # 挪到下一层查找
                            down[2] += 1
                            top[2] += 1
                            break
                    else:
                        # 挪到下一层查找
                        down[2] += 1
                        top[2] += 1
                        break

        # 判断下一个线段是沿着Y轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
        elif graflow['Route'][Point_Number + 1][1] > graflow['Route'][Point_Number + 2][1]:

            while 1:
                print('d')
                if down[2] > StructWorkArea3D_With_GraFlow.shape[2]:
                    raise Exception('In Against_wall():遍历完了所有层，没有找到合适的位置')
                else:
                    for route in graflow['Route']:
                        route[2] = down[2]

                find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]

                while 1:
                    if 255 in find_255list and len(find_255list) >= Graflow_Pixel:
                        Start_Index = int(np.argwhere(find_255list == 255)[0])
                        if Start_Index + Graflow_Pixel < len(find_255list):
                            if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255 * Graflow_Pixel:
                                Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                Move_Point = top.copy()
                                Move_Point[1] -= (len(find_255list) - Move_Point_y)
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][1] = Move_Point[1]
                                graflow['Route'][Point_Number + 1][1] = Move_Point[1]
                                return graflow
                            else:
                                find_255list = find_255list[Start_Index + 1:]
                        else:
                            # 挪到下一层查找
                            down[2] += 1
                            top[2] += 1
                            break
                    else:
                        # 挪到下一层查找
                        down[2] += 1
                        top[2] += 1
                        break

        else:
            raise Exception('Eoor2 in Against_wall()')


    print('Out test in Against_wall_GraFlow--->Against_wall()')
    return graflow










# 把当前线段开始后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
# Segment的格式Segment=[[[x1,y1)],[x2,y2]],[[x2,y2],[x3,y3]]...]
def Reduce_Z(Point_Number,Segment,segment_number,pixel_number):
    #输出Segment=[[[x1,y1],[x2,y2]],[[x2-pixel_number,y2-pixel_number],[x3-pixel_number,y3-pixel_number]]...]
    for index_segment in range(Point_Number+1,len(Segment[segment_number])):
        Segment[segment_number][index_segment][2]+=pixel_number

    for i in range(segment_number+1,len(Segment)):
        for j in range(len(Segment[i])):
            Segment[i][j][2]+=pixel_number

    return Segment

def Calculate_NewSzie(graflow):
    return graflow['NewSize'][0]





#计算起始地到冲突点的距离,到时用来更新遗留长度
def Calculate_distance(Start_point,conflict_point):
    distance = max(Start_point[0]-conflict_point[0]+1, Start_point[1]-conflict_point[1]+1 )

    #distance=math.ceil(np.sqrt(np.square(Start_point[0]-conflict_point[0])+np.square(Start_point[1]-conflict_point[1])+np.square(Start_point[2]-conflict_point[2])))

    return distance



def calculate_corridor_topdown(Start_point,Final_point,StructWorkArea3D_With_GraFlow):
    Start_point = np.array(Start_point)
    Final_point = np.array(Final_point)
    print('==================================In  calculate_corridor_topdown========================')

    # 创建conflict_point_list[]用来存放跟走廊发生冲突的点判断是否跟y轴平行
    derection_flag = Direction_Segment(Start_point, Final_point)
    # Tmp_Start_Point_array要来存放线段终点,四分之一点,四分之三点
    Tmp_Start_Point_array = []
    # conflict_point_array用来存放三个不同起点出发发生冲突
    first_conflict_point_array = []
    second_conflict_point_array = []
    find_255list = []
    # 分别当前线段的中点,四分之一点，四分之三,垂直于当前线段沿y轴向上作一条长度为走廊宽度的线段(不取首、终点，因为图像边缘有些锯齿什么的，导致不准）
    # Tmp_Start_Point_array.append(Start_point)
    # Tmp_Start_Point_array.append(Final_point)
    Tmp_Start_Point_array.append((Start_point + Final_point) / 2)
    Tmp_Start_Point_array.append((Tmp_Start_Point_array[0] + Start_point) / 2)
    Tmp_Start_Point_array.append((Tmp_Start_Point_array[0] + Final_point) / 2)
    Tmp_Start_Point_array = np.array(Tmp_Start_Point_array).astype(int)
    print('Point_List in calculate_corridor_topdown: ')
    print(Tmp_Start_Point_array)
    '''使用少武的函数'''
    LEN,down,top=calculate_corridor_topdown_chen(StructWorkArea3D_With_GraFlow, Tmp_Start_Point_array)
    print('\n top in calculate_corridor_topdown():',top)
    print('\n down in calculate_corridor_topdown():',down)
    print('=================out from calculate_corridor_topdown========================')

    return LEN,down,top



# 观察走廊和管线,修改线段的起点，转折点，终点 使得走廊排的下又不跟别的管道冲突
'''参数列表加入了Point_Number'''
'''这个函数被调用是最后一个参数是Return_List[2]'''
def Find_Room_GraFlow(Point_Number,down_length,segment_number,Start_point,Final_point,Segment, StructWorkArea3D_With_GraFlow, Graflow, graflow,Return_List,FlagCrossBeam_segment):

    #如果这个线段之前没有穿梁
    if len(FlagCrossBeam_segment)==0:
        print('\n Test in Find_Room_GraFlow')
        print('这个线段之前没有穿梁')

        pixel_number = down_length
        #下降后的点
        Down_Point = np.array(Return_List[3]) + np.array([0,0,pixel_number])

        #判断这个线段的方向
        Direction_Flat=Direction_Segment(Start_point, Final_point)
        # 因为管线两边都需要安装空间,所以space剩以2
        Graflow_Pixel = graflow['NewSizePixelLen'][0] + graflow['SpacePixelLen'] * 2
        graflow_255list = [255] * Graflow_Pixel
        '''待修改'''
        #找到当前线段所处的走廊宽度和top/down两点
        LEN,down,top = calculate_corridor_topdown(Start_point, Final_point, StructWorkArea3D_With_GraFlow)
        #当前线段是沿着Y轴方向
        if Direction_Flat:
            print('Y方向')
            # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层

            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0], down[1], down[2]]
            # find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0]+1, down[1], down[2]]

            #先判断当前线段是不是最后一个线段,如果不是最后一个线段
            if segment_number<len(Segment)-1:

                #判断下一个线段是沿着X轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
                if Segment[segment_number+1][0][0]<Segment[segment_number+1][1][0]:
                    while 1:
                        #如果走廊宽度大于管道宽度且这一层走廊还有空间
                        if 255 in find_255list and len(find_255list)>=Graflow_Pixel:
                            print('in if 255 in find_255list and len(find_255list)>=Graflow_Pixel: ')                           
                            Start_Index = int(np.argwhere(find_255list==255)[-1]) # 从可行空间中x较大一头开始查找
                            if Start_Index - Graflow_Pixel>=0: #如果可行空间中x最大的索引值比管道宽度大
                                #从x最大值点开始的一段空间是否全为空
                                if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                    Move_Point = down.copy()
                                    Move_Point[0] += Move_Point_y
                                    #改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][0]=Move_Point[0]
                                    #如果这个线段是管线的第一个线段
                                    if segment_number ==0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    #如果这个线段不是管线的第一个线段
                                    else: # 根据当前线段的起始点改变上一个线段的终点,也就是把当前线段的起始点加到上一个线段的末尾
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        #从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number],egment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list=find_255list[:Start_Index]
                            else:
                                print('in else: #这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降')
                                # 根据冲突点的值
                                conflict_value = Return_List[0]
                                '''算出需要下降多少pixel_number'''

                                # pixel_number = Graflow[0]['NewSizePixelLen'] + 2 * Graflow[0]['SpacePixelLen'] + graflow['NewSizePixelLen'] + 2*gralow['SpacePixelLen']

                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[3])

                                Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        #这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                        else:
                            print('in else: #这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降')
                            # 根据冲突点的值
                            conflict_value = Return_List[0]
                            '''算出需要下降多少pixel_number'''
                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            # 在管线中加入冲突点(也就是下降点)
                            Segment[segment_number].insert((Point_Number + 1), Return_List[3])



                            Segment[segment_number].insert((Point_Number + 2), Down_Point)

                            Point_Number += 2
                            # 更新起始点和终点
                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            remain_length = 0
                            return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point


                #判断下一个线段是沿着X轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
                else:
                    while 1:
                        if 255 in find_255list and len(find_255list) >= Graflow_Pixel:
                            Start_Index = int(np.argwhere(find_255list==255)[0])
                            if Start_Index + Graflow_Pixel<len(find_255list):
                                if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                    Move_Point = top
                                    Move_Point[0] = top[0] - (len(find_255list) - Move_Point_y)
                                    # 改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][0] = Move_Point[0]
                                    # 如果这个线段是管线的第一个线段
                                    if segment_number == 0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    # 如果这个线段不是管线的第一个线段
                                    else:  # 根据当前线段的起始点改变上一个线段的终点
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        #从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number],egment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list= find_255list[Start_Index+1:]
                            else:
                                # 根据冲突点的值
                                conflict_value = Return_List[0]
                                '''算出需要下降多少pixel_number'''

                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[3])
                                Segment[segment_number].insert((Point_Number + 2), Down_Point)
                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                        else:
                            # 根据冲突点的值
                            conflict_value = Return_List[0]
                            '''算出需要下降多少pixel_number'''

                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            # 在管线中加入冲突点(也就是下降点)
                            Segment[segment_number].insert((Point_Number + 1), Return_List[3])


                            ''''''
                            Segment[segment_number].insert((Point_Number + 2), Down_Point)

                            Point_Number += 2
                            # 更新起始点和终点
                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            remain_length = 0
                            return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
            #如果是最后一个线段
            else:
                print('是最后一段')
                #当前线段沿着Y轴由小到大,靠墙就需要往X的负方向靠
                if Segment[segment_number][0][1]<Segment[segment_number][1][1]:
                    print('从小到大')
                    while 1:
                        if 255 in find_255list and len(find_255list) >= Graflow_Pixel:

                            Start_Index = int(np.argwhere(find_255list == 255)[0])
                            if Start_Index + Graflow_Pixel>len(find_255list):
                                # if find_255list[Start_Index - Graflow_Pixel : Start_Index].sum() == 255* Graflow_Pixel:
                                if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255 * Graflow_Pixel:

                                    print('找到了一段255')
                                    Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                    Move_Point = top.copy()
                                    Move_Point[0] = top[0] - (len(find_255list) - Move_Point_y)
                                    # 改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][0] = Move_Point[0]
                                    # 如果是单线段管线
                                    if segment_number == 0:
                                        print('单线段管')
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                   Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    # 不是单线段管线,是多线段管线的最后一段
                                    else:  # 根据当前线段的起始点改变上一个线段的终点
                                        print('不是单  线段管')
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        # 从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                   Segment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list = find_255list[Start_Index+1:]
                            else:

                                print('没有可容纳的')
                                # 根据冲突点的值
                                conflict_value = Return_List[0]

                                '''算出需要下降多少pixel_number'''
                                print('Segment befor Reduce_z')
                                print(Segment)
                                print('conflict_value', conflict_value)

                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                print('===\nSegment after Reduce_z')
                                print(Segment)
                                print('===\n')
                                if Segment[segment_number][0][1] == Return_List[2][1]:
                                    Segment[segment_number][0][2] += pixel_number
                                    remain_length = 0
                                    print('一开始就平行撞，本点也下降，则Segment:')
                                    print('Segment')
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                else:
                                    # 把当前Start_poi
                                    # 在管线中加入冲突点(也就是下降点)
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                    ''''''
                                    Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                    Point_Number += 2
                                    # 更新起始点和终点
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                    remain_length = 0
                                    print('Segment ')
                                    print(Segment)
                                    print('out of here \n')
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                        else:
                            print('没有可容纳的')
                            # 根据冲突点的值
                            conflict_value = Return_List[0]

                            '''算出需要下降多少pixel_number'''
                            print('Segment befor Reduce_z')
                            print(Segment)
                            print('conflict_value',conflict_value)

                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            print('===\nSegment after Reduce_z')
                            print(Segment)
                            print('===\n')
                            if Segment[segment_number][0][1]==Return_List[2][1]:
                                Segment[segment_number][0][2]+=pixel_number
                                remain_length=0
                                print('一开始就平行撞，本点也下降，则Segment:')
                                print('Segment')
                                Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            else:
                                # 把当前Start_poi
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                ''''''
                                Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Segment ')
                                print(Segment)
                                print('out of here \n')
                            return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                #当前线段沿着Y轴由大到小,靠墙就需要往X的正方向靠
                else:
                    while 1:
                        if 255 in find_255list and len(find_255list)>=Graflow_Pixel:
                            print('in if 255 in find_255list and len(find_255list)>=Graflow_Pixel: ')
                            # 反向查找
                            '''需要修改rindex'''
                            Start_Index = int(np.argwhere(find_255list==255)[-1])
                            if Start_Index - Graflow_Pixel>=0:
                                if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                    Move_Point = down
                                    Move_Point[0] += Move_Point_y
                                    #改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][0]=Move_Point[0]
                                    #如果这个线段是管线的第一个线段
                                    if segment_number ==0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    #如果这个线段不是管线的第一个线段
                                    else: # 根据当前线段的起始点改变上一个线段的终点,也就是把当前线段的起始点加到上一个线段的末尾
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        #从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number],egment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list=find_255list[:Start_Index]
                            else:

                                print('没有可容纳的')
                                # 根据冲突点的值
                                conflict_value = Return_List[0]

                                '''算出需要下降多少pixel_number'''
                                print('Segment befor Reduce_z')
                                print(Segment)
                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                print('Segment after Reduce_z')
                                print(Segment)
                                if Segment[segment_number][0][1] == Return_List[2][1]:
                                    Segment[segment_number][0][2] += pixel_number
                                    print(Segment)
                                    remain_length = 0
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                else:
                                    # 把当前Start_poi
                                    # 在管线中加入冲突点(也就是下降点)
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                    ''''''
                                    Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                    Point_Number += 2
                                    # 更新起始点和终点
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                    remain_length = 0
                                    print('Segment ')
                                    print(Segment)
                                    print('out of here \n')
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        #这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                        else:
                            print('没有可容纳的')
                            # 根据冲突点的值
                            conflict_value = Return_List[0]

                            '''算出需要下降多少pixel_number'''
                            print('Segment befor Reduce_z')
                            print(Segment)
                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            print('Segment after Reduce_z')
                            print(Segment)
                            if Segment[segment_number][0][1] == Return_List[2][1]:
                                Segment[segment_number][0][2] += pixel_number
                                print(Segment)
                                remain_length = 0
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                            else:
                                # 把当前Start_poi
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                ''''''
                                Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Segment ')
                                print(Segment)
                                print('out of here \n')
                            return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point

        # 当前线段是沿着x轴方向
        else:
            # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
            # 因为管线两边都需要安装空间,所以space剩以2
            Graflow_Pixel = graflow['NewSizePixelLen'][0] + graflow['SpacePixelLen'] * 2
            graflow_255list = [255] * Graflow_Pixel
            # 先判断当前线段是不是最后一个线段,如果不是最后一个线段
            if segment_number < len(Segment) - 1:
                # 判断下一个线段是沿着Y轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
                if Segment[segment_number + 1][0][1] < Segment[segment_number + 1][-1][1]:
                    while 1:
                        if 255 in find_255list:
                            # 反向查找
                            '''需要修改rindex'''
                            Start_Index = int(np.argwhere(find_255list==255)[-1])
                            if Start_Index - Graflow_Pixel>=0:
                                if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                    Move_Point = down
                                    Move_Point[1] += Move_Point_y
                                    # 改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][1] = Move_Point[1]
                                    # 如果这个线段是管线的第一个线段
                                    if segment_number == 0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    # 如果这个线段不是管线的第一个线段
                                    else:  # 根据当前线段的起始点改变上一个线段的终点
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        # 从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                   Segment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list = find_255list[:Start_Index]
                            else:
                                # 下降到下一层
                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                Segment = Reduce_Z(Segment[segment_number], down_length, Segment, Point_Number)
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[3])

                                Segment[segment_number].insert((Point_Number + 2), Down_Point)
                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        #这一层走廊没有空间可以容纳得下这条线段
                        else:
                            #下降到下一层
                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            Segment = Reduce_Z(Segment[segment_number],down_length,Segment,Point_Number)
                            #在管线中加入冲突点(也就是下降点)
                            Segment[segment_number].insert((Point_Number+1),Return_List[3])

                            Segment[segment_number].insert((Point_Number+2), Down_Point)
                            Point_Number+=2
                            #更新起始点和终点
                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            remain_length=0
                            return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                #判断下一个线段是沿着Y轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
                else:
                    while 1:
                        if 255 in find_255list and len(find_255list)>=Graflow_Pixel:
                            Start_Index = int(np.argwhere(find_255list==255)[0])
                            if Start_Index + Graflow_Pixel<len(find_255list):
                                if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                    Move_Point = top
                                    Move_Point[1] = top[1] - (len(find_255list) - Move_Point_y)
                                    # 改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][1] = Move_Point[1]
                                    # 如果这个线段是管线的第一个线段
                                    if segment_number == 0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    # 如果这个线段不是管线的第一个线段
                                    else:  # 根据当前线段的起始点改变上一个线段的终点
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        # 从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list= find_255list[Start_Index+1:]
                            else:
                                # 根据冲突点的值
                                conflict_value = Return_List[0]
                                '''算出需要下降多少pixel_number'''

                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[3])

                                Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point

                        # 这一层走廊没有空间可以容纳得下这条线段
                        else:
                            # 根据冲突点的值
                            conflict_value = Return_List[0]
                            '''算出需要下降多少pixel_number'''

                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            # 在管线中加入冲突点(也就是下降点)
                            Segment[segment_number].insert((Point_Number + 1), Return_List[3])


                            Segment[segment_number].insert((Point_Number + 2), Down_Point)

                            Point_Number += 2
                            # 更新起始点和终点
                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            remain_length = 0
                            return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                print('\n OUT Of Test in Find_Room_GraFlow\n\n')
                return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
            # 如果是最后一个线段
            else:
                # 当前线段沿着X轴由小到大,靠墙就需要往Y的负方向靠
                if Segment[segment_number][0][0] < Segment[segment_number][1][0]:

                    while 1:
                        if 255 in find_255list:
                            Start_Index = int(np.argwhere(find_255list==255)[0])
                            if Start_Index + Graflow_Pixel<=len(find_255list):
                                if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                    Move_Point = top
                                    Move_Point[1] = top[1] - (len(find_255list) - Move_Point_y)
                                    # 改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][1] = Move_Point[1]
                                    # 如果这个线段是管线的第一个线段
                                    if segment_number == 0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    # 如果这个线段不是管线的第一个线段
                                    else:  # 根据当前线段的起始点改变上一个线段的终点
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        # 从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list= find_255list[Start_Index+1:]
                            else:

                                print('没有可容纳的')
                                # 根据冲突点的值
                                conflict_value = Return_List[0]

                                '''算出需要下降多少pixel_number'''
                                print('Segment befor Reduce_z')
                                print(Segment)
                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                print('Segment after Reduce_z')
                                print(Segment)
                                if Segment[segment_number][0][1] == Return_List[2][1]:
                                    Segment[segment_number][0][2] += pixel_number
                                    print(Segment)
                                    remain_length = 0
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                else:
                                    # 把当前Start_poi
                                    # 在管线中加入冲突点(也就是下降点)
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                    ''''''
                                    Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                    Point_Number += 2
                                    # 更新起始点和终点
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                    remain_length = 0
                                    print('Segment ')
                                    print(Segment)
                                    print('out of here \n')
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        # 这一层走廊没有空间可以容纳得下这条线段
                        else:
                            print('没有可容纳的')
                            # 根据冲突点的值
                            conflict_value = Return_List[0]

                            '''算出需要下降多少pixel_number'''
                            print('Segment befor Reduce_z')
                            print(Segment)
                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            print('Segment after Reduce_z')
                            print(Segment)
                            if Segment[segment_number][0][1] == Return_List[2][1]:
                                Segment[segment_number][0][2] += pixel_number
                                print(Segment)
                                remain_length = 0
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                            else:
                                # 把当前Start_poi
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                ''''''
                                Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Segment ')
                                print(Segment)
                                print('out of here \n')
                            return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                # 当前线段沿着X轴由大到小,靠墙就需要往Y的正方向靠
                else:
                    while 1:
                        if 255 in find_255list and len(find_255list)>=Graflow_Pixel:
                            # 反向查找
                            '''需要修改rindex'''
                            Start_Index = int(np.argwhere(find_255list==255)[-1])
                            if Start_Index - Graflow_Pixel>=0:
                                if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                    Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                    Move_Point = down
                                    Move_Point[1] += Move_Point_y
                                    # 改变这个线段所有坐标的x值
                                    for index in range(len(Segment[segment_number])):
                                        Segment[segment_number][index][1] = Move_Point[1]
                                    # 如果这个线段是管线的第一个线段
                                    if segment_number == 0:
                                        Point_Number = 0
                                        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                                        # 更新remain_length为上一个线段的的遗留长度,因为是第一个线段所以没有上一个线段的的遗留长度
                                        remain_length = 0
                                    # 如果这个线段不是管线的第一个线段
                                    else:  # 根据当前线段的起始点改变上一个线段的终点
                                        Segment[segment_number - 1].append(Segment[segment_number][0])
                                        segment_number -= 1
                                        # 从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                                        Point_Number = len(Segment[segment_number]) - 2
                                        # 更新起始点和终点为上一个线段延长部分的头尾两点
                                        Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                   Segment[segment_number][Point_Number + 1]
                                        # 更新remain_length为上一个线段的的遗留长度
                                        remain_length = remain_length_segment_number[segment_number]
                                    return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point
                                else:
                                    find_255list = find_255list[:Start_Index]
                            else:

                                print('没有可容纳的')
                                # 根据冲突点的值
                                conflict_value = Return_List[0]

                                '''算出需要下降多少pixel_number'''
                                print('Segment befor Reduce_z')
                                print(Segment)
                                # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                                '''函数参数列表加多了Point_Number OK'''
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                print('Segment after Reduce_z')
                                print(Segment)
                                if Segment[segment_number][0][1] == Return_List[2][1]:
                                    Segment[segment_number][0][2] += pixel_number
                                    print(Segment)
                                    remain_length = 0
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                else:
                                    # 把当前Start_poi
                                    # 在管线中加入冲突点(也就是下降点)
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                    ''''''
                                    Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                    Point_Number += 2
                                    # 更新起始点和终点
                                    Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                               Segment[segment_number][Point_Number + 1]
                                    remain_length = 0
                                    print('Segment ')
                                    print(Segment)
                                    print('out of here \n')
                                return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point
                        #这一层走廊没有空间可以容纳得下这条线段
                        else:
                            print('没有可容纳的')
                            # 根据冲突点的值
                            conflict_value = Return_List[0]

                            '''算出需要下降多少pixel_number'''
                            print('Segment befor Reduce_z')
                            print(Segment)
                            # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                            '''函数参数列表加多了Point_Number OK'''
                            Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                            print('Segment after Reduce_z')
                            print(Segment)
                            if Segment[segment_number][0][1] == Return_List[2][1]:
                                Segment[segment_number][0][2] += pixel_number
                                print(Segment)
                                remain_length = 0
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                            else:
                                # 把当前Start_poi
                                # 在管线中加入冲突点(也就是下降点)
                                Segment[segment_number].insert((Point_Number + 1), Return_List[2])

                                ''''''
                                Segment[segment_number].insert((Point_Number + 2), Down_Point)

                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Segment ')
                                print(Segment)
                                print('out of here \n')
                            return remain_length, Segment, segment_number, Point_Number, Start_point, Final_point

    #如果这个线段之前穿梁了,那么就只能下降
    else:
        pixel_number = down_length
        # 下降后的点
        Down_Point = np.array(Return_List[3]) + np.array([0, 0, pixel_number])

        print('in else: #这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降')
        # 根据冲突点的值
        conflict_value = Return_List[0]
        '''算出需要下降多少pixel_number'''

        # pixel_number = Graflow[0]['NewSizePixelLen'] + 2 * Graflow[0]['SpacePixelLen'] + graflow['NewSizePixelLen'] + 2*gralow['SpacePixelLen']

        # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
        '''函数参数列表加多了Point_Number OK'''
        Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
        # 在管线中加入冲突点(也就是下降点)
        Segment[segment_number].insert((Point_Number + 1), Return_List[3])

        Segment[segment_number].insert((Point_Number + 2), Down_Point)

        Point_Number += 2
        # 更新起始点和终点
        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
        remain_length = 0
        return remain_length,Segment,segment_number,Point_Number,Start_point,Final_point

def calculate_corridor_topdown_chen(StructWorkArea3D_With_GraFlow, PointList):

    print('\nTest in calculate_corridor_topdown_chen():')
    #PointList为取得走廊上5点,[起点， 中间点1， 中间点2， 中间点3，终点]
    PointList = np.array(PointList).astype(int)
    StartPoint = PointList[0]
    EndPoint = PointList[-1]

    #Direction指管线段方向
    if StartPoint[0]==EndPoint[0]:
      Direction='X_Eq'

    elif StartPoint[1]==EndPoint[1]:
      Direction='Y_Eq'
    else:
      raise Exception('Error in calculate_corridor_topdown_chen()') 

    LEN = 9999999999
    i = 0
    for i in range(len(PointList)):
        Point = PointList[i]
        Len, A_Pair_Of_Point = calculate_corridor_with_one_point_chen(Point, StructWorkArea3D_With_GraFlow, Direction )
        print('%d, Len, A_Pair_Of_Point:'%(i+1), Len, A_Pair_Of_Point)
        if Len==False:
            pass
        else:

            if Len<LEN:
                LEN = Len 
                down = np.array(A_Pair_Of_Point[0]).astype(int)
                top = np.array(A_Pair_Of_Point[1]).astype(int)
    if LEN==9999999999:
        raise Exception('没有找到top  down')
    else:
        print('down',down)
        print('top',top)
        print('out from calculate_corridor_topdown_chen\n')

    return Len, down, top

def calculate_corridor_with_one_point_chen(Point, StructWorkArea3D, Direction ):
    if Direction=='Y_Eq':
        Coordinate = np.argwhere( StructWorkArea3D[ int(Point[0]), :, Point[2]]==0 ).squeeze()
        if Coordinate.size <2:
            return False,[]
        else:
            #做差值，找走廊的两端点1
            Coordinate2 =  abs(Coordinate - Point[1] )         
            point1_Y = Coordinate[Coordinate2.argmin()]
            #做差值，找走廊的两端点2
            if point1_Y+1 in Coordinate:
                Coordinate3 = np.array([x for x in Coordinate if x<point1_Y ])
            else:
                Coordinate3 = np.array([x for x in Coordinate if x>point1_Y ])
            Coordinate4 = abs(Coordinate3 - Point[1])

            if Coordinate4.shape[0]==0:
                return False,[]
            else:
                point2_Y = Coordinate3[Coordinate4.argmin()]
       
                point1 = np.array([ Point[0], point1_Y, Point[2]])
                point2 = np.array([ Point[0], point2_Y, Point[2]])

                LEN =  abs(point1[1] - point2[1]) +1
                if point1_Y<point2_Y: 
                    return LEN, [point1, point2]
                else: 
                    return LEN, [point2, point1]


    elif Direction=='X_Eq':

 
        #取一整条线
        Coordinate = np.argwhere( StructWorkArea3D[ :, int(Point[1]), Point[2]]==0 ).squeeze()


        if Coordinate.size <2:

            return False,[]
        else:
            #做差值，找走廊的两端点1
            Coordinate2 =  abs(Coordinate - Point[0] )         
            point1_X = Coordinate[Coordinate2.argmin()]

            #做差值，找走廊的两端点2
            if point1_X+1 in Coordinate:
                Coordinate3 = np.array([x for x in Coordinate if x<point1_X ])
            else:
                Coordinate3 = np.array([x for x in Coordinate if x>point1_X ])
            Coordinate4 = abs(Coordinate3 - Point[0])

            if Coordinate4.shape[0]==0:

                return False,[]
            else:
                point2_X = Coordinate3[Coordinate4.argmin()]
           
                point1 = np.array([ point1_X, Point[1],  Point[2]])
                point2 = np.array([ point2_X, Point[1],  Point[2]])

                LEN =  abs(point2[0] - point1[0]) +1

                if point1_X<point2_X: 
                    return LEN, [point1, point2]
                else: 
                    return LEN, [point2, point1]


#最后一个线段或者是单线段的往左边靠墙
def put_final_segment(Point_Number, graflow, GraFlow, StructWorkArea3D_With_GraFlow):
    print('\n================Test in put_final_segment()=====================')

    Start_point, Final_point = graflow['Route'][Point_Number], graflow['Route'][Point_Number + 1]
    # 判断这个线段的方向
    Direction_Flat = Direction_Segment(Start_point, Final_point)
    # 因为管线两边都需要安装空间,所以space剩以2
    Graflow_Pixel = graflow['NewSizePixelLen'][Point_Number][0] + graflow['SpacePixelLen'] * 2
    graflow_255list = np.array([255] * Graflow_Pixel)
    '''待修改 ok'''
    LEN, down, top = calculate_corridor_topdown(Start_point, Final_point, StructWorkArea3D_With_GraFlow)
    print('Start_point',Start_point)
    print('Final_point',Final_point)
    print('LEN:',LEN)
    print('down:',down)
    print('top:',top)

    #如果是单线段管线
    if len(graflow['Route'])==2:
        # 当前线段是沿着Y轴方向
        if Direction_Flat:
            # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0]+1, down[1], down[2]]

            # 如果线段沿着Y轴从大到小,那么线段就想X的正方向靠
            if Start_point[1] > Final_point[1]:
                while 1:
                    print('\nin loop1 put_final_segment')
                    if (255 in find_255list) and (len(find_255list) >= Graflow_Pixel):
                        # 反向查找
                        Start_Index = int(np.argwhere(find_255list==255)[-1])
                        if Start_Index - Graflow_Pixel>=0:
                            if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                Move_Point = down
                                Move_Point[0] += Move_Point_y
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][0], graflow['Route'][Point_Number][2] = Move_Point[0], Move_Point[2]
                                graflow['Route'][Point_Number+1][0], graflow['Route'][Point_Number+1][2] = Move_Point[0], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[:Start_Index]
                        else:
                            down[2] += 1
                            top[2] += 1
                            '''更新find_255list'''
                            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]
                    # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:

                        down[2] +=1
                        top[2] += 1
                        '''更新find_255list'''
                        find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]
            # 如果线段沿着Y轴从小到大,那么线段就想X的反方向靠
            else:
                while 1:
                    print('\nin loop2 put_final_segment')
                    if (255 in find_255list) and (len(find_255list) >= Graflow_Pixel):
                        Start_Index = int(np.argwhere(find_255list==255)[0])
                        if Start_Index + Graflow_Pixel<len(find_255list):
                            if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:

                                New_X = top[0] - (len(find_255list) - (Start_Index + math.ceil(Graflow_Pixel / 2)))
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][0] = New_X
                                graflow['Route'][Point_Number+1][0] = New_X
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[Start_Index+1:]
                        else:
                            down[1] += 1
                            top[1] += 1
                            '''更新find_255list'''
                            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]

                    # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:
                        down[1] += 1
                        top[1] += 1
                        '''更新find_255list'''
                        find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]

        # 当前线段是沿着x轴方向
        else:
            # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
            # 当前线段是沿着X轴正方向
            if Start_point[0] < Final_point[0]:
                while 1:
                    print('\nin loop3 put_final_segment')
                    if 255 in find_255list:
                        # 反向查找
                        '''需要修改rindex'''
                        Start_Index = int(np.argwhere(find_255list==255)[-1])
                        if Start_Index - Graflow_Pixel>=0:
                            if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                Move_Point = down
                                Move_Point[1] += Move_Point_y
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][1], graflow['Route'][Point_Number][2] = Move_Point[1], Move_Point[2]
                                graflow['Route'][Point_Number+1][1], graflow['Route'][Point_Number+1][2] = Move_Point[1], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[:Start_Index]
                        else:
                            down[2] += 1
                            top[2] += 1
                            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
                        # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:
                        down[2] += 1
                        top[2] += 1
                        find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
            # 判断下一个线段是沿着X轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
            else:
                print('test0425:Route before put_finial():',graflow['Route'])
                while 1:
                    print('\nin loo4p put_final_segment')
                    if 255 in find_255list and len(find_255list) >= Graflow_Pixel:
                        Start_Index = int(np.argwhere(find_255list==255)[0])
                        if Start_Index + Graflow_Pixel<len(find_255list):
                            if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                Move_Point = top
                                Move_Point[1] -= (len(find_255list) - Move_Point_y)
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][1], graflow['Route'][Point_Number][2] = Move_Point[1], Move_Point[2]
                                graflow['Route'][Point_Number+1][1], graflow['Route'][Point_Number+1][2] = Move_Point[1], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[Start_Index+1:]
                        else:
                            down[2] += 1
                            top[2] += 1
                            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
                    # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:
                        down[2] += 1
                        top[2] += 1
                        find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
        print('test0425:Route after put_finial():', graflow['Route'])
        return graflow


    #如果不是单线段管线
    else:
        print('#如果不是单线段管线')
        # 当前线段是沿着Y轴方向
        if Direction_Flat:
            # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]
            #判断上一个线段的方向(反过来看)
            #如果上一个线段是X从小到大,那本线段就得向X的正方向靠
            if graflow['Route'][Point_Number][0]<graflow['Route'][Point_Number-1][0]:
                while 1:
                    print('\nin loop1 put_final_segment')
                    if (255 in find_255list) and (len(find_255list) >= Graflow_Pixel):
                        # 反向查找
                        Start_Index = int(np.argwhere(find_255list==255)[-1])
                        if Start_Index - Graflow_Pixel>=0:
                            if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                Move_Point = down
                                Move_Point[0] += Move_Point_y
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][0], graflow['Route'][Point_Number][2] = Move_Point[0], Move_Point[2]
                                graflow['Route'][Point_Number+1][0], graflow['Route'][Point_Number+1][2] = Move_Point[0], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[:Start_Index]
                        else:
                            down[2] += 1
                            top[2] += 1
                            '''更新find_255list'''
                            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]
                    # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:

                        down[2] +=1
                        top[2] += 1
                        '''更新find_255list'''
                        find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]
            # 如果上一个线段是X从大到小,那本线段就得向X的负方向靠
            else:
                while 1:
                    print('\nin loop2 put_final_segment')
                    if (255 in find_255list) and (len(find_255list) >= Graflow_Pixel):
                        Start_Index = int(np.argwhere(find_255list==255)[0])
                        if Start_Index + Graflow_Pixel<len(find_255list):
                            if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                Move_Point = top.copy()
                                Move_Point[0] -= (len(find_255list) - Move_Point_y)
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][0], graflow['Route'][Point_Number][2] = Move_Point[0], Move_Point[2]
                                graflow['Route'][Point_Number+1][0], graflow['Route'][Point_Number+1][2] = Move_Point[0], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[Start_Index+1:]
                        else:
                            down[1] += 1
                            top[1] += 1
                            '''更新find_255list'''
                            find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]

                    # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:
                        down[1] += 1
                        top[1] += 1
                        '''更新find_255list'''
                        find_255list = StructWorkArea3D_With_GraFlow[down[0]:top[0] + 1, down[1], down[2]]
        # 当前线段是沿着X轴方向
        else:
            # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层
            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
            # 判断上一个线段的方向(反过来看)
            # 如果上一个线段是Y从小到大,那本线段就得向Y的正方向靠
            if graflow['Route'][Point_Number][1]<graflow['Route'][Point_Number-1][1]:
                while 1:
                    print('\nin loop3 put_final_segment')
                    if 255 in find_255list:
                        # 反向查找
                        '''需要修改rindex'''
                        Start_Index = int(np.argwhere(find_255list==255)[-1])
                        if Start_Index - Graflow_Pixel>=0:
                            if find_255list[Start_Index - Graflow_Pixel:Start_Index].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index - math.ceil(Graflow_Pixel / 2)
                                Move_Point = down
                                Move_Point[1] += Move_Point_y
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][1], graflow['Route'][Point_Number][2] = Move_Point[1], Move_Point[2]
                                graflow['Route'][Point_Number+1][1], graflow['Route'][Point_Number+1][2] = Move_Point[1], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[:Start_Index]
                        else:
                            down[2] += 1
                            top[2] += 1
                            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
                        # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:
                        down[2] += 1
                        top[2] += 1
                        find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
            # 判断上一个线段的方向(反过来看)
            # 如果上一个线段是Y从大到小,那本线段就得向Y的负方向靠
            else:
                print('test0425:Route before put_finial():',graflow['Route'])
                while 1:
                    print('\nin loo4p put_final_segment')
                    if 255 in find_255list and len(find_255list) >= Graflow_Pixel:
                        Start_Index = int(np.argwhere(find_255list==255)[0])
                        if Start_Index + Graflow_Pixel<len(find_255list):
                            if find_255list[Start_Index:Start_Index + Graflow_Pixel].sum() == 255* Graflow_Pixel:
                                Move_Point_y = Start_Index + math.ceil(Graflow_Pixel / 2)
                                Move_Point = top
                                Move_Point[1] -= (len(find_255list) - Move_Point_y)
                                # 改变这个线段所有坐标(也就是头尾两个点)的x值
                                graflow['Route'][Point_Number][1], graflow['Route'][Point_Number][2] = Move_Point[1], Move_Point[2]
                                graflow['Route'][Point_Number+1][1], graflow['Route'][Point_Number+1][2] = Move_Point[1], Move_Point[2]
                                print('out of loop put_final_segment\n')
                                break
                            else:
                                find_255list = find_255list[Start_Index+1:]
                        else:
                            down[2] += 1
                            top[2] += 1
                            find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
                    # 这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降
                    else:
                        down[2] += 1
                        top[2] += 1
                        find_255list = StructWorkArea3D_With_GraFlow[down[0], down[1]:top[1], down[2]]
        return graflow




