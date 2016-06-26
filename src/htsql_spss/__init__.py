#
# Copyright (c) 2016, Prometheus Research, LLC
#

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import datetime
import math
import os
import savReaderWriter
import tempfile

from htsql.core.adapter import Adapter, adapt, adapt_many, call
from htsql.core.addon import Addon
from htsql.core.cmd.summon import SummonFormat
from htsql.core.fmt.accept import Accept
from htsql.core.fmt.format import Format
from htsql.core.fmt.emit import EmitHeaders, Emit
from htsql.core.domain import Domain, BooleanDomain, NumberDomain, \
    FloatDomain, DecimalDomain, TextDomain, EnumDomain, DateDomain, \
    TimeDomain, DateTimeDomain, ListDomain, RecordDomain, UntypedDomain, \
    VoidDomain, IntegerDomain, Profile
from htsql.core.util import listof


SPSS_MAX_STRING_LENGTH = 32767
SPSS_MIME_TYPE = 'application/x-spss-sav'
SPSS_GREGORIAN_OFFSET = (datetime.datetime.fromtimestamp(0) - datetime.datetime(1582, 10, 14)).total_seconds()


class SPSSAddon(Addon):
    name = 'htsql_spss'
    hint = 'Basic support for IBM SPSS files'


class ToSPSS(Adapter):
    adapt(Domain)

    def __init__(self, domain, profiles):
        assert isinstance(domain, Domain)
        assert isinstance(profiles, listof(Profile)) and len(profiles) > 0
        self.domain = domain
        self.profiles = profiles
        self.width = 1

    def sav_config(self, data):
        sav_config = {}
        sav_config['var_names'] = []
        sav_config['var_types'] = {}
        sav_config['formats'] = {}
        sav_config['column_widths'] = {}
        return sav_config

    def __call__(self):
        return self

    def widths(self, data):
        if data is None:
            return [0]
        return [len(self.domain.dump(data))]


class RecordToSPSS(ToSPSS):
    adapt(RecordDomain)

    def __init__(self, domain, profiles):
        super(RecordToSPSS, self).__init__(domain, profiles)
        self.fields_to_spss = [
            to_spss(field.domain, profiles + [field])
            for field in domain.fields
        ]
        self.width = 0
        for field_to_spss in self.fields_to_spss:
            self.width += field_to_spss.width

    def sav_config(self, record):
        sav_config = super(RecordToSPSS, self).sav_config(record)

        if record is None:
            record = [None]*self.width

        for item, field_to_spss in zip(record, self.fields_to_spss):
            # import pdb; pdb.set_trace()

            field_sav_config = field_to_spss.sav_config(item)
            sav_config['var_names'].extend(field_sav_config['var_names'])
            sav_config['var_types'].update(field_sav_config['var_types'])
            sav_config['formats'].update(field_sav_config['formats'])
            sav_config['column_widths'].update(field_sav_config['column_widths'])

        return sav_config

    def cells(self, record):
        if not self.width:
            return
        if record is None:
            yield [None] * self.width
        else:
            cell_streams = [
                (field_to_spss.cells(field_value), field_to_spss.width)
                for field_value, field_to_spss in zip(record, self.fields_to_spss)
            ]
            is_done = False
            while not is_done:
                is_done = True
                row = []
                for cell_stream, field_width in cell_streams:
                    subrow = next(cell_stream, None)
                    if subrow is None:
                        subrow = [None] * field_width
                    else:
                        is_done = False
                    row.extend(subrow)
                if not is_done:
                    yield row

    def widths(self, data):
        widths = []
        if data is None:
            data = [None]*self.width
        for item, field_to_spss in zip(data, self.fields_to_spss):
            widths += field_to_spss.widths(item)
        return widths


class ListToSPSS(ToSPSS):
    adapt(ListDomain)

    def __init__(self, domain, profiles):
        super(ListToSPSS, self).__init__(domain, profiles)
        self.item_to_spss = to_spss(domain.item_domain, profiles)
        self.width = self.item_to_spss.width

    def sav_config(self, list_value):
        sav_config = super(ListToSPSS, self).sav_config(list_value)

        for item in list_value:
            item_sav_config = self.item_to_spss.sav_config(item)
            for var_name in item_sav_config['var_names']:
                if var_name not in sav_config['var_names']:
                    sav_config['var_names'].append(var_name)
            sav_config['var_types'].update(item_sav_config['var_types'])
            sav_config['formats'].update(item_sav_config['formats'])
            sav_config['column_widths'].update(item_sav_config['column_widths'])

        return sav_config

    def cells(self, list_value):
        if not self.width:
            return
        if list_value is not None:
            item_to_cells = self.item_to_spss.cells
            for item in list_value:
                for cell in item_to_cells(item):
                    yield cell

    def widths(self, data):
        widths = [0]*self.width
        if not data:
            data = [None]
        for item in data:
            widths = [max(width, item_width)
                      for width, item_width
                            in zip(widths, self.item_to_spss.widths(item))]
        return widths


