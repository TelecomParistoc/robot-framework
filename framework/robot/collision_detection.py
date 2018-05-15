import time, math
import motion

#all distances are in mm
TABLE_DIMENSION     = [3000, 2000]
NO_SENSOR_DISTANCE  = 300
SENSOR_RANGE        = 200

#all durations are in seconds
SENSOR_MANAGER_PERIOD = 0.05
DELAY_BEFORE_BYPASSING_OBSTACLE = 0.5

def closest_distance_to_edge(x, y):
    return min([x, y, TABLE_DIMENSION[0] - x, TABLE_DIMENSION[1] - y])

def get_intermediate_goal(robot, front_obstacle, rear_obstacle, direction):
    """
        computes a new point to reach before going to the final goal
        the idea is to avoid an obstacle
        front obstacle, rear_obstacle == booleans
    """
    DETOUR_LENGTH = 200 #mm

    x = robot.get_pos_X()
    y = robot.get_pos_Y()
    theta = robot.get_heading() * math.pi / 180.

    new_x = x
    new_y = y

    if direction == motion.DIR_FORWARD:
        new_x = x - DETOUR_LENGTH * math.cos(theta)
        new_y = y - DETOUR_LENGTH * math.sin(theta)

    if direction == motion.DIR_BACKWARD:
        new_x = x + DETOUR_LENGTH * math.cos(theta)
        new_y = y + DETOUR_LENGTH * math.sin(theta)

    return (int(new_x), int(new_y))

    p_left_x    = x + DETOUR_LENGTH * math.cos(theta -  math.pi / 2.)
    p_left_y    = y + DETOUR_LENGTH * math.sin(theta -  math.pi / 2.)
    p_right_x   = x + DETOUR_LENGTH * math.cos(theta +  math.pi / 2.)
    p_right_y   = y + DETOUR_LENGTH * math.sin(theta +  math.pi / 2.)

    #we go as far from edges as possible
    if (closest_distance_to_edge(p_left_x, p_left_y)
            > closest_distance_to_edge(p_right_x, p_right_y)):
	print "[Collision Detection] Setting new goal to the left" 
        return (int(p_left_x), int(p_left_y))
    print "[Collision Detection] Setting new goal to the right" 
    return (int(p_right_x), int(p_right_y))


def is_collision(robot, front_detection, rear_detection, direction):

    #disable collision_detection when robot is turning
    if robot.turning:
        return False, False

    x = robot.get_pos_X()
    y = robot.get_pos_Y()

    theta = robot.get_heading()
    tmp = theta * math.pi / 180.

    dx = SENSOR_RANGE * math.cos(tmp)
    dy = SENSOR_RANGE * math.sin(tmp)

    forward_obstacle = False
    backward_obstacle = False
    
    #if the robot is close from an edge, the sensors are ignored
    if (direction == motion.DIR_FORWARD and front_detection()
        and closest_distance_to_edge(x + dx, y + dy) >= NO_SENSOR_DISTANCE):
        print "[Collision Detection] front obstacle detected at ", x + dx, y + dy, " ; (x, y) = ", x, y
        forward_obstacle = True

    if (direction == motion.DIR_BACKWARD and rear_detection()
        and closest_distance_to_edge(x - dx, y - dy) >= NO_SENSOR_DISTANCE):
        print "[Collision Detection] rear obstacle detected at ", x - dx, y - dy, " ; (x, y) = ", x, y
        backward_obstacle = True

    return forward_obstacle, backward_obstacle
    
def sensor_manager(robot, front_detection, rear_detection):

    """
        see Robot.start_collision_detection for a more detailled documentation

        this function assumes +x axis corresponds to heading 0 degree
        and +y axis corresponds to heading 90 degrees
    """ 
    #Because python... (we want just_print_to_be_deleted to have access to must_resume, but it isn't called in the right scope...)  
    class local:
        must_resume = False
 
    def just_print_to_be_deleted():
        if local.must_resume:
            return
        #Actually not to be deleted
        print "[Collision Detection] Moving to intermediate goal at : ", x, ", ", y, " => REACHED"
        local.must_resume = True

    while robot.enable_collision_detection:

        direction = robot.getDirection()
        forward_obstacle, backward_obstacle = is_collision(robot,
                                                front_detection, rear_detection, direction)
        if forward_obstacle or backward_obstacle:
            if forward_obstacle: print "[Collision Detection] [!] obstacle detected forwards!"
            if backward_obstacle: print "[Collision Detection] [!] obstacle detected backwards!"
            robot.stop_motion()
            time.sleep(0.1)
		
            x, y = get_intermediate_goal(robot, forward_obstacle,
                                                backward_obstacle,
                                                direction)
            #Should give a point Ncm behind the robot, relative to the direction it should be moving forward in
            print "[Collision Detection] Moving to intermediate goal at : ", x, ", ", y
	    #robot.moveTo(x, y, final_heading=-1, callback = just_print_to_be_deleted)
	    #if (forward_obstacle and not rear_detection()) or (backward_obstacle and not front_detection()):
            motion.moveTo(x, y, -1, just_print_to_be_deleted)
            #time.sleep(DELAY_BEFORE_BYPASSING_OBSTACLE)

        elif local.must_resume:
            print "[Collision Detection] Obstacle is gone! Resuming..."
            x = robot.get_pos_X()
            y = robot.get_pos_Y()
            theta = robot.get_heading()
            tmp = theta * math.pi / 180.
            dx = SENSOR_RANGE * math.cos(tmp)
            dy = SENSOR_RANGE * math.sin(tmp)
            print robot.getDirection(), front_detection(), closest_distance_to_edge(x + dx, y + dy)

            robot.resume_motion()
            local.must_resume = False

        time.sleep(SENSOR_MANAGER_PERIOD)
