#include "python_callback.h"


static PyObject* callbacks[MAX_CALLBACKS];
static int keep_callbacks[MAX_CALLBACKS];


int add_callback(PyObject* callback, int keep_when_used)
{
    int index = 0;
    while(index<MAX_CALLBACKS && callbacks[index])
        index++;

    if(index>=MAX_CALLBACKS)
        return -1;

    PyObject *temp;
    if (PyArg_ParseTuple(callback, "O:set_callback", &temp))
    {
        if (!PyCallable_Check(temp))
        {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            return -1;
        }
        Py_XINCREF(temp);
        callbacks[index] = temp;
        keep_callbacks[index] = keep_when_used;

        return index;
    }

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
    if(!callbacks[index])
        return -1;
    else
    {
        PyObject *result;
        result = PyEval_CallObject(callbacks[index], NULL);
        if(result == NULL)
            return -2;
        Py_DECREF(result);

        if(!keep_callbacks[index])
        {
            Py_XDECREF(callbacks[index]);
            callbacks[index] = NULL;
        }
        return 0;
    }
}
