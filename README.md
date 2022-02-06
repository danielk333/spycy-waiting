# spycy-waiting

A bit spycier way of procrastinating while waiting for time-consuming tasks to finish. 

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

There is a quite slow bash script in the repository called `example.sh`. Try waiting for it in a spycy way with

```bash
waiting ./example.sh
```

or more verbosly, picking the game as well

```bash
waiting -g space-invaders  -- ./example.sh
```