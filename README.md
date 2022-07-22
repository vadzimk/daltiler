# daltiler

## Overview
**daltiler** is a desktop GUI application to automate product data entry from pdf catalogue into ERP for one particular vendor.  
Because the PDF catalog is also a price-list, **daltiler** is used each time PDF catalog is updated.

### **daltiler** project uses 
- tabula-java as an engine for text extraction from PDF
- tabula-python as an interface to python language
- Python and Pandas for data transformation into client required shape
- Qt for python as GUI library
- Qt threads to separate GUI from background process
- Python threads and atomic queue to speed up background I/O bound processing


![Dailtiler ui final](running.png "Daltiler ui final")
![Runing Daltiler app](Daltiler_ui.gif "Running Daltiler app")

## Requirements
- Java 8
- Windows 10, 64-bit
- System PATH variable set for Java runtime environment
- Tabula

Java installation links:  
https://www.java.com/en/download/  
https://www.java.com/en/download/help/path.html
Tabula installation link:  
https://tabula.technology/

## Usage
Before running **daltiler2**, export tabula-template.json of the pdf catalog with the help of Tabula for Windows. Use autodetect tables to create tabula-template.json. Save template in the same directory with the program.


## Input
- pdf file containing pages with tables from Daltile catalog
- tabula-template.json file

## Output
product_table.csv - *structured data extracted from all fields of tables*   
target.csv - *client's template for ERP*  
uom.csv - *another client's template containing units conversion for ERP* 