class SimpleToSPSS(ToSPSS):
    adapt_many(
        UntypedDomain,
        TextDomain,
        EnumDomain,
    )

    def sav_config(self, data):
        sav_config = super(SimpleToSPSS, self).sav_config(data)

        profile = self.profiles[-1]
        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        # import pdb; pdb.set_trace()

        max_len = self.widths(data)[0]
        max_len = min(max_len, SPSS_MAX_STRING_LENGTH)

        sav_config['var_types'] = {column_id: max_len}
        sav_config['formats'] = {column_id: 'A' + str(max_len)}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        yield [value]


class BooleanToSPSS(ToSPSS):
    adapt(BooleanDomain)

    def sav_config(self, data):
        sav_config = super(BooleanToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 5}
        sav_config['formats'] = {column_id: 'A5'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        yield [self.domain.dump(value)]


class IntegerToSPSS(ToSPSS):
    adapt(IntegerDomain)

    def sav_config(self, data):
        sav_config = super(IntegerToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 0}
        sav_config['formats'] = {column_id: 'F40'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            yield [self.domain.dump(value)]


class FloatToSPSS(ToSPSS):
    adapt_many(FloatDomain)

    def sav_config(self, data):
        sav_config = super(FloatToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 0}
        sav_config['formats'] = {column_id: 'F40.16'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        if value is None or math.isinf(value) or math.isnan(value):
            yield [None]
        else:
            yield [value]


class DecimalToSPSS(ToSPSS):
    adapt(DecimalDomain)

    def sav_config(self, data):
        sav_config = super(DecimalToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 0}
        sav_config['formats'] = {column_id: 'F40.16'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        if value is None or not value.is_finite():
            yield [None]
        else:
            yield [value]


class DateToSPSS(ToSPSS):
    adapt(DateDomain)

    def sav_config(self, data):
        sav_config = super(DateToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 0}
        sav_config['formats'] = {column_id: 'DATE11'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            unix_timestamp = (value - datetime.date.fromtimestamp(0)).total_seconds()
            yield [unix_timestamp + SPSS_GREGORIAN_OFFSET]


class TimeToSPSS(ToSPSS):
    adapt(TimeDomain)

    def sav_config(self, data):
        sav_config = super(TimeToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 0}
        sav_config['formats'] = {column_id: 'TIME10'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            # value is a datetime.time object
            seconds = value.hour * 3600 + value.minute * 60 + value.second + value.microsecond / 1.0e6
            yield [seconds]


class DateTimeToSPSS(ToSPSS):
    adapt(DateTimeDomain)

    def sav_config(self, data):
        sav_config = super(DateTimeToSPSS, self).sav_config(data)

        column_id = '__'.join(p.tag for p in self.profiles)

        sav_config['var_names'] = [column_id]
        sav_config['var_types'] = {column_id: 0}
        sav_config['formats'] = {column_id: 'DATETIME22'}
        sav_config['column_widths'] = {column_id: 10}

        return sav_config

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            unix_timestamp = (value - datetime.datetime.fromtimestamp(0)).total_seconds()
            yield [unix_timestamp + SPSS_GREGORIAN_OFFSET]


to_spss = ToSPSS.__invoke__  # pylint: disable=invalid-name


def make_name(meta):
    filename = None
    if meta.header:
        filename = meta.header.encode('utf-8')
    if not filename:
        filename = 'data'
    filename = filename.replace('\\', '\\\\').replace('"', '\\"')
    return filename


class SPSSFormat(Format):
    pass


class SummonSPSS(SummonFormat):
    call('spss')
    format = SPSSFormat


class AcceptSPSS(Accept):
    call(SPSS_MIME_TYPE)
    format = SPSSFormat


class EmitSPSSHeaders(EmitHeaders):
    adapt(SPSSFormat)

    content_type = SPSS_MIME_TYPE
    file_extension = 'sav'

    def __call__(self):
        yield (
            'Content-Type',
            self.content_type,
        )
        yield (
            'Content-Disposition',
            'attachment; filename="%s.%s"' % (
                make_name(self.meta),
                self.file_extension,
            ),
        )


class EmitSPSS(Emit):
    adapt(SPSSFormat)

    def __call__(self):
        product = to_spss(self.meta.domain, [self.meta])
        output = StringIO()
        self.render(output, product)
        yield output.getvalue()

    def render(self, stream, product):
        output_file, output_path = tempfile.mkstemp(suffix='.sav')

        try:
            sav_config = product.sav_config(self.data)

            # import pdb; pdb.set_trace()

            writer_kwargs = {
                'savFileName': output_path,
                'varNames': sav_config['var_names'],
                'varTypes': sav_config['var_types'],
                'formats': sav_config['formats'],
                'columnWidths': sav_config['column_widths'],
                'ioUtf8': True
            }

            with savReaderWriter.SavWriter(**writer_kwargs) as writer:
                for record in product.cells(self.data):
                    # import pdb; pdb.set_trace()
                    writer.writerow(record)

            with open(output_path, 'rb') as output_file:
                while True:
                    chunk = output_file.read(1024*1024)
                    if chunk:
                        stream.write(chunk)
                    else:
                        break

        finally:
            os.remove(output_path)
