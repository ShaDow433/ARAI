from function_chen import *
from function_zheng import *
from function_zhang import *

'''main函数的输入减去HMAX'''
'''注意参数LenPixel是多少毫米一个坐标'''

def Against_wall_GraFlow(StructWorkArea3D_With_GraFlow, GraFlow, LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict):
    print('\nTest in Against_wall_GraFlow():\n')
    print('Before Against_wall_GraFlow:',GraFlow)
    #Temporary_StructWorkArea3D_With_GraFlow只是用于下面Against_wall函数靠墙处,并不是真正用于输出的矩阵
    Temporary_StructWorkArea3D_With_GraFlow = StructWorkArea3D_With_GraFlow.copy()
    #把所有重力流管线的z轴都调到最高,z=0
    GraFlow = up_graflow(GraFlow)
    #每条管线进行遍历,graflow_number为第几个管线
    i = 1
    for graflow_number in range(len(GraFlow)):

        print('====================第%d条管============================='%i)
        i+=1

        Point_Number = 0     #表示现在是管线的第几个坐标

        while(Point_Number<len(GraFlow[graflow_number]['Route'])-2):  #如果是最后一个坐标,说明这条管线已经处理完了

            #根据当前线段离两边(障碍物距离)的距离,
            #把当前线段起始点和终点往距离少的一遍靠经(坐标改变)
            #输入线段的头和尾坐标，输出头尾新坐标
            #注：目前障碍物包括管线和墙,也要考虑这一层排不下，需要到下一层，z值加1
            GraFlow[graflow_number] =  Against_wall(GraFlow, Point_Number,GraFlow[graflow_number],Temporary_StructWorkArea3D_With_GraFlow)

            Point_Number+=1

        print('GraFlow[graflow_number] 1:\n', GraFlow[graflow_number])
        print('开始 put_finalsegment()')
        #最后一个线段的往左边靠墙
        GraFlow[graflow_number]=put_final_segment(Point_Number,GraFlow[graflow_number], GraFlow, Temporary_StructWorkArea3D_With_GraFlow)

        print('type(GraFlow[graflow_number])', type(GraFlow[graflow_number]))
        print('GraFlow[graflow_number] 2: \n',GraFlow[graflow_number])

        # 根据更新好了的坐标去排布管线(不考虑冲突直接排布),更新Temporary_StructWorkArea3D_With_GraFlow，用于上面Against_wall函数
        # 给area的点赋值，只考虑平面，
        Temporary_StructWorkArea3D_With_GraFlow = pre_put_graflow(GraFlow[graflow_number], Temporary_StructWorkArea3D_With_GraFlow, LenPixel)

    #修改水管的z坐标，考虑锯齿下降。
    GraFlow = Add_Ratio_Z_For_Against_wall_GraFlow(GraFlow)

    print('Against_wall_GraFlow Test out \n\n')

    return GraFlow

def pre_put_graflow(graflow, StructWorkArea3D_With_GraFlow, LenPixel):
    print('Test in pre_put_graflow():', )

    Z = graflow['Route'][0][2]
    if Z != graflow['Route'][-1][2]:
        raise Exception('Error in pre_put_graflow()')

    for PointNumber in range(len(graflow['Route']) - 1):

        StartPoint = graflow['Route'][PointNumber]
        EndPoint = graflow['Route'][PointNumber + 1]
        FlagDirection = 'X_EqValue' if StartPoint[0] == EndPoint[0] else 'Y_EqValue'

        if FlagDirection == 'X_EqValue':
            Y_Star_Index = min(StartPoint[1], EndPoint[1])
            Y_End_Index = max(StartPoint[1], EndPoint[1])

            X_Star_Index = StartPoint[0] - np.ceil(graflow['NewSize'][PointNumber][0] / LenPixel / 2).astype(int)
            X_End_Index = StartPoint[0] + np.ceil(graflow['NewSize'][PointNumber][0] / LenPixel / 2).astype(int)

            StructWorkArea3D_With_GraFlow[
            (X_Star_Index - graflow['SpacePixelLen']): (X_End_Index + graflow['SpacePixelLen'] + 1),
            Y_Star_Index: Y_End_Index + 1, Z] = graflow['X_Eq_SpaceValue']
            StructWorkArea3D_With_GraFlow[X_Star_Index:X_End_Index + 1, Y_Star_Index: Y_End_Index + 1, Z] = graflow[
                'X_EqValue']

        elif FlagDirection == 'Y_EqValue':
            X_Star_Index = min(StartPoint[0], EndPoint[0])
            X_End_Index = max(StartPoint[0], EndPoint[0])

            Y_Star_Index = StartPoint[1] - np.ceil(graflow['NewSize'][PointNumber][1] / LenPixel / 2).astype(int)
            Y_End_Index = StartPoint[1] + np.ceil(graflow['NewSize'][PointNumber][1] / LenPixel / 2).astype(int)
            #给3Darea中代表管道的点赋值，根据平行于X轴或Y轴赋不同的值(只考虑平面)
            StructWorkArea3D_With_GraFlow[X_Star_Index: X_End_Index,
            (Y_Star_Index - graflow['SpacePixelLen']): (Y_End_Index + graflow['SpacePixelLen'] + 1), Z] = graflow[
                'Y_Eq_SpaceValue']
            StructWorkArea3D_With_GraFlow[X_Star_Index:X_End_Index + 1, Y_Star_Index: Y_End_Index + 1, Z] = graflow[
                'Y_EqValue']

    print('pre put Test Out\n\n\n')
    return StructWorkArea3D_With_GraFlow

def Add_Ratio_Z_For_Against_wall_GraFlow(GraFlow):
    #up_graflow

    for graflow in GraFlow:
        graflow['Route'] = np.array(graflow['Route'])
        if graflow['Route'][0][2]== graflow['Route'][-1][2]==0:  #z=0，第一层
            #重新修改管道的z值，考虑了管道的深度
            graflow['Route'] += [0, 0,  math.ceil(graflow['NewSizePixelLen'][0][0]/2) + graflow['SpacePixelLen']]

        elif  graflow['Route'][0][2]== graflow['Route'][-1][2]==1: #z=1，第2层，多下降了一个管道的空间

            graflow['Route'] += [0, 0,  math.ceil(graflow['NewSizePixelLen'][0][0]/2) + graflow['SpacePixelLen'] + \
                GraFlow[0]['NewSizePixelLen'][0][0] + 2 * GraFlow[0]['SpacePixelLen']  ]
        else:
            raise Exception('Error in Add_Ratio_Z_For_Against_wall_GraFlow()')


    #考虑Ratio
    for graflow in GraFlow:

        for i in range(graflow['Route'].shape[0]-1):
            #由于水管是锯齿状下降的，所以根据管的长度和总下降高度，让管道分成几段下降，表现形式为z值得增加。导致第一层的水管可能会撞到第二层的水管
            Z_Add = np.ceil(max( abs(graflow['Route'][i][0] - graflow['Route'][i+1][0]), abs(graflow['Route'][i][1] -  \
                graflow['Route'][i+1][1]))/graflow['Ratio']).astype(int)
            graflow['Route'][i+1][2] =  graflow['Route'][i][2] + Z_Add


    return GraFlow

