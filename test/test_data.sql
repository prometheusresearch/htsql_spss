COPY individual (id, code,sex) FROM stdin DELIMITER ',';
1,Q64H3201,male
2,W19K8934,female
3,B78M1629,female
4,K24T0567,male
5,U40L3956,female
6,M20H6038,female
7,W34P094800000,male
8,S12T4027,male
9,B39J6014,male
10,R99D0886,male
\.

COPY sample_type (id, code, title) FROM stdin DELIMITER ',';
1,blood,Whole Blood
2,wb-dna,Whole Blood DNA
3,genetic,Genetic
4,dna,DNA
5,rna,RNA
6,pl,Plasma
7,skin,Skin
8,urine,Urine
9,feces,Feces
10,hair,Hair
11,cp-dna,Cell Line DNA
12,lcl,Lymphoblastoid Cell Lines
13,spit-dna,Saliva Derived DNA
14,cpl,CPL
15,ep-dna,epDNA
16,ep-pl,epPlasma
17,fwb,fwb
18,pbmc,pbmc
19,ssc-kit,SSC
20,svip-kit,SVIP
21,wb,Whole Blood
\.

COPY sample (id, sample_type__id, individual_id, code, contaminated, date_collected, time_collected, date_time_collected) FROM stdin DELIMITER ',';
1,1,3,1,false,2016-06-18,01:02:03.004005,2016-06-18 01:02:03.004005
2,3,2,1,true,\N,\N,\N
3,1,2,1,false,\N,\N,\N
4,1,2,2,false,\N,\N,\N
5,1,9,1,false,\N,\N,\N
6,1,9,2,false,\N,\N,\N
7,4,9,1,false,\N,\N,\N
8,1,7,1,false,\N,\N,\N
\.

COPY tube (id, sample_id, code, volume_amount, volume_unit, location_memo) FROM stdin DELIMITER ',';
1,1,1,5.0,ml,Freezer 1
2,6,1,5.1,ml,Freezer 1
3,6,2,\N,ml,Freezer 2
4,7,1,3,ml,
5,8,1,3,ml,\N
\.
