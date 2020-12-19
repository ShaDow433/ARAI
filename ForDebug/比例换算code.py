
def Consider_install(red_point, StructWorkArea3D, mid_TurningPoint):
    print(red_point)
    size = len(red_point)
    # 第几个坐标是大转折点
    n = 0
    for i in range(0, size):
        if (red_point[i][0] == mid_TurningPoint[0] and red_point[i][1] == mid_TurningPoint[1]):
            n = i
            break
    # print(n)
    # 实际坐标集合
    real_point = []
    for i in range(0, size):
        real_point.append([red_point[i][0] * 300 + 150, red_point[i][1] * 300 + 150, red_point[i][2] * 300 + 150])
    # 第一个大线段需要Y方向
    first_need_Y_left = 0
    first_need_Y_right = 0
    # 第二个大线段需要X方向
    second_need_X_left = 0
    second_need_X_right = 0
    # 判断起始点到大转折点的方向
    if (red_point[0][1] == red_point[n][1]):  # 如果方向沿X轴
        # 判断Y方向是否靠近了梁
        # 遍历起始点到大转折点之间所有转折点的，看左边和右边是否有梁
        for j in range(0, n + 1):
            if (StructWorkArea3D[red_point[j][0], red_point[j][1] - 1, red_point[j][2]] == 100):
                # 需要右移
                first_need_Y_right = 1
                break
            if (StructWorkArea3D[red_point[j][0], red_point[j][1] + 1, red_point[j][2]] == 100):
                # 需要左移
                first_need_Y_left = 1
                break
    # 转折点到终点的方向
    if (red_point[n][0] == red_point[-1][0]):  # 如果方向沿Y轴
        # 判断x方向是否靠近了梁
        # 遍历大转折点到终点之间所有转折点，看左边和右边是否有梁
        for j in range(n, size):
            if (StructWorkArea3D[red_point[j][0] - 1, red_point[j][1], red_point[j][2]] == 100):
                # 需要右移
                second_need_X_right = 1
                break
            if (StructWorkArea3D[red_point[j][0] + 1, red_point[j][1], red_point[j][2]] == 100):
                # 需要左移
                second_need_X_left = 1
                break
    # 针对第一个模型
    # 第一个大线段终点的所有小线段
    segment_mid = copy.deepcopy(red_point[0])
    # print("red_point[i][0]")
    # print(red_point[i][0])
    for i in range(n):
        # 求小线段的中点
        for j in range(3):
            temp_red_point = copy.deepcopy(red_point)
            segment_mid[j] = temp_red_point[i][j] + temp_red_point[i + 1][j]
        segment_mid = numpy.array(segment_mid)
        for j in range(3):
            segment_mid[j] = segment_mid[j] / 2
        # 沿着X轴不沿着Z轴
        if (red_point[i][2] == red_point[i + 1][2]):
            if ((segment_mid[2] - 1) >= 0 and StructWorkArea3D[
                int(segment_mid[0]), int(segment_mid[1]), int(segment_mid[2] - 1)] == 100):
                real_point[i][2] += 100
                real_point[i + 1][2] += 100
                red_point[i][2] += 1
                red_point[i + 1][2] += 1
            if ((segment_mid[2] + 1) <= 4 and StructWorkArea3D[
                int(segment_mid[0]), int(segment_mid[1]), int(segment_mid[2] + 1)] == 100):
                real_point[i][2] -= 100
                real_point[i + 1][2] -= 100
                red_point[i][2] -= 1
                red_point[i + 1][2] -= 1
        else:
            # 看小线段的中点，因为第一个模型第一个大线段是沿X轴
            if (StructWorkArea3D[int(segment_mid[0] + 1), int(segment_mid[1]), int(segment_mid[2])] == 100):
                real_point[i][0] -= 100
                real_point[i + 1][0] -= 100
                red_point[i][0] -= 1
                red_point[i + 1][0] -= 1
            if (StructWorkArea3D[int(segment_mid[0] - 1), int(segment_mid[1]), int(segment_mid[2])] == 100):
                real_point[i][0] += 100
                real_point[i + 1][0] += 100
                red_point[i][0] += 1
                red_point[i + 1][0] += 1

    if first_need_Y_left:
        for i in range(0, n + 1):
            real_point[i][1] -= 100
    if first_need_Y_right:
        for i in range(0, n + 1):
            real_point[i][1] += 100
    for i in range(n, size - 1):
        # 求小线段的中点
        for j in range(3):
            copy.deepcopy(red_point)
            segment_mid[j] = red_point[i][j]
            segment_mid[j] += red_point[i + 1][j]
        segment_mid = numpy.array(segment_mid)
        for j in range(3):
            segment_mid[j] = segment_mid[j] / 2
        # 不沿着Z轴
        if (red_point[i][2] == red_point[i + 1][2]):
            if ((segment_mid[2] + 1) <= 4 and StructWorkArea3D[
                int(segment_mid[0]), int(segment_mid[1]), int(segment_mid[2] + 1)] == 100):
                real_point[i][2] -= 100
                real_point[i + 1][2] -= 100
                red_point[i][2] -= 1
                red_point[i + 1][2] -= 1
            if ((segment_mid[2] - 1) >= 0 and StructWorkArea3D[
                int(segment_mid[0]), int(segment_mid[1]), int(segment_mid[2] - 1)] == 100):
                real_point[i][2] += 100
                real_point[i + 1][2] += 100
                red_point[i][2] += 1
                red_point[i + 1][2] += 1
        else:
            if (StructWorkArea3D[int(segment_mid[0]), int(segment_mid[1] + 1), int(segment_mid[2])] == 100):
                real_point[i][1] -= 100
                real_point[i + 1][1] -= 100
                red_point[i][1] -= 1
                red_point[i + 1][1] -= 1
            if (StructWorkArea3D[int(segment_mid[0]), int(segment_mid[1] - 1), int(segment_mid[2])] == 100):
                real_point[i][1] += 100
                real_point[i + 1][1] += 100
                red_point[i][1] += 1
                red_point[i + 1][1] += 1
        # # 看小线段的中点，因为第一个模型第二个大线段是沿Y轴
        # if (StructWorkArea3D[int(segment_mid[0]), int(segment_mid[1]+1), int(segment_mid[2])] == 100):
        #     real_point[i][1] -= 100
        #     real_point[i + 1][1] -= 100
        #     red_point[i][1] -= 1
        #     red_point[i + 1][1] -= 1
        # if (StructWorkArea3D[int(segment_mid[0]), int(segment_mid[1]-1), int(segment_mid[2])] == 100):
        #     real_point[i][1] += 100
        #     real_point[i + 1][1] += 100
        #     red_point[i][1] += 1
        #     red_point[i + 1][1] += 1
        # if ((segment_mid[2]+1)<=4 and StructWorkArea3D[int(segment_mid[0]), int(segment_mid[1]), int(segment_mid[2]+1)] == 100):
        #     real_point[i][2] -= 100
        #     real_point[i + 1][2] -= 100
        #     red_point[i][2] -= 1
        #     red_point[i + 1][2] -= 1
        # if ((segment_mid[2]-1)>=0 and StructWorkArea3D[int(segment_mid[0]), int(segment_mid[1]), int(segment_mid[2]-1)] == 100):
        #     real_point[i][2] += 100
        #     real_point[i + 1][2] += 100
        #     red_point[i][2] += 1
        #     red_point[i + 1][2] += 1
    if second_need_X_left:
        for i in range(n, size):
            real_point[i][0] -= 100
    if second_need_X_right:
        for i in range(n, size):
            real_point[i][0] += 100
    return real_point

# 把点区分出切成段，分成起始点，转折点，终点
def segmentation(red_list):
    size = len(red_list)
    # 管线的起始点转折点终点
    red_point = []
    red_point.append(red_list[0])
    i = 0
    for i in range(1, size - 1):
        a = red_list[i - 1]
        b = red_list[i]
        c = red_list[i + 1]
        first = [a[i] - b[i] for i in range(3)]
        second = [b[i] - c[i] for i in range(3)]
        print(c)

        if (first == second):
            i = 0
        else:
            red_point.append(red_list[i])
    print("输出模型中管线起始点，转折点，终点")
    red_point.append(red_list[-1])
    return red_point