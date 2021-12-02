from collections.abc import Hashable
import re
import sys
import os
import ast
import tokenize


def check_001(line_num, line):
    if len(line) > 79:
        return f'{line_num}001 Too long'
    return None


def check_002(line_num, line):
    if (len(line) - len(line.lstrip())) % 4:
        return f'{line_num}002 Indentation is not a multiple of four'
    return None


def check_003(line_num, line):
    if re.search(';', line):
        report_it = True
        m = re.search("'.+'", line)
        m2 = re.search('".+"', line)
        c = re.search('#', line)

        if m:
            r = m.span()
            if r[0] < line.index(';') < r[1]:
                report_it = False
        if m2:
            r2 = m2.span()
            if r2[0] < line.index(';') < r2[1]:
                report_it = False
        if c:
            r3 = c.span()
            if r3[0] < line.index(';'):
                report_it = False
        if report_it:
            return f'{line_num}003 Unnecessary semicolon'
    return None


def check_004(line_num, line):
    if re.search(".+#", line) and not re.search("  #", line):
        return f'{line_num}004 At least two spaces required before inline comments'
    return None


def check_005(line_num, line):
    if re.search("#.?TODO", line, re.IGNORECASE):
        return f'{line_num}005 TODO found'
    return None


def check_006(line_num, blanks):
    # print('Num of blanks', blanks)
    if blanks > 2:
        return f'{line_num}006 More than two blank lines used before this line'
    return None


def check_007(line_num, line):
    defect = False
    literal = "class"
    if re.search('class ', line):
        if re.search("class [ ]+", line):
            defect = True
    if re.search(' def ', line):
        if re.search(" def [ ]+", line):
            defect = True
            literal = "def"
    if defect:
        return f'{line_num}007 Too many spaces after \'{literal}\''
    return None


def check_008(line_num, line):
    tokens = line.split()
    # print(tokens)

    if 'class' in tokens:
        name_of_class = tokens[tokens.index('class') + 1].replace(':', '')
        # print(name_of_class)
        if name_of_class != name_of_class.upper() and name_of_class != name_of_class.lower() \
                and name_of_class[0] == name_of_class.capitalize()[0] and "_" not in name_of_class:
            pass
        else:
            return f'{line_num}008 Class name \'{name_of_class}\' should use CamelCase'
    return None


def check_009(line_num, line):
    tokens = line.split()
    # print(tokens)

    if 'def' in tokens:
        name_of_func = tokens[tokens.index('def') + 1]
        name_of_func = name_of_func[:name_of_func.index('(')]
        if name_of_func == name_of_func.lower() and re.match("^[A-Za-z0-9_]*$", name_of_func):
            pass
        else:
            return f'{line_num}009 Function name \'{name_of_func}\' should use snake_case'
    return None


def check_010(file_path):
    outcome = []
    for item in ast.walk(parse_file(file_path)):
        if isinstance(item, ast.FunctionDef):
            if item.args.args:
                for i in item.args.args:
                    if i.arg == i.arg.lower() and re.match("^[A-Za-z0-9_]*$", i.arg):
                        pass
                    else:
                        outcome.append(f'{i.lineno}010 Argument name \'{i.arg}\' should be snake_case')
    if len(outcome):
        return outcome
    return None


def check_011(file_path):
    outcome = []
    variable_names = []
    for item in ast.walk(parse_file(file_path)):
        if isinstance(item, ast.Name):
            # print(f'Found name on line: {item.lineno} args: {item.id}')
            if item.id == item.id.lower() and re.match("^[A-Za-z0-9_]*$", item.id):
                pass
            else:
                if item.id not in variable_names:
                    outcome.append(f'{item.lineno}011 Variable \'{item.id}\' in function should be snake_case')
                variable_names.append(item.id)
    if len(outcome):
        return outcome
    return None


def check_012(file_path):
    outcome = []
    for item in ast.walk(parse_file(file_path)):
        if isinstance(item, ast.FunctionDef):
            for i in ast.iter_child_nodes(item):
                if isinstance(i, ast.arguments):
                    if i.defaults:
                        for elem in i.defaults:
                            if isinstance(elem, ast.List) or isinstance(elem, ast.Dict) or isinstance(elem, ast.Set):
                                outcome.append(f'{elem.lineno}012 Default argument value is mutable')
    if len(outcome):
        return outcome
    return None


def parse_file(filename):
    with tokenize.open(filename) as f:
        return ast.parse(f.read(), filename=filename)


def code_check(some_path):
    if some_path.endswith(".py"):
        # print(f'Will check: {some_path}')
        check_file(some_path)
    else:
        for root, dirs, files in os.walk(some_path, topdown=False):
            # print(dirs)
            for name in files:
                if name.endswith(".py"):
                    # print(os.path.join(root, name), end=' ')
                    check_file(os.path.join(root, name))
            for name in dirs:
                # print(os.path.join(root, name))
                pass


def comp(o):
    return int(o.split()[0])


def check_file(file_path):
    results = []
    code_file = open(file_path, 'r')

    lines = code_file.readlines()
    line_number = 0
    blank_count = 0

    for line in lines:
        line_number += 1
        # print(blank_count)
        if len(line.strip()) > 0:
            error_report = check_001(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_002(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_003(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_004(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_005(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_006(line_number, blank_count)
            if error_report:
                results.append(error_report)
            error_report = check_007(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_008(line_number, line)
            if error_report:
                results.append(error_report)
            error_report = check_009(line_number, line)
            if error_report:
                results.append(error_report)
            blank_count = 0
        else:
            blank_count += 1

    error_report = check_010(file_path)
    if error_report:
        results += error_report
    error_report = check_011(file_path)
    if error_report:
        results += error_report
    error_report = check_012(file_path)
    if error_report:
        results += error_report

    code_file.close()

    results.sort(key=comp)
    # print(results)
    for err in results:
        formatted_err = err.split()[0]
        formatted_err = f'{formatted_err[:-3]}: S{formatted_err[-3:]}'
        # print(formatted_err)
        print(f'{file_path}: Line {formatted_err} {err[err.index(" ") + 1:]}')


def main():
    args = sys.argv
    # print(args[1])
    path_to_check = args[1]
    code_check(path_to_check)


if __name__ == "__main__":
    main()
