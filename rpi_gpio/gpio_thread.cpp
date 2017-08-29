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

    int wpi_to_gpio(int wpi);

    void set_pin_mode(int pin, int mode);
    void set_pull_up_down(int pin, int mode);

    int pin_state(int pin);
    void set_pin_state(int pin, int state);
    unsigned int pin_read(int pin);
    void pin_write(int pin, int val);
    int analog_read(int pin);
    void analog_write(int pin, int val);
    void pwm_write(int pin, int val);

    void assign_callback_on_gpio_change(int pin, c_fct_ptr callback, bool one_shot = false);
    void assign_callback_on_gpio_down(int pin, c_fct_ptr callback, bool one_shot = false);
    void assign_callback_on_gpio_up(int pin, c_fct_ptr callback, bool one_shot = false);

    void remove_callbacks_on_gpio_change(int pin);
    void remove_callbacks_on_gpio_down(int pin);
    void remove_callbacks_on_gpio_up(int pin);
    void remove_callbacks_on_gpio(int pin);
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

        for(std::map<int, GPIO>::iterator it : gpios)
        {
            int current = digitalRead(it.first);
            if(current != it->second.get_value())
            {
                it->second.set_value(current);
                it->second.call_on_gpio_change();
                if(current)
                    it->second.call_on_gpio_up();
                else
                    it->second.call_on_gpio_down();
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


int wpi_to_gpio(int wpi)
{return wpiPinToGpio(wpi);}


void set_pin_mode(int pin, int mode)
{return pinMode(pin, mode);}

void set_pull_up_down(int pin, int mode)
{return pullUpDnControl(pin, mode);}


int pin_state(int pin)
{return digitalRead(pin);}

void set_pin_state(int pin, int state)
{return digitalWrite(pin, state);}

unsigned int pin_read(int pin)
{return digitalRead8(pin);}

void pin_write(int pin, int val)
{return digitalWrite8(pin, val);}

int analog_read(int pin)
{return analogRead(pin);}

void analog_write(int pin, int val)
{return analogWrite(pin, val);}

void pwm_write(int pin, int val)
{return pwmWrite(pin, val);}


void assign_callback_on_gpio_change(int pin, c_fct_ptr callback, bool one_shot)
{
    main_mutex.lock();
    create_thread_if_not_running();

    if(!gpios.count(pin))
        gpios[pin] = GPIO(pin, digitalRead(pin));

    gpios[pin].add_attached_on_gpio_change(_callback(callback), one_shot);

    main_mutex.unlock();
}

void assign_callback_on_gpio_down(int pin, c_fct_ptr callback, bool one_shot)
{
    main_mutex.lock();
    create_thread_if_not_running();

    if(!gpios.count(pin))
        gpios[pin] = GPIO(pin, digitalRead(pin));

    gpios[pin].add_attached_on_gpio_down(_callback(callback), one_shot);

    main_mutex.unlock();
}

void assign_callback_on_gpio_up(int pin, c_fct_ptr callback, bool one_shot)
{
    main_mutex.lock();
    create_thread_if_not_running();

    if(!gpios.count(pin))
        gpios[pin] = GPIO(pin, digitalRead(pin));

    gpios[pin].add_attached_on_gpio_up(_callback(callback), one_shot);

    main_mutex.unlock();
}

void remove_callbacks_on_gpio_change(int pin)
{
    main_mutex.lock();

    if(!gpios.count(pin))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (pin "<<pin<<")"<<std::endl;
        return;
    }

    gpios[pin].clean_on_gpio_change();
    main_mutex.unlock();
}

void remove_callbacks_on_gpio_down(int pin)
{
    main_mutex.lock();

    if(!gpios.count(pin))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (pin "<<pin<<")"<<std::endl;
        return;
    }

    gpios[pin].clean_on_gpio_down();
    main_mutex.unlock();
}

void remove_callbacks_on_gpio_up(int pin)
{
    main_mutex.lock();

    if(!gpios.count(pin))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (pin "<<pin<<")"<<std::endl;
        return;
    }

    gpios[pin].clean_on_gpio_up();
    main_mutex.unlock();
}

void remove_callbacks_on_gpio(int pin)
{
    main_mutex.lock();

    if(!gpios.count(pin))
    {
        std::cerr<<"[-] Unable to remove callbacks of inexisting gpio (pin "<<pin<<")"<<std::endl;
        return;
    }

    gpios[pin].clean_callbacks();
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
