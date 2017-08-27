#include "python_callback.h"

#include <stdio.h>

static PyObject* callbacks[MAX_CALLBACKS];
static int keep_callbacks[MAX_CALLBACKS];
static int initialized = 0;


void initialize()
{
    Py_Initialize();
    printf("Initializeing\n");
    initialized = 1;
}

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
    printf("a %lx %x\n", (long int)callback, keep_when_used);
    PyGILState_STATE gstate = PyGILState_Ensure();
    printf("%d\n", gstate);

    if(PyArg_ParseTuple(callback, "O:set_callback", &temp))
    {
        printf("b\n");
        if(!PyCallable_Check(temp))
        {
            printf("c\n");
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            PyGILState_Release(gstate);
            return -1;
        }
        printf("d\n");
        Py_XINCREF(temp);
        printf("e\n");
        callbacks[index] = temp;
        keep_callbacks[index] = keep_when_used;

        printf("Returning %d %lx\n", index, (long int)temp);

        PyGILState_Release(gstate);
        return index;
    }

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
        printf("Calling %d %lx\n", index, (long int)callbacks[index]);

        if(!keep_callbacks[index])
            callbacks[index] = NULL;
        return 0;

        PyGILState_STATE gstate = PyGILState_Ensure();

        PyObject *result;
        result = PyEval_CallObject(callbacks[index], NULL);
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
