
#include <Python.h>
#include <pthread.h>

#include "python_callback/python_callback.h"


void (* callback)(int);

static void* thread_function(void *);
void void_bidon(PyObject* self, PyObject* callback);
void call_fct(void (*fct)(int), int);
void call_fct_with_thread(void (*fct)(int), int);


void void_bidon(PyObject* self, PyObject* callback){
	
	printf("Hi from C world ! \n");
	//en fait callback est un tuple contenant 1 fonction
	// mais n'est pas une fonction
	int index = add_callback(callback, 0);

	printf("Callback number = %d\n", index);
	call_python_callback(index);

	printf("Python callback done\n");

}

static void *thread_function(void* threadid) {

	printf("Hello from the thread\n");

	callback(*((int *) threadid));
	pthread_exit(NULL);
}


void call_fct(void (* fct)(int), int arg1){

	printf("la fonction va etre appelee avec arg = %d\n", arg1);
	
	fct(arg1);

	printf("fin de call_fct");
}

void call_fct_with_thread(void (* fct)(int), int arg){

	pthread_t thread;

	callback = fct;
	int rc = pthread_create(&thread, NULL, thread_function, &arg);

	if (rc){
		printf("creating thread failed : reutrn code = %d\n", rc);
		exit(-1);
	}

	
}
