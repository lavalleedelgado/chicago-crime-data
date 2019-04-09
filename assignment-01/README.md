# Crime in Chicago
## Assignment no. 1: Diagnostic

## Summary statistics

```

    primary_type                         2017    2018       change
--  ---------------------------------  ------  ------  -----------
 0  ARSON                                 426     373  -0.124413
 1  ASSAULT                             19112   20327   0.0635726
 2  BATTERY                             48639   49157   0.0106499
 3  BURGLARY                            12832   11553  -0.0996727
 4  CONCEALED CARRY LICENSE VIOLATION      71     133   0.873239
 5  CRIM SEXUAL ASSAULT                  1613    1665   0.0322381
 6  CRIMINAL DAMAGE                     28502   27394  -0.0388745
 7  CRIMINAL TRESPASS                    6711    6831   0.0178811
 8  DECEPTIVE PRACTICE                  17954   17770  -0.0102484
 9  GAMBLING                              190     194   0.0210526
10  HOMICIDE                             1427    1033  -0.276104
11  HUMAN TRAFFICKING                       8      15   0.875
12  INTERFERENCE WITH PUBLIC OFFICER     1080    1279   0.184259
13  INTIMIDATION                          153     162   0.0588235
14  KIDNAPPING                            193     167  -0.134715
15  LIQUOR LAW VIOLATION                  191     262   0.371728
16  MOTOR VEHICLE THEFT                 11224    9966  -0.112081
17  NARCOTICS                           11349   12640   0.113755
18  NON-CRIMINAL                           36      36   0
19  NON-CRIMINAL (SUBJECT SPECIFIED)        1       3   2
20  OBSCENITY                              85      86   0.0117647
21  OFFENSE INVOLVING CHILDREN           2178    2214   0.0165289
22  OTHER NARCOTIC VIOLATION               11       1  -0.909091
23  OTHER OFFENSE                       16727   16868   0.00842949
24  PROSTITUTION                          707     627  -0.113154
25  PUBLIC INDECENCY                        8      13   0.625
26  PUBLIC PEACE VIOLATION               1470    1359  -0.0755102
27  ROBBERY                             11728    9711  -0.171982
28  SEX OFFENSE                           979    1038   0.0602656
29  STALKING                              188     189   0.00531915
30  THEFT                               63333   63125  -0.00328423
31  WEAPONS VIOLATION                    4671    5404   0.156926


    community                 2017    2018        change
--  ----------------------  ------  ------  ------------
 0  ALBANY PARK               2425    2340  -0.0350515
 1  ARCHER HEIGHTS             828     832   0.00483092
 2  ARMOUR SQUARE              993     982  -0.0110775
 3  ASHBURN                   2335    2334  -0.000428266
 4  AUBURN GRESHAM            7407    7267  -0.018901
 5  AUSTIN                   15034   14633  -0.0266729
 6  AVALON PARK               1269    1178  -0.07171
 7  AVONDALE                  2293    2264  -0.0126472
 8  BELMONT CRAGIN            4545    4411  -0.0294829
 9  BEVERLY                    865     870   0.00578035
10  BRIDGEPORT                1484    1463  -0.0141509
11  BRIGHTON PARK             2228    2138  -0.040395
12  BURNSIDE                   361     383   0.0609418
13  CALUMET HEIGHTS           1308    1380   0.0550459
14  CHATHAM                   6351    6515   0.0258227
15  CHICAGO LAWN              5699    5549  -0.0263204
16  CLEARING                   851     889   0.0446533
17  DOUGLAS                   2541    2653   0.0440771
18  DUNNING                   1468    1495   0.0183924
19  EAST GARFIELD PARK        4669    4950   0.0601842
20  EAST SIDE                 1201    1073  -0.106578
21  EDGEWATER                 2581    2752   0.0662534
22  EDISON PARK                251     239  -0.0478088
23  ENGLEWOOD                 5877    6157   0.0476434
24  FOREST GLEN                534     482  -0.0973783
25  FULLER PARK                896     836  -0.0669643
26  GAGE PARK                 2258    2044  -0.0947741
27  GARFIELD RIDGE            1888    2066   0.0942797
28  GRAND BOULEVARD           3419    3206  -0.0622989
29  GREATER GRAND CROSSING    6396    6389  -0.00109443
30  HEGEWISCH                  650     601  -0.0753846
31  HERMOSA                   1483    1413  -0.0472016
32  HUMBOLDT PARK             7999    7932  -0.00837605
33  HYDE PARK                 1688    1884   0.116114
34  IRVING PARK               2951    2745  -0.0698068
35  JEFFERSON PARK            1034    1082   0.0464217
36  KENWOOD                   1494    1431  -0.0421687
37  LAKE VIEW                 5631    5782   0.0268158
38  LINCOLN PARK              4378    4883   0.115349
39  LINCOLN SQUARE            1970    1902  -0.0345178
40  LOGAN SQUARE              4920    4778  -0.0288618
41  LOOP                     10530   10606   0.00721747
42  LOWER WEST SIDE           2575    2351  -0.0869903
43  MCKINLEY PARK             1032     890  -0.137597
44  MONTCLARE                  590     592   0.00338983
45  MORGAN PARK               2069    2124   0.0265829
46  MOUNT GREENWOOD            544     485  -0.108456
47  NEAR NORTH SIDE          12173   12736   0.0462499
48  NEAR SOUTH SIDE           1907    1806  -0.0529628
49  NEAR WEST SIDE            8966    9228   0.0292215
50  NEW CITY                  4605    4095  -0.110749
51  NORTH CENTER              1410    1305  -0.0744681
52  NORTH LAWNDALE            8921    9074   0.0171505
53  NORTH PARK                 939     950   0.0117146
54  NORWOOD PARK              1050    1096   0.0438095
55  OAKLAND                    673     626  -0.0698366
56  OHARE                     1589    1476  -0.0711139
57  PORTAGE PARK              3308    3189  -0.0359734
58  PULLMAN                   1087    1176   0.0818767
59  RIVERDALE                 1323    1354   0.0234316
60  ROGERS PARK               4065    3697  -0.0905289
61  ROSELAND                  6853    6835  -0.00262659
62  SOUTH CHICAGO             4516    4326  -0.0420726
63  SOUTH DEERING             1722    1689  -0.0191638
64  SOUTH LAWNDALE            4504    4485  -0.00421847
65  SOUTH SHORE               8638    8501  -0.0158602
66  UPTOWN                    3531    3546   0.00424809
67  WASHINGTON HEIGHTS        3061    3167   0.0346292
68  WASHINGTON PARK           2735    2771   0.0131627
69  WEST ELSDON                999    1023   0.024024
70  WEST ENGLEWOOD            6890    7015   0.0181422
71  WEST GARFIELD PARK        5278    5597   0.0604396
72  WEST LAWN                 1847    1755  -0.0498105
73  WEST PULLMAN              3948    3981   0.00835866
74  WEST RIDGE                3463    3381  -0.0236789
75  WEST TOWN                 8197    7076  -0.136757
76  WOODLAWN                  3806    3388  -0.109827

```

## Descriptive statistics

```

```

1. **What type of blocks have reports of battery?** These seems to be areas in Chicago 


2. **What type of blocks have reports of homicide?** 

3. **Does that change over time in the data you collected?**

4. **What is the difference in blocks that report “Deceptive Practice” versus “Sex Offense”?** 

## Refuting Jacob Ringer


## Part IV



