# LaTeX Linter
The one downside of using [LaTeX](latex.org) (the world's superior typesetting language),
is that you may often miss out on common writing mistakes due to the primitive
grammar/spell-checkers in most text editors. This program aims to mitigate some of those
issues, while also allowing you to define style guide rules to improve consistency in your
organizations.

## How does it work?

The style checker is a Python script that seeks out files in directory ``~/.latex-rules/`.
Each file is a list of expressions, annotated with a justification and a type. The type
system is primarily to make the rule-set easier to read and the justifications easier to
understand, but one notable difference is that capitalization is case-sensitive, while the
rest are not. See the existing files or the following sections for examples.

## Rule Types
### Capitalization Errors

Capitalize expressions match whole words, and are case-sensitive. Such expressions are
designed to help maintain uniformity of capitalization of product and project names, like
iPod. They are automatically wrapped with "\b"s to ensure that only whole words are
matched.

```
(?<!(\. ))Internet                  % Capitalization: Don't capitalize internet if it's not the start of a sentence
[^egs]\. [[:lower:]]                % Capitalization: Sentences should start with a capital letter
\\(sub){0,}section\{[[:lower:]].*\} % Capitalization: Section titles should be capitalized
```


### Formatting Errors

Formatting errors include such issues as having an extra space before a closing quote or
using a less than symbol (a symbol that does not display properly in LaTeX).

```
\s--\s         % Formatting: the en-dash should be between numbers.
\s---\s        % Formatting: The em-dash should be right up against the words.
section \\ref  % Formatting: should have ~ between section and ref
\s''           % Formatting: Either you have a space before a closing quote or forgot to open a quote with back-ticks
[<>](?!=)      % Formatting: Should be \lt or \gt
```


### Phrasing Errors

Phrases match longer phrases such as "in a satisfactory manner" or "on a monthly basis".
As with capitalize expressions, they are transparently wrapped with "\b"s, but are not
case sensitive. Some phrases that are forbidden include double words.

```
I'll                          % Phrasing: Should be "I will"
I've                          % Phrasing: Should be "I have"
IPs                           % Phrasing: Should be "IP addresses"
[dw]on't                      % Phrasing: Should be "do not" or "will not"  
(is|are) (able to|capable of) % Phrasing: Should be "can" or "may"
```


### Spelling Errors

Spelling expressions are internally handled the same as phrasing errors. These are useful
for common misspellings or typo's.

```
hte      % Spelling: Misspelled
seperate % Spelling: Misspelled
taht     % Spelling: Misspelled
teh      % Spelling: Misspelled
til      % Spelling: Misspelled
```


### Syntax

Syntax expressions are matched exactly and are case-insensitive. Any regular expression
will do. As a hint, "\b" will match word boundaries, such as spaces or hyphens.

```
[0-9]%                          % Syntax: A number followed by a percent sign is rarely intended as a comment. Space it out if it is
\\url\{(?!http|ftp|rtsp|mailto) % Syntax: URLs should include a protocol (e.g. https://)
cf\.[^\\]                       % Syntax: cf. should get an escaped space "\ "
```


### Ignored Commands

Ignore the argument to this command. If only spell checkers were this cool. The internal
implementation of ignored commands is to "replace" them with a space before the rest of
the rules are checked, so it is possible that other rules may need to take this into
account. If a listed command takes multiple required arguments (arguments in curly
braces), only the first will be ignored, along with all optional arguments (arguments in
square brackets). Commands are treated as case sensative regex. The default commands that
get ignored by default are as follows:

```
begin           % ignoredCommand
bibliography    % ignoredCommand
cite            % ignoredCommand
documentclass   % ignoredCommand
end             % ignoredCommand
figure          % ignoredCommand
includegraphics % ignoredCommand
input           % ignoredCommand
label           % ignoredCommand
newcommand      % ignoredCommand
ref             % ignoredCommand
table           % ignoredCommand
texttt          % ignoredCommand
todo            % ignoredCommand
```


## Built-in checking

In addition to configurable rules, the style checker also seeks out common errors within
the LaTeX source itself:

  * an unescaped percent-sign immediately following a number is frequently an error.
  * a \cite{} tag should precede (not follow) a period.
  * a \cite{} tag should not be used obviously as a noun in the middle of a sentence.
  * Math mode between unescaped $'s is skipped.


## How do I use it?

To install locally:
`make install`

To run the script:
`latex-lint.py *.tex`

To use custom rules (must link to a directory containing only files with rule-sets an no
other files):
`latex-lint.py --rules /path/to/rules/directory/ *.tex`

You can add this repository to your own as a submodule (so that it will be available
wherever you clone your repo, while also keeping up-to-date on the latest changes with
this one) by adding the following to a `.gitmodules` file in the root of your repository:

```
[submodule "LaTeX-Linter"]
	path = LaTeX-Linter
	url = https://github.com/hbiede/LaTeX-Linter
```


## Limitations

This is not a proof-reader, editor, spell-checker, or grammar-checker. It is only capable
of following the limited rule set defined for it. It may not catch every mistake.

## Acknowledgments
This program's rough control-flow and the basis for the original rule-set are based on [a
program with the same end-goal created by Neil
Spring](https://github.com/nspring/style-check)
