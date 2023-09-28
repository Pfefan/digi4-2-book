# Digi2book - book download

This project allows you to download books from Digi4School, a website where books are hosted online. It works by downloading all of the SVG files and then converting them to PDF.

## Features

Currently, it's only possible to download one selected book. However, the following features are planned for future implementation:

- Download only a selected page from a book
- Download a range of pages from a book
- Download all books that the user owns

## Installation

To run this program, you need to install some packages. Here's the installation process:

```bash
pip install pipwin
pipwin install cairocffi
pip install -r requirements.txt
```

This will install pipwin, use pipwin to install cairocffi, and then use pip to install the rest of the packages listed in the requirements.txt file.
Note if you are on linux, you dont need to install the pipwin libary, you just need to install the cairocffi libary
