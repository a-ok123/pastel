// Copyright (c) 2016 The Zcash developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <atomic>
#include <string>

struct AtomicCounter {
    std::atomic<int> value;

    AtomicCounter() : value {0} { }

    void increment(){
        ++value;
    }

    void decrement(){
        --value;
    }

    int get(){
        return value.load();
    }
};

extern AtomicCounter transactionsValidated;
extern AtomicCounter ehSolverRuns;
extern AtomicCounter minedBlocks;

void ThreadShowMetricsScreen();

/**
 * Heart image: https://commons.wikimedia.org/wiki/File:Heart_coraz%C3%B3n.svg
 * License: CC BY-SA 3.0
 *
 * Rendering options:
 * Zcash: img2txt -W 50 -H 26 -f utf8 -d none -g 0.7 Z-yellow.orange-logo.png
 * Heart: img2txt -W 50 -H 26 -f utf8 -d none 2000px-Heart_corazón.svg.png
 */
const std::string METRICS_ART =
"                      [0;34;40m              [0m                  	                                                  \n"
"                  [0;34;40m                      [0m              	                                                  \n"
"               [0;34;40m           [0;31;40m.;tt;. [0;34;40m           [0m          	            [0;1;31;91;41m.;t:[0m                  [0;1;31;91;41m:t;.[0m            \n"
"            [0;34;40m        [0;31;40m:[0;30;41m8[0;1;30;90;43mSX8[0;1;33;93;43mS[0;33;5;43;103m;;;:::t[0;1;33;93;43m%[0;1;30;90;43m8@[0;31;5;40;100mS[0;31;40m;[0;34;40m        [0m        	       [0;1;31;91;41m.[0;31;5;41;101mX          ;[0;1;31;91;41mS[0m        [0;1;31;91;41mS[0;31;5;41;101m;          X[0;1;31;91;41m.[0m       \n"
"          [0;34;40m       [0;31;40mt[0;1;30;90;43m%X[0;1;33;93;43mt[0;33;5;43;103m%%ttt[0;1;30;90;43m@XXXX@[0;33;5;43;103m::[0;37;5;43;103mXXXX[0;1;33;93;43m%[0;1;30;90;43mX[0;31;40mS[0;34;40m       [0m      	     [0;1;31;91;41mt[0;31;5;41;101m.               X[0m    [0;31;5;41;101mX               .[0;1;31;91;41mt[0m     \n"
"         [0;34;40m      [0;31;40m8[0;1;30;90;43mS[0;1;33;93;43m;tttt%[0;33;5;43;103m%tt[0;1;30;90;41m8[0;34;40m    [0;31;40m@[0;33;5;43;103m:;::[0;37;5;43;103mXXXXX[0;37;43mS[0;33;5;40;100m8[0;31;40m [0;34;40m     [0m     	    [0;31;5;41;101mX                   [0;1;31;91;41mtt[0;31;5;41;101m                   X[0m    \n"
"        [0;34;40m     [0;31;40m%[0;1;30;90;43mS[0;1;33;93;43m:;;;;:[0;1;30;90;43mXXX@@[0;31;40m8[0;34;40m    [0;31;40mS[0;1;33;93;43m;[0;1;30;90;43m8[0;1;33;93;43m;;tt[0;33;5;43;103m;[0;37;5;43;103mXXXX[0;1;33;93;43m%[0;31;40m8[0;34;40m      [0m   	   [0;1;31;91;41m8[0;31;5;41;101m                                          [0;1;31;91;41m8[0m   \n"
"       [0;34;40m     [0;30;41m8[0;1;30;90;43mS[0;1;33;93;43m.:::;;[0;1;30;90;43m%[0;34;40m                 [0;1;33;93;43mS[0;33;5;43;103m:[0;37;5;43;103mXXXXX[0;1;30;90;43mX[0;32;40m [0;34;40m     [0m  	   [0;31;5;41;101m                                            [0m   \n"
"      [0;34;40m     [0;1;30;90;41m8[0;1;31;91;43m8[0;1;33;93;43m....:::[0;1;30;90;43m%[0;34;40m                 [0;1;33;93;43m%[0;33;5;43;103m;::[0;37;5;43;103mXXXX[0;1;30;90;43m@[0;34;40m     [0m  	   [0;31;5;41;101m                                            [0m   \n"
"     [0;34;40m     [0;31;40mS[0;1;31;91;43m8888[0;1;33;93;43m....:[0;1;30;90;43m%[0;31;40m;;;;;;;;; [0;34;40m     [0;32;40m [0;33;5;40;100m8[0;33;5;43;103mt;;;::[0;37;5;43;103mXXX[0;33;5;40;100m8[0;34;40m     [0m 	   [0;31;5;41;101m                                            [0m   \n"
"     [0;34;40m    [0;32;40m [0;31;43mS[0;1;31;91;43m888888[0;1;33;93;43m...:::;;;;t[0;1;30;90;43mX[0;31;40m8 [0;34;40m    [0;31;40m;[0;1;30;90;43mX[0;33;5;43;103mtt;;;;;::[0;37;5;43;103mX[0;33;5;43;103mS[0;31;40m.[0;34;40m     [0m	   [0;31;5;41;101m.                                          .[0m   \n"
"    [0;34;40m     [0;31;40mt[0;1;31;91;43m888888888[0;1;33;93;43m....::::[0;33;41m8[0;31;40m [0;34;40m     [0;31;40m@[0;1;33;93;43m:[0;33;5;43;103mttttt;;;;:::[0;31;5;40;100mX[0;34;40m     [0m	   [0;1;31;91;41m%[0;31;5;41;101m                                          [0;1;31;91;41m%[0m   \n"
"    [0;34;40m     [0;31;40m8[0;1;31;91;43m88888888888[0;1;33;93;43m...:[0;1;30;90;43mS[0;31;40mS[0;34;40m     [0;31;40m [0;1;30;90;43m%[0;1;33;93;43mt%[0;33;5;43;103m%%ttttt;;;;:[0;1;30;90;43mX[0;34;40m     [0m	    [0;31;5;41;101m%                                        %[0m    \n"
"    [0;34;40m     [0;31;40m8[0;1;31;91;43m8888888888888[0;1;33;93;43m.[0;1;30;90;43mt[0;31;40m.[0;34;40m     [0;31;40m;[0;1;30;90;43mS[0;1;33;93;43mtttt%[0;33;5;43;103m%%ttttt;;;[0;1;30;90;43mS[0;34;40m     [0m	     [0;31;5;41;101m%                                      %[0m     \n"
"    [0;34;40m     [0;31;40mt[0;1;31;91;43m888888888888[0;1;30;90;43mS[0;1;30;90;41m8[0;34;40m      [0;31;40m8[0;1;30;90;43mX[0;1;33;93;43m;;;tttt%[0;33;5;43;103m%%tttt;;[0;31;5;40;100m@[0;34;40m     [0m	      [0;1;31;91;41m@[0;31;5;41;101m                                    [0;1;31;91;41m@[0m      \n"
"     [0;34;40m    [0;31;40m [0;31;43m@[0;1;31;91;43m8888888888[0;1;30;90;43m%[0;31;40m%[0;34;40m     [0;31;40m%[0;1;30;90;43m%[0;1;33;93;43m::::;;;tttt%[0;33;5;43;103m%%ttt[0;1;33;93;43mt[0;31;40m.[0;34;40m     [0m	        [0;31;5;41;101mS                                S[0m        \n"
"     [0;34;40m     [0;31;40mS[0;31;43mtt[0;1;31;91;43m8888888[0;31;43m8[0;31;40m.[0;34;40m      [0;31;40m%SSSSSSSSS[0;1;30;90;43mS[0;1;33;93;43mtttt%[0;33;5;43;103m%%t[0;31;5;40;100mX[0;34;40m     [0m 	          [0;31;5;41;101mS                            S[0m          \n"
"      [0;34;40m     [0;30;41m8[0;31;43mttt[0;1;31;91;43m8888[0;31;43mS[0;34;40m                  [0;1;30;90;43m%[0;1;33;93;43m;;tttt[0;33;5;43;103m%[0;1;30;90;43mS[0;31;40m [0;34;40m     [0m 	            [0;31;5;41;101m@                        @[0m            \n"
"      [0;34;40m      [0;31;40m8[0;31;43m%ttt[0;1;31;91;43m88[0;31;43mS[0;34;40m                  [0;1;30;90;43m%[0;1;33;93;43m;;;;tt[0;1;30;90;43m%[0;31;40m [0;34;40m     [0m  	              [0;1;31;91;41m8[0;31;5;41;101m                    [0;1;31;91;41m8[0m              \n"
"       [0;34;40m      [0;31;40m%[0;31;43m8ttttt@@@XXX[0;31;40m@[0;34;40m    [0;31;40m%[0;1;30;90;43m%%%%%%S[0;1;33;93;43m::;;[0;1;30;90;43mX[0;31;40m8[0;34;40m      [0m   	                [0;1;31;91;41m%[0;31;5;41;101m.              .[0;1;31;91;41m%[0m                \n"
"         [0;34;40m      [0;31;40m8[0;31;43m8tttt[0;1;31;91;43m88888[0;31;40m8[0;34;40m    [0;31;40mX[0;1;31;91;43m8888[0;1;33;93;43m....:[0;1;30;90;43mS[0;1;30;90;41m8[0;31;40m [0;34;40m      [0m    	                  [0;1;31;91;41m.[0;31;5;41;101m;          ;[0;1;31;91;41m.[0m                  \n"
"          [0;34;40m       [0;31;40mt[0;1;30;90;41m8[0;31;43m@ttt[0;1;31;91;43m888[0;31;43m@[0;33;41m88[0;31;43m88@[0;1;31;91;43m888888[0;1;30;90;43mS[0;31;43m8[0;31;40mS[0;34;40m       [0m      	                     [0;31;5;41;101mt      t[0m                     \n"
"            [0;34;40m        [0;31;40m:8[0;33;41m8[0;31;43m8St[0;1;31;91;43m8888888[0;1;30;90;43m%[0;31;43mS8[0;30;41m8[0;31;40m;[0;34;40m        [0m        	                       [0;31;5;41;101mS  S[0m                       \n"
"              [0;34;40m           [0;31;40m .;tt;: [0;34;40m           [0m          	                                                  \n"
"                 [0;34;40m                        [0m             	                                                  \n"
"                      [0;34;40m              [0m                  	                                                  ";

const std::string OFFSET = "        ";