def put_GraFlow(StructWorkArea3D_With_GraFlow, StructWorkArea2D, Graflow, graflow, LenPixel, Z_Max, Beams, LogPath, PipesValueDict, BeamsValueDict):
    print('\n\nTest in put_GraFlow:\n')
    #lowest_z为管线的最低点的坐标
    lowest_z=0
    #每条管线进行遍历
    '''注'''
    print('\n\n\ngraflow i:',graflow,'\n\n\n')

    # 每条管线的每条线段进行遍历,把管线分成几个线段,每个线段是一个数组,里面包括线段的起始点和终点,后续会插入一下转折点
    #Segment=[[(x1,y1),(x2,y2)],[(x2,y2),(x3,y3)]...]
    Segment = Create_Segment(graflow)
    print('1---- Original Segment:\n',Segment,'\n')

    '''定义FlagCrossBeam=[1,1,1,,1,0,0]'''
    '''remain_length_segment_number'''
    # 用来记录当前这个管线的各个大Segment中是否有撞梁
    FlagCrossBeam = {}
    for index_segment in range(len(Segment)+10):
        FlagCrossBeam[index_segment]=[]


    remain_length_segment_number=[0]*(len(Segment)+20)
    remain_length = 0  # 上一个线段的遗留长度
    segment_number = 0 # 当前是第几个线段,也就是Segment中第几个数组

    while segment_number<len(Segment):

        Point_Number = 0     #表示现在是线段的第几个坐标
        # 初始化起始点和终点为线段的头尾两点,检测冲突也是查看这Start_point,Final_point两个点之间是否有冲突
        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]

        while 1:
            #把Start_point,Final_point=Start_point之间的线段排布进一个暂时的矩阵Temporary_StructWorkArea3D_With_GraFlow
            #一开始Start_point,Final_point为线段的头坐标和尾坐标,但是如果中间出现30米下降,那么就需要在线段的数组中添加两个点,
            #一个是冲突发生的点,一个是30米下降的点,把这两个点插入到线段输入中,那么线段数组现在的元素就有[线段头坐标,冲突发生的点,30米下降的点,线段尾坐标]
            #下一步循环是就从下降后的点开始走下去(冲突处理后前面的部分就不用理他了,接着看线段的后面部分),
            # 那么更新Start_point,Final_point为线段的30米下降的点,线段尾坐标.
            #而Point_Number表示的是Start_point在线段数组中的位置,当Start_point为数组最后第二个元素,也就是Final_point数组最后第一个元素
            #并且检测没有冲突是,这个线段就检测结束,

            #从起始点沿着管线检测(30米 - 遗留长度remain_length)如果中间没有下降就发生了30米冲突，按照管线的走向进行冲突排序
            #返回flag=(1,2,3)分别表示第一个冲突类型为30米冲突,撞梁，撞管,flag=0表示没有冲突
            #返回conflict_point为第一个发生冲突的坐标,down_length为需要下降多少个像素


            print(',start_point',Start_point)
            print('Segment',Segment)
            flag, Return_List = Compare(graflow, StructWorkArea3D_With_GraFlow, Start_point,Final_point,remain_length,LenPixel,FlagCrossBeam[segment_number])
            print('What is the compare flag?',flag)



            #把发生冲突的类型flag和冲突发生在第几个线段这些信息输入到输出报告中

            ''' 未定义
            PutConflictInReport(flag,segment_number,graflow,'GraFlow')
            '''

            #如果Start_point到Final_point有冲突
            if flag != False:
                if flag==1 : #30米冲突
                    print('30米冲突')
                    #计算30米对应下降多少个像素值

                    pixel_number = math.ceil(200/LenPixel)
                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    '''函数参数列表加多了Point_Number OK'''
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    #在管线中加入冲突点(也就是下降点)
                    print('Return_List[0]',Return_List[0])
                    Segment[segment_number].insert((Point_Number+1),Return_List[0])
                    Down_Point = (np.array(Return_List[0]).copy() + [0,0,pixel_number]).astype(int)

                    Segment[segment_number].insert((Point_Number+2),Down_Point)

                    Point_Number+=2
                    #更新起始点和终点
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                    remain_length=0

                elif flag==2 : #撞梁
                    '''管线相撞也得改变考虑这跟线段是否穿梁了'''
                    '''注意撞梁一次跟多次的区别'''
                    print('\n Enter in elif flag==2')

                    ''''''
                    NewSize = Calculate_NewSzie(graflow)

                    if NewSize <= 250:
                        print('\n Enter in if NewSize <= 250')

                        # 看当前起始点到终点穿梁的位置是否刚好满足要求,是的话返回flag_across=true,反之返回flag_across=false
                        flag_across = Check_Right(graflow, Beams, Return_List[0], StructWorkArea3D_With_GraFlow,Start_point,Final_point,LenPixel,PipesValueDict, BeamsValueDict)

                        #根据冲突点的value找到他是对应哪一条梁
                        beam_value=Return_List[0]
                        #beam_index为梁的索引
                        beam_index=BeamsValueDict[beam_value]
                        #找到梁的宽对应的像素个数
                        beam_width = math.ceil(Beams[beam_index]['BWidth']/LenPixel)
                        #计算出梁的点对应撞梁的点的高度差对应的像素个数
                        high_distance=math.ceil(beam_width/graflow['Ratio'])

                        if  flag_across:  #当前冲突的位置刚好满足穿梁要求

                            print('\n Enter in if flag_across==True,当前冲突的位置刚好满足穿梁要求')

                            #把冲突的点转进线段的坐标集合里面
                            '''Return_List[2]是质心'''
                            #计算起始地到冲突点的距离,更新遗留长度
                            remain_length += Calculate_distance(Start_point,Return_List[2])
                            # Point_Number +=1

                            #先判断线段的方向
                            segment_direction = Direction_Segment(Start_point, Final_point)
                            #先定义出梁的坐标跟撞梁的坐标一样
                            beam_out = Return_List[2].copy()
                            #如果是沿着y轴方向
                            if segment_direction:
                                #沿着y轴方向由小到大,x轴坐标不变
                                if Start_point[1] < Final_point[1]:
                                    beam_out[1] += beam_width
                                    beam_out[2] += high_distance
                                # 沿着y轴方向由大到小,x轴坐标不变
                                else:
                                    beam_out[1] -= beam_width
                                    beam_out[2] += high_distance
                            #计算出梁的坐标
                            #如果是沿着x轴方向
                            else:
                                #沿着x轴方向由小到大,y轴坐标不变
                                if Start_point[0] < Final_point[0]:
                                    beam_out[0] += beam_width
                                    beam_out[2] += high_distance
                                # 沿着x轴方向由大到小,y轴坐标不变
                                else:
                                    beam_out[0] -= beam_width
                                    beam_out[2] += high_distance
                            print('Segment before:',Segment)
                            ''' 增加穿梁点与梁背后的点'''
                            Segment[segment_number].insert((Point_Number + 1), Return_List[2])
                            Segment[segment_number].insert((Point_Number + 2), beam_out)
                            print('Segment after:', Segment)
                            print('Point_Number before:', Point_Number)
                            Point_Number += 2


                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            print('2---- AfterProcessing Segment in flag_across:',Segment)
                            print('Point_Number after:',Point_Number)
                            print('len(Segment[segment_number]:',len(Segment[segment_number]))
                            print('OUT of if flag_across,当前冲突的位置刚好满足穿梁要求')
                            FlagCrossBeam[segment_number].append(Return_List[0])

                        else:
                            print('\nEnter in flag_cross==False, 当前冲突的位置不满足穿梁要求')
                            print('3---- Segment in this if in the begining:',Segment)
                            print('Conflic_Value, Conflict_Point, Confil_Cnenter, confli_center_go_back', Return_List[0],Return_List[1],Return_List[2],Return_List[3])

                            # 如果存在满足要求的穿孔位置,flag=true,返回满足要求所有穿孔的位置中离冲突点最近的一个(该点坐标不是在梁上,而是跟梁有一定距离,因为需要考虑安装空间和包裹)
                            # 反之返回flag=false
                            flag_right, The_right_point = Find_Best_Point(graflow, Return_List[0],Beams, Return_List[2],StructWorkArea3D_With_GraFlow, LenPixel,BeamsValueDict)


                            remain_length += Calculate_distance(Start_point, Return_List[2])

                            # 如果存在这个点
                            if flag_right:
                                print('\n in flag_right,存在Best_point')
                                print('Best Poing:', The_right_point)
                                #查看这条线段的前面部分是否已经穿梁了,如果是,那就不应该移动这条线段
                                #如果不是,那就可以移动这个线段。

                                if len(FlagCrossBeam[segment_number])!=0:        #说明前面装过了梁,这次又穿过另一个梁
                                    print('\nin  if len(FlagCrossBeam[segment_number])!=0:前面装过了梁,这次又穿过另一个梁')
                                    FlagCrossBeam[segment_number].append(Return_List[0])

                                    '''把回退后的点加进去'''
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[3])
                                    Point_Number+=1

                                    #只有Z不一样
                                    if Return_List[2][0] == The_right_point[0] and Return_List[2][1] == The_right_point[1]:

                                        #当前小线段后面所有的点都下降
                                        Segment = Reduce_Z(Point_Number, Segment, segment_number, The_right_point[2] - Return_List[2][2])

                                        #在回退点下面加入垂直下降点
                                        Down_Point = Return_List[3].copy
                                        Down_Point[2] = The_right_point[2]
                                        Segment[segment_number].insert((Point_Number + 1), Down_Point)

                                        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                                        remain_length = 0

                                    #存在XY不一样,Z是否一样未确定
                                    else:
                                        # 如果是冲突点的x坐标跟The_right_point点的坐标不一样
                                        if Return_List[2][0] != The_right_point[0]:
                                            Original_segment = Segment[segment_number].copy()

                                            #所处这段截至回退点
                                            Segment[segment_number] = Original_segment[:Point_Number + 1]

                                            #增加 回退点到Point_Change_X 这一段
                                            Point_Change_X = Return_List[3]
                                            Point_Change_X[0] = The_right_point[0]
                                            Segment.insert(segment_number+1, [Return_List[3], Point_Change_X])

                                            #不用改变z
                                            if Return_List[3][2] == The_right_point[2]:
                                                #原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[0] = The_right_point[0]

                                                Segment.insert(segment_number + 2, left_segment)

                                                #改变原本segment的下一个segment的首个点的X
                                                if segment_number+2 < len(Segment)-1:
                                                    Segment[segment_number + 3][0][0] = The_right_point[0]

                                            #需要改变z
                                            elif Return_List[3][2] != The_right_point[2]:
                                                #增加下降段
                                                Point_Change_X_Down = Point_Change_X.copy()
                                                Point_Change_X_Down[2] = The_right_point[2]
                                                Segment.insert(segment_number + 2, [Point_Change_X, Point_Change_X_Down])

                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[0] = The_right_point[0]

                                                Segment.insert(segment_number + 3, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number+3 < len(Segment)-1:
                                                    Segment[segment_number + 4][0][0] = The_right_point[0]

                                                #改变下降段后面所有段的点的Z值

                                                for i in range(segment_number + 3, len(Segment)):
                                                    for j in range(len(Segment[i])):
                                                        Segment[i][j][2] += (The_right_point[2] - Return_List[3][2])

                                            '''
                                            重新检测本segment到回退点这一段，它将发现没有冲突，从而把工作转移到我们新增加的segment
                                            默认新增加的segment没有冲突，否则就会产生bug！！！！
                                            '''
                                            Point_Number -= 1
                                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number+1]

                                            remain_length = 0 if segment_number==0 else remain_length_segment_number[segment_number-1]


                                        # 如果是冲突点的y坐标跟The_right_point点的坐标不一样
                                        elif Return_List[2][1] != The_right_point[1]:
                                            Original_segment = Segment[segment_number].copy()

                                            # 所处这段截至回退点
                                            Segment[segment_number] = Original_segment[:Point_Number + 1]

                                            # 增加 回退点到Point_Change_X 这一段
                                            Point_Change_Y = Return_List[3]
                                            Point_Change_Y[1] = The_right_point[1]
                                            Segment.insert(segment_number + 1, [Return_List[3], Point_Change_Y])

                                            # 不用改变z
                                            if Return_List[3][2] == The_right_point[2]:
                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[1] = The_right_point[1]

                                                Segment.insert(segment_number + 2, left_segment)

                                                # 改变原本segment的下一个segment的首个点的Y
                                                if segment_number + 2 < len(Segment)-1:
                                                    Segment[segment_number + 3][0][1] = The_right_point[1]

                                            # 需要改变z
                                            elif Return_List[3][2] != The_right_point[2]:
                                                # 增加下降段
                                                Point_Change_Y_Down = Point_Change_Y.copy()
                                                Point_Change_Y_Down[2] = The_right_point[2]
                                                Segment.insert(segment_number + 2,
                                                               [Point_Change_Y, Point_Change_Y_Down])

                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[1] = The_right_point[1]

                                                Segment.insert(segment_number + 3, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number+3 < len(Segment)-1:
                                                    Segment[segment_number + 4][0][1] = The_right_point[1]

                                                # 改变下降段后面所有段的点的Z值
                                                for i in range(segment_number + 3, len(Segment)):
                                                    for j in range(len(Segment[i])):
                                                        Segment[i][j][2] += (The_right_point[2] - Return_List[3][2])


                                            '''
                                            重新检测本segment到回退点这一段，它将发现没有冲突，从而把工作转移到我们新增加的segment
                                            默认新增加的segment没有冲突，否则就会产生bug！！！！
                                            '''
                                            Point_Number -= 1
                                            Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                       Segment[segment_number][Point_Number + 1]

                                            remain_length = 0 if segment_number == 0 else remain_length_segment_number[
                                                segment_number - 1]

                                        else:
                                            raise Exception('Error in 撞梁，bestpoint与中心点不一致的处理过程中')

                                else:
                                    # 这是第一次穿梁,所以可以整体移动
                                    print('\nin else:这是第一次穿梁')
                                    # 这个线段之前没有穿梁,根据冲突点与The_right_point的坐标差异,移动整条线段,更新segment
                                    Segment = Remove(Segment, segment_number, Return_List[2], The_right_point, Point_Number, StructWorkArea3D_With_GraFlow, graflow)

                                    Point_Number = 0
                                    segment_number = 0
                                    # Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number+1]

                                    remain_length = 0 if segment_number==0 else remain_length_segment_number[segment_number-1]

                                    print('5-- Segment after processing:',Segment)
                                    print('OUT of this if \n\n\n')

                            #如果不存在这个点
                            else:
                                print('\n\nin put_pipe() if 不存在best_point,下降梁')
                                # 根据冲突点坐标计算绕过梁需要下降多少个像素

                                pixel_number = Calculate_Down_Beam(graflow, Beams, Return_List[0], Return_List[2],LenPixel, BeamsValueDict)
                                # 在线段中加入冲突点(也就是下降点)

                                print('pixel num:',pixel_number)
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                # 先判断线段的方向
                                #segment_direction = Direction_Segment(Start_point, Final_point)
                                # 先定义回退后的点为back_point
                                back_point = Return_List[3].copy()
                                
                                back_point_Down = back_point + [0,0,pixel_number]

                                '''#把回退后的点加进去'''
                                Segment[segment_number].insert((Point_Number + 1), back_point)
                                Segment[segment_number].insert((Point_Number + 2), back_point_Down)
                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Return_List',Return_List)
                                print('back_point',back_point)
                                print('back_point_Down',back_point_Down)

                                print('6--- After processing Segment:',Segment)
                                print('OUT of this if \n\n')
                            FlagCrossBeam[segment_number].append(Return_List[0])

                    #NewSize > 250,直接绕梁
                    else:
                        print('\n================\n Enter in if Else(NewSize >= 250)')
                        # 根据冲突点的坐标计算绕过梁需要下降多少个像素

                        print('Segment Before:', Segment)
                        for index in range(len(Segment)):
                            if not isinstance(Segment[index], list):
                                Segment[index] = Segment[index].tolist()

                        pixel_number = Calculate_Down_Beam(graflow, Beams, Return_List[0], Return_List[2],LenPixel, BeamsValueDict)
                        print('pixel_number',pixel_number)
                        # 在线段中加入冲突点(也就是下降点)

                        Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                        print('Segment after Reduce_Z:', Segment)

                        # 先定义回退后的点为back_point
                        back_point = np.array(Return_List[3])

                        back_point_Down = back_point + [0,0,pixel_number]

                        '''#把回退后的点加进去'''
                        Segment[segment_number].insert((Point_Number + 1), back_point)
                        Segment[segment_number].insert((Point_Number + 2), back_point_Down)
                        Point_Number += 2
                        # 更新起始点和终点
                        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                        remain_length = 0
                        print('Segment after Out:', Segment)
                        print('out of this else\n======================\n')


                #平行撞管
                elif flag==3:
                    print('============================Enter in flag==3 平行撞管 special===============================')
                    print('segment before of pipe2')
                    print(Segment)
                    print('平行 conflictValue:', Return_List[0])

                    pixel_number = Find_point(Graflow, graflow, StructWorkArea3D_With_GraFlow, PipesValueDict, Return_List.copy())
                    # 观察走廊和管线,修改线段的起点，转折点，终点 使得走廊排的下又不跟别的管道冲突
                    '''2020/4/23 需要加回退   而且是Center0fConflictPipe'''
                    #如果这个线段没有闯过梁,说明可以移动
                    # print('type(FlagCrossBeam[segment_number]',type(FlagCrossBeam[segment_number]))

                    remain_length,Segment,segment_number,Point_Number,Start_point,Final_point = Find_Room_GraFlow(Point_Number, pixel_number,segment_number,Start_point,Final_point,Segment, StructWorkArea3D_With_GraFlow, Graflow, graflow,Return_List.copy(),FlagCrossBeam[segment_number])

                    print('segment after processing  in Find_Room_GraFlow:  ')
                    print(Segment,'\n')
                    print('=======================================Out================================\n\n')

                #两个线段交叉
                elif flag==4:
                    print('\n=========Enter in put_pipe flag=4 交叉 ')
                    print('Segment before:', Segment)
                    # 计算需要下降多少像素,绕过线段
                    pixel_number = Find_point(Graflow, graflow, StructWorkArea3D_With_GraFlow, PipesValueDict, Return_List.copy())
                    print('pixel number', pixel_number)
                    print('center conflict point ', Return_List[2])

                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    # 先定义回退后的点为back_point
                    back_point = Return_List[3]
                    Segment[segment_number].insert((Point_Number + 1), back_point)
                    down_point = Return_List[3].copy()
                    down_point[2] += pixel_number

                    Segment[segment_number].insert((Point_Number + 2), down_point)
                    Point_Number += 2
                    # 更新起始点和终点
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                    remain_length = 0
                    print('\nAfter Processing \n Segment after:',Segment)
                    print('Pointer_Number:',Point_Number)
                    print('Start point:', Start_point)
                    print('Out of if;star loop again')

                elif flag==5:
                    # '''这里统一下降200'''
                    pixel_number = math.ceil(200/LenPixel)
                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    # 先定义回退后的点为back_point
                    back_point = Return_List[3]
                    down_point = Return_List[3]
                    down_point[2] += pixel_number
                    Segment[segment_number].insert((Point_Number + 1), back_point)
                    Segment[segment_number].insert((Point_Number + 2), down_point)
                    Point_Number += 2
                    # 更新起始点和终点
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                        Point_Number + 1]
                    remain_length = 0
            #没有冲突
            else:
                print('\n\nin if 没有冲突')
                print('Segment:',Segment)

                Point_Number += 1

                # 把这个管线的遗留长度保存下来
                remain_length += Calculate_distance(Start_point, Final_point)
                # 如果是最后一个坐标,说明这条线段已经处理完了,开始进入下一个线段
                if Point_Number==(len(Segment[segment_number])-1):
                    print('进入到 没有冲突-》最后一个坐标，已经处理完毕，进入下一个阶段')
                    # 在对应线段位置segment_number上把遗留长度保存起来
                    remain_length_segment_number[segment_number] = remain_length

                    segment_number += 1
                    break
                else:
                    print('没有进入到if')

                    Start_point,Final_point=Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]

                print('Out of this if\n\n')
    return StructWorkArea3D_With_GraFlow, Segment

