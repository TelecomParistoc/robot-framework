#include "python_callback/python_callback.h"
#include <unistd.h>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <mutex>


#ifdef __cplusplus
extern "C" {
#endif

	int call_after_delay(float time, PyObject* callback);
	int local_exported_queue_size();
	int empty_queue_callback();
	void join();

#ifdef __cplusplus
}
#endif


bool is_running = false;
std::mutex main_mutex;
std::thread main_thread;
std::vector<bool> done;
std::vector<float> delays;
std::vector<int> callback_index;


void run()
{
	auto start = std::chrono::high_resolution_clock::now();

	is_running = true;
	while(is_running)
	{
		std::chrono::duration<float> duration = std::chrono::high_resolution_clock::now()-start;

		main_mutex.lock();

		for(int i=0; i<(int)done.size(); i++)
			if(!done[i] && delays[i]>duration.count())
			{
				done[i] = true;
				std::cout<<"Calling python callback with index "<<callback_index[i]<<" => return code : "<<call_python_callback(callback_index[i])<<std::endl;
			}

		main_mutex.unlock();

		usleep(1000);
	}
}

int create_thread()
{
	main_thread = std::thread(run);
	return main_thread.joinable();
}

int call_after_delay(float time, PyObject* callback)
{
	if(!is_running)
		if(create_thread()<0)
			return -1;

	main_mutex.lock();
	delays.push_back(time);
	done.push_back(false);
	callback_index.push_back(add_callback(callback, 0));
	main_mutex.unlock();

	return 0;
}

int local_exported_queue_size()
{
	return callbacks_queue_size();
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
	std::cout<<"[...] Joining thread"<<std::endl;
	is_running = false;
	if(main_thread.joinable())
		main_thread.join();
	std::cout<<"[+] Thread joint"<<std::endl;
}
