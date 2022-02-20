# spycy-waiting

A bit spycier way of procrastinating while waiting for time-consuming tasks to 
finish. 

## Installation

```bash
pip install spycy-waiting
```

or

```bash
git clone git@github.com:danielk333/spycy-waiting.git
cd spycy-waiting
pip install .
```

## Usage

To use just type `waiting` before any bash command!

## Example

There is a quite slow bash script in the repository called `example.sh`. 
Try waiting for it in a spycy way with

```bash
waiting ./example.sh
```

or more verbosly, picking the game as well

```bash
waiting -g wordle -- ./example.sh
```

## Configuration

The games (most usefully the terminal colors) can be configured trough a config 
file located by default in `$HOME/.config/spycy_waiting.conf`. If the XDG
default configuration location is avalible that will be used instead.

The default configuration is:

```conf
[General]
text-color = 1, 0
title-color = 2, 0
help-color = 11, 0
default-background-color = 0

[Wordle]
correct-letter-color = 9, 11
correct-place-color = 9, 4
```