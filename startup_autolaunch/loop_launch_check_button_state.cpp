//TODO : compile it, check it

// Main program used at startup that launch progam we indicate in config file
#include <sys/wait.h>
#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>


int main(int argc, char* argv[])
{
    if(argc<3)
    {
        std::cerr<<"[-] Usage : "<<argv[0]<<" [program config file path] [command config file path]"<<std::endl;
        std::cerr<<"Program config file path file must contain the name of program to launch, it can vary through time"<<std::endl;
        std::cerr<<"Command config file path file must contain the initialization command and a command that output 0 or 1 in test or match mode, return separated"<<std::endl;
        return -1;
    }

    std::string initialization;
    std::string command;
    std::ifstream ifs(argv[2], std::ios::in);
    ifs>>initialization;
    ifs>>command;

    system(initialization);

    std::cout<<"Main loop is initialized"<<std::endl;

    int current_state = 0;
    while(true)
    {
        system((command+" > /tmp/robot_state").c_str());
        std::ifstream ifs("/tmp/gpio_state", std::ios::in);
        ifs>>current_state;
        remove("/tmp/gpio_state");

	    std::cout<<"Read "<<current_state<<" state"<<std::endl;
        if(current_state) // game mode => main program used
        {
            std::ifstream ifs(argv[1], std::ios::in);
            std::string program;
            ifs>>program;

            int pid = fork();
            if(pid < 0)
            {
                std::cerr<<"[-] Error during fork"<<std::endl;
                exit(-1);
            }
            else if(pid)
            {
                int status = 0;
                wait(&status);
                std::cout<<"[+] Program exited with status "<<status<<std::endl;
            }
            else
            {
                std::cout<<"[+] Executing subprogram "<<program<<std::endl;
                char* args[] = {program.c_str(), NULL};
                if(execv(program.c_str(), args) < 0)
                {
                    std::cerr<<"[-] Error during execl of "<<program<<std::endl;
                    exit(-1);
                }
            }
        }
        else
            usleep(400000);

        usleep(100000);
    }
}
