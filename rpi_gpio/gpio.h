#ifndef GPIO_H
#define GPIO_H


#include <functional>
#include <vector>


typedef std::function<void()> _callback;

class GPIO
{
    public:
        GPIO(int id=-1, int initial_value=-1);

        void add_attached_on_gpio_change(const _callback& callback, bool one_shot = false);
        void add_attached_on_gpio_down(const _callback& callback, bool one_shot = false);
        void add_attached_on_gpio_up(const _callback& callback, bool one_shot = false);

        void clean_on_gpio_change();
        void clean_on_gpio_down();
        void clean_on_gpio_up();
        void clean_callbacks();

        void call_on_gpio_change();
        void call_on_gpio_down();
        void call_on_gpio_up();

        void set_value(int val);

        int get_id() const;
        int get_value() const;


    private:
        int _id, _value;

        std::vector<_callback> _attached_on_change;
        std::vector<_callback> _attached_on_down;
        std::vector<_callback> _attached_on_up;

        std::vector<size_t> _attached_on_change_one_shot;
        std::vector<size_t> _attached_on_down_one_shot;
        std::vector<size_t> _attached_on_up_one_shot;

        void remove_called_one_shot(std::vector<_callback>& callbacks, std::vector<size_t>& one_shot_index);
};


#endif
