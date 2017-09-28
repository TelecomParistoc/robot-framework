# Framework

## Overview 

This folder contains the whole core of python framework that can be use to represent and instantiate robots and their actions.

It is composed of 3 logical subfolders :
- robot : this folder is composed of everything that is common to every robot we instantiate (i.e : it does not depend of physical elements such as different motors or mechanical parts).
From the main Robot class we can instantiate a skeleton on which we could specify action sequences to do. It is possible to add attributes to this skeleton naming them (for example a specific motor, or button),
and also to add specific methods that would for instance matches real action the robot could do (like moving a servomotor from position A to position B).
- local_robot : this folder is highly customizable and should be used to specify every new robot that is created physically (creating a new file for each). Current robot in the folder (big_robot.py) shows how
to add objects like AX12 and functions like "move_AX12" on the skeleton of previous part
- tests : this folder is explicit and its content shows how to use the 2 previous folders in order to reach the goal of having a robot that performs specific actions.


For testing (the command launches every available test, one can look specifically to these in order to have a good understanding of what a real use of this framework could be) :

```
$ make test
```


## Basic tutorial

This part explains how to use this framework with a basic example. We will command 2 AX12 motors using this framework.
You can find the entiere source code of this example in *tests/basic_example_with_syntax.py*


### Construct the robot

First of all, we import the libraries we need. So we import the robot skeleton from the robot library, and the AX12 class.
```python
from robot import Robot
from AX12 import AX12
```

Now, we can "construct" the skeleton of our robot. 
```python
r = Robot()
```

For the moment, we just have an "empty" skeleton. So we will add to the skeleton each object our robot is composed of. The AX12 I use have the ID 141 and 130, but of course you may have different ID. I named the AX12 141 and 130 "motor_1" and "motor_2" respectively.
```python
r.add_object(AX12(141), "motor_1")
r.add_object(AX12(130), "motor_2")
```

### Define the actions the robot will do

We will define a sequence of actions, which will be run later. This sequence is named "seq_1".
```python
r.add_sequence("seq_1")
```

Each sequence is divided in blocks of actions. Each action in a same block will be done simultaneously, whereas blocks will be run one after the other. Generally speaking, we can add an action in a block like this :
```python
r.add_parallel(function, argument_list_of_the_function)
```

Assume that we want to move the first motor at position 100 (in degrees), and second motor at position -150 (a positiv number is for clockwise rotation, a negativ for a counter clockwise rotation). So we write :
```python
r.add_parallel(r.motor_1.move, [100])
r.add_parallel(r.motor_2.move, [-150])
```

Then we will define the end of the first block of actions. The end of a block means that we will wait for the end of the execution of the actions of this block, so :
```python
r.wait()
```

However, some actions might not be fully executed, for example if something blocks a motor. In this case, the line above will wait an infinite time and block the program... To solve this problem, there are two possibilities :
First, we can specify a maximum waiting time :
```python
r.wait(max_delay=3) #waits with a maximum waiting time of 3 seconds, safer than r.wait()
```

The second possibility is to specify not to wait for the end of all actions. It can be done when adding the action to the block : 
```python
r.add_parallel(function, arg_list, False) #the next r.wait() will not wait for the end of this action
```

Come back to our example. After the first r.wait, we can define the second block of actions. Assume that, in this block, we want to move a motor at a given speed, and not at a given position. The code to do this is :
```python
r.add_parallel(r.motor_1.move, [100], False)
r.wait(2)
``` 

So motor_1 will turn at 100% of the maximum rotation speed. Don't forget to stop it in the following block :
```
r.add_parallel(r.motor_1.turn, [0], False)
r.wait()
```

And so forth... We can of course add as many blocks as we want. After adding the last block, we must specify the end of the sequence definition :
```python
r.sequence_done()
```


### Running the sequence 
Don't forget that the code above only *defines* actions, and does nothing. To run the sequence "seq_1" :
```python
r.start_sequence("seq_1")
```

Then, like we wait for the end of a block, we wait for the end of the sequence
```python 
r.wait_sequence()
```

Finally, to quit the program :
```python
r.stop()
```







 
 