# python 3
import os  # to get files names from a directory
import sys  # for python script arguments
import datetime # date in file name for versioning

def find_class_struct(file_name, path_files="./", verbose=True):
    """Find class or struct from a .hpp/.h file"""
    result = []
    with open(path_files+file_name) as fp:              # open file
        record_lines = False
        for line in fp:
            if record_lines: # recording class lines
                result.append(line)
            details = line.split(" ")
            if "class" in details or "struct" in details: # start recording
                record_lines = True
                result.append(line)
            if line == "};\n": # end recording
                record_lines = False
    return result

def find_all_class_struct(files_names, path_files="./", verbose=True):
    result = []
    for name in files_names:
        if ".h" in name:
            result.extend(find_class_struct(name, path_files=path_files, verbose=verbose))
    return result

def find_namespace(file_name, path_files="./", verbose=True):
    """Find imported packages from a .go file"""
    result = []
    with open(path_files+file_name) as fp:              # open file
        for line in fp:
            details = line.split(" ")
            if len(details) >= 3 and "using" in details[0] and "namespace" in details[1]:
                result.append(details[2][:len(details[2])-2])
    return result

def find_all_namespaces(files_names, path_files="./", verbose=True):
    """List of imported lib from a list of files names"""
    result = []
    for name in files_names:
        if ".cpp" in name:
            result.extend(find_namespace(name, path_files=path_files, verbose=verbose))
    return list(set(result))

def find_includes(file_name, path_files="./", verbose=True):
    """Find imported packages from a .cpp file"""
    result = []
    with open(path_files+file_name) as fp:              # open file
        read_in_next_line = False
        for line in fp:
            details = line.split(" ")
            if len(details) >= 2 and "#include" in details[0] and "<" in details[1]:
                result.append(details[1][1:len(details[1])-1])
    return result

def find_all_includes(files_names, path_files="./", verbose=True):
    """List of imported lib from a list of files names"""
    result = []
    for name in files_names:
        if ".cpp" in name:
            result.extend(find_includes(name, path_files=path_files, verbose=verbose))
    return list(set(result))

def file_with_main(files_names, path_files="./"):
    """ Detect file with "func main()" """
    for name in files_names:                     # for each file name
        with open(path_files+name) as fp:        # open file
            for line in fp:
                if "main()" in line:             # if line contains "main()"
                    return name
    print("//main() was not found")
    return ""

def extract_lines_no_imports(file):
    """ Extract lines from a file, except includes and namespaces"""
    skip_next = False
    lines = []
    for line in file:
        details = line.split(" ")
        if "#include" in details:   # skip include
            pass
        elif "namespace" in details: # skip namespace
            pass
        else:
            lines.append(line)
    return lines

def glue_in_one_list(files, imports, file_main, path_files, namespaces, class_struct):
    """ Create a list with every lines contained in the files"""
    blob = []
    for include in imports:
        blob.append("#include <"+include+"\n")

    for namespace in namespaces:
        blob.append("using namespace "+namespace+";\n")

    for foo in class_struct: # for each class or struct
        for line in foo: # add each line
            blob.append(line)
        blob.append("\n")

    [blob.append(line) for line in extract_lines_no_imports(open(path_files+file_main))]  # file with main() goes first (arbitrary choice)
    for name in files:
        [blob.append(line) for line in extract_lines_no_imports(open(path_files+name)) if name != file_main and not ".h" in name]  # the other files

    return blob

def list_to_file(lines, path_output="./", file_output="defaultName.go"):
    """ Write a list to a file"""
    f = open(path_output+file_output,'w+')
    [f.write(line) for line in lines]
    f.close()

def cpp_files_list(path):
    """ List go files in a directory"""
    files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        if dirpath ==path: # remove this to explore recursively
            #print(dirpath, dirnames, filenames)
            files.extend(filenames)
    return [name for name in files if ".cpp" in name or ".h" in name or ".hpp" in name]

if __name__ == '__main__':
    if len(sys.argv) == 3:
        path_to_files = sys.argv[0]
        path_output = sys.argv[1]
        file_output = sys.argv[2]
    else:
        path_to_files = "../CG_VoxCodei/clion_prj/"
        path_output = "../CG_VoxCodei/versions/"
        d = datetime.datetime.now()
        file_output = "current_"+d.strftime('%Y-%m-%d_%H-%M')+".cpp"
    print("//path_to_files:", path_to_files)
    print("//path_output:  ", path_output)
    print("//file_output:  ", file_output)
    print("")

    files = cpp_files_list(path_to_files)
    print(files)
    includes = find_all_includes(files, path_files=path_to_files, verbose=False)
    class_and_structs = find_all_class_struct(files, path_files=path_to_files, verbose=False)
    namespaces = find_all_namespaces(files, path_files=path_to_files, verbose=False)
    file_main = file_with_main(files, path_files=path_to_files)
    #print("//main() in:", file_main)
    all_lines = glue_in_one_list(files, imports=includes, file_main=file_main, path_files=path_to_files, namespaces=namespaces, class_struct=class_and_structs)
    list_to_file(all_lines, path_output=path_output, file_output=file_output)

    [print(line) for line in all_lines]
# myscript.py | xsel -b