def Against_wall_MAVC(StructWorkArea3D_With_GraFlow_With_MVAV, MvacFlow, LenPixel, Z_Max, Beams, LogPath):
    print('\nTest in Against_wall_GraFlow():\n')
    print('Before Against_wall_GraFlow:', MvacFlow)
    # Temporary_StructWorkArea3D_With_GraFlow只是用于下面Against_wall函数靠墙处,并不是真正用于输出的矩阵
    Temporary_StructWorkArea3D_With_GraFlow_MVAV = StructWorkArea3D_With_GraFlow_With_MVAV.copy()
    # 把风管调成梁下。需要确认
    ''' 改1'''
    # GraFlow = up_graflow(GraFlow)


    # 每条管线进行遍历,graflow_number为第几个管线
    i = 1
    for mvacflow_number in range(len(MvacFlow)):

        print('====================第%d条管=============================' % i)
        i += 1

        Point_Number = 0  # 表示现在是管线的第几个坐标

        while (Point_Number < len(MvacFlow[mvacflow_number]['Route']) - 2):  # 如果是最后一个坐标,说明这条管线已经处理完了

            # 根据当前线段离两边(障碍物距离)的距离,
            # 把当前线段起始点和终点往距离少的一遍靠经(坐标改变),输入线段的头和尾坐标
            # 注：目前障碍物包括管线和墙,也要考虑这一层排不下，需要到下一层
            MvacFlow[mvacflow_number] = Against_wall(MvacFlow, Point_Number, MvacFlow[mvacflow_number],
                                                   Temporary_StructWorkArea3D_With_GraFlow_MVAV)

            Point_Number += 1

        print('GraFlow[graflow_number] 1:\n', MvacFlow[mvacflow_number])
        print('开始 put_finalsegment()')
        # 最后一个线段的往左边靠墙
        MvacFlow[mvacflow_number] = put_final_segment(Point_Number, MvacFlow[mvacflow_number], MvacFlow,
                                                    Temporary_StructWorkArea3D_With_GraFlow_MVAV)

        print('type(GraFlow[mvacflow_number])', type(MvacFlow[mvacflow_number]))
        print('GraFlow[mvacflow_number] 2: \n', MvacFlow[mvacflow_number])

        # 根据更新好了的坐标去排布管线(不考虑冲突直接排布),更新Temporary_StructWorkArea3D_With_GraFlow，用于上面Against_wall函数       
        Temporary_StructWorkArea3D_With_GraFlow_MVAV = pre_put_graflow(MvacFlow[mvacflow_number],
                                                                  Temporary_StructWorkArea3D_With_GraFlow_With_MVAV, LenPixel)

    MvacFlow = Add_Ratio_Z_For_Against_wall_GraFlow(MvacFlow)

    print('Against_wall_MvacFlow Test out \n\n')
    return None


