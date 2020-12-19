import numpy as np
import math

#在矩阵穿梁位置做一个标记,防止后续管道移位是忘记这里已经穿梁了
def Make_label(segment_number, FlagCrossBeam):

    FlagCrossBeam[:segment_number+1] = 1

    return FlagCrossBeam



#查看这条线段的前面部分是否已经穿梁了,如果是,那就不应该移动这条线段
#如果不是,那就可以移动这个线段。
def CheckCorssBeam(segment_number, FlagCrossBeam):

    return FlagCrossBeam[segment_number-1]


def Find_point(Graflow, graflow,  StructWorkArea3D_With_GraFlow,  PipesValueDict, Return_List):
    ConflictValue = Return_List[0]
    conflict_point = Return_List[1]
    CenterOfConflictPoint = Return_List[2]

    print('\nEnter in find point()')
    print('ConflictValue',ConflictValue)
    print('CenterOfConflictPoint',CenterOfConflictPoint)

    #找到冲突的已排布管线在现排布管线经过的空间的最低点Z
    Exist_graflow = Graflow[PipesValueDict[ConflictValue]]
 
    Slide_For_Searching_Lowest_Z = StructWorkArea3D_With_GraFlow[conflict_point[0], conflict_point[1],  :].copy()

    Z_Lowest = np.argwhere(Slide_For_Searching_Lowest_Z==ConflictValue).max()
    print('np.argwhere(Slide_For_Searching_Lowest_Z==ConflictValue).max():',np.argwhere(Slide_For_Searching_Lowest_Z==ConflictValue).max())
    print('conflict_point[2]',conflict_point[2])
    print('Z_Lowest',Z_Lowest)

    if ConflictValue%1000==61 or ConflictValue%1000==62 or ConflictValue%1000==63:
        print('enter in Find_Point; if ConflictValue%1000==61 or ConflictValue%1000==62 or ConflictValue%1000==63:')

        print('Z_Lowest befor:', Z_Lowest)
        Z_Lowest += Exist_graflow['SpacePixelLen']
        print('Z_Lowest after:',Z_Lowest)


    #有一种情况，就是第一层管的space被第二层侵占了，导致招到的lowest数值小得多。故向上在这里做一个比较可能的纠偏
    Slide_For_Searching_2 = StructWorkArea3D_With_GraFlow[conflict_point[0], conflict_point[1], :].copy()
    Exist_Space_Highest = np.argwhere(Slide_For_Searching_2==ConflictValue).min()
    Z_Lowest_2 = Exist_Space_Highest + Exist_graflow['SpacePixelLen'] *2 + Exist_graflow['NewSizePixelLen'][0]

    Z_Lowest = max(Z_Lowest, Z_Lowest_2)



    # 共用安装空间
    if graflow['SpacePixelLen'] <= Exist_graflow['SpacePixelLen']:
        pixel_number_cross = Z_Lowest - CenterOfConflictPoint[2] + 1 +  np.ceil(graflow['NewSizePixelLen'][1]/2).astype(int)
    else:
        pixel_number_cross = Z_Lowest - CenterOfConflictPoint[2] + 1 + np.ceil(graflow['NewSizePixelLen'][1]/2).astype(int) + graflow['SpacePixelLen'] -Exist_graflow['SpacePixelLen']

    print('pixel_number_cross：', pixel_number_cross)
    print('OUT Find_Point()\n')
    return np.ceil(pixel_number_cross).astype(int)



# 根据冲突点的坐标计算绕过梁需要下降多少个像素
def Calculate_Down_Beam(graflow, Beams, BeamValue, CenterOfConflictPipe, LenPixel,BeamsValueDict):

    Beam = Beams[BeamsValueDict[BeamValue]]
    pixel_number = Beam['DepthPixel'] + np.ceil(graflow['NewSizePixelLen'][1]/2).astype(int) + graflow['SpacePixelLen'] - CenterOfConflictPipe[2] + 1

    return pixel_number



#根据冲突的位置所对应的两条线段,判断他们的走向,如果为平行flag=true,反之flag=false
def Direction(segment,Point_Number,StructWorkArea3D_With_GraFlow,CenterOfConflictPipe):

    diff_X = segment[0][0] - segment[1][0]
    diff_Y = segment[0][1] - segment[1][1]


    #X相等为1，Y相等为0
    Direction_Segment = 1 if abs(diff_X) < abs(diff_Y) else 0 
    Direction_ConflictPipe = 1 if  str(StructWorkArea3D_With_GraFlow[CenterOfConflictPipe[0],CenterOfConflictPipe[1],CenterOfConflictPipe[2]])[-1]==1 else 0 

    return Direction_Segment==Direction_ConflictPipe


