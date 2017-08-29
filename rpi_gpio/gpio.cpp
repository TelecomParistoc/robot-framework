#include <algorithm>

#include "gpio.h"


GPIO::GPIO(int id, int initial_value) :
    _id(id),
    _value(initial_value)
{}


void GPIO::add_attached_on_gpio_change(const _callback& callback, bool one_shot)
{
    if(one_shot)
        _attached_on_change_one_shot.push_back(_attached_on_change.size());
    _attached_on_change.push_back(callback);
}

void GPIO::add_attached_on_gpio_down(const _callback& callback, bool one_shot)
{
    if(one_shot)
        _attached_on_down_one_shot.push_back(_attached_on_down.size());
    _attached_on_down.push_back(callback);
}

void GPIO::add_attached_on_gpio_up(const _callback& callback, bool one_shot)
{
    if(one_shot)
        _attached_on_up_one_shot.push_back(_attached_on_up.size());
    _attached_on_up.push_back(callback);
}


void GPIO::clean_on_gpio_change()
{_attached_on_change.clear();}

void GPIO::clean_on_gpio_down()
{_attached_on_down.clear();}

void GPIO::clean_on_gpio_up()
{_attached_on_up.clear();}

void GPIO::clean_callbacks()
{
    clean_on_gpio_change();
    clean_on_gpio_down();
    clean_on_gpio_up();
}


void GPIO::remove_called_one_shot(std::vector<_callback>& callbacks, std::vector<size_t>& one_shot_index)
{
    size_t i = 0, current = 0, max = one_shot_index.size();

    callbacks.erase(
        std::remove_if(
            callbacks.begin(),
            callbacks.end(),
            [&i, &current, &max, &one_shot_index](_callback& c) -> bool
            {
                if(current >= max)
                    return false;

                bool r = false;
                if(i == one_shot_index[current])
                {
                    r = true;
                    current++;
                }
                i++;

                return r;
            }
        ),
        callbacks.end());
}

void GPIO::call_on_gpio_change()
{
    for(auto it : _attached_on_change)
        if(it)
            it();

    remove_called_one_shot(_attached_on_change, _attached_on_change_one_shot);
}

void GPIO::call_on_gpio_down()
{
    for(auto it : _attached_on_down)
        if(it)
            it();

    remove_called_one_shot(_attached_on_down, _attached_on_down_one_shot);
}

void GPIO::call_on_gpio_up()
{
    for(auto it : _attached_on_up)
        if(it)
            it();

    remove_called_one_shot(_attached_on_up, _attached_on_up_one_shot);
}


void GPIO::set_value(int val)
{_value = val;}

int GPIO::get_id() const
{return _id;}

int GPIO::get_value() const
{return _value;}
