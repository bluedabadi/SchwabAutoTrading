# SchwabAutoTrading (SAT)
We automatically trade options via some simple algorithms and it's only applicable for Charles Schwab Accounts. 
The author is Lin with MathPhdTrading and she explains her algorithms more in details in 
her Youtube Channel: https://youtube.com/@mathphdtrading-sv2024?si=3MZf12bxZ4E5TL3x

## Installation

Before you follow the instruction below, you need to apply for a developer account from Schwab and then 
follow the instruction from Tyler Bowers's github code. Tyler Bower is the author of schwabdev, the Schwab API.
The code link is: https://github.com/tylerebowers/Schwab-API-Python. 
After you get your connection to Schwab account working, you should also put your APP key and APP secret to 
the Config class in configs/config.py.

Note: Always work under SchwabAutoTrading/, or the same level as README.md.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

You need to be in virtual environment to use pip. The following command creates a virtual environment myenv in
the current directory. You only run this when it is the first time to create a virtual environment.

```bash
python3 -m venv myenv
```

And then activate it:

```bash
source myenv/bin/activate
```

You may wish to deactivate it later by simply typing

```bash
deactivate
```

in your shell.
When it is your first time to create a virtual environment, you need to install the necessary
libraries before running the main file, you run:
```bash
pip3 install -r requirements.txt
```

Last, don't forget to add your python path in your .bashrc.

## Code Structure
Except test/ and data/, there are main.py plus 3 folders: configs, options and trading_algorithms. 
configs: stores all the constants and enum classes. This is where you should change your app 
key, app secret and account numbers. If you have different likings of expiration date and delta, you can 
change your STO_TRADING_SETTINGS. Ideally, after you modify all the necessary variables in configs.py, 
you can just run ```python3 main.py``` every day to trade. 
options: composed of basic classes like stocks, options and option_chains. 
trading: it deals with trading current positions of all accounts in trade_options.py; and it scan 
through a list of stocks and trade it if there are significant price changes. 
main.py: Run this every day to trade!!!!

## Note
If you have any questions about the code, please email me at MathPhdTrading@gmail.com. 
