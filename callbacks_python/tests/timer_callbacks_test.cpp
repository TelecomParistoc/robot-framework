#include <functional>
#include <Python.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <mutex>


#ifdef __cplusplus
extern "C" {
#endif

	#include "python_callback/python_callback.h"

	int call_after_delay(float time, void (* fct)()* callback);
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
std::vector<std::function<void(void)> > callbacks;


void run()
{
	std::cout<<"[+] Starting thread"<<std::endl;

	auto start = std::chrono::high_resolution_clock::now();

	is_running = true;
	while(is_running)
	{
		std::chrono::duration<float> duration = std::chrono::high_resolution_clock::now()-start;

		main_mutex.lock();

		for(int i=0; i<(int)done.size(); i++)
			if(!done[i] && delays[i]<duration.count())
			{
				done[i] = true;
				std::cout<<"Calling python callback with index "<<i<<" => return code : "<<callbacks[i]()<<std::endl;
			}

		main_mutex.unlock();

		usleep(1000);
	}
}

int create_thread()
{
	//PyEval_InitThreads();
	main_thread = std::thread(run);
	//PyEval_SaveThread();
	return main_thread.joinable();
}

int call_after_delay(float time, void (* fct)()* callback)
{
	if(!is_running)
		if(create_thread()<0)
		{
			std::cerr<<"[-] Unable to create thread"<<std::endl;
			return -1;
		}

	std::cout<<time<<std::endl;
	std::cout<<delays.size()<<std::endl;
	std::cout<<done.size()<<std::endl;
	main_mutex.lock();
	delays.push_back(time);
	done.push_back(false);
	//callback_index.push_back(callback_index.size());
	callbacks.push_back(std::function<void()>(callback));
	main_mutex.unlock();

	return 0;
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
