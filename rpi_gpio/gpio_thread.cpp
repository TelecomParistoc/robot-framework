#include <functional>
#include <unistd.h>
#include <iostream>
#include <thread>
#include <mutex>
#include <map>

#include "wiringPi.h"
#include "gpio.h"


typedef void (*c_fct_ptr)(void);

#ifdef __cplusplus
extern "C" {
#endif

    int pin_state(int id);
    void set_pin_state(int id, int state);

    void assign_callback_on_gpio_change(int id, c_fct_ptr callback, bool one_shot = false);
    void assign_callback_on_gpio_down(int id, c_fct_ptr callback, bool one_shot = false);
    void assign_callback_on_gpio_up(int id, c_fct_ptr callback, bool one_shot = false);

    void remove_callbacks_on_gpio_change(int id);
    void remove_callbacks_on_gpio_down(int id);
    void remove_callbacks_on_gpio_up(int id);
    void remove_callbacks_on_gpio(int id);
    void remove_all_callback();

    void init();
    void join();

#ifdef __cplusplus
}
#endif


std::map<int, GPIO> gpios;

bool is_running = false;
std::mutex main_mutex;
std::thread main_thread;


void run()
{
	std::cout<<"[+] Starting GPIO thread"<<std::endl;

	is_running = true;
	while(is_running)
	{
                main_mutex.lock();

        for(auto it : gpios)
        {
            int current = digitalRead(it.first);
            if(current != it.second.get_value())
            {
                std::cout<<"[+] Value of gpio "<<it.first<<" has changed to "<<current<<std::endl;
                it.second.set_value(current);
                it.second.call_on_gpio_change();
                if(current)
                    it.second.call_on_gpio_up();
                else
                    it.second.call_on_gpio_down();
            }
        }

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

int create_thread_if_not_running()
{
    if(!is_running)
    {
        if(create_thread()<0)
        {
            std::cerr<<"[-] Unable to create thread"<<std::endl;
            return -1;
        }
        else
            return 1;
    }

    return 0;
}

int pin_state(int id)
{return digitalRead(id);}

void set_pin_state(int id, int state)
{return digitalWrite(id, state);}

void assign_callback_on_gpio_change(int id, c_fct_ptr callback, bool one_shot)
{
    main_mutex.lock();
    create_thread_if_not_running();

    if(!gpios.count(id))
        gpios[id] = GPIO(id, digitalRead(id));

    gpios[id].add_attached_on_gpio_change(_callback(callback), one_shot);

    main_mutex.unlock();
}

void assign_callback_on_gpio_down(int id, c_fct_ptr callback, bool one_shot)
{
    main_mutex.lock();
    create_thread_if_not_running();

    if(!gpios.count(id))
        gpios[id] = GPIO(id, digitalRead(id));

    gpios[id].add_attached_on_gpio_down(_callback(callback), one_shot);

    main_mutex.unlock();
}

void assign_callback_on_gpio_up(int id, c_fct_ptr callback, bool one_shot)
{
    main_mutex.lock();
    create_thread_if_not_running();

    if(!gpios.count(id))
        gpios[id] = GPIO(id, digitalRead(id));

    gpios[id].add_attached_on_gpio_up(_callback(callback), one_shot);

    main_mutex.unlock();
}

void remove_callbacks_on_gpio_change(int id)
{
    main_mutex.lock();

    if(!gpios.count(id))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (id "<<id<<")"<<std::endl;
        return;
    }

    gpios[id].clean_on_gpio_change();
    main_mutex.unlock();
}

void remove_callbacks_on_gpio_down(int id)
{
    main_mutex.lock();

    if(!gpios.count(id))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (id "<<id<<")"<<std::endl;
        return;
    }

    gpios[id].clean_on_gpio_down();
    main_mutex.unlock();
}

void remove_callbacks_on_gpio_up(int id)
{
    main_mutex.lock();

    if(!gpios.count(id))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (id "<<id<<")"<<std::endl;
        return;
    }

    gpios[id].clean_on_gpio_up();
    main_mutex.unlock();
}

void remove_callbacks_on_gpio(int id)
{
    main_mutex.lock();

    if(!gpios.count(id))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (id "<<id<<")"<<std::endl;
        return;
    }

    gpios[id].clean_callbacks();
    main_mutex.unlock();
}

void remove_all_callback()
{
    main_mutex.lock();
    gpios.clear();
    main_mutex.unlock();
}

void init()
{
    wiringPiSetupGpio();
}

void join()
{
	std::cout<<"[...] Stopping callback thread"<<std::endl;
	is_running = false;
	if(main_thread.joinable())
		main_thread.join();
	std::cout<<"[+] Thread joint"<<std::endl;
}
