#!/usr/bin/env python3

# LaTeX-Linter by Hundter Biede (hbiede.com)
# Version 1.0
# Checks LaTeX source files for common grammatical, syntactic, and spelling errors.
# WARNING: Does not serve as a replacement for full grammar/spell-checkers

# By default, this program checks `~/.latex-rules/` for rule-set files for the system,
# but this can be overridden by using the `--rules` argument
import re
import sys
from math import log10, floor
from os import listdir
from os.path import isfile, join, isdir, expanduser
from typing import List, Dict, Tuple

Pattern = type(re.compile('', 0))
Match = type(re.match(r'\s', ' '))
default_commands = r"begin|bibliography|cite|documentclass|end|figure|includegraphics|input|label|newcommand|table" \
                   r"|texttt|todo|(auto)?ref"


def get_all_files(directory: str) -> List[str]:
    """
    Searches the top level of a given directory and returns a list of all files in the given directory

    :param directory: str
        The directory to be searched
    :rtype: List[str]
    :return: A list of file paths in the given directory
    """
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    try:
        files.remove('.DS_Store')
    except ValueError:
        pass
    return list(map(lambda file: directory + file, files))


def read_rules() -> List[str]:
    """
    Searches the command line arguments for a rule-set and defaults to the user rule-set if none is given.
    Reads all rules and returns a set of rules to be processed.

    :rtype: List[str]
    :returns rulesList (List[str]) The list of rules as read in from the rule-sets to be used
    """

    # find rule set directory(ies) in the arguments
    rules_dirs = [i for i, arg in enumerate(sys.argv) if ['-r', '--rules'].__contains__(arg)]

    if len(rules_dirs) is 0:
        # Use default rule list
        rule_set_files = get_all_files(expanduser('~') + '/.latex-rules/')
    else:
        # Use the provided rule sets
        rule_set_files = []
        rules_dirs.reverse()
        for rule_index in rules_dirs:
            rule_set_files.extend(get_all_files(sys.argv[rule_index + 1]))
            rules_dirs.pop(0)
            sys.argv.pop(rule_index)
            sys.argv.pop(rule_index)  # repeat to also remove the directory associated with the command

    rules_list = []
    for file in rule_set_files:
        f = open(file, 'r')
        for line in f:
            rules_list.append(line.strip())
    return rules_list


def parse_rules(rule_list: List[str]) -> (Dict[Pattern, str], List[str]):
    """
    Take a list of rules strings in the form 'rule_pattern % RuleType: Reasoning' and parse it out to be used

    :param rule_list: List[str]
        A list of rules to be parsed and compiled to regex and reasonings
    :rtype: Tuple[Dict[Pattern, str], List[str]]
    :return: First, a dictionary of RegEx patterns to their reasonings, and then a list of commands to ignore
    """
    rule_mapping: Dict[Pattern, str] = {
        re.compile(
            r'(?<!(etc|seq))(?<!(al))(?<!(etal))\.\s+[a-z]'): 'Capitalization: Sentences start with capital letters'
    }
    commands_to_ignore = []
    surrounding_terms = {
        'Capitalization': r'\b',
        'Phrasing': r'\b',
        'Spelling': r'\b'
    }
    case_sensitivity_mapping = {
        'Capitalization': 0,
    }
    for rule_line in rule_list:
        if rule_line.startswith('#') or len(rule_line) is 0:
            continue
        try:
            rule_str, reasoning = rule_line.split("%", 1)
        except ValueError:
            print("The following line is malformed: %s" % rule_line, file=sys.stderr)
            continue
        rule_str = rule_str.strip().replace('$', r'\b')
        reasoning = reasoning.strip()
        if reasoning == 'ignoredCommand':
            commands_to_ignore.append(rule_str)
        else:
            surrounding_term = surrounding_terms.get(reasoning.split(':')[0].strip(), '')
            case_sensitivity = case_sensitivity_mapping.get(reasoning.split(':')[0].strip(),
                                                            re.IGNORECASE) + re.UNICODE + re.MULTILINE
            regex = re.compile(surrounding_term + rule_str.replace(' ', r'\s') + surrounding_term, case_sensitivity)
            rule_mapping[regex] = reasoning
    return rule_mapping, commands_to_ignore


def read_latex() -> Dict[str, List[str]]:
    """
    Reads all files given to the command arguments (after the rule set directories have been parsed out),
    reads their contents, and returns a dictionary of the file names mapped onto lines from that file as a list

    :rtype: Dict[str, List[str]]
    :return: A dictionary of the file name mapped onto lines from that file as a list
    """
    comment_regex = re.compile(r'(([^\\]%.*)|(^%.*))$')
    files_to_read = []
    for arg in sys.argv:
        if not arg.__contains__('.tex'):
            continue
        if isfile(arg):
            files_to_read.append(arg)
        elif isdir(arg):
            files_to_read.extend(get_all_files(arg))
        else:
            print("%s is an invalid argument" % arg, file=sys.stderr)

    file_lines = {}
    for file_name in files_to_read:
        file = open(file_name, 'r')
        single_file_lines = []
        for line in file:
            line = line.strip()
            if comment_regex.search(line):
                line = comment_regex.split(line)[0]
            single_file_lines.append(line)
        file_lines[file_name] = single_file_lines
    return file_lines


