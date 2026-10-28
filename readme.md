# Sustainable Energy: Wind Generation Profiles and Solar Comparison

## Description
In this report, we:
 1. Define a SeaTitan power curve function.
 2. Fetch wind data from the NLR WIND Toolkit for Altamont Pass (37.7458°N, 121.6583°W) at 100m height.
 3. Convert the wind speed data to 125m height using a power law with an exponent of 0.10.
 4. Convert the wind speed data to power output using the SeaTitan power curve.
 5. Plot a heat map of the wind power output
 6. Fetch solar data from the NLR PVWatts API for the same location
 7. Plot a heat map of the solar power output

Everything is detailed and collated in the [PDF report](./report.pdf).

***

## Directions
If downloading the code and running it, please do the following:
 1. Create a .env file in the same directory with the following content:
    1. `NLR_API_KEY=YOUR_API_KEY_HERE`
    2. `NLR_EMAIL=YOUR_EMAIL_HERE`
 2. Install the required packages (if not already installed):
    `pip install numpy pandas matplotlib seaborn requests python-dotenv`
 3. Run the script:
    `python3 main.py`

 Please also note, we are using the NLR WIND Toolkit and PVWatts API, which require an API key and email for access. 
 You can obtain these by registering at [NRL Developer Network](https://developer.nlr.gov/).

 We are also using a Python virtual environment to manage dependencies. 
 If you are not familiar with this, please refer to the Python documentation on [virtual environments](https://docs.python.org/3/library/venv.html).

***

## License
MIT License

Copyright (c) 2026 Joshan Singh Rai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
