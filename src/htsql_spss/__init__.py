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
    VoidDomain, OpaqueDomain, IntegerDomain, Profile
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

    def __call__(self):
        return self

    def var_names(self):
        return [self.profiles[-1].tag]

    def var_types(self, rows):
        raise NotImplementedError

    def formats(self, rows):
        raise NotImplementedError

    def column_widths(self):
        profile = self.profiles[-1]
        return {profile.tag: 10}

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            yield [self.domain.dump(value)]


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

    def var_names(self):
        row = []
        for field_to_spss in self.fields_to_spss:
            row.extend(field_to_spss.var_names())
        return row

    def var_types(self, rows):
        types = {}
        for field_to_spss in self.fields_to_spss:
            types.update(field_to_spss.var_types(rows))
        return types

    def formats(self, rows):
        formats = {}
        for field_to_spss in self.fields_to_spss:
            formats.update(field_to_spss.formats(rows))
        return formats

    def column_widths(self):
        widths = {}
        for field_to_spss in self.fields_to_spss:
            widths.update(field_to_spss.column_widths())
        return widths

    def cells(self, value):
        if not self.width:
            return
        if value is None:
            yield [None] * self.width
        else:
            streams = [
                (field_to_spss.cells(item), field_to_spss.width)
                for item, field_to_spss in zip(value, self.fields_to_spss)
            ]
            is_done = False
            while not is_done:
                is_done = True
                row = []
                for stream, width in streams:
                    subrow = next(stream, None)
                    if subrow is None:
                        subrow = [None] * width
                    else:
                        is_done = False
                    row.extend(subrow)
                if not is_done:
                    yield row


class ListToSPSS(ToSPSS):
    adapt(ListDomain)

    def __init__(self, domain, profiles):
        super(ListToSPSS, self).__init__(domain, profiles)
        self.item_to_spss = to_spss(domain.item_domain, profiles)
        self.width = self.item_to_spss.width

    def var_names(self):
        return self.item_to_spss.var_names()

    def var_types(self, rows):
        return self.item_to_spss.var_types(rows)

    def formats(self, rows):
        return self.item_to_spss.formats(rows)

    def column_widths(self):
        return self.item_to_spss.column_widths()

    def cells(self, value):
        if not self.width:
            return
        if value is not None:
            item_to_cells = self.item_to_spss.cells
            for item in value:
                for row in item_to_cells(item):
                    yield row


class SimpleToSPSS(ToSPSS):
    adapt_many(
        UntypedDomain,
        TextDomain,
        EnumDomain,
    )

    def var_types(self, rows):
        profile = self.profiles[-1]

        max_len = 0
        for row in rows:
            value = getattr(row, profile.tag)
            max_len = max(max_len, len(str(value)))

        max_len = min(max_len, SPSS_MAX_STRING_LENGTH)
        return {profile.tag: max_len}

    def formats(self, rows):
        profile = self.profiles[-1]

        max_len = 0
        for row in rows:
            value = getattr(row, profile.tag)
            max_len = max(max_len, len(str(value)))

        max_len = min(max_len, SPSS_MAX_STRING_LENGTH)
        format = 'A' + str(max_len)
        return {profile.tag: format}

    def cells(self, value):
        yield [value]


class BooleanToSPSS(ToSPSS):
    adapt(BooleanDomain)

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 5}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'A5'}


class IntegerToSPSS(ToSPSS):
    adapt(IntegerDomain)

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 0}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'F40'}


class FloatToSPSS(ToSPSS):
    adapt_many(FloatDomain)

    def cells(self, value):
        if value is None or math.isinf(value) or math.isnan(value):
            yield [None]
        else:
            yield [value]

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 0}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'F40.16'}


class DecimalToSPSS(ToSPSS):
    adapt(DecimalDomain)

    def cells(self, value):
        if value is None or not value.is_finite():
            yield [None]
        else:
            yield [value]

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 0}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'F40.16'}


class DateToSPSS(ToSPSS):
    adapt(DateDomain)

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 0}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'DATE11'}

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            unix_timestamp = (value - datetime.date.fromtimestamp(0)).total_seconds()
            yield [unix_timestamp + SPSS_GREGORIAN_OFFSET]


class TimeToSPSS(ToSPSS):
    adapt(TimeDomain)

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 0}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'TIME10'}

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            # value is a datetime.time object
            seconds = value.hour * 3600 + value.minute * 60 + value.second + value.microsecond / 1.0e6
            yield [seconds]


class DateTimeToSPSS(ToSPSS):
    adapt(DateTimeDomain)

    def var_types(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 0}

    def formats(self, rows):
        profile = self.profiles[-1]
        return {profile.tag: 'DATETIME22'}

    def cells(self, value):
        if value is None:
            yield [None]
        else:
            unix_timestamp = (value - datetime.datetime.fromtimestamp(0)).total_seconds()
            yield [unix_timestamp + SPSS_GREGORIAN_OFFSET]


class OpaqueToSPSS(ToSPSS):
    adapt(OpaqueDomain)

    def cells(self, value):
        if value is None:
            yield [None]
            return
        if not isinstance(value, unicode):
            try:
                value = str(value).decode('utf-8')
            except UnicodeDecodeError:
                value = unicode(repr(value))
        yield [value]


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
            writer_kwargs = {
                "savFileName": output_path,
                "varNames": product.var_names(),
                "varTypes": product.var_types(self.data),
                "formats": product.formats(self.data),
                "columnWidths": product.column_widths(),
                "ioUtf8": True,
            }

            with savReaderWriter.SavWriter(**writer_kwargs) as writer:
                for record in product.cells(self.data):
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
