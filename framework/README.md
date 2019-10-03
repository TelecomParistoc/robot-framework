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

### Define actions to be executed by the robot

The file `action.py` defines multiple classes.

#### Abstract action

An Action is an object that has to meet several requirements.
The two most important ones to know are :

 * The action is started using `action.exec()`.
 * You can specify that the end of the action has to be waited for before executing the next action using `action.wait()`.

`action.exec()` has to be non-blocking unless `action.wait()` has been set. In this case, it has to block the execution until the action is over.
This property makes parallel actions possible.

```
action1.exec()
action2.exec()
action3.exec()
```
Here, action1, action2 and action3 are started together and will therefore be parallel. However, if you add:
```
action2.wait()

action1.exec()
action2.exec()
action3.exec()
```
`action1` and `action2` will are started in parallel however `action3` will only start when `action2` is over (`action2.exec()` ends).

#### Function

Function is an Action that executes a custom function `fun` given as an argument.
```
function = Function(fun)
```
The function `fun` has to be non-blocking, or else `function.exec()` can be blocking even if `function.wait()` has not been called at the definition. If fun takes a non-trivial amount of time to execute, you can instead use a `ThreadedFunction`:
```
function = ThreadedFunction(fun)
```
in this case, `fun` is executed on another thread. Beware of concurrency.

#### Sequence

A sequence is a special type of action whose purpose is to define a group of actions that have to be executed together or in a specific order.

The following syntaxes create the same sequence :
```
sequence = Sequence()
sequence.add_action(action1)
sequence.add_action(action2)
sequence.add_action(action3)

sequence = Sequence([action1, action2, action3])
```
`sequence.exec()` calls `exec()` on all action in the sequence in order, which can be used for parallel or sequential execution, depending on whether or not the actions have been defined as "to be waited for".
By default, this method is non-blocking.

If the robot has to wait for all actions of the sequence to be over before doing anything else, you can add to the definition of the sequence:
```
sequence.wait()
```
If this method is used, `sequence.exec()` will block until all callbacks are received.

#### Other action_list

Other useful actions are defined in [robot/action.py](robot/action.py):
* MoveToAction
* AX12MoveAction
Please take a look at the file to learn more.
