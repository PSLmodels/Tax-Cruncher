How to specify CSV input file
------

To analyze multiple tax filers, the user must specify a csv file with the filers' data. Each row of the csv file represents a filer and each column represents a variable. The file should **not** have column headings and must be **comma-delimited**. 

The input file should have 24 columns in the following order:

1. RECID (ID for tax filer)
2. year
3. mstat (1 - single; 2 - joint (married); 6 - seperate (married); 8 - dependent)
4. page (age of primary taxpayer)
5. sage (age of spouse)
6. depx (number of dependents)
7. dep13 (number of children under 13)
8. dep17 (number of children under 17)
9. dep18 (number of qualifying children for EITC)
10. pwages (wage of primary taxpayer)
11. swages (wage of spouse)
12. dividends (dividend income)
13. intrec (interest received)
14. stcg (short term capital gains)
15. ltcg (long term capital gains)
16. otherprop (other property income subject to NIIT)
17. nonprop (other non-property income)
18. pensions (taxable pensions)
19. gssi (gross social security benefits)
20. ui (unemployment insurance)
21. proptax (real estate taxes paid)
22. otheritem (other itemized deductions)
23. childcare (child care expenses)
24. mortgage (deductions not included in 'otheritem')

For example, a 50-year old single filer with 3 dependents under 13 who makes $50,000 per year could be represented by the following:

```
1,2019,1,50,0,3,3,3,3,50000,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```
