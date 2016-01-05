# Main class for python simulator
import sys
import simulator


def run():
    hardware = simulator.Simulator(verbose, reset, gust, dataToUI)

    while 1:
        hardware.update()

    # Example calls:
    # hardware.getAWA()
    # hardware.getWindSpeed()


if __name__ == '__main__':
    try:
        verbose = reset = gust = dataToUI = False
        for arg in sys.argv:
            if arg == "--help":
                print "Sailing condition simulator for the UBC Sailbot Transat MCU"
                print "Usage instructions: 'python main.py <flags>'"
                print " Pass desired flags separated by spaces"
                print " -v : Verbose output"
                print " -r : Reset simulation"
                print " -g : Gust simulation enabled"
                print " -d : Send data to UI (do not use with Route Making)"
                sys.exit()
            if arg == "-v":
                verbose = True
            if arg == "-r":
                reset = True
            if arg == "-g":
                gust = True
            if arg == "-d":
                dataToUI = True
        sys.exit(run())
    except KeyboardInterrupt:
        print "\n Exit - Keyboard Interrupt"
