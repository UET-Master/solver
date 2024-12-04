def main():
    cplus_file = 'examples/average.cpp'

    cplus_codes = list()
    with open(cplus_file, mode='r') as file:
        file_lines = file.readlines()
        cplus_codes = [line.strip() for line in file_lines]

    print(cplus_codes)

if '__main__' == __name__:
    main()