def put_output(graflow, StructWorkArea3D_With_GraFlow, StructWorkArea2D, segment, Z_Max, LenPixel):
    print('\nTest in put_output():')
    print('小segment:', segment)

    FlagDirection = 'X_EqValue' if segment[0][0] == segment[-1][0] else 'Y_EqValue'

    if FlagDirection == 'X_EqValue':
        Flag = 'LowToHigh' if segment[0][1] < segment[-1][1] else 'HighToLow'

    else:
        Flag = 'LowToHigh' if segment[0][0] < segment[-1][0] else 'HighToLow'

    Ratio = graflow['Ratio']
    SpacePixelLen = graflow['SpacePixelLen']
    HalfNewSizePixelLen = np.ceil(graflow['NewSizePixelLen'][0][0] / 2).astype(int)

    lowest_z = segment[-1][2] + HalfNewSizePixelLen

    if lowest_z > Z_Max:
        print('穿假天花了')
        print('Segment[-1]:', segment[-1], '\n')
        '''
        增加StructWorkArea3D_With_GraFlow厚度，
        报告穿板
        '''
        StructWorkArea3D_Append = np.zeros(
            (StructWorkArea2D.shape[0], StructWorkArea2D.shape[1], lowest_z - Z_Max)) + StructWorkArea2D[:, :,
                                                                                        np.newaxis]
        StructWorkArea3D_With_GraFlow = np.append(StructWorkArea3D_With_GraFlow, StructWorkArea3D_Append, axis=2)


    # 分段, 画Space
    for i in range(len(segment) - 1):

        # 垂直下降段
        if segment[i][0] == segment[i + 1][0] and segment[i][1] == segment[i + 1][1]:

            StructWorkArea3D_With_GraFlow[
                     (segment[i][0] - HalfNewSizePixelLen - SpacePixelLen): (segment[i][0] + HalfNewSizePixelLen + SpacePixelLen),
                     (segment[i][1] - HalfNewSizePixelLen - SpacePixelLen): (segment[i][1] + HalfNewSizePixelLen + SpacePixelLen),
                                                             segment[i][2]: segment[i + 1][2] + 1 ] = graflow['Z_Eq_SpaceValue']
            #
            # StructWorkArea3D_With_GraFlow[
            #         (segment[i][0] - HalfNewSizePixelLen): (segment[i][0] + HalfNewSizePixelLen),
            #         (segment[i][1] - HalfNewSizePixelLen): (segment[i][1] + HalfNewSizePixelLen),
            #                                 segment[i][2]: segment[i + 1][2] + 1 ] = graflow['Z_EqValue']
        else:  # 水平非垂直段

            # 每段有几个锯齿段
            Times = abs(segment[i][0] - segment[i + 1][0]) if FlagDirection == 'Y_EqValue' else abs(
                segment[i][1] - segment[i + 1][1])
            Times = np.ceil(Times / Ratio).astype(int)

            # 分锯齿 ; 先整体填充Space，再在这个基础上填充管线NewSize;
            for j in range(Times):
                print(j)

                Space_Z_Strat = segment[i][2] - HalfNewSizePixelLen - SpacePixelLen + j
                Space_Z_End = segment[i][2] + HalfNewSizePixelLen + SpacePixelLen + j
                NewSize_Z_Start = segment[i][2] + j - HalfNewSizePixelLen
                NewSize_Z_End = segment[i][2] + j + HalfNewSizePixelLen

                if FlagDirection == "X_EqValue":

                    if Flag == 'LowToHigh':  # Y从小到大

                        StructWorkArea3D_With_GraFlow[(segment[i][0] - HalfNewSizePixelLen - SpacePixelLen):  (
                                    segment[i][0] + HalfNewSizePixelLen + SpacePixelLen),
                        (segment[i][1] + Ratio * j): min(segment[i][1] + Ratio * (j + 1) + 1, segment[i + 1][1] + 1),
                        Space_Z_Strat: Space_Z_End
                        ] = graflow['X_Eq_SpaceValue']

                        # StructWorkArea3D_With_GraFlow[
                        # (segment[i][0] - HalfNewSizePixelLen): (segment[i][0] + HalfNewSizePixelLen),
                        # (segment[i][1] + Ratio * j): min(segment[i][1] + Ratio * (j + 1) + 1, segment[i + 1][1] + 1),
                        # NewSize_Z_Start: (NewSize_Z_End)
                        # ] = graflow['X_EqValue']

                    elif Flag == 'HighToLow':  # Y从大到小

                        StructWorkArea3D_With_GraFlow[(segment[i][0] - HalfNewSizePixelLen - SpacePixelLen):  (
                                    segment[i][0] + HalfNewSizePixelLen + SpacePixelLen),
                        max((segment[i][1] - Ratio * (j + 1)), segment[i + 1][1]): (segment[i][1] - Ratio * j + 1),
                        Space_Z_Strat: (Space_Z_End)
                        ] = graflow['X_Eq_SpaceValue']

                        # StructWorkArea3D_With_GraFlow[
                        # (segment[i][0] - HalfNewSizePixelLen): (segment[i][0] + HalfNewSizePixelLen),
                        # max((segment[i][1] - Ratio * (j + 1)), segment[i + 1][1]): (segment[i][1] - Ratio * j + 1),
                        # NewSize_Z_Start: (NewSize_Z_End)
                        # ] = graflow['X_EqValue']

                elif FlagDirection == "Y_EqValue":

                    if Flag == 'LowToHigh':
                        StructWorkArea3D_With_GraFlow[
                        (segment[i][0] + Ratio * j): min(segment[i][0] + Ratio * (j + 1) + 1, segment[i + 1][0] + 1),
                        (segment[i][1] - HalfNewSizePixelLen - SpacePixelLen): (
                                    segment[i][1] + HalfNewSizePixelLen + SpacePixelLen),
                        Space_Z_Strat: (Space_Z_End)
                        ] = graflow['Y_Eq_SpaceValue']

                        # StructWorkArea3D_With_GraFlow[
                        # (segment[i][0] + Ratio * j): min(segment[i][0] + Ratio * (j + 1) + 1, segment[i + 1][0] + 1),
                        # (segment[i][1] - HalfNewSizePixelLen): (segment[i][1] + HalfNewSizePixelLen),
                        # NewSize_Z_Start: (NewSize_Z_End)
                        # ] = graflow['Y_EqValue']

                    elif Flag == 'HighToLow':

                        StructWorkArea3D_With_GraFlow[
                        max((segment[i][0] - Ratio * (j + 1)), segment[i + 1][0]): (segment[i][0] - Ratio * j + 1),
                        (segment[i][1] - HalfNewSizePixelLen - SpacePixelLen): (
                                    segment[i][1] + HalfNewSizePixelLen + SpacePixelLen),
                        Space_Z_Strat: (Space_Z_End)
                        ] = graflow['Y_Eq_SpaceValue']

                        # StructWorkArea3D_With_GraFlow[
                        # max((segment[i][0] - Ratio * (j + 1)), segment[i + 1][0]): (segment[i][0] - Ratio * j + 1),
                        # (segment[i][1] - HalfNewSizePixelLen): (segment[i][1] + HalfNewSizePixelLen),
                        # NewSize_Z_Start: (NewSize_Z_End)
                        # ] = graflow['Y_EqValue']


    #分段，画NewSize
    for i in range(len(segment) - 1):

        # 垂直下降段
        if segment[i][0] == segment[i + 1][0] and segment[i][1] == segment[i + 1][1]:

            # StructWorkArea3D_With_GraFlow[
            # (segment[i][0] - HalfNewSizePixelLen - SpacePixelLen): (
            #             segment[i][0] + HalfNewSizePixelLen + SpacePixelLen),
            # (segment[i][1] - HalfNewSizePixelLen - SpacePixelLen): (
            #             segment[i][1] + HalfNewSizePixelLen + SpacePixelLen),
            # segment[i][2]: segment[i + 1][2] + 1] = graflow['Z_Eq_SpaceValue']

            StructWorkArea3D_With_GraFlow[
            (segment[i][0] - HalfNewSizePixelLen): (segment[i][0] + HalfNewSizePixelLen),
            (segment[i][1] - HalfNewSizePixelLen): (segment[i][1] + HalfNewSizePixelLen),
            segment[i][2]: segment[i + 1][2] + 1] = graflow['Z_EqValue']
        else:  # 水平非垂直段

            # 每段有几个锯齿段
            Times = abs(segment[i][0] - segment[i + 1][0]) if FlagDirection == 'Y_EqValue' else abs(
                segment[i][1] - segment[i + 1][1])
            Times = np.ceil(Times / Ratio).astype(int)

            # 分锯齿 ; 先整体填充Space，再在这个基础上填充管线NewSize;
            for j in range(Times):
                print(j)

                Space_Z_Strat = segment[i][2] - HalfNewSizePixelLen - SpacePixelLen + j
                Space_Z_End = segment[i][2] + HalfNewSizePixelLen + SpacePixelLen + j
                NewSize_Z_Start = segment[i][2] + j - HalfNewSizePixelLen
                NewSize_Z_End = segment[i][2] + j + HalfNewSizePixelLen

                if FlagDirection == "X_EqValue":

                    if Flag == 'LowToHigh':  # Y从小到大

                        StructWorkArea3D_With_GraFlow[
                        (segment[i][0] - HalfNewSizePixelLen): (segment[i][0] + HalfNewSizePixelLen),
                        (segment[i][1] + Ratio * j): min(segment[i][1] + Ratio * (j + 1) + 1, segment[i + 1][1] + 1),
                        NewSize_Z_Start: (NewSize_Z_End)
                        ] = graflow['X_EqValue']

                    elif Flag == 'HighToLow':  # Y从大到小

                        StructWorkArea3D_With_GraFlow[
                        (segment[i][0] - HalfNewSizePixelLen): (segment[i][0] + HalfNewSizePixelLen),
                        max((segment[i][1] - Ratio * (j + 1)), segment[i + 1][1]): (segment[i][1] - Ratio * j + 1),
                        NewSize_Z_Start: (NewSize_Z_End)
                        ] = graflow['X_EqValue']

                elif FlagDirection == "Y_EqValue":

                    if Flag == 'LowToHigh':

                        StructWorkArea3D_With_GraFlow[
                        (segment[i][0] + Ratio * j): min(segment[i][0] + Ratio * (j + 1) + 1, segment[i + 1][0] + 1),
                        (segment[i][1] - HalfNewSizePixelLen): (segment[i][1] + HalfNewSizePixelLen),
                        NewSize_Z_Start: (NewSize_Z_End)
                        ] = graflow['Y_EqValue']

                    elif Flag == 'HighToLow':

                        StructWorkArea3D_With_GraFlow[
                        max((segment[i][0] - Ratio * (j + 1)), segment[i + 1][0]): (segment[i][0] - Ratio * j + 1),
                        (segment[i][1] - HalfNewSizePixelLen): (segment[i][1] + HalfNewSizePixelLen),
                        NewSize_Z_Start: (NewSize_Z_End)
                        ] = graflow['Y_EqValue']



    print('Test Out from put——output()\n\n')
    return lowest_z, StructWorkArea3D_With_GraFlow