def test_line(line_to_test: str, rule_patterns: Dict[Pattern, str]) \
        -> List[Tuple[Pattern, Match]]:
    """
    Test a given string against all rule patters
    :param line_to_test: str
        The string to be tested against the RegEx patterns for a match
    :param rule_patterns: Dict[Pattern, str]
        A dictionary mapping the list of RegEx patterns onto their reasoning strings
    :rtype: List[Tuple[Pattern, Match]]
    :return: A list of rules broken and the Match objects that define the start and end points of the match in the test
        string
    """
    rules_broken = []
    for rule in rule_patterns:
        match = rule.search(line_to_test)
        if match is not None:
            rules_broken.append((rule, match))
    return rules_broken


def remove_commands(line: str, commands: Pattern) -> str:
    """
    Strip a LaTeX source string of commands defined as needing to be ignored
    :param line: str
        The LaTeX source string
    :param commands: Pattern
        The pattern compiled of all the commands to ignore
    :rtype: str
    :return: The source string, with the commands and their arguments removed
    """
    # noinspection RegExpRedundantEscape
    clear_of_french_spacing = re.search(r'\s[\.\?!,;:]', line) is None
    return_val = commands.sub('', line)
    if len(return_val) > 1 and clear_of_french_spacing:
        return_val = re.sub(r'[~\s]*(?=[.?!,;:])', '', return_val)
    return return_val


def remove_math(latex: Dict[str, List[str]]):
    """
    Removes all characters enclosed in a math block
    :param latex: Dict[str, List[str]]
        A mapping of file names onto a list of that file's lines
    """
    for file_name in latex:
        file = latex[file_name]
        math_mode: bool = False
        for i in range(len(file)):
            new_line = ''
            for c in file[i]:
                if c is '$':
                    math_mode = not math_mode
                elif not math_mode:
                    new_line += c
            file[i] = new_line
    return latex


def process_files(file_lines: Dict[str, List[str]], rule_patterns: Dict[Pattern, str],
                  ignored_command_regex: Pattern) -> List[str]:
    """
    Takes all the lines that need to be checked, removes any math blocks and commands, then checks them for broken
        rules (including those that span multiple lines)
    :param file_lines: Dict[str, List[str]]
        A mapping of file names onto a list of that file's lines
    :param rule_patterns: Dict[Pattern, str]
        A dictionary mapping the list of RegEx patterns onto their reasoning strings
    :param ignored_command_regex:
        The pattern compiled of all the commands to ignore
    :rtype: List[str]
    :return: A list of strings reporting each rule broken formatted for output
    """
    remove_math(file_lines)
    errors = []
    for file_name in file_lines:
        file = file_lines[file_name]
        format_length = str(floor(log10(len(file)) + 1))
        rules_broken = dict()
        for i in range(len(file)):
            first_line = remove_commands(file[i], ignored_command_regex)
            if first_line == '':
                continue
            second_line = remove_commands('' if i is len(file) - 1 else '\n' + file[i + 1].strip(),
                                          ignored_command_regex)
            combined_line = first_line + second_line
            rule_broken_on_line = test_line(combined_line, rule_patterns)
            for rule_broken, error in rule_broken_on_line:
                try:
                    line_break_index = combined_line.index('\n')
                except ValueError:
                    line_break_index = len(combined_line)
                error_line = i + 1 if error.span()[0] < line_break_index else i + 2
                if error != '' and (len(errors) is 0 or not rules_broken.get(error_line, []).__contains__(rule_broken)):
                    error_string = combined_line[max(0, min(line_break_index, error.span()[0] - 5)):
                                                 min(len(combined_line), error.span()[1] + 5)].strip().replace('\n',
                                                                                                               ' ')
                    errors.append(("%s:%0" + format_length + "d:(%s) - %s") %
                                  (file_name, error_line, error_string, rule_patterns[rule_broken]))
                    rules_broken_list = rules_broken.get(error_line, [])
                    if rules_broken_list:
                        rules_broken_list.append(rule_broken)
                    else:
                        rules_broken[error_line] = [rule_broken]
    return errors


def compile_command(commands: List[str]) -> Pattern:
    """
    Generates a pattern to be used in removing commands from LaTeX source lines
    :param commands: List[str]
        A list of command names (case-sensitive) to be ignored
    :rtype: Pattern
    :return: The compiled pattern
    """
    return re.compile(r'\\(' + '|'.join(commands) + r')(\[[^\]]*\])?{[^{}]*}')


if __name__ == '__main__':
    rules, ignored_commands = parse_rules(read_rules())
    if len(rules) is 0:
        print("Define some rules before using", file=sys.stderr)
        exit(-1)
    ignored_commands.extend(default_commands.split('|'))

    command_regex = compile_command(ignored_commands)

    rules_broken_report = process_files(read_latex(), rules, command_regex)
    for rule_reported in rules_broken_report:
        print(rule_reported)
    exit()
