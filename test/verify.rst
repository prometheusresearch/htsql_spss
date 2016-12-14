Setup::

    >>> from htsql import HTSQL
    >>> from htsql.ctl.request import Request
    >>> db = HTSQL('pgsql:htsql_spss_test', {'htsql_spss': None})
    >>> from savReaderWriter import SavReader
    >>> import traceback

    >>> def run_query(query, output_path='sandbox/output'):
    ...     request = Request.prepare(method='GET', query=query)
    ...     response = request.execute(db)
    ...     if response.exc_info:
    ...         print ''.join(traceback.format_exception(*response.exc_info))
    ...     else:
    ...         with open(output_path, 'wb') as output:
    ...             output.write(response.body)
    
Check individual table::

    >>> run_query("/individual.sort(id){id(), *} /:spss", output_path='sandbox/individual.sav')
    >>> with SavReader('sandbox/individual.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'individual.id', 'individual.code', 'individual.sex']
    ['Q64H3201', 1.0, 'Q64H3201', 'male']
    ['W19K8934', 2.0, 'W19K8934', 'female']
    ['B78M1629', 3.0, 'B78M1629', 'female']
    ['K24T0567', 4.0, 'K24T0567', 'male']
    ['U40L3956', 5.0, 'U40L3956', 'female']
    ['M20H6038', 6.0, 'M20H6038', 'female']
    ['W34P094800000', 7.0, 'W34P094800000', 'male']
    ['S12T4027', 8.0, 'S12T4027', 'male']
    ['B39J6014', 9.0, 'B39J6014', 'male']
    ['R99D0886', 10.0, 'R99D0886', 'male']

    >>> run_query("/individual{code-, sex} /:spss", output_path='sandbox/individual.sav')
    >>> with SavReader('sandbox/individual.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['individual.code', 'individual.sex']
    ['W34P094800000', 'male']
    ['W19K8934', 'female']
    ['U40L3956', 'female']
    ['S12T4027', 'male']
    ['R99D0886', 'male']
    ['Q64H3201', 'male']
    ['M20H6038', 'female']
    ['K24T0567', 'male']
    ['B78M1629', 'female']
    ['B39J6014', 'male']

    >>> run_query("/individual{code, code, code} /:spss", output_path='sandbox/individual.sav')
    >>> with SavReader('sandbox/individual.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['individual.code', 'individual.code_1', 'individual.code_2']
    ['B39J6014', 'B39J6014', 'B39J6014']
    ['B78M1629', 'B78M1629', 'B78M1629']
    ['K24T0567', 'K24T0567', 'K24T0567']
    ['M20H6038', 'M20H6038', 'M20H6038']
    ['Q64H3201', 'Q64H3201', 'Q64H3201']
    ['R99D0886', 'R99D0886', 'R99D0886']
    ['S12T4027', 'S12T4027', 'S12T4027']
    ['U40L3956', 'U40L3956', 'U40L3956']
    ['W19K8934', 'W19K8934', 'W19K8934']
    ['W34P094800000', 'W34P094800000', 'W34P094800000']


Check sample table::

    >>> run_query("/sample.sort(id) /:spss", output_path='sandbox/sample.sav')
    >>> with SavReader('sandbox/sample.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['sample.id', 'sample.sample_type__id', 'sample.individual_id', 'sample.code', 'sample.contaminated', 'sample.date_collected', 'sample.time_collected', 'sample.date_time_collected']
    [1.0, 1.0, 3.0, 1.0, 'false', '2016-06-18', '1:02:03.004005', '2016-06-18 01:02:03']
    [2.0, 3.0, 2.0, 1.0, 'true', None, None, None]
    [3.0, 1.0, 2.0, 1.0, 'false', None, None, None]
    [4.0, 1.0, 2.0, 2.0, 'false', None, None, None]
    [5.0, 1.0, 9.0, 1.0, 'false', None, None, None]
    [6.0, 1.0, 9.0, 2.0, 'false', None, None, None]
    [7.0, 4.0, 9.0, 1.0, 'false', None, None, None]
    [8.0, 1.0, 7.0, 1.0, 'false', None, None, None]

Check tube table::

    >>> run_query("/tube.sort(id) /:spss", output_path='sandbox/tube.sav')
    >>> with SavReader('sandbox/tube.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['tube.id', 'tube.sample_id', 'tube.code', 'tube.volume_amount', 'tube.volume_unit', 'tube.location_memo']
    [1.0, 1.0, 1.0, 5.0, 'ml', 'Freezer 1']
    [2.0, 6.0, 1.0, 5.1, 'ml', 'Freezer 1']
    [3.0, 6.0, 2.0, None, 'ml', 'Freezer 2']
    [4.0, 7.0, 1.0, 3.0, 'ml', '']
    [5.0, 8.0, 1.0, 3.0, 'ml', '']

Check a nested query::

    >>> run_query("/sample.sort(id){*, /tube.sort(id)} /:spss", output_path='sandbox/sample_tube.sav')
    >>> with SavReader('sandbox/sample_tube.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['sample.id', 'sample.sample_type__id', 'sample.individual_id', 'sample.code', 'sample.contaminated', 'sample.date_collected', 'sample.time_collected', 'sample.date_time_collected', 'tube.id', 'tube.sample_id', 'tube.code', 'tube.volume_amount', 'tube.volume_unit', 'tube.location_memo']
    [1.0, 1.0, 3.0, 1.0, 'false', '2016-06-18', '1:02:03.004005', '2016-06-18 01:02:03', 1.0, 1.0, 1.0, 5.0, 'ml', 'Freezer 1']
    [2.0, 3.0, 2.0, 1.0, 'true', None, None, None, None, None, None, None, '', '']
    [3.0, 1.0, 2.0, 1.0, 'false', None, None, None, None, None, None, None, '', '']
    [4.0, 1.0, 2.0, 2.0, 'false', None, None, None, None, None, None, None, '', '']
    [5.0, 1.0, 9.0, 1.0, 'false', None, None, None, None, None, None, None, '', '']
    [6.0, 1.0, 9.0, 2.0, 'false', None, None, None, 2.0, 6.0, 1.0, 5.1, 'ml', 'Freezer 1']
    [None, None, None, None, '', None, None, None, 3.0, 6.0, 2.0, None, 'ml', 'Freezer 2']
    [7.0, 4.0, 9.0, 1.0, 'false', None, None, None, 4.0, 7.0, 1.0, 3.0, 'ml', '']
    [8.0, 1.0, 7.0, 1.0, 'false', None, None, None, 5.0, 8.0, 1.0, 3.0, 'ml', '']

Check a duplicate column name from a different table::

    >>> run_query("/sample.sort(id){id(), individual.code} /:spss", output_path='sandbox/sample_individual.sav')
    >>> with SavReader('sandbox/sample_individual.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'individual.code']
    ['B78M1629.blood.1', 'B78M1629']
    ['W19K8934.genetic.1', 'W19K8934']
    ['W19K8934.blood.1', 'W19K8934']
    ['W19K8934.blood.2', 'W19K8934']
    ['B39J6014.blood.1', 'B39J6014']
    ['B39J6014.blood.2', 'B39J6014']
    ['B39J6014.dna.1', 'B39J6014']
    ['W34P094800000.blood.1', 'W34P094800000']


Check a calculation::

    >>> run_query("/tube.sort(id){id(), volume_amount*2} /:spss", output_path='sandbox/calculation.sav')
    >>> with SavReader('sandbox/calculation.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'volume_amount_2']
    ['B78M1629.blood.1.1', 10.0]
    ['B39J6014.blood.2.1', 10.2]
    ['B39J6014.blood.2.2', None]
    ['B39J6014.dna.1.1', 6.0]
    ['W34P094800000.blood.1.1', 6.0]

Check a string column containing solely empty (zero-width) values::

    >>> run_query("/tube.filter(location_memo=''){id(), location_memo} /:spss", output_path='sandbox/empty.sav')
    >>> with SavReader('sandbox/empty.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'tube.location_memo']
    ['B39J6014.dna.1.1', '']

Check a string column containing solely null values::

    >>> run_query("/tube.filter(is_null(location_memo)){id(), location_memo} /:spss", output_path='sandbox/null.sav')
    >>> with SavReader('sandbox/null.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'tube.location_memo']
    ['W34P094800000.blood.1.1', '']

Check a query returning zero rows::

    >>> run_query("/tube.filter(false){id(), location_memo} /:spss", output_path='sandbox/no_rows.sav')
    >>> with SavReader('sandbox/no_rows.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'tube.location_memo']

Check a query containing long column name::

    >>> run_query("/demo_medical_history{id(), please_indicate_if_you_currently_have_or_have_circulatory} /:spss", output_path='sandbox/long_name.sav')
    >>> with SavReader('sandbox/long_name.sav') as reader:
    ...     print "Header:", reader.header
    ...     for line in reader:
    ...         print(line)
    Header: ['id__', 'demo_medical_history.please_indicate_if_you_currently_have_or_h']
