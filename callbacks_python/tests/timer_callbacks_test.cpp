#include "python_callback/python_callback.h"
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <mutex>


bool is_running = false;
std::mutex main_mutex;
std::thread main_thread;
std::vector<float> delays;

int call_after_delay(float time, PyObject* callback)
{
	if(!is_running)
		if(create_thread()<0)
			return -1;
	main_mutex.lock();
	delays.push_back(time);
	add_callback(callback, 0);
	main_mutex.unlock();

	return 0;
}

void run()
{
	is_running = true;
	while(is_running)
	{
		usleep(1000);
	}
}

int create_thread()
{
	main_thread = std::thread(run);
	return main_thread.joinable();
}

int empty_queue_callback()
{
	main_mutex.lock();
	int s = callbacks_queue_size();
	main_mutex.unlock();
	if(s<0)
		return s;
	else if(!s)
		return 1;
	else
		return 0;
}

void join()
{
	is_running = false;
	if(main_thread.joinable())
		main_thread.join();
}
