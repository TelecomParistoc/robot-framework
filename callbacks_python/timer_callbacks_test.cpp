#include <functional>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <mutex>


typedef void (*c_fct_ptr)(void);

#ifdef __cplusplus
extern "C" {
#endif

	int call_after_delay(float time, c_fct_ptr callback);
	int empty_queue_callback();
	int done_callbacks();
	void join();

#ifdef __cplusplus
}
#endif


bool is_running = false;
size_t number_done = 0;
std::mutex main_mutex;
std::thread main_thread;
std::vector<bool> done;
std::vector<float> delays;
std::vector<std::function<void()> > callbacks;


void run()
{
	std::cout<<"[+] Executing multithread python callback with delay calls"<<std::endl;
	std::cout<<"[+] Starting thread"<<std::endl;

	auto start = std::chrono::high_resolution_clock::now();

	is_running = true;
	while(is_running)
	{
		std::chrono::duration<float> duration = std::chrono::high_resolution_clock::now()-start;

		main_mutex.lock();

		number_done = 0;
		for(int i=0; i<(int)done.size(); i++)
			if(!done[i] && delays[i]<duration.count())
			{
				done[i] = true;
				std::cout<<"Calling python callback with index "<<i<<std::endl;
				callbacks[i]();
			}
			else if(done[i])
				number_done++;

		main_mutex.unlock();

		usleep(1000);
	}
}

int create_thread()
{
	if(!main_thread.joinable())
		main_thread = std::thread(run);
	return main_thread.joinable();
}

int call_after_delay(float time, c_fct_ptr callback)
{
	main_mutex.lock();
	if(!is_running)
		if(create_thread()<0)
		{
			std::cerr<<"[-] Unable to create thread"<<std::endl;
			return -1;
		}

	delays.push_back(time);
	done.push_back(false);
	callbacks.push_back(std::function<void(void)>(std::bind(callback)));
	main_mutex.unlock();

	return 0;
}

int empty_queue_callback()
{
	main_mutex.lock();
	size_t s = number_done;
	main_mutex.unlock();
	if(s<done.size())
		return 0;
	else
		return 1;
}

int done_callbacks()
{
	main_mutex.lock();
	size_t r = number_done;
	main_mutex.unlock();
	return r;
}

void join()
{
	std::cout<<"[...] Joining thread"<<std::endl;
	is_running = false;
	if(main_thread.joinable())
		main_thread.join();
	std::cout<<"[+] Thread joint"<<std::endl;
}