def put_MVAC(StructWorkArea3D_With_GraFlow_With_MVAV, MVAC_Against_Wall, Mvacflow, LenPixel, Z_Max, Beams, LogPath, PipesValueDict, BeamsValueDict):
    print('\n\nTest in put_GraFlow:\n')
    # lowest_z为管线的最低点的坐标
    lowest_z = 0
    # 每条管线进行遍历
    '''注'''
    print('\n\n\ngraflow i:', Mvacflow, '\n\n\n')

    # 每条管线的每条线段进行遍历,把管线分成几个线段,每个线段是一个数组,里面包括线段的起始点和终点,后续会插入一下转折点
    # Segment=[[(x1,y1),(x2,y2)],[(x2,y2),(x3,y3)]...]
    Segment = Create_Segment(Mvacflow)
    print('1---- Original Segment:\n', Segment, '\n')

    '''定义FlagCrossBeam=[1,1,1,,1,0,0]'''
    '''remain_length_segment_number'''
    # 用来记录当前这个管线的各个大Segment中是否有撞梁
    FlagCrossBeam = {}
    for index_segment in range(len(Segment) + 10):
        FlagCrossBeam[index_segment] = []

    #remain_length_segment_number = [0] * (len(Segment) + 20)
    remain_length = 0  # 上一个线段的遗留长度,风管不需要检测30米,为了程序输入参数保留.
    segment_number = 0  # 当前是第几个线段,也就是Segment中第几个数组

    while segment_number < len(Segment):

        Point_Number = 0  # 表示现在是线段的第几个坐标
        # 初始化起始点和终点为线段的头尾两点,检测冲突也是查看这Start_point,Final_point两个点之间是否有冲突
        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]

        while 1:
            # 把Start_point,Final_point=Start_point之间的线段排布进一个暂时的矩阵Temporary_StructWorkArea3D_With_GraFlow
            # 一开始Start_point,Final_point为线段的头坐标和尾坐标,但是如果中间出现30米下降,那么就需要在线段的数组中添加两个点,
            # 一个是冲突发生的点,一个是30米下降的点,把这两个点插入到线段输入中,那么线段数组现在的元素就有[线段头坐标,冲突发生的点,30米下降的点,线段尾坐标]
            # 下一步循环是就从下降后的点开始走下去(冲突处理后前面的部分就不用理他了,接着看线段的后面部分),
            # 那么更新Start_point,Final_point为线段的30米下降的点,线段尾坐标.
            # 而Point_Number表示的是Start_point在线段数组中的位置,当Start_point为数组最后第二个元素,也就是Final_point数组最后第一个元素
            # 并且检测没有冲突是,这个线段就检测结束,

            # 从起始点沿着管线检测(30米 - 遗留长度remain_length)如果中间没有下降就发生了30米冲突，按照管线的走向进行冲突排序
            # 返回flag=(1,2,3)分别表示第一个冲突类型为30米冲突,撞梁，撞管,flag=0表示没有冲突
            # 返回conflict_point为第一个发生冲突的坐标,down_length为需要下降多少个像素

            print(',start_point', Start_point)
            print('Segment', Segment)
            flag, Return_List = Compare(Mvacflow, StructWorkArea3D_With_GraFlow_With_MVAV, Start_point, Final_point, remain_length,
                                        LenPixel, FlagCrossBeam[segment_number])
            print('What is the compare flag?', flag)

            # 把发生冲突的类型flag和冲突发生在第几个线段这些信息输入到输出报告中

            ''' 未定义
            PutConflictInReport(flag,segment_number,graflow,'GraFlow')
            '''

            # 如果Start_point到Final_point有冲突
            if flag != False:
                if flag == 2:  # 撞梁
                    '''管线相撞也得改变考虑这跟线段是否穿梁了'''
                    '''注意撞梁一次跟多次的区别'''
                    print('\n Enter in elif flag==2')

                    ''''''
                    NewSize = Calculate_NewSzie(graflow)

                    if NewSize <= 250:
                        print('\n Enter in if NewSize <= 250')

                        # 看当前起始点到终点穿梁的位置是否刚好满足要求,是的话返回flag_across=true,反之返回flag_across=false
                        flag_across = Check_Right(graflow, Beams, Return_List[0], StructWorkArea3D_With_GraFlow,
                                                  Start_point, Final_point, LenPixel, PipesValueDict, BeamsValueDict)

                        # 根据冲突点的value找到他是对应哪一条梁
                        beam_value = Return_List[0]
                        # beam_index为梁的索引
                        beam_index = BeamsValueDict[beam_value]
                        # 找到梁的宽对应的像素个数
                        beam_width = math.ceil(Beams[beam_index]['BWidth'] / LenPixel)
                        # 计算出梁的点对应撞梁的点的高度差对应的像素个数
                        high_distance = math.ceil(beam_width / graflow['Ratio'])

                        if flag_across:  # 当前冲突的位置刚好满足穿梁要求

                            print('\n Enter in if flag_across==True,当前冲突的位置刚好满足穿梁要求')

                            # 把冲突的点转进线段的坐标集合里面
                            '''Return_List[2]是质心'''
                            # 计算起始地到冲突点的距离,更新遗留长度
                            remain_length += Calculate_distance(Start_point, Return_List[2])
                            # Point_Number +=1

                            # 先判断线段的方向
                            segment_direction = Direction_Segment(Start_point, Final_point)
                            # 先定义出梁的坐标跟撞梁的坐标一样
                            beam_out = Return_List[2].copy()
                            # 如果是沿着y轴方向
                            if segment_direction:
                                # 沿着y轴方向由小到大,x轴坐标不变
                                if Start_point[1] < Final_point[1]:
                                    beam_out[1] += beam_width
                                    beam_out[2] += high_distance
                                # 沿着y轴方向由大到小,x轴坐标不变
                                else:
                                    beam_out[1] -= beam_width
                                    beam_out[2] += high_distance
                            # 计算出梁的坐标
                            # 如果是沿着x轴方向
                            else:
                                # 沿着x轴方向由小到大,y轴坐标不变
                                if Start_point[0] < Final_point[0]:
                                    beam_out[0] += beam_width
                                    beam_out[2] += high_distance
                                # 沿着x轴方向由大到小,y轴坐标不变
                                else:
                                    beam_out[0] -= beam_width
                                    beam_out[2] += high_distance
                            print('Segment before:', Segment)
                            ''' 增加穿梁点与梁背后的点'''
                            Segment[segment_number].insert((Point_Number + 1), Return_List[2])
                            Segment[segment_number].insert((Point_Number + 2), beam_out)
                            print('Segment after:', Segment)
                            print('Point_Number before:', Point_Number)
                            Point_Number += 2

                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                                Point_Number + 1]
                            print('2---- AfterProcessing Segment in flag_across:', Segment)
                            print('Point_Number after:', Point_Number)
                            print('len(Segment[segment_number]:', len(Segment[segment_number]))
                            print('OUT of if flag_across,当前冲突的位置刚好满足穿梁要求')
                            FlagCrossBeam[segment_number].append(Return_List[0])

                        else:
                            print('\nEnter in flag_cross==False, 当前冲突的位置不满足穿梁要求')
                            print('3---- Segment in this if in the begining:', Segment)
                            print('Conflic_Value, Conflict_Point, Confil_Cnenter, confli_center_go_back',
                                  Return_List[0], Return_List[1], Return_List[2], Return_List[3])

                            # 如果存在满足要求的穿孔位置,flag=true,返回满足要求所有穿孔的位置中离冲突点最近的一个(该点坐标不是在梁上,而是跟梁有一定距离,因为需要考虑安装空间和包裹)
                            # 反之返回flag=false
                            flag_right, The_right_point = Find_Best_Point(graflow, Return_List[0], Beams,
                                                                          Return_List[2], StructWorkArea3D_With_GraFlow,
                                                                          LenPixel, BeamsValueDict)

                            remain_length += Calculate_distance(Start_point, Return_List[2])

                            # 如果存在这个点
                            if flag_right:
                                print('\n in flag_right,存在Best_point')
                                print('Best Poing:', The_right_point)
                                # 查看这条线段的前面部分是否已经穿梁了,如果是,那就不应该移动这条线段
                                # 如果不是,那就可以移动这个线段。

                                if len(FlagCrossBeam[segment_number]) != 0:  # 说明前面装过了梁,这次又穿过另一个梁
                                    print('\nin  if len(FlagCrossBeam[segment_number])!=0:前面装过了梁,这次又穿过另一个梁')
                                    FlagCrossBeam[segment_number].append(Return_List[0])

                                    '''把回退后的点加进去'''
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[3])
                                    Point_Number += 1

                                    # 只有Z不一样
                                    if Return_List[2][0] == The_right_point[0] and Return_List[2][1] == The_right_point[
                                        1]:

                                        # 当前小线段后面所有的点都下降
                                        Segment = Reduce_Z(Point_Number, Segment, segment_number,
                                                           The_right_point[2] - Return_List[2][2])

                                        # 在回退点下面加入垂直下降点
                                        Down_Point = Return_List[3].copy
                                        Down_Point[2] = The_right_point[2]
                                        Segment[segment_number].insert((Point_Number + 1), Down_Point)

                                        Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                   Segment[segment_number][Point_Number + 1]
                                        remain_length = 0

                                    # 存在XY不一样,Z是否一样未确定
                                    else:
                                        # 如果是冲突点的x坐标跟The_right_point点的坐标不一样
                                        if Return_List[2][0] != The_right_point[0]:
                                            Original_segment = Segment[segment_number].copy()

                                            # 所处这段截至回退点
                                            Segment[segment_number] = Original_segment[:Point_Number + 1]

                                            # 增加 回退点到Point_Change_X 这一段
                                            Point_Change_X = Return_List[3]
                                            Point_Change_X[0] = The_right_point[0]
                                            Segment.insert(segment_number + 1, [Return_List[3], Point_Change_X])

                                            # 不用改变z
                                            if Return_List[3][2] == The_right_point[2]:
                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[0] = The_right_point[0]

                                                Segment.insert(segment_number + 2, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number + 2 < len(Segment) - 1:
                                                    Segment[segment_number + 3][0][0] = The_right_point[0]

                                            # 需要改变z
                                            elif Return_List[3][2] != The_right_point[2]:
                                                # 增加下降段
                                                Point_Change_X_Down = Point_Change_X.copy()
                                                Point_Change_X_Down[2] = The_right_point[2]
                                                Segment.insert(segment_number + 2,
                                                               [Point_Change_X, Point_Change_X_Down])

                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[0] = The_right_point[0]

                                                Segment.insert(segment_number + 3, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number + 3 < len(Segment) - 1:
                                                    Segment[segment_number + 4][0][0] = The_right_point[0]

                                                # 改变下降段后面所有段的点的Z值

                                                for i in range(segment_number + 3, len(Segment)):
                                                    for j in range(len(Segment[i])):
                                                        Segment[i][j][2] += (The_right_point[2] - Return_List[3][2])

                                            '''
                                            重新检测本segment到回退点这一段，它将发现没有冲突，从而把工作转移到我们新增加的segment
                                            默认新增加的segment没有冲突，否则就会产生bug！！！！
                                            '''
                                            Point_Number -= 1
                                            Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                       Segment[segment_number][Point_Number + 1]

                                            remain_length = 0 if segment_number == 0 else remain_length_segment_number[
                                                segment_number - 1]


                                        # 如果是冲突点的y坐标跟The_right_point点的坐标不一样
                                        elif Return_List[2][1] != The_right_point[1]:
                                            Original_segment = Segment[segment_number].copy()

                                            # 所处这段截至回退点
                                            Segment[segment_number] = Original_segment[:Point_Number + 1]

                                            # 增加 回退点到Point_Change_X 这一段
                                            Point_Change_Y = Return_List[3]
                                            Point_Change_Y[1] = The_right_point[1]
                                            Segment.insert(segment_number + 1, [Return_List[3], Point_Change_Y])

                                            # 不用改变z
                                            if Return_List[3][2] == The_right_point[2]:
                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[1] = The_right_point[1]

                                                Segment.insert(segment_number + 2, left_segment)

                                                # 改变原本segment的下一个segment的首个点的Y
                                                if segment_number + 2 < len(Segment) - 1:
                                                    Segment[segment_number + 3][0][1] = The_right_point[1]

                                            # 需要改变z
                                            elif Return_List[3][2] != The_right_point[2]:
                                                # 增加下降段
                                                Point_Change_Y_Down = Point_Change_Y.copy()
                                                Point_Change_Y_Down[2] = The_right_point[2]
                                                Segment.insert(segment_number + 2,
                                                               [Point_Change_Y, Point_Change_Y_Down])

                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[1] = The_right_point[1]

                                                Segment.insert(segment_number + 3, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number + 3 < len(Segment) - 1:
                                                    Segment[segment_number + 4][0][1] = The_right_point[1]

                                                # 改变下降段后面所有段的点的Z值
                                                for i in range(segment_number + 3, len(Segment)):
                                                    for j in range(len(Segment[i])):
                                                        Segment[i][j][2] += (The_right_point[2] - Return_List[3][2])

                                            '''
                                            重新检测本segment到回退点这一段，它将发现没有冲突，从而把工作转移到我们新增加的segment
                                            默认新增加的segment没有冲突，否则就会产生bug！！！！
                                            '''
                                            Point_Number -= 1
                                            Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                       Segment[segment_number][Point_Number + 1]

                                            remain_length = 0 if segment_number == 0 else remain_length_segment_number[
                                                segment_number - 1]

                                        else:
                                            raise Exception('Error in 撞梁，bestpoint与中心点不一致的处理过程中')

                                else:
                                    # 这是第一次穿梁,所以可以整体移动
                                    print('\nin else:这是第一次穿梁')
                                    # 这个线段之前没有穿梁,根据冲突点与The_right_point的坐标差异,移动整条线段,更新segment
                                    Segment = Remove(Segment, segment_number, Return_List[2], The_right_point,
                                                     Point_Number, StructWorkArea3D_With_GraFlow, graflow)

                                    Point_Number = 0
                                    segment_number = 0
                                    # Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number+1]

                                    remain_length = 0 if segment_number == 0 else remain_length_segment_number[
                                        segment_number - 1]

                                    print('5-- Segment after processing:', Segment)
                                    print('OUT of this if \n\n\n')

                            # 如果不存在这个点
                            else:
                                print('\n\nin put_pipe() if 不存在best_point,下降梁')
                                # 根据冲突点坐标计算绕过梁需要下降多少个像素

                                pixel_number = Calculate_Down_Beam(graflow, Beams, Return_List[0], Return_List[2],
                                                                   LenPixel, BeamsValueDict)
                                # 在线段中加入冲突点(也就是下降点)

                                print('pixel num:', pixel_number)
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                # 先判断线段的方向
                                # segment_direction = Direction_Segment(Start_point, Final_point)
                                # 先定义回退后的点为back_point
                                back_point = Return_List[3].copy()

                                back_point_Down = back_point + [0, 0, pixel_number]

                                '''#把回退后的点加进去'''
                                Segment[segment_number].insert((Point_Number + 1), back_point)
                                Segment[segment_number].insert((Point_Number + 2), back_point_Down)
                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                           Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Return_List', Return_List)
                                print('back_point', back_point)
                                print('back_point_Down', back_point_Down)

                                print('6--- After processing Segment:', Segment)
                                print('OUT of this if \n\n')
                            FlagCrossBeam[segment_number].append(Return_List[0])

                    # NewSize > 250,直接绕梁
                    else:
                        print('\n================\n Enter in if Else(NewSize >= 250)')
                        # 根据冲突点的坐标计算绕过梁需要下降多少个像素

                        print('Segment Before:', Segment)
                        for index in range(len(Segment)):
                            if not isinstance(Segment[index], list):
                                Segment[index] = Segment[index].tolist()

                        pixel_number = Calculate_Down_Beam(graflow, Beams, Return_List[0], Return_List[2], LenPixel,
                                                           BeamsValueDict)
                        print('pixel_number', pixel_number)
                        # 在线段中加入冲突点(也就是下降点)

                        Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                        print('Segment after Reduce_Z:', Segment)

                        # 先定义回退后的点为back_point
                        back_point = np.array(Return_List[3])

                        back_point_Down = back_point + [0, 0, pixel_number]

                        '''#把回退后的点加进去'''
                        Segment[segment_number].insert((Point_Number + 1), back_point)
                        Segment[segment_number].insert((Point_Number + 2), back_point_Down)
                        Point_Number += 2
                        # 更新起始点和终点
                        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                            Point_Number + 1]
                        remain_length = 0
                        print('Segment after Out:', Segment)
                        print('out of this else\n======================\n')


                # 平行撞管
                elif flag == 3:
                    print('============================Enter in flag==3 平行撞管 special===============================')
                    print('、nsegment before of pipe2')
                    print(Segment)
                    print('平行 conflictValue:', Return_List[0])

                    pixel_number = Find_point(MVAC_Against_Wall, Mvacflow, StructWorkArea3D_With_GraFlow_With_MVAV, PipesValueDict,
                                              Return_List.copy())
                    # 观察走廊和管线,修改线段的起点，转折点，终点 使得走廊排的下又不跟别的管道冲突
                    '''2020/4/23 需要加回退   而且是Center0fConflictPipe'''
                    # 如果这个线段没有闯过梁,说明可以移动
                    # print('type(FlagCrossBeam[segment_number]',type(FlagCrossBeam[segment_number]))

                    remain_length, Segment, segment_number, Point_Number, Start_point, Final_point = Find_Room_GraFlow(
                        Point_Number, pixel_number, segment_number, Start_point, Final_point, Segment,
                        StructWorkArea3D_With_GraFlow, Graflow, graflow, Return_List.copy(),
                        FlagCrossBeam[segment_number])

                    print('segment after processing  in Find_Room_GraFlow:  ')
                    print(Segment, '\n')
                    print('=======================================Out================================\n\n')

                # 两个线段交叉
                elif flag == 4:
                    print('\n=========Enter in put_pipe flag=4 交叉 ')
                    print('Segment before:', Segment)
                    # 计算需要下降多少像素,绕过线段
                    pixel_number = Find_point(MVAC_Against_Wall, Mvacflow, StructWorkArea3D_With_GraFlow_With_MVAV, PipesValueDict,
                                              Return_List.copy())
                    print('pixel number', pixel_number)
                    print('center conflict point ', Return_List[2])

                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    # 先定义回退后的点为back_point
                    back_point = Return_List[3]
                    Segment[segment_number].insert((Point_Number + 1), back_point)
                    down_point = Return_List[3].copy()
                    down_point[2] += pixel_number

                    Segment[segment_number].insert((Point_Number + 2), down_point)

                    #计算绕过冲突交叉管道所需长度？？？
                    collisionPipeLen = calculate_collision_length()

                    #定义绕过冲突后的点为 pass_point
                    pass_point = Return_List[3].copy
                    pass_point[1] += collisionPipeLen
                    Segment[segment_number].insert((Point_Number + 3), pass_point)

                    #定义绕过冲突后，上升的点为parallel_point
                    parallel_point = Return_List[3].copy()
                    parallel_point[2] -= pixel_number
                    Segment[segment_number].insert((Point_Number + 4), parallel_point)

                    #point number 的增加 ？？？
                    Point_Number += 4

                    # 更新起始点和终点 ???
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                        Point_Number + 1]

                    remain_length = 0
                    print('\nAfter Processing \n Segment after:', Segment)
                    print('Pointer_Number:', Point_Number)
                    print('Start point:', Start_point)
                    print('Out of if;star loop again')

                elif flag == 5:
                    # '''这里统一下降200'''
                    pixel_number = math.ceil(200 / LenPixel)
                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    # 先定义回退后的点为back_point
                    back_point = Return_List[3]
                    down_point = Return_List[3]
                    down_point[2] += pixel_number
                    Segment[segment_number].insert((Point_Number + 1), back_point)
                    Segment[segment_number].insert((Point_Number + 2), down_point)
                    Point_Number += 2
                    # 更新起始点和终点
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                        Point_Number + 1]
                    remain_length = 0
            # 没有冲突
            else:
                print('\n\nin if 没有冲突')
                print('Segment:', Segment)

                Point_Number += 1

                # 把这个管线的遗留长度保存下来
                remain_length += Calculate_distance(Start_point, Final_point)
                # 如果是最后一个坐标,说明这条线段已经处理完了,开始进入下一个线段
                if Point_Number == (len(Segment[segment_number]) - 1):
                    print('进入到 没有冲突-》最后一个坐标，已经处理完毕，进入下一个阶段')
                    # 在对应线段位置segment_number上把遗留长度保存起来
                    remain_length_segment_number[segment_number] = remain_length

                    segment_number += 1
                    break
                else:
                    print('没有进入到if')

                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                        Point_Number + 1]

                print('Out of this if\n\n')
    return StructWorkArea3D_With_GraFlow, Segment

    return None