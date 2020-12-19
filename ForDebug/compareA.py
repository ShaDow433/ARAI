'''
Descripttion: 
version: 
Author: Zhiting Zhang
email: 1149357968@qq.com
Date: 2020-09-18 01:23:53
LastEditors: Zhiting Zhang
LastEditTime: 2020-12-05 15:55:43
'''
if flag==2 : #撞梁
                    '''管线相撞也得改变考虑这跟线段是否穿梁了'''
                    '''注意撞梁一次跟多次的区别'''
                    print('\n Enter in elif flag==2')
                    NewSize = Calculate_NewSize(mvacflow)
                    if NewSize <= 250:
                        print('\n Enter in if NewSize <= 250')

                        # 看当前起始点到终点穿梁的位置是否刚好满足要求,是的话返回flag_across=true,反之返回flag_across=false
                        flag_across = Check_Right(mvacflow, Beams, Return_List[0], StructWorkArea3D_With_GraFlow,Start_point,Final_point,LenPixel,PipesValueDict, BeamsValueDict)

                        #根据冲突点的value找到他是对应哪一条梁
                        beam_value=Return_List[0]
                        #beam_index为梁的索引
                        beam_index=BeamsValueDict[beam_value]
                        #找到梁的宽对应的像素个数
                        beam_width = math.ceil(Beams[beam_index]['BWidth']/LenPixel)
                        #计算出梁的点对应撞梁的点的高度差对应的像素个数
                        high_distance=math.ceil(beam_width/mvacflow['Ratio'])

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
                            flag_right, The_right_point = Find_Best_Point(mvacflow, Return_List[0],Beams, Return_List[2],StructWorkArea3D_With_GraFlow, LenPixel,BeamsValueDict)


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
                                    Segment = Remove(Segment, segment_number, Return_List[2], The_right_point, Point_Number, StructWorkArea3D_With_GraFlow, mvacflow)

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

                                pixel_number = Calculate_Down_Beam(mvacflow, Beams, Return_List[0], Return_List[2],LenPixel, BeamsValueDict)
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

                        pixel_number = Calculate_Down_Beam(mvacflow, Beams, Return_List[0], Return_List[2],LenPixel, BeamsValueDict)
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
