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

    >>> run_query("/individual /:spss", output_path='sandbox/individual.sav')
    >>> with SavReader('sandbox/individual.sav') as reader:
    ...     for line in reader:
    ...         print(line)
    [1.0, 'Q64H3201']
    [2.0, 'W19K8934']
    [3.0, 'B78M1629']
    [4.0, 'K24T0567']
    [5.0, 'U40L3956']
    [6.0, 'M20H6038']
    [7.0, 'W34P0948']
    [8.0, 'S12T4027']
    [9.0, 'B39J6014']
    [10.0, 'R99D0886']

Check sample table::

    >>> run_query("/sample /:spss", output_path='sandbox/sample.sav')
    >>> with SavReader('sandbox/sample.sav') as reader:
    ...     for line in reader:
    ...         print(line)
    [1.0, 1.0, 3.0, 1.0, 'false', '2016-06-18', '1:02:03.004005', '2016-06-18 01:02:03']
    [2.0, 3.0, 2.0, 1.0, 'true', None, None, None]
    [3.0, 1.0, 2.0, 1.0, 'false', None, None, None]
    [4.0, 1.0, 2.0, 2.0, 'false', None, None, None]
    [5.0, 1.0, 9.0, 1.0, 'false', None, None, None]
    [6.0, 1.0, 9.0, 2.0, 'false', None, None, None]
    [7.0, 4.0, 9.0, 1.0, 'false', None, None, None]
    [8.0, 1.0, 7.0, 1.0, 'false', None, None, None]

Check tube table::

    >>> run_query("/tube /:spss", output_path='sandbox/tube.sav')
    >>> with SavReader('sandbox/tube.sav') as reader:
    ...     for line in reader:
    ...         print(line)
    [1.0, 1.0, 1.0, 5.0, 'ml', 'Freezer 1']
    [2.0, 6.0, 1.0, 5.0, 'ml', 'Freezer 1']
    [3.0, 6.0, 2.0, 3.0, 'ml', 'Freezer 2']

