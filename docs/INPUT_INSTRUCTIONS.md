How to specify CSV input file
------

To analyze multiple tax filers, the user creates a csv file with the filers' data. Each row of the csv file represents a filer and each column represents a variable. Please note that the file should not have column headings and the year must be the same for all observations. The input file should have 28 columns in the following order:

1. RECID (ID for tax filer)
2. year
3. mstat (1 - single; 2 - married)
4. page (age of primary taxpayer)
5. sage (age of spouse)
6. dep13 (number of children under 13)
7. dep17 (number of children from 13 to 16)
8. dep18 (number of children from 17 to 18 AND from 19 to 24 and a full-time student)
9. otherdep (other dependents)
10. pwages (wage of primary taxpayer)
11. swages (wage of spouse)
12. dividends (dividend income)
13. intrec (interest received)
14. stcg (short term capital gains)
15. ltcg (long term capital gains)
16. businc (business income)
17. sstb (1 - business income from professional services business; 0 - business income not from professional pervices business)
18. w2paid (W-2 wages paid by business)
19. qualprop (filer's share of qualified property)
20. otherprop (other property income subject to NIIT)
21. nonprop (other non-property income)
22. pensions (taxable pensions)
23. gssi (gross social security benefits)
24. ui (unemployment insurance received)
25. proptax (real estate taxes paid)
26. otheritem (other itemized deductions subject to SALT cap, e.g. state and local taxes)
27. childcare (child care expenses)
28. mortgage (itemized deductions not subject to SALT cap, e.g. charitable contributions and home mortgage interest)


For example, a 50-year old single filer with 3 dependents under 13 who makes $50,000 per year could be represented by the following:

```
1,2019,1,50,0,3,0,0,0,50000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```
