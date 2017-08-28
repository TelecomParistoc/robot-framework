#include "python_callback.h"

#include <stdio.h>

static PyObject* callbacks[MAX_CALLBACKS];
static int keep_callbacks[MAX_CALLBACKS];
static int initialized = 0;


int add_callback(PyObject* callback, int keep_when_used)
{
    if(!initialized)
    {
	fprintf(stderr, "Non initilized !\n");
	exit(1);
    }

    int index = 0;

    while(index<MAX_CALLBACKS && callbacks[index])
        index++;


    if(index>=MAX_CALLBACKS)
        return -1;

    PyObject *temp;
    PyGILState_STATE gstate = PyGILState_Ensure();
    printf("%d\n", gstate);

    if(PyArg_ParseTuple(callback, "O:set_callback", &temp))
    {
        if(!PyCallable_Check(temp))
        {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            PyGILState_Release(gstate);
            return -1;
        }

        Py_XINCREF(temp);
        callbacks[index] = temp;
        keep_callbacks[index] = keep_when_used;

        PyGILState_Release(gstate);
        return index;
    }
    printf("Error : callback was not added\n");
    PyGILState_Release(gstate);
    return -1;
}


int remove_callback(int index)
{
    if(!callbacks[index])
        return -1;
    else
    {
        Py_XDECREF(callbacks[index]);
        callbacks[index] = NULL;
        return 0;
    }
}


int call_python_callback(int index)
{
    if(index<0 || index>=MAX_CALLBACKS)
        return -1;

    if(!callbacks[index])
        return -1;
    else
    {
        PyGILState_STATE gstate = PyGILState_Ensure();

        PyObject *result;
        PyObject *empty_tuple = PyTuple_New(0);
        result = PyEval_CallObject(callbacks[index], empty_tuple);
        Py_DECREF(empty_tuple);

        if(result == NULL)
        {
            PyGILState_Release(gstate);
            return -2;
        }
        Py_DECREF(result);

        if(!keep_callbacks[index])
        {
            Py_XDECREF(callbacks[index]);
            callbacks[index] = NULL;
        }

        PyGILState_Release(gstate);
        return 0;
    }
}


int callbacks_queue_size()
{
    int index = 0, n = 0;
    for(; index<MAX_CALLBACKS; index++)
        if(callbacks[index])
            n++;

    return n;
}
