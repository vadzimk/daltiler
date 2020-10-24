##daltiler
`daltiler` is CLI executable application to extract product attributes from a pdf catalog of a specific format.  

It is intended to automate entry of data arriving from its supplier into the ERP system of their client who cannot obtain product and price data in machine readable format. 
 
Because the catalog is extensive it makes sense to use daltiler each time the catalog is updated.

###Requirements
- Java 8
- Windows 10, 64-bit
- System PATH variable set for Java runtime environment  

Java installation links:  
https://www.java.com/en/download/  
https://www.java.com/en/download/help/path.html


###Usage
Follow interactive input / output.

####Input
pdf file containing pages with tables from Daltile catalog

#### Output
product_table.csv - *structured data extracted from all fields of tables*   
target.csv - *client's template for upload in ERP*  
uom.csv - *another client's template containing units conversion for upload in ERP*  