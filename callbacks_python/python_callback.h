/*
*  Following functions describe a not yet thread safe interface in order to call python from C.
*  If you want to allow the programmer to specify a python callback that is called when an action is finished (motor at right position for instance),
*  you MUST take the callback argument as a PyObject*, passing it to add_callback function, and keeping the index returned in order to call call_python_callback with this index.
*/

#ifndef PYTHON_CALLBACKS
#define PTYHON_CALLBACKS


#include <Python.h>


#define MAX_CALLBACKS 1000 //defines the maximum number of callbacks that can be kept in memory


/* performs insertion of python callback in a table waiting for it to be called or keeping it
*  common arguments :
*       callback : the python callback object to be called
*       keep_when_used : 0 if callback shouldn't be kept in memory when used, otherwise callback will be kept until erasure
*  returns :
*       -1 if add failed
*       index of generated callback otherwise
*/
int add_callback(PyObject* callback, int keep_when_used);


/* performs deletion of python callback if it exists
*  common arguments :
*       index : the python callback index in table, should be returned by add_callback
*  returns :
*       0 if a callback were at index index
*       -1 otherwise
*/
int remove_callback(int index);


/* performs call and possible deletion of python callback if it exists
*  common arguments :
*       index : the python callback index in table, should be returned by add_callback
*  returns :
*       0 if a callback were at index index
*       -1 if callback doesn't exist
*       -2 if python call failed
*/
int call_python_callback(int index);


/* returns size of current table of current stored callbacks
*/
int callbacks_queue_size();


#endif
