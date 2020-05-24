"""A `dowel.logger.LogOutput` for CSV files."""
import csv
import warnings

from dowel import TabularInput
from dowel.simple_outputs import FileOutput
from dowel.utils import colorize


class CsvOutput(FileOutput):
    """CSV file output for logger.

    :param file_name: The file this output should log to.
    """

    def __init__(self, file_name):
        super().__init__(file_name, mode='r+')
        self._writer = None
        self._fieldnames = None
        self._warned_once = set()
        self._disable_warnings = False

    @property
    def types_accepted(self):
        """Accept TabularInput objects only."""
        return (TabularInput, )

    def record(self, data, prefix=''):
        """Log tabular data to CSV."""
        if isinstance(data, TabularInput):
            to_csv = data.as_primitive_dict

            if not to_csv.keys() and not self._writer:
                return

            if not self._writer:
                self._fieldnames = set(to_csv.keys())
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    restval='',
                    extrasaction='ignore')
                self._writer.writeheader()

            if to_csv.keys() != self._fieldnames:
                self._fieldnames |= to_csv.keys()
                if not set(to_csv.keys()).issubset(self._fieldnames):
                    self.add_key()
            else:
                self._writer.writerow(to_csv)

            for k in to_csv.keys():
                data.mark(k)
        else:
            raise ValueError('Unacceptable type.')

    def add_key(self, to_csv):
        """
        add key or keys from to_csv if they are not present in current log
        :param to_csv: data to be added to csv
        """
        rewrite_csv = list()
        reader = csv.DictReader(self._log_file)
        fieldnames = reader.fieldnames
        for row in reader:
            for key in to_csv.keys():
                if key not in fieldnames:
                    row[key] = ''
            rewrite_csv.append(dict(row))
        rewrite_csv.append(to_csv)
        writer = csv.DictWriter(self._log_file, fieldnames=set(to_csv.keys()))
        self._log_file.seek(0)
        writer.writeheader()
        writer.writerows(rewrite_csv)
        self._log_file.truncate()
