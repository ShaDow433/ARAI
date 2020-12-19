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
                          
                                #print('\n\nin put_pipe() if 不存在best_point,下降梁')
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
