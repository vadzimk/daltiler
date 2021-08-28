# daltiler
`daltiler` is a CLI executable application packaged with pyInstaller to extract product attributes from a pdf catalog of a specific format and to produce csv files required by the client.  

It is intended to automate entry of data arriving from its supplier into the ERP system of their client who cannot obtain product and price data in machine readable format. 
 
Because the catalog is extensive it makes sense to use `daltiler` each time the catalog is updated.

`daltiler` uses tabula-java as an engine for reading the pdf file one page at a time in several modes. It uses tabula-python as an interface and python as the language for the application.

[Runing Daltiler app!](Daltiler_ui.gif "Running Daltiler app")

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
Before running `daltiler2`, export tabula-template.json of the pdf catalog with the help of Tabula for Windows. Use autodetect tables to create template. Save template in the same directory with the program.
Follow interactive input/output instructions of the program.

## Input
pdf file containing pages with tables from Daltile catalog
tabula-template.json file

## Output
product_table.csv - *structured data extracted from all fields of tables*   
target.csv - *client's template for upload in ERP*  
uom.csv - *another client's template containing units conversion for upload in ERP*  

