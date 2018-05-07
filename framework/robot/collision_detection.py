import time, math
import motion

#all distances are in mm
TABLE_DIMENSION     = [3000, 2000]
NO_SENSOR_DISTANCE  = 100
SENSOR_RANGE        = 200

#all durations are in seconds
SENSOR_MANAGER_PERIOD = 0.05
DELAY_BEFORE_BYPASSING_OBSTACLE = 2.

def closest_distance_to_edge(x, y):
    return min([x, y, TABLE_DIMENSION[0] - x, TABLE_DIMENSION[1] - y])

def get_intermediate_goal(robot, front_obstacle, rear_obstacle):
    """
        computes a new point to reach before going to the final goal
        the idea is to avoid an obstacle
        front obstacle, rear_obstacle == booleans
    """
    DETOUR_LENGTH = 200 #mm
    x = robot.get_pos_X()
    y = robot.get_pos_Y()
    theta = robot.get_heading() * math.pi / 180.

    p_left_x    = x + DETOUR_LENGTH * math.cos(theta - math.pi / 2.)
    p_left_y    = y + DETOUR_LENGTH * math.sin(theta - math.pi / 2.)
    p_right_x   = x + DETOUR_LENGTH * math.cos(theta + math.pi / 2.)
    p_right_y   = y + DETOUR_LENGTH * math.sin(theta + math.pi / 2.)

    #we go as far from edges as possible
    if (closest_distance_to_edge(p_left_x, p_left_y)
            > closest_distance_to_edge(p_right_x, p_right_y)):
        return (int(p_left_x), int(p_left_y))
    return (int(p_right_x), int(p_right_y))


def is_collision(robot, front_detection, rear_detection):

    #disable collision_detection when robot is turning
    if robot.turning:
        return False, False

    x = robot.get_pos_X()
    y = robot.get_pos_Y()

    theta = robot.get_heading()
    tmp = theta * math.pi / 180.

    dx = SENSOR_RANGE * math.sin(tmp)
    dy = SENSOR_RANGE * math.cos(tmp)

    forward_obstacle = False
    backward_obstacle = False
    direction = robot.getDirection()

    #if the robot is close from an edge, the sensors are ignored
    if (direction == motion.DIR_FORWARD and front_detection()
        and closest_distance_to_edge(x + dx, y + dy) >= NO_SENSOR_DISTANCE):
        forward_obstacle = True

    if (direction == motion.DIR_BACKWARD and rear_detection()
        and closest_distance_to_edge(x - dx, y - dy) >= NO_SENSOR_DISTANCE):
        backward_obstacle = True

    return forward_obstacle, backward_obstacle

def sensor_manager(robot, front_detection, rear_detection):

    """
        see Robot.start_collision_detection for a more detailled documentation

        this function assumes +x axis corresponds to heading 0 degree
        and +y axis corresponds to heading 90 degrees
    """

    while robot.enable_collision_detection:

        forward_obstacle, backward_obstacle = is_collision(robot,
                                                front_detection, rear_detection)
        if forward_obstacle or backward_obstacle:
            if forward_obstacle: print "[!] obstacle detected backwards!"
            if backward_obstacle: print "[!] obstacle detected forwards!"
            robot.emergency_stop()
            time.sleep(DELAY_BEFORE_BYPASSING_OBSTACLE)

            ## -------------------- MEANS OUR STRATEGY IS STOP ------------###
            #must be improved !!!!!!
            continue

            #check if obstacle is still there
            forward_obstacle, backward_obstacle = is_collision(robot,
                                                front_detection, rear_detection)
            if not forward_obstacle and not backward_obstacle:
                continue

            x, y = get_intermediate_goal(robot, forward_obstacle,
                                                backward_obstacle)
            robot.moveTo(x, y, final_heading=-1, callback=None)
            robot.emergency_resume()

        time.sleep(SENSOR_MANAGER_PERIOD)
