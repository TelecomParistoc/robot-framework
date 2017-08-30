# Framework

This folder contains the whole core of python framework that can be use to represent and instantiate robots and their actions.

It is composed of 3 logical subfolders :
- robot : this folder is composed of everything that is common to every robot we instantiate (i.e : it does not depend of physical elements such as different motors or mechanical parts).
From the main Robot class we can instantiate a skeleton on which we could specify action sequences to do. It is possible to add attributes to this skeleton naming them (for example a specific motor, or button),
and also to add specific methods that would for instance matches real action the robot could do (like moving a servomotor from position A to position B).
- local_robot : this folder is highly customizable and should be used to specify every new robot that is created physically (creating a new file for each). Current robot in the folder (big_robot.py) shows how
to add objects like AX12 and functions like "move_AX12" on the skeleton of previous part
- tests : this folder is explicit and its content shows how to use the 2 previous folders in order to reach the goal of having a robot that performs specific actions.


For testing (the command launches every available test, one can look specifically to these in order to have a good understanding of what a real use of this framework could be) :

*make test*