#输入矩阵,线段起始点和终点,管线的方向direction_flag,线段横截面的长length_pixel,宽width_pixel(包括Newsize,不包括安装空间space)
#在重力流水管中length=width
#在矩阵中管线的路径所占据的矩阵块中沿着管线的方向找到第一个指定的像素值value的点,返回这个点的坐标
def Compare(graflow, StructWorkArea3D_With_GraFlow_Temp, start_point, final_point, remain_length, LenPixel, ValueList):

    StructWorkArea3D_With_GraFlow = StructWorkArea3D_With_GraFlow_Temp.copy()
    for Value in ValueList:
        StructWorkArea3D_With_GraFlow[StructWorkArea3D_With_GraFlow==Value]=255



    Ratio  = graflow['Ratio'] 
    SpacePixelLen = graflow['SpacePixelLen']
    HalfNewSizePixelLen = np.ceil( graflow['NewSizePixelLen'][0][0]/2 ).astype(int)

    PixelLen30m = np.ceil( 30000/LenPixel ).astype(int)
    PixelLen_Left = PixelLen30m -  remain_length
    assert(PixelLen30m>=remain_length)





    FlagDirection = 'X_EqValue' if start_point[0]==final_point[0] else 'Y_EqValue'

    LenOfSegment = max( abs(start_point[0] - final_point[0]+1) , abs(start_point[1] - final_point[1]+1))

    if  FlagDirection =='X_EqValue':
        Flag = 'LowToHigh' if start_point[1]<final_point[1] else 'HighToLow'

        if LenOfSegment + remain_length >= PixelLen30m:
            flag_30m = True
            if Flag == 'LowToHigh':
                CoordinateOf30m = [start_point[0], start_point[1]+PixelLen_Left, start_point[2] + np.ceil(PixelLen_Left/Ratio).astype(int)]
            elif Flag == 'HighToLow':
                CoordinateOf30m = [start_point[0], start_point[1]-PixelLen_Left, start_point[2] + np.ceil(PixelLen_Left/Ratio).astype(int)]
        else: 
            flag_30m = False
            remain_length = remain_length +  LenOfSegment

    elif FlagDirection =='Y_EqValue':
        Flag = 'LowToHigh' if start_point[0]<final_point[0] else 'HighToLow'
        if LenOfSegment + remain_length >= PixelLen30m:
            flag_30m = True
            if Flag == 'LowToHigh':
                CoordinateOf30m = [start_point[0]+PixelLen_Left, start_point[1], start_point[2] + np.ceil(PixelLen_Left/Ratio).astype(int)]
            elif Flag == 'HighToLow':
                CoordinateOf30m = [start_point[0]-PixelLen_Left, start_point[1], start_point[2] + np.ceil(PixelLen_Left/Ratio).astype(int)]
        else: 
            flag_30m = False
            remain_length = remain_length +  LenOfSegment
    else:
        raise Exception('FlagDirection has to be X_EqValue or Y_EqValue') 



    if FlagDirection == "X_EqValue":

        NewSize_X_Start = start_point[0] - HalfNewSizePixelLen 
        NewSize_X_End = start_point[0] + HalfNewSizePixelLen 
    else:

        NewSize_Y_Start = start_point[1] - HalfNewSizePixelLen
        NewSize_Y_End = start_point[1] + HalfNewSizePixelLen


    #有几个锯齿段
    Times = np.ceil(LenOfSegment/Ratio).astype(int)

    print('\nTest in Compare():')
    print('Times:',Times)
    print('start_point', start_point)
    #分锯齿 ; 以NewSize为探测基础;
    for j in range(Times):
        print('j:',j)


        NewSize_Z_Start = start_point[2] - HalfNewSizePixelLen + j
        NewSize_Z_End = start_point[2] + HalfNewSizePixelLen + j                        
        
        if FlagDirection == "X_EqValue":
            print('\nTest in Compare(): if FlagDirection == "X_EqValue"::')

            if Flag == 'LowToHigh':  #Y从小到大  
                assert(start_point[1]<=final_point[1])

                Y_Start = start_point[1] + Ratio*j

                SearchArea = StructWorkArea3D_With_GraFlow[ NewSize_X_Start : (NewSize_X_End),
                                                            Y_Start : min(start_point[1]+Ratio*(j+1)+1, final_point[1] +1),
                                                            NewSize_Z_Start : (NewSize_Z_End) ].copy()
                #代表自身管道的空间的值应该重新设为255(可行).否则出现自己和自己冲突的情况
                SearchArea[SearchArea == graflow['Y_EqValue']] = 255
                SearchArea[SearchArea == graflow['Y_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['X_EqValue']] = 255
                SearchArea[SearchArea == graflow['X_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['Z_EqValue']] = 255
                SearchArea[SearchArea == graflow['Z_Eq_SpaceValue']] = 255

                Coordinate = np.argwhere(SearchArea!=255).tolist()


                Coordinate = sorted(sorted(sorted(Coordinate, key = lambda x: x[0]), key = lambda x: x[2], reverse=True), key = lambda x: x[1])

                if len(Coordinate)==0:  #没有其他冲突
                    if flag_30m == True and CoordinateOf30m[1] <= min(start_point[1]+Ratio*(j+1)+1, final_point[1] +1):
                        print('\n30m冲突  Out of Test in Compare()')
                        return 1, [CoordinateOf30m]


                    elif flag_30m == False:  # 而且没有30米冲突
                         if j==Times-1:      #而且是最后一个锯齿段
                          print('test: j= %d,False,无冲突'%j)
                          print('\nOut of Test in Compare()')
                          return False, []

                else:#有其他冲突
                        
                    #第一个冲突点各个坐标
                    Conflict_X = NewSize_X_Start +  Coordinate[0][0] 
                    Conflict_Y =         Y_Start +  Coordinate[0][1]
                    Conflict_Z = NewSize_Z_Start +  Coordinate[0][2]
                    Conflict_Point = np.array([ Conflict_X, Conflict_Y, Conflict_Z ] )

                    #30米和这个冲突哪个先？
                    if flag_30m and CoordinateOf30m[1] < Conflict_Y:
                        print('\n30米冲突 Out of Test in Compare()')
                        return 1, [CoordinateOf30m]
                        print('\n')
                    else:

                        Value_Conflict = StructWorkArea3D_With_GraFlow[Conflict_X, Conflict_Y, Conflict_Z]
                        Value_Conflict_mod = Value_Conflict % 1000

                        CenterOfConflictPipe = np.array([start_point[0], Conflict_Y, start_point[2]+j])
                        CenterOfConflictPipe_GoBack = np.array([start_point[0], Conflict_Y - HalfNewSizePixelLen - SpacePixelLen, start_point[2]+j])

                        if Value_Conflict_mod==127: #撞梁
                            print('test: j= %d,撞梁 '%j)
                            flag = 2
                            print('CenterOfConflictPipe',CenterOfConflictPipe)
                            print('HalfNewSizePixelLen',HalfNewSizePixelLen)
                            print('SpacePixelLen',SpacePixelLen)
                            print('CenterOfConflictPipe_GoBack',CenterOfConflictPipe_GoBack)
                            print('\nOut of Test in Compare()')
                            return flag, [ Value_Conflict, Conflict_Point, CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==61 or Value_Conflict_mod==100:#平行撞管
                            flag = 3
                            print('\ntest: j= %d,平行撞管 Out of Test in Compare()'%j)
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==62 or Value_Conflict_mod==101:#交叉撞管
                            flag = 4
                            print('\ntest: j= %d 交叉撞管 Out of Test in Compare()'%j)
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==63 or Value_Conflict_mod==102:#撞垂直管
                            flag = 5
                            print('\ntest: j= %d 撞垂直管 Out of Test in Compare()'%j)
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict == 0:
                            raise Exception('/n/nIn Compare Value_Conflict == 0，撞结构？应该是find_room或靠墙出现了问题/n/n')
                        print('\n')

               
            elif Flag == 'HighToLow': #Y从大到小
                print('大到小')
                assert(start_point[1]>=final_point[1])




                Y_Start = max( (start_point[1] - Ratio*(j+1)+1), final_point[1] )

                SearchArea = StructWorkArea3D_With_GraFlow[ NewSize_X_Start : (NewSize_X_End),                    
                                                                    Y_Start : (start_point[1] -Ratio*j ),
                                                            NewSize_Z_Start : (NewSize_Z_End) ].copy()

                SearchArea[SearchArea == graflow['Y_EqValue']]=255
                SearchArea[SearchArea == graflow['Y_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['X_EqValue']] = 255
                SearchArea[SearchArea == graflow['X_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['Z_EqValue']] = 255
                SearchArea[SearchArea == graflow['Z_Eq_SpaceValue']] = 255


                Coordinate = np.argwhere(SearchArea!=255).tolist()
                Coordinate = sorted(sorted(sorted(Coordinate, key = lambda x: x[0]), key = lambda x: x[2], reverse=True), key = lambda x: x[1], reverse = True)




                if len(Coordinate)==0:  #没有其他冲突
                    if flag_30m == True and CoordinateOf30m[1] >= Y_Start:
                        return 1, [CoordinateOf30m]

                    elif flag_30m == False:  # 没有30米冲突
                        if j==Times-1: #是最后一段
                            print('test: j= %d,False,无冲突'%j)
                            print('\nOut of Test in Compare()')
                            return False, []

                else:#有其他冲突
                        
                    #第一个冲突点各个坐标
                    Conflict_X = NewSize_X_Start +  Coordinate[0][0]
                    Conflict_Y =         Y_Start +  Coordinate[0][1]
                    Conflict_Z = NewSize_Z_Start +  Coordinate[0][2]
                    Conflict_Point = np.array([ Conflict_X, Conflict_Y, Conflict_Z ] )

                    #30米和这个冲突哪个先？
                    if flag_30m and CoordinateOf30m[1] > Conflict_Y:
                        return 1, [CoordinateOf30m]
                    else:

                        Value_Conflict = StructWorkArea3D_With_GraFlow[Conflict_X, Conflict_Y, Conflict_Z]
                        Value_Conflict_mod = Value_Conflict % 1000

                        CenterOfConflictPipe = np.array([start_point[0], Conflict_Y, start_point[2]+j])
                        CenterOfConflictPipe_GoBack = np.array([start_point[0], Conflict_Y + HalfNewSizePixelLen + SpacePixelLen, start_point[2]+j])

                            
                        if Value_Conflict_mod==127: #撞梁
                            print('test: j= %d,撞梁 '%j)
                            flag = 2
                            print('CenterOfConflictPipe',CenterOfConflictPipe)
                            print('CenterOfConflictPipe_GoBack',CenterOfConflictPipe_GoBack)
                            print('\nOut of Test in Compare()/n')
                            return flag, [ Value_Conflict, Conflict_Point, CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==61 or Value_Conflict_mod==100:#平行撞管
                            flag = 3
                            print('\nOut of Test in Compare()')
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==62 or Value_Conflict_mod==101:#交叉撞管
                            flag = 4
                            print('交叉撞')
                            print('\nOut of Test in Compare()')
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==63 or Value_Conflict_mod==102:#撞垂直管
                            flag = 5
                            print('\nOut of Test in Compare()')
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict == 0:
                            raise Exception('/n/nIn Compare Value_Conflict == 0，撞结构？应该是find_room或靠墙出现了问题/n/n')


        elif FlagDirection == "Y_EqValue":
            print('Enter Compare "Y_EqValue"')

            if Flag == 'LowToHigh':
                assert(start_point[0]<=final_point[0])

                X_Start = start_point[0] + Ratio*j
                SearchArea = StructWorkArea3D_With_GraFlow[          X_Start : min(start_point[0]+Ratio*(j+1) +1, final_point[0] +1),
                                                             NewSize_Y_Start : (NewSize_Y_End ),
                                                             NewSize_Z_Start : (NewSize_Z_End ) ].copy()

                SearchArea[SearchArea==graflow['Y_EqValue']] = 255
                SearchArea[SearchArea == graflow['Y_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['X_EqValue']] = 255
                SearchArea[SearchArea == graflow['X_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['Z_EqValue']] = 255
                SearchArea[SearchArea == graflow['Z_Eq_SpaceValue']] = 255


                Coordinate = np.argwhere(SearchArea!=255).tolist()
                Coordinate = sorted(sorted(sorted(Coordinate, key = lambda x: x[1]), key = lambda x: x[2], reverse=True), key = lambda x: x[0])


                if len(Coordinate)==0:  #没有其他冲突
                    if flag_30m == True and CoordinateOf30m[0] <= min(start_point[0]+Ratio*(j+1) +1, final_point[0] +1):
                        return 1, [CoordinateOf30m]

                    elif flag_30m==False:
                        if j== Times-1:
                            print('test: j= %d,False,无冲突'%j)
                            print('\nOut of Test in Compare()')
                            return False, []

                else:#有其他冲突
                        
                    #第一个冲突点各个坐标
                    Conflict_X =         X_Start +  Coordinate[0][0]
                    Conflict_Y = NewSize_Y_Start +  Coordinate[0][1]
                    Conflict_Z = NewSize_Z_Start +  Coordinate[0][2]
                    Conflict_Point = np.array( [ Conflict_X, Conflict_Y, Conflict_Z ] )

                    

                    #30米和这个冲突哪个先？
                    if flag_30m and CoordinateOf30m[0] < Conflict_X:
                        print('\nOut of Test in Compare()')
                        return 1, [CoordinateOf30m]
                    else:

                        Value_Conflict = StructWorkArea3D_With_GraFlow[Conflict_X, Conflict_Y, Conflict_Z]
                        Value_Conflict_mod = Value_Conflict % 1000

                        print('Value_of_conflict',Value_Conflict)

                        CenterOfConflictPipe = np.array([Conflict_X, start_point[1], start_point[2]+j])
                        CenterOfConflictPipe_GoBack = np.array([Conflict_X - HalfNewSizePixelLen - SpacePixelLen, start_point[1], start_point[2]+j])
                            
                        if Value_Conflict_mod==127: #撞梁
                            flag = 2
                            return flag, [ Value_Conflict, Conflict_Point, CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==62 or Value_Conflict_mod==101:#平行撞管
                            flag = 3
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==61 or Value_Conflict_mod==100:#交叉撞管
                            flag = 4
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==63 or Value_Conflict_mod==102:#撞垂直管
                            flag = 5
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict == 0:
                            raise Exception('/n/nIn Compare Value_Conflict == 0，撞结构？应该是find_room或靠墙出现了问题/n/n')
           
            elif Flag == 'HighToLow':
                assert(start_point[0]>=final_point[0])

                X_Start = max( (start_point[0] - Ratio*(j+1)), final_point[0] )

                SearchArea = StructWorkArea3D_With_GraFlow[         X_Start : (start_point[0] -Ratio*j+1),
                                                            NewSize_Y_Start : (NewSize_Y_End ),
                                                            NewSize_Z_Start : (NewSize_Z_End ) ].copy()
                SearchArea[SearchArea==graflow['Y_EqValue']]=255
                SearchArea[SearchArea == graflow['Y_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['X_EqValue']] = 255
                SearchArea[SearchArea == graflow['X_Eq_SpaceValue']] = 255
                SearchArea[SearchArea == graflow['Z_EqValue']] = 255
                SearchArea[SearchArea == graflow['Z_Eq_SpaceValue']] = 255


                Coordinate = np.argwhere(SearchArea!=255).tolist()
                Coordinate = sorted(sorted(sorted(Coordinate, key = lambda x: x[1]), key = lambda x: x[2], reverse=True), key = lambda x: x[0], reverse = True)

                if len(Coordinate)==0:  #没有其他冲突
                    if flag_30m == True and CoordinateOf30m[0] >= X_Start:
                        return 1, [CoordinateOf30m]
                    elif flag_30m == False:
                        if j==Times-1:
                            return False, []

                else:#有其他冲突
                        
                    #第一个冲突点各个坐标
                    Conflict_X =         X_Start +  Coordinate[0][0]
                    Conflict_Y = NewSize_Y_Start +  Coordinate[0][1]
                    Conflict_Z = NewSize_Z_Start +  Coordinate[0][2]
                    Conflict_Point = np.array([ Conflict_X, Conflict_Y, Conflict_Z ] )

                    #30米和这个冲突哪个先？
                    if flag_30m and CoordinateOf30m[0] > Conflict_X:
                        return 1, [CoordinateOf30m]
                    else:

                        Value_Conflict = StructWorkArea3D_With_GraFlow[Conflict_X, Conflict_Y, Conflict_Z]
                        Value_Conflict_mod = Value_Conflict % 1000

                        CenterOfConflictPipe = np.array([Conflict_X, start_point[1], start_point[2]+j])
                        CenterOfConflictPipe_GoBack = np.array([Conflict_X + HalfNewSizePixelLen + SpacePixelLen, start_point[1], start_point[2]+j])
                        
                        if Value_Conflict_mod==127: #撞梁
                            flag = 2
                            return flag, [ Value_Conflict, Conflict_Point, CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==62 or Value_Conflict_mod==101:#平行撞管
                            flag = 3
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==61 or Value_Conflict_mod==100:#交叉撞管
                            flag = 4
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

                        elif Value_Conflict_mod==63 or Value_Conflict_mod==102:#撞垂直管
                            flag = 5
                            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]
                        elif Value_Conflict == 0:
                            raise Exception('/n/nIn Compare Value_Conflict == 0，撞结构？应该是find_room或靠墙出现了问题/n/n')



def Find_Best_Point(graflow, BeamValue, Beams, CenterOfConflictPipe, StructWorkArea3D_With_GraFlow, LenPixel, BeamsValueDict):
    #目前策略是对梁1/3到2/3进行全局搜索进行
    #首先截出1/3 2/3 的地方;
    #!!!而且要考虑回退1/2NewSIZE
    Beam = Beams[BeamsValueDict[BeamValue]]

    print('\nTest for find_Best_Point()\n.CenterOfConFlictPipe:',CenterOfConflictPipe[0])
    print('BeamValue:',BeamValue)
    print('\n')

    #撞梁截面处管线的含包裹最高点Z、最低点Z
    HalfHighPixel =  np.ceil(graflow['NewSize'][1] / LenPixel / 2).astype(int)
    Pipe_Z_Highest = CenterOfConflictPipe[2] - HalfHighPixel #注意 最高点的Z轴是0，越低Z值反而越大
    Pipe_Z_Lowest = CenterOfConflictPipe[2] + HalfHighPixel    

    if Beam['Route'][0][0] == Beam['Route'][1][0]:#梁平行于Y轴，那么与之垂直的管必是平行于X轴
        Flag_Beam = 'X_Eq'
        ValueOfPipe = 62
        ValueOfSpace = 101
        
        OneToTwoThird = StructWorkArea3D_With_GraFlow[CenterOfConflictPipe[0], (Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel) :(Beam['ScopeOfOneToTwoThird'][1]-HalfHighPixel+1), 0:Beam['DepthPixel']+1]
        OneToTwoThird_Append = StructWorkArea3D_With_GraFlow[CenterOfConflictPipe[0], (Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel) :(Beam['ScopeOfOneToTwoThird'][1]-HalfHighPixel+1), 0:Beam['DepthPixel']+graflow['NewSizePixelLen'][1]]
        
        Offset_Point = [CenterOfConflictPipe[0], Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel, 0]

        Pipe_Leftest =  CenterOfConflictPipe[1] - HalfHighPixel
        Pipe_Rightest = CenterOfConflictPipe[1] + HalfHighPixel


    else:
        Flag_Beam = 'Y_Eq'
        ValueOfPipe = 61
        ValueOfSpace = 100

        OneToTwoThird = StructWorkArea3D_With_GraFlow[(Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel):(Beam['ScopeOfOneToTwoThird'][1]-HalfHighPixel+1), CenterOfConflictPipe[1], 0:Beam['DepthPixel']+1].copy()
        OneToTwoThird_Append = StructWorkArea3D_With_GraFlow[(Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel):(Beam['ScopeOfOneToTwoThird'][1]-HalfHighPixel+1), CenterOfConflictPipe[1], 0:Beam['DepthPixel']+graflow['NewSizePixelLen'][1]].copy()
        
        Offset_Point = [Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel, CenterOfConflictPipe[1], 0]

        Pipe_Leftest =  CenterOfConflictPipe[0] - HalfHighPixel
        Pipe_Rightest = CenterOfConflictPipe[0] + HalfHighPixel

    OneToTwoThird_Append[OneToTwoThird_Append==255] = BeamValue

    #250MM对应的Pixel个数
    NumPixel250 = np.ceil(250/LenPixel).astype(int)

    #找到已有管线的最高点和最低点
    Coordinate =  np.argwhere(OneToTwoThird%1000 == ValueOfPipe)

    #该梁之前没有穿过管线
    if Coordinate.size==0:
        if Flag_Beam == 'X_Eq':
            if Pipe_Leftest < Beam['ScopeOfOneToTwoThird'][0]:
              return True, [CenterOfConflictPipe[0], Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel, CenterOfConflictPipe[2]]
            elif Pipe_Rightest > Beam['ScopeOfOneToTwoThird'][1]:
              return True, [CenterOfConflictPipe[0], Beam['ScopeOfOneToTwoThird'][1]-HalfHighPixel, CenterOfConflictPipe[2]]
            else:
              raise Exception('Eoor in Find_Best_Point()')

        elif Flag_Beam == 'Y_Eq':

            if Pipe_Leftest < Beam['ScopeOfOneToTwoThird'][0]:
              return True, [Beam['ScopeOfOneToTwoThird'][0]+HalfHighPixel, CenterOfConflictPipe[1],  CenterOfConflictPipe[2]]
            elif Pipe_Rightest > Beam['ScopeOfOneToTwoThird'][1]:
              return True, [Beam['ScopeOfOneToTwoThird'][1]-HalfHighPixel, CenterOfConflictPipe[1],  CenterOfConflictPipe[2]]
            else:
              raise Exception('Eoor in Find_Best_Point()')              
    else:

        Coordinate_Z_Highest = Coordinate[:,1].min()
        Coordinate_Z_Lowest  = Coordinate[:,1].max()

        RemainderPixels = NumPixel250 - (Coordinate_Z_Lowest - Coordinate_Z_Highest + 1)

        #锁定可调整范围
        if Coordinate_Z_Lowest==Beam['DepthPixel']: #已占最低点为梁底
            Z_Lowest = Beam['DepthPixel'] + NumPixel250
            Z_Highset = Beam['DepthPixel'] - NumPixel250
        else:
            Z_Highset = Coordinate_Z_Highest - RemainderPixels 
            Z_Lowest = Coordinate_Z_Lowest + RemainderPixels


     
        #卷积
        h = graflow['NewSizePixelLen'][1] 
        w = graflow['NewSizePixelLen'][0] 
        H = OneToTwoThird_Append.shape[0] - h + 1
        W = OneToTwoThird_Append.shape[1] - w + 1

        Result = np.zeros((H, W))

        for i in range(H):
            for j in range(W):
                Result[i][j] = OneToTwoThird_Append[i:i+h, j:j+w].sum()  #这里绝对不用加1，如果长度是h的话。

        print('BeamValue:',BeamValue)

        Coordinate_Conv = np.argwhere(Result==BeamValue*h*w)

        if Coordinate_Conv.size == 0:  #没有符合条件的点
            print('1没有符合条件的点')
            return False, []

        else:
            
            if Flag_Beam == 'X_Eq':
                #确定真实坐标:相对于管线左上角
                Coordinate_Conv_Real = np.insert( Coordinate_Conv, 0, 0, axis = 1 ) + Offset_Point + [np.ceil(w/2).astype(int), 0, np.ceil(h/2).astype(int)]

                #挑选 Z大于CenterOfConflictPipe的坐标点
                Coordinate_Conv_Real = Coordinate_Conv_Real[:, Coordinate_Conv_Real[:,2]>=CenterOfConflictPipe[2]]
                #挑选250限制下可选的坐标点
                Coordinate_Conv_Real = Coordinate_Conv_Real[:, Coordinate_Conv_Real[:,2]>=Z_Highset]
                Coordinate_Conv_Real = Coordinate_Conv_Real[:, Coordinate_Conv_Real[:,2]<=Z_Lowest]

                if Coordinate_Conv_Real.size==0:
                    print('===============2没有符合条件的点====================')
                    return False, []
                else:
                    #选择坐标变动最小的点
                    Coordinate_Conv_Real = sorted(Coordinate_Conv_Real.tolist(), key = lambda x: abs(x[0]-CenterOfConflictPipe[0]))
                    Coordinate_Conv_Real = sorted(Coordinate_Conv_Real, key = lambda x: abs(x[2] - CenterOfConflictPipe[2]))
                    print('===============3没有符合条件的点===================')
                    return True, Coordinate_Conv_Real[0]



            elif Flag_Beam == 'Y_Eq':
                #确定真实坐标:相对于管线左上角;加上卷积带来的偏移h-1,w-1
                print('CenterOfConflictPipe ', CenterOfConflictPipe)
                Coordinate_Conv_Real = np.insert( Coordinate_Conv, 1, 0, axis = 1 ) + Offset_Point + [np.ceil(w/2).astype(int), 0, np.ceil(h/2).astype(int)]

                #挑选 Z大于CenterOfConflictPipe的坐标点
                Coordinate_Conv_Real = np.array([x for x in Coordinate_Conv_Real if x[2]>=CenterOfConflictPipe[2]])


                #挑选250限制下可选的坐标点
                Coordinate_Conv_Real = np.array([x for x in Coordinate_Conv_Real if x[2]>=Z_Highset])


                Coordinate_Conv_Real = np.array([x for x in Coordinate_Conv_Real if x[2]<=Z_Lowest])
                print('==============best_point_group shape:=======================',Coordinate_Conv_Real.shape)

                if len(Coordinate_Conv_Real)==0:
                    print('===============4没有符合条件的点===================')
                    return False, []
                else:
                    #选择坐标变动最小的点
                    Coordinate_Conv_Real = sorted(Coordinate_Conv_Real.tolist(), key = lambda x: abs(x[1]-CenterOfConflictPipe[1]))
                    Coordinate_Conv_Real = sorted(Coordinate_Conv_Real, key = lambda x: abs(x[2] - CenterOfConflictPipe[2]))
                    return True, Coordinate_Conv_Real[0]






def Check_Right(graflow, Beams, BeamValue, StructWorkArea3D_With_GraFlow, Value_Conflict, CenterOfConflictPipe, LenPixel, PipesValueDict, BeamsValueDict):

    #撞梁截面处管线的含包裹最高点Z、最低点Z
    HalfHighPixel =  np.ceil(graflow['NewSizePixelLen'][1] / 2).astype(int)
    Pipe_Z_Highest = CenterOfConflictPipe[2] - HalfHighPixel #注意 最高点的Z轴是0，越低Z值反而越大
    Pipe_Z_Lowest = CenterOfConflictPipe[2] + HalfHighPixel


    Beam = Beams[BeamsValueDict[BeamValue]]

    if Beam['Route'][0][0] == Beam['Route'][1][0]:  # 梁平行于Y轴，那么与之垂直的管必是平行于X轴
        Flag_Beam = 'X_Eq'
        ValueOfPipe = 62
        ValueOfSpace = 101

        OneToTwoThird = StructWorkArea3D_With_GraFlow[CenterOfConflictPipe[0], (Beam['ScopeOfOneToTwoThird'][0] + HalfHighPixel):(Beam['ScopeOfOneToTwoThird'][1] - HalfHighPixel + 1), 0:Beam['DepthPixel'] + 1]
        OneToTwoThird_Append = StructWorkArea3D_With_GraFlow[CenterOfConflictPipe[0],(Beam['ScopeOfOneToTwoThird'][0] + HalfHighPixel):( Beam['ScopeOfOneToTwoThird'][1] - HalfHighPixel + 1),0:Beam['DepthPixel'] + graflow['NewSizePixelLen'][1]]

        Offset_Point = [CenterOfConflictPipe[0], Beam['ScopeOfOneToTwoThird'][0] + HalfHighPixel, 0]

        Pipe_Leftest = CenterOfConflictPipe[1] - HalfHighPixel
        Pipe_Rightest = CenterOfConflictPipe[1] + HalfHighPixel


    else:
        Flag_Beam = 'Y_Eq'
        ValueOfPipe = 61
        ValueOfSpace = 100

        OneToTwoThird = StructWorkArea3D_With_GraFlow[(Beam['ScopeOfOneToTwoThird'][0] + HalfHighPixel):( Beam['ScopeOfOneToTwoThird'][1] - HalfHighPixel + 1), CenterOfConflictPipe[1], 0:Beam['DepthPixel'] + 1].copy()
        OneToTwoThird_Append = StructWorkArea3D_With_GraFlow[(Beam['ScopeOfOneToTwoThird'][0] + HalfHighPixel):( Beam['ScopeOfOneToTwoThird'][1] - HalfHighPixel + 1), CenterOfConflictPipe[1],  0:Beam['DepthPixel'] + graflow['NewSizePixelLen'][1]].copy()

        Offset_Point = [Beam['ScopeOfOneToTwoThird'][0] + HalfHighPixel, CenterOfConflictPipe[1], 0]

        Pipe_Leftest = CenterOfConflictPipe[0] - HalfHighPixel
        Pipe_Rightest = CenterOfConflictPipe[0] + HalfHighPixel

    #1/3 2/3要求
    if Pipe_Leftest<Beam['ScopeOfOneToTwoThird'][0] or Pipe_Rightest>Beam['ScopeOfOneToTwoThird'][1]:
        return False
    else:        

          #250MM对应的Pixel个数
          NumPixel250 = np.ceil(250/LenPixel).astype(int)

          #找到已有管线的最高点和最低点
          Coordinate =  np.argwhere(OneToTwoThird%1000 == ValueOfPipe)
          if Coordinate.shape[0]==0: #该梁之前没有穿过管线
              return True
          else:

              Coordinate_Z_Highest = Coordinate[:,1].min()
              Coordinate_Z_Lowest  = Coordinate[:,1].max()
              RemainderPixels = NumPixel250 - (Coordinate_Z_Lowest - Coordinate_Z_Highest + 1)

              #锁定可调整范围(250)
              if Coordinate_Z_Lowest==Beam['DepthPixel']: #已占最低点为梁底
                  Z_Lowest = Beam['DepthPixel'] + NumPixel250
                  Z_Highset = NumPixel250 - (Coordinate_Z_Highest - Beam['DepthPixel'] +1)
              else:
                  Z_Highset = Coordinate_Z_Highest - RemainderPixels 
                  Z_Lowest = Coordinate_Z_Lowest + RemainderPixels


              if Pipe_Z_Highest>=Z_Highset and Pipe_Z_Lowest<=Z_Lowest:
                  if Flag_Beam == 'X_Eq':
                      Test = np.argwhere(StructWorkArea3D_With_GraFlow[CenterOfConflictPipe[0], Pipe_Leftest:Pipe_Rightest+1, Pipe_Z_Highest:Pipe_Z_Lowest+1]%1000 != 127)
                  elif Flag_Beam == 'Y_Eq':
                      Test = np.argwhere(StructWorkArea3D_With_GraFlow[Pipe_Leftest:Pipe_Rightest+1, CenterOfConflictPipe[1], Pipe_Z_Highest:Pipe_Z_Lowest+1]%1000 != 127)

                  if Test.size==0:
                      return True
                  else:
                      return False

              else:
                  return False






#找走廊宽度
def find_Length(StructWorkArea3D, Point, Direction):

    #Point为你取得走廊上一点；Direction为点上走廊垂线

    if Direction=='平行于Y轴':

        #取一整条线
        Coordinate = np.argwhere( StructWorkArea3D[ Point[0], :, 0]==0 ) 

        if len(Coordinate) == 0:
            print('没有经过走廊')
            return False

        #做差值，找abs最小的那两个点，就是走廊的两端点
        Coordinate2 =  abs(Coordinate - Point[1] )         
        point1_Y = Coordinate2.argmin()
        point2_Y = Len(Coordinate2) - Coordinate2[::-1].argmin() -('1')

        if point1_Y == point2_Y:
            print("只有一半走廊")
            return False
        else:
            LEN =  point1_Y - point2_Y
            return LEN

    elif Direction=='平行于X轴':
 
        #取一整条线
        Coordinate = np.argwhere( StructWorkArea3D[ :, Point[1], 0]==0 ) 

        if len(Coordinate) == 0:
            print('没有经过走廊')
            return False

        #做差值，找abs最小的那两个点，就是走廊的两端点
        Coordinate2 =  abs(Coordinate - Point[0] )         
        point1_X = Coordinate2.argmin()
        point2_X = Len(Coordinate2) - Coordinate2[::-1].argmin() -1
        

        if point1_X == point2_X:
            print("只有一半走廊")
            return False
        else:
            LEN =  point1_X - point2_X
            return LEN





# 根据从conflict_point变化到conflict_point_next所作出坐标值改变
# 把相应的变化也反应在Segment[segment_number][-1]
# 如从conflict_point变化到conflict_point_next,x轴减少了10,那么Segment[segment_number][-1]的x轴也减少了10

#增加转折点的情况下
'''转折点，bestpoint，穿梁(背面)点后的点全部加入的情况下的best_point的point_number'''
def ChangePointFromConflict(Segment, segment_number, CenterOfConflictPipe, BestPoint, PointNumber_BestPoint):  

    if CenterOfConflictPipe[1]==BestPoint[1]:#那么将是X改变
 
        LengthOfSegment = len(Segment[segment_number])   

        Add_Z = BestPoint[2] - CenterOfConflictPipe[2]
        Segment[segment_number][PointNumber_BestPoint+2][0] = BestPoint[0]
        Segment[segment_number][PointNumber_BestPoint+2][2] += Add_Z

        if PointNumber_BestPoint+3==len(Segment[segment_number]): #紧挨着最后一点，那么下一个Segment第一个点也需改变
            Segment[segment_number+1][0][0] = BestPoint[0]


        for seg in Segment[segment_number:]:
            for point in seg:
                point[2] += Add_Z
        return Segment

    elif CenterOfConflictPipe[0]==BestPoint[0]:#那么将是Y改变

        LengthOfSegment = len(Segment[segment_number])  

        Add_Z = BestPoint[2] - CenterOfConflictPipe[2]        
        Segment[segment_number][PointNumber_BestPoint+2][1] = BestPoint[1]
        Segment[segment_number][PointNumber_BestPoint+2][2] += Add_Z

        if PointNumber_BestPoint+3==len(Segment[segment_number]): #紧挨着最后一点，那么下一个Segment第一个点也需改变
            Segment[segment_number+1][0][1] = BestPoint[1]
        
        for seg in Segment[segment_number:]:
            for point in seg:
                point[2] += Add_Z
        return Segment

    else:
        raise Exception('Error in function:function_Chen.ChangePointFromConflict()') 


    


# 根据冲突点与The_right_point的坐标差异,移动整条线段,更新segment
def Remove(Segment, segment_number, CenterOfConflictPipe, BestPoint, PointNumber, StructWorkArea3D_With_GraFlow, graflow):
    print('===========In REMOVE==============')
    print('Best_Point:',BestPoint)
    print('CenterOfConflictPipe: ',CenterOfConflictPipe)
    print('TYPE OF SEGMENT', type(Segment))

    print('Segment before:\n', Segment)


    if CenterOfConflictPipe[1]==BestPoint[1]:


        for point in Segment[segment_number]:
            point[0] = BestPoint[0]

        if segment_number > 0:
            Segment[segment_number - 1][-1][0] = BestPoint[0]
        if segment_number < len(Segment)-1:
            Segment[segment_number + 1][0][0] = BestPoint[0]


        Add_Z = BestPoint[2] - CenterOfConflictPipe[2]
        assert(Add_Z>=0)

        #整体下移
        for seg in Segment:
            for point in seg:
                point[2] += Add_Z

        print('Segment after:\n',Segment)
        print('==========================')
        return Segment


    elif CenterOfConflictPipe[0]==BestPoint[0]:

        for point in Segment[segment_number]:
            point[1] = BestPoint[1]

        if segment_number > 0:
            Segment[segment_number - 1][-1][1] = BestPoint[1]
        if segment_number < len(Segment)-1:
            Segment[segment_number + 1][0][1] = BestPoint[1]


        Add_Z = BestPoint[2] - CenterOfConflictPipe[2]
        assert(Add_Z>=0)

        #整体下移
        for seg in Segment:
            for point in seg:
                point[2] += Add_Z

        print('Segment after:\n',Segment)
        print('==========================')
        return Segment

    else:
        raise Exception('Error in function:function_Chen.Remove()')

